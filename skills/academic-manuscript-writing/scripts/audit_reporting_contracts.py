#!/usr/bin/env python3
from pathlib import Path
import argparse, json, sys
from collections import defaultdict
from _common import load_json, load_jsonl, section_roles

VALID_ROLES={'primary','secondary','sensitivity','exploratory'}

def main():
    ap=argparse.ArgumentParser(description='Audit main-result reporting contracts across evidence and manuscript sections.')
    ap.add_argument('workspace', nargs='?', default='.')
    ap.add_argument('--profile', choices=['draft','standard','release'], default='standard')
    ap.add_argument('--report')
    args=ap.parse_args()
    root=Path(args.workspace).resolve()
    project=load_json(root/'project.json')
    claims=load_jsonl(root/'claims.jsonl')
    active_claims=[c for c in claims if (c.get('lifecycle_state') or 'active')=='active']
    evidence=load_jsonl(root/'evidence.jsonl')
    plan=load_json(root/'section_plan.json') if (root/'section_plan.json').exists() else {}
    path=root/'reporting_contracts.jsonl'
    contracts=load_jsonl(path) if path.exists() else []
    errors=[]; warnings=[]; details=[]
    ev={e.get('evidence_id'):e for e in evidence}
    families=defaultdict(list)
    for c in active_claims:
        if c.get('claim_family_id'):
            families[c.get('claim_family_id')].append(c)
    method_coverage=defaultdict(list)
    qualifier_coverage=defaultdict(list)
    for c in active_claims:
        for eid in c.get('evidence_ids') or []:
            roles=section_roles(root, c.get('section'))
            if 'methods' in roles or c.get('claim_type')=='method': method_coverage[eid].append(c.get('claim_id'))
            if c.get('claim_type') in {'limitation','interpretation'} or roles & {'discussion','conclusion'}:
                qualifier_coverage[eid].append(c.get('claim_id'))

    main_families=set(plan.get('main_claim_families') or [])
    contract_families=set()
    seen=set()
    for r in contracts:
        rid=r.get('contract_id','?')
        if rid in seen: errors.append(f'duplicate reporting contract_id: {rid}')
        seen.add(rid)
        fid=r.get('claim_family_id')
        if not fid: errors.append(f'{rid}: missing claim_family_id'); continue
        contract_families.add(fid)
        if fid not in families: errors.append(f'{rid}: unknown/uninstantiated claim_family_id {fid}')
        role=r.get('role','primary')
        if role not in VALID_ROLES: warnings.append(f'{rid}: unusual role={role}')
        rows=families.get(fid,[])
        result_claim_evidence=set()
        family_sections={c.get('section') for c in rows}
        object_sources=set()
        for c in rows:
            if c.get('claim_type')=='result': result_claim_evidence.update(c.get('evidence_ids') or [])
            for ref in c.get('object_refs') or []:
                if isinstance(ref,dict) and ref.get('source_id'): object_sources.add(ref.get('source_id'))
        for eid in r.get('result_evidence_ids') or []:
            if eid not in ev: errors.append(f'{rid}: unknown result_evidence_id {eid}')
            elif ev[eid].get('evidence_type') not in {'result','figure_observation'}:
                warnings.append(f"{rid}: result_evidence_id {eid} has evidence_type={ev[eid].get('evidence_type')!r}")
            if eid not in result_claim_evidence:
                msg=f'{rid}: result evidence {eid} is not represented by a result claim in family {fid}'
                (errors if args.profile=='release' else warnings).append(msg)
        for eid in r.get('method_evidence_ids') or []:
            if eid not in ev:
                errors.append(f'{rid}: unknown method_evidence_id {eid}')
                continue
            if ev[eid].get('evidence_type')!='method': warnings.append(f"{rid}: method_evidence_id {eid} has evidence_type={ev[eid].get('evidence_type')!r}")
            if not method_coverage.get(eid):
                msg=f'{rid}: method evidence {eid} has no Methods/method claim'
                (errors if args.profile=='release' else warnings).append(msg)
        for eid in r.get('qualifier_evidence_ids') or []:
            if eid not in ev:
                errors.append(f'{rid}: unknown qualifier_evidence_id {eid}')
                continue
            if not qualifier_coverage.get(eid):
                msg=f'{rid}: qualifier evidence {eid} is not represented in a limitation/interpretive Discussion or Conclusion claim'
                (errors if args.profile=='release' else warnings).append(msg)
        for sid in r.get('object_source_ids') or []:
            if sid not in object_sources:
                msg=f'{rid}: expected figure/table source {sid} is not referenced by family {fid}'
                (errors if args.profile=='release' else warnings).append(msg)
        for sec in r.get('required_sections') or []:
            if sec not in family_sections:
                msg=f'{rid}: family {fid} missing required section {sec}'
                (errors if args.profile=='release' else warnings).append(msg)
        family_roles=set()
        for c in rows:
            family_roles.update(section_roles(root, c.get('section')))
        if r.get('abstract_eligible') is False and 'abstract' in family_roles:
            errors.append(f'{rid}: family {fid} appears in an abstract-role section but abstract_eligible=false')
        details.append({'contract_id':rid,'claim_family_id':fid,'role':role,'sections':sorted(x for x in family_sections if x)})

    scope=project.get('manuscript_scope','full_manuscript')
    if scope in {'full_manuscript','multi_section'} and main_families:
        missing=sorted(main_families-contract_families)
        if missing:
            msg=f'main claim families without reporting contracts: {missing}'
            (errors if args.profile=='release' else warnings).append(msg)

    report={'ok':not errors,'profile':args.profile,'contracts':details,'errors':errors,'warnings':warnings,
            'summary':{'contract_count':len(contracts),'error_count':len(errors),'warning_count':len(warnings)}}
    if args.report:
        (root/args.report).write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    print(json.dumps(report,indent=2,ensure_ascii=False))
    sys.exit(0 if report['ok'] else 1)

if __name__=='__main__': main()
