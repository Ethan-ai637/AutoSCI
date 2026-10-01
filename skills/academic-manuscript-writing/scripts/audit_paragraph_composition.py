#!/usr/bin/env python3
from pathlib import Path
import argparse, json, re, sys
from collections import defaultdict
from _common import load_jsonl

HEADING_RE = re.compile(r'^(#{1,6})\s+(.+?)\s*$', re.M)
CLAIM_RE = re.compile(r'<!--\s*(CLAIM:[A-Za-z0-9_.:-]+)\s*-->')
PARAGRAPH_RE = re.compile(r'<!--\s*PARAGRAPH:([A-Za-z0-9_.:-]+)\s*-->')
COMMENT_RE = re.compile(r'<!--.*?-->', re.S)
SECTION_ALIASES = {
    'title':'Title','abstract':'Abstract','introduction':'Introduction','background':'Introduction',
    'methods':'Methods','materials and methods':'Methods','materials methods':'Methods','method':'Methods',
    'results':'Results','discussion':'Discussion','conclusion':'Conclusion','conclusions':'Conclusion'
}
VALID_COMPOSITIONS = {'additive','comparison','contrast','qualified','result_interpretation','synthesis','method_context'}
VALID_COMPANION_SCOPES = {'same_paragraph','same_section','manuscript'}


def norm(s):
    return re.sub(r'\s+', ' ', str(s or '').strip()).lower()


def canonical_section(s):
    raw=str(s or '').strip()
    key=re.sub(r'[^a-z ]+','',norm(raw))
    return SECTION_ALIASES.get(key, raw)


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
    out=[]; cursor=0
    for part in re.split(r'\n\s*\n', section_text):
        idx=section_text.find(part,cursor)
        if idx<0: idx=cursor
        cursor=idx+len(part)
        raw=part.strip()
        if raw:
            lead=len(part)-len(part.lstrip())
            out.append((base_offset+idx+lead, raw))
    return out


def severity(profile, errors, warnings, msg):
    (errors if profile=='release' else warnings).append(msg)


