#!/usr/bin/env python3
from pathlib import Path
import argparse, json, sys
from _common import load_jsonl, load_json

VALID_ORIGINS={'reviewer','editor','user','internal_audit'}
VALID_DISPOSITIONS={'pending','completed','not_applicable','declined_with_rationale'}
VALID_ACTIONS={'manuscript_change','analysis','citation','clarification','no_change'}
VALID_VERIFY={'pending','verified','blocked'}


def main():
    ap=argparse.ArgumentParser(description='Audit reviewer/editor/user revision obligations against verified changes and revision diff.')
    ap.add_argument('workspace', nargs='?', default='.')
    ap.add_argument('--profile', choices=['draft','standard','release'], default='standard')
    ap.add_argument('--report')
    args=ap.parse_args()
    root=Path(args.workspace).resolve()
    path=root/'revision_obligations.jsonl'
    obligations=load_jsonl(path) if path.exists() else []
    revisions=load_jsonl(root/'revision_log.jsonl') if (root/'revision_log.jsonl').exists() else []
    claims=load_jsonl(root/'claims.jsonl')
    evidence=load_jsonl(root/'evidence.jsonl')
    sources=load_jsonl(root/'sources.jsonl')
    diff=load_json(root/'revision_diff.json') if (root/'revision_diff.json').exists() else None
    errors=[]; warnings=[]; details=[]

    rev_by_id={}
    for r in revisions:
        rid=r.get('change_id')
        if not rid:
            errors.append('revision_log row missing change_id')
            continue
        if rid in rev_by_id:
            errors.append(f'duplicate revision change_id: {rid}')
        rev_by_id[rid]=r
    claim_ids={c.get('claim_id') for c in claims if c.get('claim_id')}
    evidence_ids={e.get('evidence_id') for e in evidence if e.get('evidence_id')}
    source_ids={s.get('source_id') for s in sources if s.get('source_id')}
    for r in revisions:
        rid=r.get('change_id','?')
        if r.get('verification') not in {'pending','verified','blocked'}:
            warnings.append(f'{rid}: unusual revision verification={r.get("verification")!r}')
        for cid in r.get('affected_claim_ids') or []:
            if cid not in claim_ids:
                errors.append(f'{rid}: revision references unknown affected claim_id {cid}')
        for sid in r.get('source_ids') or []:
            if sid not in source_ids:
                warnings.append(f'{rid}: revision source_id {sid} is not represented by any evidence row')
    seen=set()
    changed_claim_ids=set(); changed_sections=set(); anchor_issue_ids=set()
    if diff:
        changed_claim_ids={x.get('claim_id') for x in diff.get('changed_claims',[]) if x.get('claim_id')}
        changed_sections=set(diff.get('changed_sections') or [])
        transitions=(diff.get('removed_claim_anchors') or []) + (diff.get('added_claim_anchors') or [])
        if not transitions:
            transitions=diff.get('missing_or_moved_anchors',[]) or []
        anchor_issue_ids={x.get('claim_id') for x in transitions if x.get('claim_id')}

    for o in obligations:
        oid=o.get('obligation_id','?')
        if oid in seen: errors.append(f'duplicate obligation_id: {oid}')
        seen.add(oid)
        origin=o.get('origin')
        disposition=o.get('disposition','pending')
        verification=o.get('verification','pending')
        actions=set(o.get('required_actions') or [])
        cids=list(o.get('affected_claim_ids') or [])
        eids=list(o.get('evidence_ids') or [])
        chids=list(o.get('change_ids') or [])
        sections=set(o.get('affected_sections') or [])

        if origin not in VALID_ORIGINS: warnings.append(f'{oid}: unusual origin={origin!r}')
        if disposition not in VALID_DISPOSITIONS: errors.append(f'{oid}: invalid disposition={disposition!r}')
        if verification not in VALID_VERIFY: errors.append(f'{oid}: invalid verification={verification!r}')
        unknown_actions=actions-VALID_ACTIONS
        if unknown_actions: errors.append(f'{oid}: unknown required_actions={sorted(unknown_actions)}')
        if 'manuscript_change' in actions and 'no_change' in actions:
            errors.append(f'{oid}: required_actions cannot contain both manuscript_change and no_change')
        for cid in cids:
            if cid not in claim_ids: errors.append(f'{oid}: unknown affected claim_id {cid}')
        for eid in eids:
            if eid not in evidence_ids: errors.append(f'{oid}: unknown evidence_id {eid}')
        for chid in chids:
            if chid not in rev_by_id: errors.append(f'{oid}: unknown revision change_id {chid}')

        if disposition in {'not_applicable','declined_with_rationale'} and not str(o.get('rationale') or '').strip():
            msg=f'{oid}: disposition={disposition} requires rationale'
            (errors if args.profile=='release' else warnings).append(msg)

        if disposition=='completed':
            if verification!='verified':
                msg=f'{oid}: completed obligation is not verification=verified'
                (errors if args.profile=='release' else warnings).append(msg)
            if 'manuscript_change' in actions:
                if not chids:
                    msg=f'{oid}: manuscript_change obligation has no linked change_ids'
                    (errors if args.profile=='release' else warnings).append(msg)
                linked=[rev_by_id[x] for x in chids if x in rev_by_id]
                unverified=[r.get('change_id') for r in linked if r.get('verification')!='verified']
                if unverified:
                    msg=f'{oid}: linked revision changes are not verified: {unverified}'
                    (errors if args.profile=='release' else warnings).append(msg)
                if args.profile=='release':
                    if diff is None:
                        errors.append(f'{oid}: release manuscript_change obligation requires revision_diff.json')
                    else:
                        if cids and not (set(cids) & (changed_claim_ids|anchor_issue_ids)):
                            errors.append(f'{oid}: revision_diff shows no affected claim change/removal for {sorted(cids)}')
                        if sections and not (sections & changed_sections):
                            errors.append(f'{oid}: revision_diff shows no change in declared affected_sections {sorted(sections)}')
            if actions & {'analysis','citation'} and not (eids or chids):
                msg=f'{oid}: completed {sorted(actions & {"analysis","citation"})} obligation has neither evidence_ids nor change_ids'
                (errors if args.profile=='release' else warnings).append(msg)

        if args.profile=='release' and disposition=='pending':
            errors.append(f'{oid}: release obligation is still pending')
        if args.profile=='release' and disposition=='completed' and origin in {'reviewer','editor'} and not str(o.get('response_text') or '').strip():
            warnings.append(f'{oid}: completed reviewer/editor obligation has empty response_text')

        details.append({'obligation_id':oid,'origin':origin,'disposition':disposition,'verification':verification,
                        'required_actions':sorted(actions),'change_ids':chids,'affected_claim_ids':cids})

    report={'ok':not errors,'profile':args.profile,'obligations':details,'errors':errors,'warnings':warnings,
            'summary':{'obligation_count':len(obligations),'pending_count':sum(1 for x in details if x['disposition']=='pending'),
                       'completed_count':sum(1 for x in details if x['disposition']=='completed'),
                       'error_count':len(errors),'warning_count':len(warnings)}}
    if args.report:
        (root/args.report).write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    print(json.dumps(report,indent=2,ensure_ascii=False))
    sys.exit(0 if report['ok'] else 1)

if __name__=='__main__': main()
