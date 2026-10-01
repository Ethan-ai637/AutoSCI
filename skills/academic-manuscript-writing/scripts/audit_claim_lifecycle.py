#!/usr/bin/env python3
from pathlib import Path
import argparse, json, re, sys
from collections import defaultdict
from _common import load_json, load_jsonl

VALID_LIFECYCLE={'active','superseded','retired'}
COMMENT_RE=re.compile(r'<!--.*?-->', re.S)

def norm(s):
    s=COMMENT_RE.sub(' ', str(s or ''))
    s=re.sub(r'\s+',' ',s).strip().lower()
    return s

def main():
    ap=argparse.ArgumentParser(description='Audit active/superseded/retired claim lifecycle and manuscript residue.')
    ap.add_argument('workspace', nargs='?', default='.')
    ap.add_argument('--profile', choices=['draft','standard','release'], default='standard')
    ap.add_argument('--report')
    args=ap.parse_args()
    root=Path(args.workspace).resolve()
    claims=load_jsonl(root/'claims.jsonl')
    manuscript=(root/'manuscript.md').read_text(encoding='utf-8') if (root/'manuscript.md').exists() else ''
    plan=load_json(root/'section_plan.json') if (root/'section_plan.json').exists() else {}
    errors=[]; warnings=[]; details=[]
    by_id={c.get('claim_id'):c for c in claims if c.get('claim_id')}
    active_families=set()
    family_states=defaultdict(set)

    for c in claims:
        cid=c.get('claim_id','?')
        state=c.get('lifecycle_state') or 'active'
        if state not in VALID_LIFECYCLE:
            errors.append(f'{cid}: invalid lifecycle_state={state!r}')
            continue
        fid=c.get('claim_family_id')
        if fid:
            family_states[fid].add(state)
            if state=='active': active_families.add(fid)
        supersedes=list(c.get('supersedes_claim_ids') or [])
        superseded_by=list(c.get('superseded_by_claim_ids') or [])
        anchor=c.get('manuscript_anchor')
        anchor_present=bool(anchor and anchor in manuscript)
        text_present=bool(norm(c.get('text')) and norm(c.get('text')) in norm(manuscript))

        for old_id in supersedes:
            if old_id not in by_id:
                errors.append(f'{cid}: supersedes unknown claim_id {old_id}')
            else:
                old=by_id[old_id]
                if (old.get('lifecycle_state') or 'active')=='active':
                    msg=f'{cid}: supersedes {old_id}, but the older claim is still lifecycle_state=active'
                    (errors if args.profile=='release' else warnings).append(msg)
                if cid not in (old.get('superseded_by_claim_ids') or []):
                    msg=f'{cid}: supersession link to {old_id} is not reciprocal in superseded_by_claim_ids'
                    (errors if args.profile=='release' else warnings).append(msg)
        for new_id in superseded_by:
            if new_id not in by_id:
                errors.append(f'{cid}: superseded_by unknown claim_id {new_id}')
            elif cid not in (by_id[new_id].get('supersedes_claim_ids') or []):
                msg=f'{cid}: superseded_by link to {new_id} is not reciprocal in supersedes_claim_ids'
                (errors if args.profile=='release' else warnings).append(msg)

        if state=='active':
            if superseded_by:
                warnings.append(f'{cid}: active claim declares superseded_by_claim_ids; verify lifecycle direction')
        elif state=='superseded':
            if not superseded_by:
                msg=f'{cid}: superseded claim has no superseded_by_claim_ids'
                (errors if args.profile=='release' else warnings).append(msg)
            else:
                active_targets=[x for x in superseded_by if x in by_id and (by_id[x].get('lifecycle_state') or 'active')=='active']
                if not active_targets:
                    msg=f'{cid}: superseded claim has no active replacement claim'
                    (errors if args.profile=='release' else warnings).append(msg)
        elif state=='retired':
            if superseded_by:
                warnings.append(f'{cid}: retired claim also declares superseded_by_claim_ids; use superseded when there is a direct replacement')
            if not str(c.get('retirement_reason') or '').strip():
                msg=f'{cid}: retired claim has no retirement_reason'
                (errors if args.profile=='release' else warnings).append(msg)

        if state in {'superseded','retired'}:
            if anchor_present:
                msg=f'{cid}: inactive claim anchor still appears in current manuscript: {anchor}'
                (errors if args.profile in {'standard','release'} else warnings).append(msg)
            if text_present:
                msg=f'{cid}: inactive claim text still appears verbatim in current manuscript'
                (errors if args.profile=='release' else warnings).append(msg)

        details.append({'claim_id':cid,'claim_family_id':fid,'lifecycle_state':state,'anchor_present':anchor_present,'text_present':text_present})

    main_families=set(plan.get('main_claim_families') or [])
    for fid in sorted(main_families):
        if fid not in active_families:
            msg=f'section_plan main claim family {fid} has no active claims'
            (errors if args.profile=='release' else warnings).append(msg)

    report={'ok':not errors,'profile':args.profile,'claims':details,'errors':errors,'warnings':warnings,
            'summary':{'active':sum(1 for x in details if x['lifecycle_state']=='active'),
                       'superseded':sum(1 for x in details if x['lifecycle_state']=='superseded'),
                       'retired':sum(1 for x in details if x['lifecycle_state']=='retired'),
                       'error_count':len(errors),'warning_count':len(warnings)}}
    if args.report:
        (root/args.report).write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    print(json.dumps(report,indent=2,ensure_ascii=False))
    sys.exit(0 if report['ok'] else 1)

if __name__=='__main__': main()
