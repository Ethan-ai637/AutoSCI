#!/usr/bin/env python3
from pathlib import Path
import argparse, json, re, sys
from collections import defaultdict
from _common import load_jsonl

HEADING_RE = re.compile(r'^(#{1,6})\s+(.+?)\s*$', re.M)
ANCHOR_RE = re.compile(r'<!--\s*(CLAIM:[A-Za-z0-9_.:-]+)\s*-->')
COMMENT_RE = re.compile(r'<!--.*?-->', re.S)

SECTION_ALIASES = {
    'title':'Title','abstract':'Abstract','introduction':'Introduction','background':'Introduction',
    'methods':'Methods','materials and methods':'Methods','materials methods':'Methods','method':'Methods',
    'results':'Results','discussion':'Discussion','conclusion':'Conclusion','conclusions':'Conclusion'
}

def norm(s):
    return re.sub(r'\s+', ' ', str(s or '').strip()).lower()

def prose_norm(s):
    s=str(s or '')
    s=COMMENT_RE.sub('',s)
    s=re.sub(r'\[(?:@[^\]]+|\d[\d,;\-–— ]*)\]', ' ', s)
    s=re.sub(r'\([^()]*\b(?:19|20)\d{2}[a-z]?[^()]*\)', ' ', s)
    s=re.sub(r'[*_`]+','',s)
    return norm(s)

def canonical_section(s):
    s = re.sub(r'[^a-z ]+', '', norm(s))
    return SECTION_ALIASES.get(s, str(s or '').strip())

def object_key(label):
    s = norm(label).replace('–','-').replace('—','-')
    m = re.search(r'\b(?:fig(?:ure)?\.?)[ ]*(s?\d+)(?:\s*([a-z]))?', s, re.I)
    if m:
        return ('figure', m.group(1).lower(), (m.group(2) or '').lower())
    m = re.search(r'\btable[ ]*(s?\d+)(?:\s*([a-z]))?', s, re.I)
    if m:
        return ('table', m.group(1).lower(), (m.group(2) or '').lower())
    return None

def section_at(text, pos):
    current = 'Title'
    for m in HEADING_RE.finditer(text):
        if m.start() > pos:
            break
        current = canonical_section(m.group(2))
    return current

def anchor_block(text, match):
    start = match.start()
    end = text.find('\n\n', match.end())
    if end < 0:
        end = len(text)
    block = text[start:end]
    return norm(COMMENT_RE.sub('', block))

def main():
    ap=argparse.ArgumentParser(description='Audit active ledger claims against manuscript placement/text and figure/table identity.')
    ap.add_argument('workspace', nargs='?', default='.')
    ap.add_argument('--profile', choices=['draft','standard','release'], default='standard')
    ap.add_argument('--report')
    args=ap.parse_args()
    root=Path(args.workspace).resolve()
    claims=load_jsonl(root/'claims.jsonl')
    sources=load_jsonl(root/'sources.jsonl')
    evidence=load_jsonl(root/'evidence.jsonl')
    sm={s.get('source_id'):s for s in sources}
    ev={e.get('evidence_id'):e for e in evidence}
    manuscript=(root/'manuscript.md').read_text(encoding='utf-8') if (root/'manuscript.md').exists() else ''
    errors=[]; warnings=[]; details=[]

    anchor_matches=defaultdict(list)
    for m in ANCHOR_RE.finditer(manuscript):
        anchor_matches[m.group(1)].append(m)

    source_labels=defaultdict(set)
    active_claims=[c for c in claims if (c.get('lifecycle_state') or 'active')=='active']
    for c in active_claims:
        cid=c.get('claim_id','?')
        anchor=c.get('manuscript_anchor')
        if anchor:
            ms=anchor_matches.get(anchor, [])
            if not ms:
                msg=f'{cid}: manuscript anchor not found: {anchor}'
                (errors if args.profile=='release' else warnings).append(msg)
            elif len(ms)>1:
                errors.append(f'{cid}: manuscript anchor occurs {len(ms)} times: {anchor}')
            else:
                m=ms[0]
                actual=section_at(manuscript,m.start())
                declared=canonical_section(c.get('section'))
                if declared and actual and norm(declared)!=norm(actual):
                    msg=f'{cid}: declared section={declared} but anchor is under {actual}'
                    (errors if args.profile=='release' else warnings).append(msg)
                block=anchor_block(manuscript,m)
                txt=prose_norm(c.get('text'))
                normalized_block=prose_norm(block)
                if txt and txt not in normalized_block:
                    msg=f'{cid}: claim ledger text is not synchronized with its anchored manuscript block'
                    (errors if args.profile=='release' else warnings).append(msg)
                linked=[ev[eid] for eid in (c.get('evidence_ids') or []) if eid in ev]
                evidence_tokens=[]
                for e in linked:
                    evidence_tokens += [str(x) for x in (e.get('value_tokens') or []) if str(x)]
                required=c.get('required_value_tokens')
                if required is None:
                    required=evidence_tokens if c.get('claim_type')=='result' else []
                for tok in [str(x) for x in (required or []) if str(x)]:
                    if tok not in block:
                        msg=f'{cid}: anchored manuscript block is missing required value token: {tok}'
                        (errors if args.profile=='release' else warnings).append(msg)
                details.append({'claim_id':cid,'anchor':anchor,'declared_section':declared,'actual_section':actual})

        for ref in c.get('object_refs') or []:
            if not isinstance(ref,dict):
                continue
            sid=ref.get('source_id'); label=ref.get('label')
            if sid and label:
                source_labels[sid].add(object_key(label) or ('raw',norm(label)))
            if sid in sm and label and sm[sid].get('object_label'):
                expected=object_key(sm[sid].get('object_label'))
                actual=object_key(label)
                if expected and actual and expected != actual:
                    errors.append(f"{cid}: object_ref label {label!r} conflicts with source {sid} object_label {sm[sid].get('object_label')!r}")
                elif not expected and norm(sm[sid].get('object_label')) != norm(label):
                    msg=f"{cid}: object_ref label {label!r} differs from source {sid} object_label {sm[sid].get('object_label')!r}"
                    (errors if args.profile=='release' else warnings).append(msg)

    for sid, labels in source_labels.items():
        if len(labels)>1:
            errors.append(f'{sid}: same figure/table source is referenced with conflicting active labels: {sorted(map(str,labels))}')

    # Every manuscript CLAIM anchor should correspond to some ledger claim. Lifecycle audit decides whether an inactive one may remain.
    known={c.get('manuscript_anchor') for c in claims if c.get('manuscript_anchor')}
    for anchor in anchor_matches:
        if anchor not in known:
            msg=f'manuscript contains unregistered claim anchor: {anchor}'
            (errors if args.profile=='release' else warnings).append(msg)

    report={'ok':not errors,'profile':args.profile,'details':details,'errors':errors,'warnings':warnings,
            'summary':{'checked_active_claims':len(active_claims),'inactive_claims_skipped':len(claims)-len(active_claims),
                       'anchored_active_claims':sum(1 for c in active_claims if c.get('manuscript_anchor')),
                       'error_count':len(errors),'warning_count':len(warnings)}}
    if args.report:
        (root/args.report).write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    print(json.dumps(report,indent=2,ensure_ascii=False))
    sys.exit(0 if report['ok'] else 1)

if __name__=='__main__': main()