def main():
    ap=argparse.ArgumentParser(description='Audit multi-claim paragraph composition contracts and required claim companions.')
    ap.add_argument('workspace', nargs='?', default='.')
    ap.add_argument('--profile', choices=['draft','standard','release'], default='standard')
    ap.add_argument('--report')
    args=ap.parse_args()
    root=Path(args.workspace).resolve()
    claims=load_jsonl(root/'claims.jsonl') if (root/'claims.jsonl').exists() else []
    contracts=load_jsonl(root/'paragraph_contracts.jsonl') if (root/'paragraph_contracts.jsonl').exists() else []
    manuscript=(root/'manuscript.md').read_text(encoding='utf-8') if (root/'manuscript.md').exists() else ''
    errors=[]; warnings=[]; details=[]

    active=[c for c in claims if (c.get('lifecycle_state') or 'active')=='active']
    by_id={c.get('claim_id'):c for c in active if c.get('claim_id')}
    by_anchor=defaultdict(list)
    for c in active:
        if c.get('manuscript_anchor'):
            by_anchor[c.get('manuscript_anchor')].append(c)

    contract_by_id={}
    for i,row in enumerate(contracts,1):
        pid=row.get('paragraph_id')
        if not pid:
            errors.append(f'paragraph_contracts.jsonl row {i} missing paragraph_id')
            continue
        if pid in contract_by_id:
            errors.append(f'duplicate paragraph_id in paragraph_contracts.jsonl: {pid}')
        contract_by_id[pid]=row
        composition=row.get('composition')
        if composition not in VALID_COMPOSITIONS:
            errors.append(f'{pid}: invalid composition={composition!r}')
        claim_ids=row.get('claim_ids') or []
        if len(set(claim_ids))!=len(claim_ids):
            errors.append(f'{pid}: duplicate claim_ids in paragraph contract')
        for cid in claim_ids:
            if cid not in by_id:
                severity(args.profile,errors,warnings,f'{pid}: contract references unknown/inactive claim_id {cid}')
        primary=row.get('primary_claim_id')
        if primary and primary not in claim_ids:
            errors.append(f'{pid}: primary_claim_id {primary} is not in claim_ids')
        qualifiers=row.get('qualifier_claim_ids') or []
        if any(q not in claim_ids for q in qualifiers):
            errors.append(f'{pid}: qualifier_claim_ids must be a subset of claim_ids')
        if composition=='qualified' and not qualifiers:
            errors.append(f'{pid}: composition=qualified requires qualifier_claim_ids')
        for tok in row.get('required_text_tokens') or []:
            if not str(tok): errors.append(f'{pid}: required_text_tokens cannot contain empty values')
        for term in row.get('forbidden_terms') or []:
            if not str(term): errors.append(f'{pid}: forbidden_terms cannot contain empty values')

    paragraph_locations=[]
    section_claims=defaultdict(set)
    manuscript_claims=set()
    paragraph_for_claim=defaultdict(list)
    seen_paragraph_ids=defaultdict(int)
    counters=defaultdict(int)

    for section,start,end,body in split_sections(manuscript):
        for pos,raw in split_paragraphs(body,start):
            prose=re.sub(r'\s+',' ',COMMENT_RE.sub('',raw)).strip()
            anchors=CLAIM_RE.findall(raw)
            rows=[]
            for a in anchors:
                rows.extend(by_anchor.get(a,[]))
            claim_ids=[]
            for c in rows:
                cid=c.get('claim_id')
                if cid and cid not in claim_ids: claim_ids.append(cid)
            pids=PARAGRAPH_RE.findall(raw)
            counters[section]+=1
            display=f'{section}:{counters[section]}'
            for pid in pids: seen_paragraph_ids[pid]+=1
            for cid in claim_ids:
                manuscript_claims.add(cid); section_claims[section].add(cid); paragraph_for_claim[cid].append(display)
            paragraph_locations.append({'display':display,'section':section,'raw':raw,'prose':prose,'claim_ids':claim_ids,'paragraph_ids':pids})

            if len(claim_ids)>=2:
                if len(pids)!=1:
                    severity(args.profile,errors,warnings,f'{display}: multi-claim paragraph requires exactly one PARAGRAPH:<id> marker')
                else:
                    pid=pids[0]; contract=contract_by_id.get(pid)
                    if not contract:
                        severity(args.profile,errors,warnings,f'{display}: multi-claim paragraph {pid} has no paragraph_contracts.jsonl entry')
                    else:
                        declared=contract.get('claim_ids') or []
                        if set(declared)!=set(claim_ids):
                            severity(args.profile,errors,warnings,f'{pid}: contract claim_ids {sorted(declared)} do not match manuscript paragraph claims {sorted(claim_ids)}')
                        if canonical_section(contract.get('section'))!=section:
                            severity(args.profile,errors,warnings,f'{pid}: contract section={contract.get("section")!r} but manuscript paragraph is under {section}')
                        ctypes={by_id[c].get('claim_type') for c in claim_ids if c in by_id}
                        if contract.get('composition')=='result_interpretation' and not ({'result','interpretation'} <= ctypes):
                            severity(args.profile,errors,warnings,f'{pid}: result_interpretation requires at least one result claim and one interpretation claim')
                        if contract.get('composition')=='qualified':
                            missing=[q for q in (contract.get('qualifier_claim_ids') or []) if q not in claim_ids]
                            if missing:
                                severity(args.profile,errors,warnings,f'{pid}: qualified paragraph is missing qualifier claims {missing}')
                        pnorm=norm(prose)
                        for tok in contract.get('required_text_tokens') or []:
                            if norm(tok) not in pnorm:
                                severity(args.profile,errors,warnings,f'{pid}: required paragraph text token not found: {tok}')
                        for term in contract.get('forbidden_terms') or []:
                            if norm(term) in pnorm:
                                severity(args.profile,errors,warnings,f'{pid}: forbidden paragraph term found: {term}')
                        details.append({'paragraph_id':pid,'location':display,'section':section,'claim_ids':claim_ids,'composition':contract.get('composition')})
            elif pids:
                if len(pids)>1:
                    errors.append(f'{display}: paragraph has multiple PARAGRAPH markers: {pids}')
                else:
                    pid=pids[0]; contract=contract_by_id.get(pid)
                    if not contract:
                        severity(args.profile,errors,warnings,f'{display}: paragraph marker {pid} has no paragraph contract')
                    else:
                        declared=contract.get('claim_ids') or []
                        if set(declared)!=set(claim_ids):
                            severity(args.profile,errors,warnings,f'{pid}: contract claim_ids {sorted(declared)} do not match manuscript paragraph claims {sorted(claim_ids)}')

    for pid,count in seen_paragraph_ids.items():
        if count>1: errors.append(f'PARAGRAPH:{pid} occurs {count} times in manuscript')
    for pid in contract_by_id:
        if seen_paragraph_ids.get(pid,0)==0:
            severity(args.profile,errors,warnings,f'{pid}: paragraph contract is not represented by a manuscript PARAGRAPH marker')

    # Claim-level companion constraints. They protect qualifiers/limitations from being dropped during revision.
    for c in active:
        cid=c.get('claim_id','?')
        for i,comp in enumerate(c.get('required_companions') or [],1):
            if not isinstance(comp,dict):
                errors.append(f'{cid}: required_companions entry {i} must be an object')
                continue
            target=comp.get('claim_id'); scope=comp.get('scope','same_paragraph')
            if scope not in VALID_COMPANION_SCOPES:
                errors.append(f'{cid}: invalid required companion scope={scope!r}')
                continue
            if target not in by_id:
                severity(args.profile,errors,warnings,f'{cid}: required companion {target} is unknown or inactive')
                continue
            if cid not in manuscript_claims:
                continue
            if scope=='manuscript':
                ok=target in manuscript_claims
            elif scope=='same_section':
                source_sections=[p['section'] for p in paragraph_locations if cid in p['claim_ids']]
                ok=any(target in section_claims[s] for s in source_sections)
            else:
                ok=any(cid in p['claim_ids'] and target in p['claim_ids'] for p in paragraph_locations)
            if not ok:
                severity(args.profile,errors,warnings,f'{cid}: required companion {target} is not present in scope={scope}')

    report={
        'ok':not errors,
        'profile':args.profile,
        'paragraph_contract_count':len(contracts),
        'details':details,
        'errors':errors,
        'warnings':warnings,
        'summary':{
            'active_claim_count':len(active),
            'multi_claim_paragraph_count':sum(1 for p in paragraph_locations if len(p['claim_ids'])>=2),
            'paragraph_contract_count':len(contracts),
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
