#!/usr/bin/env python3
from pathlib import Path
import argparse, json, re, difflib
from _common import load_jsonl, sha256_file

HEADING=re.compile(r'^(#{1,6})\s+(.+?)\s*$')
COMMENT=re.compile(r'<!--.*?-->',re.S)


def section_blocks(text):
    lines=text.splitlines()
    blocks={}
    current='Preamble'; start=0
    for i,line in enumerate(lines):
        m=HEADING.match(line)
        if m:
            if current in blocks:
                n=2; key=f'{current} ({n})'
                while key in blocks: n+=1; key=f'{current} ({n})'
                blocks[key]='\n'.join(lines[start:i]).strip()
            else:
                blocks[current]='\n'.join(lines[start:i]).strip()
            current=m.group(2).strip(); start=i
    if current in blocks:
        n=2; key=f'{current} ({n})'
        while key in blocks: n+=1; key=f'{current} ({n})'
        blocks[key]='\n'.join(lines[start:]).strip()
    else:
        blocks[current]='\n'.join(lines[start:]).strip()
    return blocks


def anchor_block(text, anchor):
    if not anchor or anchor not in text: return None
    paras=re.split(r'\n\s*\n', text)
    for p in paras:
        if anchor in p: return p.strip()
    return None




def anchor_suffix(anchor):
    if isinstance(anchor,str) and anchor.startswith('CLAIM:') and len(anchor)>6:
        return anchor[6:]
    return None


def exact_claim_span(text, anchor):
    suffix=anchor_suffix(anchor)
    if not suffix: return None
    start_re=re.compile(r'<!--\s*'+re.escape(anchor)+r'\s*-->')
    end_re=re.compile(r'<!--\s*END-CLAIM:'+re.escape(suffix)+r'\s*-->')
    starts=list(start_re.finditer(text))
    ends=list(end_re.finditer(text))
    if len(starts)!=1 or len(ends)!=1: return None
    start=starts[0]; end=ends[0]
    if end.start() <= start.end(): return None
    return text[start.end():end.start()].strip()


def claim_comparison_blocks(old,new,claim):
    anchor=claim.get('manuscript_anchor')
    if not anchor:
        return None,None,'none'
    old_anchor_present=anchor in old
    new_anchor_present=anchor in new
    if not old_anchor_present or not new_anchor_present:
        return anchor_block(old,anchor), anchor_block(new,anchor), 'paragraph'
    if claim.get('anchor_precision')=='span':
        a=exact_claim_span(old,anchor); b=exact_claim_span(new,anchor)
        if a is not None and b is not None:
            return a,b,'exact_span'
        # A historical baseline may predate v1.8 end markers. Preserve revision-diff compatibility.
        return anchor_block(old,anchor), anchor_block(new,anchor), 'paragraph_fallback_legacy'
    return anchor_block(old,anchor), anchor_block(new,anchor), 'paragraph'

def clean_prose(text):
    text=COMMENT.sub(' ',text or '')
    # Markdown syntax and table separators should not dominate locality metrics.
    text=re.sub(r'^\s*#{1,6}\s+','',text,flags=re.M)
    text=re.sub(r'^\s*\|?\s*:?-{3,}.*$',' ',text,flags=re.M)
    text=re.sub(r'[`*_~]','',text)
    text=re.sub(r'\s+',' ',text).strip()
    return text


def tokens(text):
    return re.findall(r"[A-Za-z0-9]+(?:[._/+%-][A-Za-z0-9]+)*", clean_prose(text).lower())


def similarity(a,b):
    aa=tokens(a); bb=tokens(b)
    if not aa and not bb: return 1.0
    if not aa or not bb: return 0.0
    return difflib.SequenceMatcher(None,aa,bb,autojunk=False).ratio()


def prose_paragraphs(text):
    out=[]
    for raw in re.split(r'\n\s*\n', text or ''):
        p=clean_prose(raw)
        if not p: continue
        # Ignore naked headings / tiny structural fragments.
        if len(tokens(p)) < 4: continue
        out.append(p)
    return out


