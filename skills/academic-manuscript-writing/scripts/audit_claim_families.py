#!/usr/bin/env python3
from pathlib import Path
import argparse, json, sys
from collections import defaultdict
from _common import load_jsonl, section_roles

ORDERED_SECTIONS = ['Title','Abstract','Introduction','Methods','Results','Discussion','Conclusion']

def main():
    ap=argparse.ArgumentParser(description='Audit cross-section consistency for active claim families.')
    ap.add_argument('workspace', nargs='?', default='.')
    ap.add_argument('--profile', choices=['draft','standard','release'], default='standard')
    ap.add_argument('--report')
    args=ap.parse_args()
    root=Path(args.workspace).resolve()
    claims=load_jsonl(root/'claims.jsonl')
    evidence=load_jsonl(root/'evidence.jsonl')
    ev={e.get('evidence_id'):e for e in evidence}
    fam=defaultdict(list)
    errors=[]; warnings=[]; details=[]
    inactive_count=0
    for c in claims:
        if (c.get('lifecycle_state') or 'active')!='active':
            inactive_count+=1
            continue
        fid=c.get('claim_family_id')
        if fid:
            fam[fid].append(c)
        elif args.profile in {'standard','release'} and c.get('claim_type') in {'result','interpretation','limitation'}:
            warnings.append(f"{c.get('claim_id')}: no claim_family_id; cross-section propagation cannot be audited")

    for fid, rows in sorted(fam.items()):
        sections={c.get('section') for c in rows if c.get('section')}
        roles=set()
        for c in rows:
            roles.update(section_roles(root, c.get('section')))
        result_rows=[c for c in rows if c.get('claim_type')=='result']
        strengths={c.get('strength') for c in rows if c.get('strength')}
        scopes={c.get('source_scope') for c in rows if c.get('source_scope')}
        result_evidence=[set(c.get('evidence_ids') or []) for c in result_rows]
        shared=set.intersection(*result_evidence) if len(result_evidence)>1 else (result_evidence[0] if result_evidence else set())
        if 'causal' in strengths and any(s in strengths for s in {'descriptive','associational'}):
            msg=f'{fid}: inconsistent claim strength across active sections: {sorted(strengths)}'
            (errors if args.profile=='release' else warnings).append(msg)
        if len(scopes)>1:
            warnings.append(f'{fid}: source_scope differs across active sections: {sorted(scopes)}')
        if len(result_rows)>1 and not shared:
            warnings.append(f'{fid}: active result claims across sections share no evidence_id; verify they express the same scientific claim')
        if 'abstract' in roles and result_rows and 'results' not in roles:
            msg=f'{fid}: active empirical claim appears in an abstract-role section without a results-role family counterpart'
            (errors if args.profile=='release' else warnings).append(msg)
        if 'conclusion' in roles and result_rows and not ({'results','discussion'} & roles):
            msg=f'{fid}: active empirical claim appears in a conclusion-role section without results/discussion family counterpart'
            (errors if args.profile=='release' else warnings).append(msg)
        for c in rows:
            for eid in c.get('evidence_ids') or []:
                if eid not in ev:
                    errors.append(f"{c.get('claim_id')}: family {fid} references unknown evidence_id {eid}")
        details.append({
            'claim_family_id':fid,
            'claim_ids':[c.get('claim_id') for c in rows],
            'sections':sorted(sections, key=lambda x: ORDERED_SECTIONS.index(x) if x in ORDERED_SECTIONS else 999),
            'scientific_roles':sorted(roles),
            'strengths':sorted(strengths),
            'shared_result_evidence_ids':sorted(shared)
        })
    report={'ok':not errors,'profile':args.profile,'families':details,'errors':errors,'warnings':warnings,
            'summary':{'family_count':len(fam),'inactive_claims_skipped':inactive_count,'error_count':len(errors),'warning_count':len(warnings)}}
    if args.report:
        (root/args.report).write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    print(json.dumps(report,indent=2,ensure_ascii=False))
    sys.exit(0 if report['ok'] else 1)

if __name__=='__main__': main()
