#!/usr/bin/env python3
from pathlib import Path
import argparse, json, re, sys
from collections import defaultdict
from _common import load_json, load_jsonl

HEADING_RE = re.compile(r'^(#{1,6})\s+(.+?)\s*$', re.M)
ANCHOR_RE = re.compile(r'<!--\s*(CLAIM:[A-Za-z0-9_.:-]+)\s*-->')
COMMENT_RE = re.compile(r'<!--.*?-->', re.S)
EXEMPT_RE = re.compile(r'<!--\s*COVERAGE:EXEMPT\s+reason=["\']([^"\']+)["\']\s*-->', re.I)
BRACKET_RE = re.compile(r'\[([^\]]*@[^\]]+)\]')
CITE_KEY_RE = re.compile(r'@([A-Za-z0-9_.:-]+)')
OBJECT_RE = re.compile(r'\b(?:Fig(?:ure)?\.?|Table)\s*(S?\d+)(?:\s*([A-Za-z]))?', re.I)

SECTION_ALIASES = {
    'title':'Title','abstract':'Abstract','introduction':'Introduction','background':'Introduction',
    'methods':'Methods','materials and methods':'Methods','materials methods':'Methods','method':'Methods',
    'results':'Results','discussion':'Discussion','conclusion':'Conclusion','conclusions':'Conclusion'
}
DEFAULT_REQUIRED_SECTIONS = ['Abstract','Methods','Results','Discussion','Conclusion']
VALID_PRESENCE = {'required','optional','not_in_manuscript'}


def norm(s):
    return re.sub(r'\s+', ' ', str(s or '').strip()).lower()


def canonical_section(s):
    raw = str(s or '').strip()
    key = re.sub(r'[^a-z ]+', '', norm(raw))
    return SECTION_ALIASES.get(key, raw)


def object_key(label):
    s = norm(label).replace('–','-').replace('—','-')
    m = re.search(r'\b(?:fig(?:ure)?\.?)\s*(s?\d+)(?:\s*([a-z]))?', s, re.I)
    if m:
        return ('figure', m.group(1).lower(), (m.group(2) or '').lower())
    m = re.search(r'\btable\s*(s?\d+)(?:\s*([a-z]))?', s, re.I)
    if m:
        return ('table', m.group(1).lower(), (m.group(2) or '').lower())
    return None


def split_sections(text):
    matches=list(HEADING_RE.finditer(text))
    if not matches:
        return [('Title',0,len(text),text)]
    out=[]
    if matches[0].start()>0:
        out.append(('Title',0,matches[0].start(),text[:matches[0].start()]))
    for i,m in enumerate(matches):
        start=m.end(); end=matches[i+1].start() if i+1<len(matches) else len(text)
        out.append((canonical_section(m.group(2)),start,end,text[start:end]))
    return out


def split_paragraphs(section_text, base_offset):
    out=[]
    cursor=0
    for part in re.split(r'\n\s*\n', section_text):
        idx=section_text.find(part,cursor)
        if idx < 0:
            idx=cursor
        cursor=idx+len(part)
        raw=part.strip()
        if raw:
            lead=len(part)-len(part.lstrip())
            out.append((base_offset+idx+lead,raw))
    return out


def visible_prose(raw):
    return re.sub(r'\s+',' ',COMMENT_RE.sub('',raw)).strip()


def citation_keys(raw):
    keys=[]
    for b in BRACKET_RE.finditer(raw):
        keys.extend(CITE_KEY_RE.findall(b.group(1)))
    return keys


def object_refs(raw):
    refs=[]
    for m in OBJECT_RE.finditer(raw):
        token=m.group(0)
        # object_key needs the Fig/Table family, preserved in token.
        k=object_key(token)
        if k:
            refs.append((token,k))
    return refs


def severity(profile, errors, warnings, msg):
    (errors if profile=='release' else warnings).append(msg)