def first_title(text):
    for line in (text or '').splitlines():
        m=re.match(r'^#\s+(.+?)\s*$',line)
        if m: return m.group(1).strip()
    return None


def main():
    ap=argparse.ArgumentParser(description='Audit which manuscript sections and anchored claims changed between two drafts.')
    ap.add_argument('--old', required=True)
    ap.add_argument('--new', required=True)
    ap.add_argument('--claims', required=True)
    ap.add_argument('--report', default='revision_diff.json')
    args=ap.parse_args()
    old_path=Path(args.old); new_path=Path(args.new)
    old=old_path.read_text(encoding='utf-8')
    new=new_path.read_text(encoding='utf-8')
    claims=load_jsonl(Path(args.claims))
    ob=section_blocks(old); nb=section_blocks(new)
    changed_sections=[]
    section_similarity={}
    for sec in sorted(set(ob)|set(nb)):
        if ob.get(sec,'') != nb.get(sec,''):
            changed_sections.append(sec)
        section_similarity[sec]=round(similarity(ob.get(sec,''),nb.get(sec,'')),6)
    changed_claims=[]; removed=[]; added=[]; absent_both=[]
    for c in claims:
        anchor=c.get('manuscript_anchor')
        if not anchor: continue
        a,b,comparison_scope=claim_comparison_blocks(old,new,c)
        item={'claim_id':c.get('claim_id'),'claim_family_id':c.get('claim_family_id'),'section':c.get('section'),
              'lifecycle_state':c.get('lifecycle_state') or 'active','anchor':anchor,'comparison_scope':comparison_scope}
        if a is not None and b is not None:
            if a != b: changed_claims.append(item)
        elif a is not None and b is None:
            removed.append(item)
        elif a is None and b is not None:
            added.append(item)
        else:
            absent_both.append(item)
    legacy=[]
    for x in removed:
        legacy.append({'claim_id':x['claim_id'],'anchor':x['anchor'],'old_present':True,'new_present':False})
    for x in added:
        legacy.append({'claim_id':x['claim_id'],'anchor':x['anchor'],'old_present':False,'new_present':True})
    for x in absent_both:
        legacy.append({'claim_id':x['claim_id'],'anchor':x['anchor'],'old_present':False,'new_present':False})

    old_paras=prose_paragraphs(old); new_paras=prose_paragraphs(new)
    new_set=set(new_paras)
    preserved=sum(1 for p in old_paras if p in new_set)
    paragraph_fraction=(preserved/len(old_paras)) if old_paras else 1.0
    title_old=first_title(old); title_new=first_title(new)
    all_sections=set(ob)|set(nb)
    changed_fraction=(len(changed_sections)/len(all_sections)) if all_sections else 0.0

    locality={
        'prose_token_similarity':round(similarity(old,new),6),
        'old_word_count':len(tokens(old)),
        'new_word_count':len(tokens(new)),
        'old_paragraph_count':len(old_paras),
        'new_paragraph_count':len(new_paras),
        'exact_old_paragraphs_preserved':preserved,
        'preserved_old_paragraph_fraction':round(paragraph_fraction,6),
        'changed_section_fraction':round(changed_fraction,6),
        'section_similarity':section_similarity,
        'old_title':title_old,
        'new_title':title_new,
        'title_changed':title_old != title_new,
    }

    report={'schema_version':4,'old_manuscript_sha256':sha256_file(old_path),'new_manuscript_sha256':sha256_file(new_path),
            'changed_sections':changed_sections,'changed_claims':changed_claims,
            'removed_claim_anchors':removed,'added_claim_anchors':added,'anchors_absent_in_both':absent_both,
            'missing_or_moved_anchors':legacy,'locality':locality,
            'summary':{'changed_section_count':len(changed_sections),'changed_claim_count':len(changed_claims),
                       'removed_anchor_count':len(removed),'added_anchor_count':len(added),'absent_both_count':len(absent_both),
                       'anchor_transition_count':len(legacy)}}
    Path(args.report).write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    print(json.dumps(report,indent=2,ensure_ascii=False))

if __name__=='__main__': main()
