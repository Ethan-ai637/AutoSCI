#!/usr/bin/env python3
from pathlib import Path
import argparse, json, re, sys
from collections import defaultdict
from _common import load_json, load_jsonl

HEADING_RE = re.compile(r'^(#{1,6})\s+(.+?)\s*$', re.M)
START_RE = re.compile(r'<!--\s*(CLAIM:([A-Za-z0-9_.:-]+))\s*-->')
END_RE = re.compile(r'<!--\s*END-CLAIM:([A-Za-z0-9_.:-]+)\s*-->')
COMMENT_RE = re.compile(r'<!--.*?-->', re.S)
COVERAGE_EXEMPT_RE = re.compile(r'<!--\s*COVERAGE:EXEMPT\s+reason=["\']([^"\']+)["\']\s*-->', re.I)
SPAN_EXEMPT_RE = re.compile(r'<!--\s*SPAN-COVERAGE:EXEMPT\s+reason=["\']([^"\']+)["\']\s*-->', re.I)
BRACKET_RE = re.compile(r'\[([^\]]*@[^\]]+)\]')
CITE_KEY_RE = re.compile(r'@([A-Za-z0-9_.:-]+)')
NUMERIC_CITE_RE = re.compile(r'\[(?:\s*\d+\s*)(?:(?:[,;]|[-–—])\s*\d+\s*)*\]')
OBJECT_RE = re.compile(r'\b(?:Fig(?:ure)?\.?|Table)\s*(S?\d+)(?:\s*([A-Za-z]))?', re.I)
WORD_RE = re.compile(r"\b[\w][\w'’-]*\b", re.UNICODE)

SECTION_ALIASES = {
    'title':'Title','abstract':'Abstract','introduction':'Introduction','background':'Introduction',
    'methods':'Methods','materials and methods':'Methods','materials methods':'Methods','method':'Methods',
    'results':'Results','discussion':'Discussion','conclusion':'Conclusion','conclusions':'Conclusion'
}
DEFAULT_REQUIRED_SECTIONS = ['Abstract','Methods','Results','Discussion','Conclusion']
DEFAULT_REQUIRED_TYPES = ['result','method','interpretation','limitation','literature_context']
VALID_PRECISION = {'paragraph','span'}


def norm(s):
    return re.sub(r'\s+', ' ', str(s or '').strip()).lower()


def semantic_norm(s):
    s = str(s or '')
    s = COMMENT_RE.sub('', s)
    s = re.sub(r'\[[^\]]*@[^\]]+\]', ' ', s)
    s = re.sub(r'[*_`]+', '', s)
    return norm(s)


def canonical_section(s):
    raw = str(s or '').strip()
    key = re.sub(r'[^a-z ]+', '', norm(raw))
    return SECTION_ALIASES.get(key, raw)


def split_sections(text):
    matches = list(HEADING_RE.finditer(text))
    if not matches:
        return [('Title', 0, len(text), text)]
    out = []
    if matches[0].start() > 0:
        out.append(('Title', 0, matches[0].start(), text[:matches[0].start()]))
    for i, m in enumerate(matches):
        start = m.end(); end = matches[i+1].start() if i+1 < len(matches) else len(text)
        out.append((canonical_section(m.group(2)), start, end, text[start:end]))
    return out


def split_paragraphs(section_text, base_offset):
    out=[]; cursor=0
    for part in re.split(r'\n\s*\n', section_text):
        idx=section_text.find(part,cursor)
        if idx < 0: idx=cursor
        cursor=idx+len(part)
        raw=part.strip()
        if raw:
            lead=len(part)-len(part.lstrip())
            out.append((base_offset+idx+lead, base_offset+idx+lead+len(raw), raw))
    return out


def section_at(text, pos):
    current='Title'
    for m in HEADING_RE.finditer(text):
        if m.start() > pos: break
        current=canonical_section(m.group(2))
    return current


def citation_keys(raw):
    keys=[]
    for b in BRACKET_RE.finditer(raw):
        keys.extend(CITE_KEY_RE.findall(b.group(1)))
    return keys


def object_key(label):
    s=norm(label).replace('–','-').replace('—','-')
    m=re.search(r'\b(?:fig(?:ure)?\.?)\s*(s?\d+)(?:\s*([a-z]))?',s,re.I)
    if m: return ('figure',m.group(1).lower(),(m.group(2) or '').lower())
    m=re.search(r'\btable\s*(s?\d+)(?:\s*([a-z]))?',s,re.I)
    if m: return ('table',m.group(1).lower(),(m.group(2) or '').lower())
    return None


