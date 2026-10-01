#!/usr/bin/env python3
from pathlib import Path
import argparse, json, re, sys
from _common import load_json, load_jsonl

DEFAULT_META_TERMS=[
    'this refresh',
    'this refreshed',
    'supplied methods notes',
    'supplied current table',
    'supplied current results',
    'allowed sources',
    'source-conflict note',
    'benchmark materials',
    'benchmark prompt',
    'source scope',
]
COMMENT=re.compile(r'<!--.*?-->',re.S)


def severity(profile, errors, warnings, msg):
    (errors if profile=='release' else warnings).append(msg)


def main():
    ap=argparse.ArgumentParser(description='Audit revision locality and preservation of an existing manuscript.')
    ap.add_argument('workspace', nargs='?', default='.')
    ap.add_argument('--profile', choices=['draft','standard','release'], default='standard')
    ap.add_argument('--report')
    args=ap.parse_args()
    root=Path(args.workspace).resolve()
    project=load_json(root/'project.json')
    errors=[]; warnings=[]; details={}
    mode=project.get('mode')
    policy=project.get('revision_policy')

    # Backwards compatibility: pre-v1.7 workspaces without an explicit policy are not reinterpreted.
    if mode not in {'revise','refresh'} or not isinstance(policy,dict):
        report={'ok':True,'profile':args.profile,'skipped':True,'reason':'revision_policy not enabled for this workspace',
                'errors':[],'warnings':[],'summary':{'error_count':0,'warning_count':0}}
        if args.report:
            (root/args.report).write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
        print(json.dumps(report,indent=2,ensure_ascii=False)); return

    preserve=policy.get('preserve_existing_manuscript',True)
    if not preserve:
        report={'ok':True,'profile':args.profile,'skipped':True,'reason':'preserve_existing_manuscript=false',
                'errors':[],'warnings':[],'summary':{'error_count':0,'warning_count':0}}
        if args.report:
            (root/args.report).write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
        print(json.dumps(report,indent=2,ensure_ascii=False)); return

    diff_path=root/'revision_diff.json'
    if not diff_path.exists():
        severity(args.profile,errors,warnings,'revision locality policy is enabled but revision_diff.json is missing')
        diff={}
    else:
        try: diff=load_json(diff_path)
        except Exception as e: errors.append(f'revision_diff.json: {e}'); diff={}

    if diff and int(diff.get('schema_version',0)) < 3:
        severity(args.profile,errors,warnings,'revision locality policy requires revision_diff.json schema_version >= 3')
    locality=diff.get('locality') or {}
    details['locality']=locality

    allow_global=bool(policy.get('allow_global_rewrite',False))
    min_similarity=float(policy.get('min_prose_token_similarity',0.55))
    min_preserved=float(policy.get('min_preserved_old_paragraph_fraction',0.35))
    allow_title=bool(policy.get('allow_title_change',False))

    if locality:
        sim=locality.get('prose_token_similarity')
        pfrac=locality.get('preserved_old_paragraph_fraction')
        if not allow_global:
            if sim is not None and sim < min_similarity:
                severity(args.profile,errors,warnings,f'revision is too global for preserve-existing-manuscript policy: prose_token_similarity={sim} < {min_similarity}')
            if pfrac is not None and pfrac < min_preserved:
                severity(args.profile,errors,warnings,f'revision preserves too few original prose paragraphs: preserved_old_paragraph_fraction={pfrac} < {min_preserved}')
        else:
            reason=str(policy.get('global_rewrite_reason') or '').strip()
            change_ids=policy.get('global_rewrite_change_ids') or []
            if not reason:
                severity(args.profile,errors,warnings,'allow_global_rewrite=true requires global_rewrite_reason')
            if not change_ids:
                severity(args.profile,errors,warnings,'allow_global_rewrite=true requires global_rewrite_change_ids')
            revisions=load_jsonl(root/'revision_log.jsonl') if (root/'revision_log.jsonl').exists() else []
            verified={r.get('change_id') for r in revisions if r.get('verification')=='verified'}
            missing=[x for x in change_ids if x not in verified]
            if missing:
                severity(args.profile,errors,warnings,f'global rewrite authorization points to unverified/unknown change_ids: {missing}')

        if locality.get('title_changed') and not allow_title:
            severity(args.profile,errors,warnings,
                     f"revision changed manuscript title without allow_title_change=true: {locality.get('old_title')!r} -> {locality.get('new_title')!r}")

    manuscript=(root/'manuscript.md').read_text(encoding='utf-8') if (root/'manuscript.md').exists() else ''
    prose=COMMENT.sub(' ',manuscript).lower()
    terms=policy.get('forbidden_meta_manuscript_terms')
    if terms is None: terms=DEFAULT_META_TERMS
    found=[]
    for term in terms or []:
        if str(term).strip() and str(term).lower() in prose:
            found.append(str(term))
    if found:
        severity(args.profile,errors,warnings,
                 'manuscript contains workflow/meta-writing that should remain in ledgers or response files, not scientific prose: '+', '.join(found))
    details['forbidden_meta_terms_found']=found

    report={'ok':not errors,'profile':args.profile,'skipped':False,'details':details,'errors':errors,'warnings':warnings,
            'summary':{'error_count':len(errors),'warning_count':len(warnings)}}
    if args.report:
        (root/args.report).write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    print(json.dumps(report,indent=2,ensure_ascii=False))
    sys.exit(0 if report['ok'] else 1)

if __name__=='__main__': main()
