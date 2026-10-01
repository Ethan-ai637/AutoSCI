#!/usr/bin/env python3
from pathlib import Path
import argparse, shutil

HERE=Path(__file__).resolve().parent.parent
TEMPL=HERE/'templates'

def main():
    ap=argparse.ArgumentParser(description='Initialize an academic-manuscript-writing workspace.')
    ap.add_argument('outdir')
    ap.add_argument('--force', action='store_true')
    args=ap.parse_args()
    out=Path(args.outdir)
    if out.exists() and any(out.iterdir()) and not args.force:
        raise SystemExit(f'{out} is not empty; use --force to overwrite template files')
    out.mkdir(parents=True, exist_ok=True)
    mapping={
      'project.template.json':'project.json',
      'sources.template.jsonl':'sources.jsonl',
      'evidence.template.jsonl':'evidence.jsonl',
      'claims.template.jsonl':'claims.jsonl',
      'revision_log.template.jsonl':'revision_log.jsonl',
      'section_plan.template.json':'section_plan.json',
      'writing_sources.template.jsonl':'writing_sources.jsonl',
      'writing_profile.template.json':'writing_profile.json',
      'manuscript_contract.template.json':'manuscript_contract.json',
    }
    for src,dst in mapping.items():
        target=out/dst
        if not target.exists() or args.force:
            shutil.copyfile(TEMPL/src,target)
    # Reporting/paragraph contracts and revision obligations are optional during drafting; initialize empty ledgers.
    reporting=out/'reporting_contracts.jsonl'
    if not reporting.exists() or args.force:
        reporting.write_text('', encoding='utf-8')
    paragraphs=out/'paragraph_contracts.jsonl'
    if not paragraphs.exists() or args.force:
        paragraphs.write_text('', encoding='utf-8')
    obligations=out/'revision_obligations.jsonl'
    if not obligations.exists() or args.force:
        obligations.write_text('', encoding='utf-8')
    manuscript=out/'manuscript.md'
    if not manuscript.exists() or args.force:
        manuscript.write_text('# Manuscript\n\n',encoding='utf-8')
    print(f'Initialized {out.resolve()}')

if __name__=='__main__': main()