def main():
    ap=argparse.ArgumentParser(description='Audit bidirectional claim/manuscript coverage plus reverse citation and figure/table identity.')
    ap.add_argument('workspace', nargs='?', default='.')
    ap.add_argument('--profile', choices=['draft','standard','release'], default='standard')
    ap.add_argument('--report')
    args=ap.parse_args()
    root=Path(args.workspace).resolve()
    project=load_json(root/'project.json')
    claims=load_jsonl(root/'claims.jsonl')
    sources=load_jsonl(root/'sources.jsonl')
    manuscript=(root/'manuscript.md').read_text(encoding='utf-8') if (root/'manuscript.md').exists() else ''
    errors=[]; warnings=[]; details=[]

    policy=project.get('coverage_policy') or {}
    required_sections=[canonical_section(x) for x in (policy.get('required_sections') or DEFAULT_REQUIRED_SECTIONS)]
    required_sections=set(required_sections)
    allow_exemptions=policy.get('allow_exemptions', True)
    scope=project.get('manuscript_scope','full_manuscript')

    claim_by_anchor={}
    active_claims=[]
    for c in claims:
        if (c.get('lifecycle_state') or 'active')!='active':
            continue
        active_claims.append(c)
        a=c.get('manuscript_anchor')
        if a:
            claim_by_anchor.setdefault(a,[]).append(c)

    # Forward closure: current ledger claims intended for core manuscript sections must resolve to manuscript anchors.
    for c in active_claims:
        cid=c.get('claim_id','?')
        section=canonical_section(c.get('section'))
        presence=c.get('manuscript_presence')
        if presence is None:
            presence='required' if section in required_sections and scope in {'full_manuscript','multi_section'} else 'optional'
        if presence not in VALID_PRESENCE:
            errors.append(f'{cid}: invalid manuscript_presence={presence!r}')
            continue
        anchor=c.get('manuscript_anchor')
        if presence=='required' and not anchor:
            severity(args.profile,errors,warnings,f'{cid}: active claim requires manuscript presence but has no manuscript_anchor')
        if presence=='not_in_manuscript':
            if not str(c.get('manuscript_presence_reason') or '').strip():
                severity(args.profile,errors,warnings,f'{cid}: manuscript_presence=not_in_manuscript requires manuscript_presence_reason')
            if anchor and anchor in manuscript:
                severity(args.profile,errors,warnings,f'{cid}: claim is marked not_in_manuscript but its anchor is present in manuscript')

    citation_source={}
    for s in sources:
        ck=s.get('citation_key')
        if ck:
            citation_source.setdefault(str(ck),[]).append(s.get('source_id'))

    source_object=defaultdict(list)
    for s in sources:
        sid=s.get('source_id')
        for label in [s.get('object_label'),s.get('locator')]:
            k=object_key(label)
            if k and sid not in source_object[k]:
                source_object[k].append(sid)

    paragraph_counter=defaultdict(int)
    uncovered=[]; exemptions=[]
    for section,start,end,body in split_sections(manuscript):
        if section not in required_sections:
            continue
        for pos,raw in split_paragraphs(body,start):
            prose=visible_prose(raw)
            if not prose:
                continue
            paragraph_counter[section]+=1
            pid=f'{section}:{paragraph_counter[section]}'
            ex=EXEMPT_RE.search(raw)
            if ex:
                reason=ex.group(1).strip()
                if not allow_exemptions:
                    severity(args.profile,errors,warnings,f'{pid}: coverage exemption is not allowed by project coverage_policy')
                elif not reason:
                    severity(args.profile,errors,warnings,f'{pid}: coverage exemption has no reason')
                exemptions.append({'paragraph_id':pid,'section':section,'reason':reason,'preview':prose[:180]})
                continue

            anchors=ANCHOR_RE.findall(raw)
            active=[]
            unknown=[]
            for a in anchors:
                rows=claim_by_anchor.get(a,[])
                if rows: active.extend(rows)
                else: unknown.append(a)
            if not anchors:
                uncovered.append({'paragraph_id':pid,'section':section,'preview':prose[:220]})
                severity(args.profile,errors,warnings,f'{pid}: scientific manuscript paragraph has no claim anchor')
            elif not active:
                severity(args.profile,errors,warnings,f'{pid}: paragraph has claim anchors but none resolve to active ledger claims: {anchors}')

            if unknown:
                severity(args.profile,errors,warnings,f'{pid}: paragraph contains unregistered/inactive claim anchors: {sorted(set(unknown))}')

            declared_citations=set()
            declared_objects=set()
            for c in active:
                declared_citations.update(str(x) for x in (c.get('citation_keys') or []))
                for ref in c.get('object_refs') or []:
                    if isinstance(ref,dict):
                        k=object_key(ref.get('label'))
                        if k: declared_objects.add(k)

            for key in citation_keys(raw):
                if key not in citation_source:
                    severity(args.profile,errors,warnings,f'{pid}: manuscript citation key @{key} has no matching source citation_key')
                if active and key not in declared_citations:
                    severity(args.profile,errors,warnings,f'{pid}: manuscript citation @{key} is not declared by any active claim in the paragraph')

            for token,k in object_refs(raw):
                mapped=source_object.get(k,[])
                if not mapped:
                    severity(args.profile,errors,warnings,f'{pid}: manuscript object reference {token!r} has no matching source object_label/locator')
                elif len(mapped)>1:
                    severity(args.profile,errors,warnings,f'{pid}: manuscript object reference {token!r} maps ambiguously to sources {mapped}')
                if active and k not in declared_objects:
                    severity(args.profile,errors,warnings,f'{pid}: manuscript object reference {token!r} is not declared in object_refs of an active claim in the paragraph')

            details.append({'paragraph_id':pid,'section':section,'anchors':anchors,'active_claim_ids':[c.get('claim_id') for c in active],
                            'citation_keys':citation_keys(raw),'object_refs':[x[0] for x in object_refs(raw)],'preview':prose[:180]})

    report={
        'ok':not errors,
        'profile':args.profile,
        'coverage_policy':{'required_sections':sorted(required_sections),'allow_exemptions':allow_exemptions},
        'paragraphs':details,
        'uncovered_paragraphs':uncovered,
        'exemptions':exemptions,
        'errors':errors,
        'warnings':warnings,
        'summary':{
            'active_claim_count':len(active_claims),
            'checked_paragraph_count':len(details)+len(exemptions),
            'uncovered_paragraph_count':len(uncovered),
            'exemption_count':len(exemptions),
            'error_count':len(errors),
            'warning_count':len(warnings),
        }
    }
    if args.report:
        (root/args.report).write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    print(json.dumps(report,indent=2,ensure_ascii=False))
    sys.exit(0 if report['ok'] else 1)

if __name__=='__main__':
    main()
