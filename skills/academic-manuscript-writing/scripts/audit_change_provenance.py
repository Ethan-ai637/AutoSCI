#!/usr/bin/env python3
from pathlib import Path
import argparse, json, sys
from _common import load_json, load_jsonl, sha256_file
from _state import build_state, compare_record_maps


def add_msg(profile, errors, warnings, msg, release_hard=True):
    if profile == 'release' and release_hard:
        errors.append(msg)
    else:
        warnings.append(msg)


def main():
    ap = argparse.ArgumentParser(description='Audit semantic changes against a prior workspace checkpoint and verified revision records.')
    ap.add_argument('workspace', nargs='?', default='.')
    ap.add_argument('--profile', choices=['draft','standard','release'], default='standard')
    ap.add_argument('--baseline', default='workspace_state.previous.json')
    ap.add_argument('--report')
    args = ap.parse_args()
    root = Path(args.workspace).resolve()
    project = load_json(root/'project.json')
    mode = project.get('mode', 'build')
    baseline_path = root/args.baseline
    errors=[]; warnings=[]

    current, _ = build_state(root)
    if not baseline_path.exists():
        if mode in {'revise','refresh'}:
            add_msg(args.profile, errors, warnings,
                    f'{mode} workflow has no {args.baseline}; capture the pre-edit state before making material changes',
                    release_hard=True)
        report = {
            'ok': not errors,
            'profile': args.profile,
            'mode': mode,
            'baseline_present': False,
            'current_state_id': current['state_id'],
            'errors': errors,
            'warnings': warnings,
            'changes': {},
        }
        if args.report:
            (root/args.report).write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
        print(json.dumps(report,indent=2,ensure_ascii=False))
        sys.exit(0 if report['ok'] else 1)

    try:
        baseline = load_json(baseline_path)
    except Exception as e:
        errors.append(f'{args.baseline}: {e}')
        baseline = {}

    if baseline.get('schema_version') != 1:
        warnings.append(f'{args.baseline}: unexpected schema_version={baseline.get("schema_version")!r}')
    if baseline.get('project_id') and baseline.get('project_id') != project.get('project_id'):
        errors.append(f'{args.baseline}: project_id does not match current project')

    changes={}
    for group in ['sources','evidence','claims','reporting_contracts','paragraph_contracts','writing_sources']:
        changes[group]=compare_record_maps((baseline.get('records') or {}).get(group,{}), (current.get('records') or {}).get(group,{}))

    old_files=baseline.get('files') or {}
    new_files=current.get('files') or {}
    changed_files=sorted(name for name in set(old_files)|set(new_files) if old_files.get(name) != new_files.get(name))
    changes['changed_semantic_files']=changed_files
    changes['source_artifacts']=compare_record_maps(baseline.get('source_files') or {}, current.get('source_files') or {})
    changes['writing_source_artifacts']=compare_record_maps(baseline.get('writing_source_files') or {}, current.get('writing_source_files') or {})
    manuscript_changed = old_files.get('manuscript.md') != new_files.get('manuscript.md')

    revisions=load_jsonl(root/'revision_log.jsonl') if (root/'revision_log.jsonl').exists() else []
    baseline_id=baseline.get('state_id')
    material_file_changes=list(changes['changed_semantic_files'])
    any_semantic_change = bool(material_file_changes or changes['source_artifacts']['added'] or changes['source_artifacts']['removed'] or changes['source_artifacts']['changed'] or changes['writing_source_artifacts']['added'] or changes['writing_source_artifacts']['removed'] or changes['writing_source_artifacts']['changed'])
    baseline_bound=[r for r in revisions if r.get('verification')=='verified' and r.get('base_state_id')==baseline_id]
    verified=[r for r in baseline_bound if r.get('verified_state_id')==current.get('state_id')]
    stale_verified=[r.get('change_id') for r in baseline_bound if r.get('verified_state_id') != current.get('state_id')]
    if stale_verified and mode in {'revise','refresh'}:
        add_msg(args.profile, errors, warnings,
                f'verified revision rows are not bound to the current semantic state {current.get("state_id")}: {stale_verified}',
                release_hard=True)
    if mode in {'revise','refresh'} and any_semantic_change and not verified:
        add_msg(args.profile, errors, warnings,
                f'current semantic state differs from baseline {baseline_id}, but no verified revision_log row is bound to both the baseline and current state',
                release_hard=True)

    covered_claims=set()
    covered_evidence=set()
    covered_sources=set()
    covered_writing_sources=set()
    covered_artifacts=set()
    covered_sections=set()
    for r in verified:
        covered_claims.update(r.get('affected_claim_ids') or [])
        covered_evidence.update(r.get('affected_evidence_ids') or [])
        covered_sources.update(r.get('source_ids') or [])
        covered_writing_sources.update(r.get('writing_source_ids') or [])
        covered_artifacts.update(r.get('changed_artifacts') or [])
        covered_sections.update(r.get('affected_sections') or [])

    changed_claim_ids=set(changes['claims']['added']+changes['claims']['removed']+changes['claims']['changed'])
    missing_claims=sorted(changed_claim_ids-covered_claims)
    if missing_claims and mode in {'revise','refresh'}:
        add_msg(args.profile, errors, warnings,
                f'semantic claim changes are not covered by a verified revision record bound to the baseline: {missing_claims}',
                release_hard=True)

    changed_evidence_ids=set(changes['evidence']['added']+changes['evidence']['removed']+changes['evidence']['changed'])
    missing_evidence=sorted(changed_evidence_ids-covered_evidence)
    if missing_evidence and mode in {'revise','refresh'}:
        add_msg(args.profile, errors, warnings,
                f'evidence ledger changes are not covered by affected_evidence_ids in a verified revision record: {missing_evidence}',
                release_hard=True)

    changed_source_ids=set(changes['sources']['added']+changes['sources']['removed']+changes['sources']['changed']+changes['source_artifacts']['added']+changes['source_artifacts']['removed']+changes['source_artifacts']['changed'])
    missing_sources=sorted(changed_source_ids-covered_sources)
    if missing_sources and mode in {'revise','refresh'}:
        add_msg(args.profile, errors, warnings,
                f'source ledger changes are not covered by source_ids in a verified revision record: {missing_sources}',
                release_hard=True)

    changed_writing_source_ids=set(changes['writing_sources']['added']+changes['writing_sources']['removed']+changes['writing_sources']['changed']+changes['writing_source_artifacts']['added']+changes['writing_source_artifacts']['removed']+changes['writing_source_artifacts']['changed'])
    missing_writing_sources=sorted(changed_writing_source_ids-covered_writing_sources)
    if missing_writing_sources and mode in {'revise','refresh'}:
        add_msg(args.profile, errors, warnings,
                f'writing-source changes are not covered by writing_source_ids in a verified revision record: {missing_writing_sources}',
                release_hard=True)

    governed_artifacts={'project.json','section_plan.json','reporting_contracts.jsonl','paragraph_contracts.jsonl','writing_profile.json','manuscript_contract.json'}
    changed_governed=sorted(set(changed_files)&governed_artifacts)
    missing_artifacts=sorted(set(changed_governed)-covered_artifacts)
    if missing_artifacts and mode in {'revise','refresh'}:
        add_msg(args.profile, errors, warnings,
                f'governed manuscript contracts changed without changed_artifacts coverage in a verified revision record: {missing_artifacts}',
                release_hard=True)

    diff_path=root/'revision_diff.json'
    diff=None
    if manuscript_changed and mode in {'revise','refresh'}:
        if not diff_path.exists():
            add_msg(args.profile, errors, warnings,
                    'manuscript.md changed from the baseline but revision_diff.json is missing',
                    release_hard=True)
        else:
            try:
                diff=load_json(diff_path)
                old_sha=diff.get('old_manuscript_sha256')
                new_sha=diff.get('new_manuscript_sha256')
                if old_sha != old_files.get('manuscript.md'):
                    add_msg(args.profile, errors, warnings,
                            'revision_diff.json old_manuscript_sha256 does not match the baseline manuscript hash',
                            release_hard=True)
                if new_sha != new_files.get('manuscript.md'):
                    add_msg(args.profile, errors, warnings,
                            'revision_diff.json new_manuscript_sha256 does not match the current manuscript hash',
                            release_hard=True)
                diff_sections=set(diff.get('changed_sections') or [])
                if verified and diff_sections and not (diff_sections & covered_sections):
                    add_msg(args.profile, errors, warnings,
                            'revision_diff.json reports manuscript section changes, but verified baseline-bound revision rows do not cover any changed section',
                            release_hard=True)
            except Exception as e:
                errors.append(f'revision_diff.json: {e}')

    if not any_semantic_change and verified:
        warnings.append('verified baseline-bound revision records exist, but the current semantic state is identical to the baseline')

    report={
        'ok': not errors,
        'profile': args.profile,
        'mode': mode,
        'baseline_present': True,
        'baseline_state_id': baseline_id,
        'current_state_id': current.get('state_id'),
        'changes': changes,
        'coverage': {
            'verified_change_ids': [r.get('change_id') for r in verified],
            'stale_verified_change_ids': stale_verified,
            'covered_claim_ids': sorted(covered_claims),
            'covered_evidence_ids': sorted(covered_evidence),
            'covered_source_ids': sorted(covered_sources),
            'covered_artifacts': sorted(covered_artifacts),
            'covered_sections': sorted(covered_sections),
        },
        'errors': errors,
        'warnings': warnings,
    }
    if args.report:
        (root/args.report).write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    print(json.dumps(report,indent=2,ensure_ascii=False))
    sys.exit(0 if report['ok'] else 1)

if __name__=='__main__':
    main()
