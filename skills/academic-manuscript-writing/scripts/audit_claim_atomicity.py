#!/usr/bin/env python3
from pathlib import Path
import argparse, json, re, sys
from _common import load_json, load_jsonl

DEFAULT_TYPES={'result','method','limitation'}


def severity(profile, errors, warnings, msg):
    (errors if profile=='release' else warnings).append(msg)


def top_level_split(text):
    """Split obvious independent top-level propositions while protecting parenthetical statistics."""
    text=str(text or '').strip()
    if not text: return []
    chunks=[]; buf=[]; depth=0; i=0
    while i < len(text):
        ch=text[i]
        if ch in '([{': depth+=1
        elif ch in ')]}' and depth>0: depth-=1
        # top-level semicolons are strong compound-claim signals
        if ch==';' and depth==0:
            part=''.join(buf).strip(' ,;')
            if part: chunks.append(part)
            buf=[]; i+=1; continue
        # sentence boundary followed by uppercase/digit/markdown start
        if ch in '.?!' and depth==0 and i+1 < len(text):
            nxt=text[i+1:]
            m=re.match(r'\s+([A-Z0-9])',nxt)
            if m:
                buf.append(ch)
                part=''.join(buf).strip()
                if part: chunks.append(part)
                buf=[]; i+=1; continue
        buf.append(ch); i+=1
    part=''.join(buf).strip()
    if part: chunks.append(part)

    # A top-level contrast often joins distinct scientific propositions even without a semicolon.
    out=[]
    contrast=re.compile(r'\s+(?:whereas|while|however|but)\s+',re.I)
    for chunk in chunks:
        parts=contrast.split(chunk)
        out.extend([p.strip(' ,') for p in parts if p.strip(' ,')])
    return out


def material_clause(clause):
    c=clause.lower()
    # Ignore short connective fragments. Count a clause as material if it has quantitative content
    # or a scientific/provenance predicate that could stand as its own ledger proposition.
    if re.search(r'(?<![a-z])[-+]?\d+(?:\.\d+)?(?:e[-+]?\d+)?%?',c): return True
    return bool(re.search(r'\b(averag|achiev|outperform|higher|lower|increase|decrease|improv|report|show|support|suggest|indicat|demonstrat|specif|use[sd]?|label|reproduc|unresolved|conflict|cannot|does not|is not|lack|limited|overhead|latency|memory|caus|mechanism)\w*\b',c))


def main():
    ap=argparse.ArgumentParser(description='Audit high-risk claims for obvious compound scientific propositions.')
    ap.add_argument('workspace', nargs='?', default='.')
    ap.add_argument('--profile', choices=['draft','standard','release'], default='standard')
    ap.add_argument('--report')
    args=ap.parse_args()
    root=Path(args.workspace).resolve()
    project=load_json(root/'project.json')
    claims=load_jsonl(root/'claims.jsonl')
    evidence=load_jsonl(root/'evidence.jsonl') if (root/'evidence.jsonl').exists() else []
    ev={e.get('evidence_id'):e for e in evidence if e.get('evidence_id')}
    errors=[]; warnings=[]; details=[]

    policy=project.get('claim_atomicity_policy') or {}
    enforce_types=set(policy.get('enforce_claim_types') or sorted(DEFAULT_TYPES))
    max_clauses=int(policy.get('max_top_level_scientific_clauses',1))
    allow_exemptions=policy.get('allow_exemptions',True)

    for c in claims:
        if (c.get('lifecycle_state') or 'active')!='active': continue
        cid=c.get('claim_id','?'); ctype=c.get('claim_type')
        if ctype not in enforce_types: continue
        text=c.get('text') or ''
        clauses=top_level_split(text)
        material=[x for x in clauses if material_clause(x)]
        linked=[ev[eid] for eid in (c.get('evidence_ids') or []) if eid in ev]
        evidence_types=sorted({e.get('evidence_type') for e in linked if e.get('evidence_type')})
        exemption=str(c.get('atomicity_exemption_reason') or '').strip()

        issues=[]
        if len(material)>max_clauses:
            issues.append(f'{len(material)} top-level scientific clauses (max {max_clauses})')
        # Result claims that simultaneously depend on non-result evidence are high-risk compounds.
        if ctype=='result':
            non_result=[x for x in evidence_types if x not in {'result','figure_observation'}]
            if non_result:
                issues.append(f'result claim mixes evidence types {evidence_types}')
        if ctype=='method':
            non_method=[x for x in evidence_types if x not in {'method','user_fact'}]
            if non_method:
                issues.append(f'method claim mixes evidence types {evidence_types}')

        if issues:
            if exemption:
                if not allow_exemptions:
                    severity(args.profile,errors,warnings,f'{cid}: atomicity exemption is disabled by project policy')
                details.append({'claim_id':cid,'claim_type':ctype,'scientific_clauses':material,'issues':issues,'exempted':True,'reason':exemption})
            else:
                severity(args.profile,errors,warnings,
                         f"{cid}: obvious compound claim; split into atomic claims/companions or provide atomicity_exemption_reason ({'; '.join(issues)})")
                details.append({'claim_id':cid,'claim_type':ctype,'scientific_clauses':material,'issues':issues,'exempted':False})
        elif exemption:
            warnings.append(f'{cid}: atomicity_exemption_reason is present but no compound-claim signal was detected')

    report={'ok':not errors,'profile':args.profile,'details':details,'errors':errors,'warnings':warnings,
            'summary':{'checked_claim_count':sum(1 for c in claims if (c.get('lifecycle_state') or 'active')=='active' and c.get('claim_type') in enforce_types),
                       'compound_signal_count':len(details),'error_count':len(errors),'warning_count':len(warnings)}}
    if args.report:
        (root/args.report).write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    print(json.dumps(report,indent=2,ensure_ascii=False))
    sys.exit(0 if report['ok'] else 1)

if __name__=='__main__': main()