def object_refs(raw):
    refs=[]
    for m in OBJECT_RE.finditer(raw):
        token=m.group(0); k=object_key(token)
        if k: refs.append((token,k))
    return refs


def severity(profile, errors, warnings, msg):
    (errors if profile=='release' else warnings).append(msg)


def version_tuple(v):
    try:
        parts=[int(x) for x in str(v).split('.')[:2]]
        return tuple((parts+[0,0])[:2])
    except Exception:
        return (0,0)


def manuscript_anchor_suffix(anchor):
    if isinstance(anchor,str) and anchor.startswith('CLAIM:') and len(anchor)>6:
        return anchor[6:]
    return None


def main():
    ap=argparse.ArgumentParser(description='Audit exact claim spans, span-scoped references, and sentence/span coverage closure.')
    ap.add_argument('workspace', nargs='?', default='.')
    ap.add_argument('--profile', choices=['draft','standard','release'], default='standard')
    ap.add_argument('--report')
    args=ap.parse_args()
    root=Path(args.workspace).resolve()
    project=load_json(root/'project.json')
    claims=load_jsonl(root/'claims.jsonl')
    sources=load_jsonl(root/'sources.jsonl')
    evidence=load_jsonl(root/'evidence.jsonl')
    manuscript=(root/'manuscript.md').read_text(encoding='utf-8') if (root/'manuscript.md').exists() else ''
    errors=[]; warnings=[]; details=[]; exemptions=[]; uncovered=[]

    policy=project.get('claim_span_policy') or {}
    enabled = version_tuple(project.get('skill_version')) >= (1,8) or bool(policy)
    if not enabled:
        report={'ok':True,'profile':args.profile,'enabled':False,'errors':[],'warnings':[],
                'summary':{'checked_span_claims':0,'error_count':0,'warning_count':0}}
        if args.report:
            (root/args.report).write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
        print(json.dumps(report,indent=2,ensure_ascii=False)); return

    required_sections={canonical_section(x) for x in (policy.get('required_sections') or DEFAULT_REQUIRED_SECTIONS)}
    required_types=set(policy.get('required_claim_types') or DEFAULT_REQUIRED_TYPES)
    allow_exemptions=policy.get('allow_exemptions', True)
    max_uncovered=policy.get('max_uncovered_words_per_paragraph', 2)
    exact_text=policy.get('require_exact_claim_text', True)
    reverse_refs=policy.get('enforce_reverse_references', True)

    ev={e.get('evidence_id'):e for e in evidence}
    active=[c for c in claims if (c.get('lifecycle_state') or 'active')=='active']
    by_id={c.get('claim_id'):c for c in active if c.get('claim_id')}
    by_anchor=defaultdict(list)
    for c in active:
        if c.get('manuscript_anchor'): by_anchor[c.get('manuscript_anchor')].append(c)

    citation_source={}
    for s in sources:
        ck=s.get('citation_key')
        if ck: citation_source.setdefault(str(ck),[]).append(s.get('source_id'))
    source_object=defaultdict(list)
    for s in sources:
        sid=s.get('source_id')
        for label in [s.get('object_label'),s.get('locator')]:
            k=object_key(label)
            if k and sid not in source_object[k]: source_object[k].append(sid)

    starts_by_suffix=defaultdict(list)
    ends_by_suffix=defaultdict(list)
    for m in START_RE.finditer(manuscript): starts_by_suffix[m.group(2)].append(m)
    for m in END_RE.finditer(manuscript): ends_by_suffix[m.group(1)].append(m)

    spans=[]
    paragraph_fallback_anchors=set()
    for c in active:
        cid=c.get('claim_id','?')
        section=canonical_section(c.get('section'))
        ctype=c.get('claim_type')
        presence=c.get('manuscript_presence')
        if presence=='not_in_manuscript':
            continue
        required = section in required_sections and ctype in required_types
        precision=c.get('anchor_precision') or 'paragraph'
        exemption=str(c.get('span_exemption_reason') or '').strip()
        if precision not in VALID_PRECISION:
            errors.append(f'{cid}: invalid anchor_precision={precision!r}')
            continue
        if required and precision!='span':
            if allow_exemptions and exemption:
                paragraph_fallback_anchors.add(c.get('manuscript_anchor'))
                exemptions.append({'claim_id':cid,'type':'claim_fallback','reason':exemption})
            else:
                severity(args.profile,errors,warnings,f'{cid}: v1.8 span policy requires anchor_precision=span in {section}/{ctype}')
            continue
        if precision!='span':
            continue
        anchor=c.get('manuscript_anchor')
        suffix=manuscript_anchor_suffix(anchor)
        if not suffix:
            severity(args.profile,errors,warnings,f'{cid}: span claim requires manuscript_anchor in CLAIM:<id> form')
            continue
        sm=starts_by_suffix.get(suffix,[]); em=ends_by_suffix.get(suffix,[])
        if len(sm)!=1:
            severity(args.profile,errors,warnings,f'{cid}: span claim requires exactly one start marker <!-- {anchor} -->; found {len(sm)}')
            continue
        if len(em)!=1:
            severity(args.profile,errors,warnings,f'{cid}: span claim requires exactly one end marker <!-- END-CLAIM:{suffix} -->; found {len(em)}')
            continue
        start=sm[0]; end=em[0]
        if end.start() <= start.end():
            errors.append(f'{cid}: END-CLAIM marker occurs before claim span content')
            continue
        actual_section=section_at(manuscript,start.start())
        end_section=section_at(manuscript,end.start())
        if actual_section!=end_section:
            errors.append(f'{cid}: claim span crosses manuscript sections: {actual_section} -> {end_section}')
        if section and actual_section and norm(section)!=norm(actual_section):
            severity(args.profile,errors,warnings,f'{cid}: declared section={section} but span is under {actual_section}')
        raw_span=manuscript[start.end():end.start()]
        visible=semantic_norm(raw_span)
        declared=semantic_norm(c.get('text'))
        if exact_text and declared!=visible:
            severity(args.profile,errors,warnings,f'{cid}: span text does not exactly match claim ledger text after citation/format normalization')
        elif not exact_text and declared and declared not in visible:
            severity(args.profile,errors,warnings,f'{cid}: claim ledger text is not contained in exact manuscript span')
        required_tokens=c.get('required_value_tokens')
        if required_tokens is None:
            inferred=[]
            if ctype=='result':
                for eid in c.get('evidence_ids') or []:
                    e=ev.get(eid)
                    if e: inferred.extend(str(x) for x in (e.get('value_tokens') or []) if str(x))
            required_tokens=inferred
        for tok in [str(x) for x in (required_tokens or []) if str(x)]:
            if tok not in raw_span:
                severity(args.profile,errors,warnings,f'{cid}: exact claim span is missing required value token: {tok}')

        actual_cites=set(citation_keys(raw_span)); declared_cites=set(str(x) for x in (c.get('citation_keys') or []))
        if reverse_refs:
            for m in NUMERIC_CITE_RE.finditer(raw_span):
                severity(args.profile,errors,warnings,f'{cid}: unstructured numeric citation {m.group(0)!r} cannot be reverse-audited at claim-span level; use structured citation keys')
            for key in actual_cites:
                if key not in citation_source:
                    severity(args.profile,errors,warnings,f'{cid}: span citation @{key} has no matching source citation_key')
                if key not in declared_cites:
                    severity(args.profile,errors,warnings,f'{cid}: span citation @{key} is not declared by this claim')
            for key in declared_cites-actual_cites:
                severity(args.profile,errors,warnings,f'{cid}: declared citation_key @{key} is not present inside the exact claim span')

        declared_objects={}
        for ref in c.get('object_refs') or []:
            if isinstance(ref,dict):
                k=object_key(ref.get('label'))
                if k: declared_objects.setdefault(k,[]).append(ref.get('source_id'))
        actual_objects=object_refs(raw_span)
        if reverse_refs:
            for token,k in actual_objects:
                mapped=source_object.get(k,[])
                if not mapped:
                    severity(args.profile,errors,warnings,f'{cid}: span object reference {token!r} has no matching source object_label/locator')
                elif len(mapped)>1:
                    severity(args.profile,errors,warnings,f'{cid}: span object reference {token!r} maps ambiguously to sources {mapped}')
                if k not in declared_objects:
                    severity(args.profile,errors,warnings,f'{cid}: span object reference {token!r} is not declared in this claim object_refs')
                elif mapped and not (set(declared_objects.get(k,[])) & set(mapped)):
                    severity(args.profile,errors,warnings,f'{cid}: span object reference {token!r} resolves to {mapped} but this claim declares sources {declared_objects.get(k,[])}')
            actual_keys={k for _,k in actual_objects}
            for k in set(declared_objects)-actual_keys:
                severity(args.profile,errors,warnings,f'{cid}: declared object_ref {k} is not present inside the exact claim span')

        span={'claim_id':cid,'anchor':anchor,'suffix':suffix,'start':start.start(),'content_start':start.end(),
              'content_end':end.start(),'end':end.end(),'section':actual_section,'raw':raw_span}
        spans.append(span)
        details.append({'claim_id':cid,'section':actual_section,'anchor_precision':'span',
                        'citation_keys':sorted(actual_cites),'object_refs':[x[0] for x in actual_objects],
                        'preview':re.sub(r'\s+',' ',COMMENT_RE.sub('',raw_span)).strip()[:180]})

    # Forbid overlapping/nested exact spans. Composition should use adjacent atomic spans, not ambiguous nesting.
    ordered=sorted(spans,key=lambda x:(x['start'],x['end']))
    for i,a in enumerate(ordered):
        for b in ordered[i+1:]:
            if b['start'] >= a['end']: break
            errors.append(f"claim spans overlap: {a['claim_id']} and {b['claim_id']}")

    # Orphan END markers and END markers for paragraph-only claims are suspicious in a governed v1.8 manuscript.
    active_suffixes={manuscript_anchor_suffix(c.get('manuscript_anchor')) for c in active if manuscript_anchor_suffix(c.get('manuscript_anchor'))}
    for suffix,ms in ends_by_suffix.items():
        if suffix not in active_suffixes:
            severity(args.profile,errors,warnings,f'manuscript contains END-CLAIM:{suffix} with no active ledger claim')

    # Span coverage closure: covered sections may not contain material visible prose outside exact spans.
    span_intervals=[(s['start'],s['end'],s['claim_id']) for s in spans]
    counters=defaultdict(int)
    for section,sstart,send,body in split_sections(manuscript):
        if section not in required_sections: continue
        for pstart,pend,raw in split_paragraphs(body,sstart):
            visible_all=re.sub(r'\s+',' ',COMMENT_RE.sub('',raw)).strip()
            if not visible_all: continue
            counters[section]+=1; pid=f'{section}:{counters[section]}'
            if COVERAGE_EXEMPT_RE.search(raw):
                continue
            anchors=START_RE.findall(raw)
            anchor_tokens=[x[0] for x in anchors]
            if any(a in paragraph_fallback_anchors for a in anchor_tokens):
                continue

            chars=list(manuscript[pstart:pend])
            covering=[]
            for a,b,cid in span_intervals:
                lo=max(a,pstart); hi=min(b,pend)
                if lo < hi:
                    covering.append(cid)
                    for j in range(lo-pstart,hi-pstart): chars[j]=' '
            outside=''.join(chars)
            outside=COMMENT_RE.sub(' ',outside)
            outside=re.sub(r'\[([^\]]*@[A-Za-z0-9_.:-]+[^\]]*)\]',' ',outside)
            outside=re.sub(r'[*_`#>|\-]+',' ',outside)
            words=WORD_RE.findall(outside)
            if len(words) > max_uncovered:
                ex=SPAN_EXEMPT_RE.search(raw)
                if ex and allow_exemptions and ex.group(1).strip():
                    exemptions.append({'paragraph_id':pid,'type':'span_coverage','reason':ex.group(1).strip(),'uncovered_words':words[:20]})
                else:
                    uncovered.append({'paragraph_id':pid,'section':section,'uncovered_word_count':len(words),
                                      'uncovered_preview':' '.join(words[:24]),'covering_claim_ids':covering})
                    severity(args.profile,errors,warnings,f'{pid}: {len(words)} visible words fall outside exact claim spans: {" ".join(words[:16])}')

    report={
        'ok':not errors,'profile':args.profile,'enabled':True,
        'claim_span_policy':{
            'required_sections':sorted(required_sections),
            'required_claim_types':sorted(required_types),
            'allow_exemptions':allow_exemptions,
            'max_uncovered_words_per_paragraph':max_uncovered,
            'require_exact_claim_text':exact_text,
            'enforce_reverse_references':reverse_refs,
        },
        'spans':details,'exemptions':exemptions,'uncovered':uncovered,
        'errors':errors,'warnings':warnings,
        'summary':{
            'active_claim_count':len(active),'checked_span_claims':len(spans),
            'span_exemption_count':len(exemptions),'uncovered_paragraph_count':len(uncovered),
            'error_count':len(errors),'warning_count':len(warnings)
        }
    }
    if args.report:
        (root/args.report).write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    print(json.dumps(report,indent=2,ensure_ascii=False))
    sys.exit(0 if report['ok'] else 1)

if __name__=='__main__':
    main()
