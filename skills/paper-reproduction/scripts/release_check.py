#!/usr/bin/env python3
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

from _util import load_json, read_jsonl


def main() -> int:
    ap = argparse.ArgumentParser(description="Release gate for paper-reproduction workspace.")
    ap.add_argument("workspace", type=Path)
    args = ap.parse_args()
    ws = args.workspace.resolve()

    preflight = Path(__file__).resolve().parent / "preflight.py"
    cp = subprocess.run([sys.executable, str(preflight), str(ws), "--output", str(ws / "preflight.json")], check=False)
    if cp.returncode != 0:
        print("Release check failed: structural preflight failed.", file=sys.stderr)
        return 1

    contract = load_json(ws / "reproduction_contract.json")
    mode = contract.get("mode")
    profile = contract.get("profile")
    if profile != "release":
        print("Release check failed: reproduction_contract.profile must be 'release'.", file=sys.stderr)
        return 1

    if mode != "REPO_AUDIT":
        claims = {c.get("claim_id") for c in contract.get("target_claims") or [] if c.get("claim_id")}
        assessments = load_json(ws / "reproduction_assessment.json").get("assessments") or []
        assessed = {a.get("claim_id") for a in assessments if a.get("claim_id")}
        if claims - assessed:
            print(f"Release check failed: missing assessments for {sorted(claims - assessed)}", file=sys.stderr)
            return 1

    # JSONL parse itself is part of release integrity.
    for name in ["run_ledger.jsonl", "claim_code_map.jsonl", "discrepancies.jsonl", "underspecifications.jsonl"]:
        read_jsonl(ws / name)

    print("release_check: pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
