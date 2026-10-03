#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

from _util import load_json, read_jsonl, utc_now, write_json


def status(ok: bool | None, partial: bool = False, blocked: bool = False) -> str:
    if blocked: return "blocked"
    if ok is True and not partial: return "ready"
    if ok is True and partial: return "partial"
    if ok is False: return "missing"
    return "not_checked"


def main() -> int:
    ap=argparse.ArgumentParser(description="Produce dimension-level repository reproduction readiness without a numeric score.")
    ap.add_argument("workspace",type=Path); ap.add_argument("--output",type=Path)
    args=ap.parse_args(); ws=args.workspace.resolve()
    repo=load_json(ws/'repository_manifest.json') if (ws/'repository_manifest.json').exists() else {}
    mappings=read_jsonl(ws/'claim_code_map.jsonl')
    data=load_json(ws/'data_manifest.json').get('datasets',[]) if (ws/'data_manifest.json').exists() else []
    ckpts=read_jsonl(ws/'checkpoint_manifest.jsonl')
    ledger=read_jsonl(ws/'run_ledger.jsonl')
    detected=repo.get('detected') or {}; rev=repo.get('source_revision') or {}
    map_states=[m.get('mapping_status') for m in mappings]
    dimensions={
      'paper_identity_evidence': status(bool(repo.get('identity_evidence'))),
      'paper_era_revision': status(bool(rev.get('commit')), partial=rev.get('selection_basis') in {'current_head_fallback','unknown'}),
      'environment_specification': status(bool(detected.get('environment_files') or detected.get('container_files'))),
      'dataset_availability': status(bool(data), partial=bool(data) and any(d.get('retrieval_status') not in {'available','verified','retrieved'} for d in data)),
      'checkpoint_availability': status(bool(ckpts), partial=bool(ckpts) and any(c.get('retrieval_status') not in {'available','verified','retrieved'} for c in ckpts)),
      'entrypoint_discoverability': status(bool(detected.get('entrypoint_candidates'))),
      'config_traceability': status(bool(detected.get('config_candidates'))),
      'claim_code_mapping': status(bool(mappings), partial=bool(mappings) and any(s != 'verified' for s in map_states)),
      'smoke_test_evidence': status(any(r.get('run_kind')=='smoke' and r.get('exit_code')==0 for r in ledger) if ledger else None),
    }
    out_obj={'schema_version':'1.1','generated_at':utc_now(),'dimensions':dimensions,'overall_score':None,'notes':'Dimension-level readiness only; no universal reproducibility score is computed.'}
    out=args.output.resolve() if args.output else ws/'repository_readiness.json'; write_json(out,out_obj)
    print(f"repository readiness -> {out}")
    return 0
if __name__=='__main__': raise SystemExit(main())
