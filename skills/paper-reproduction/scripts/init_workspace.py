#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import shutil
from pathlib import Path

from _util import utc_now, write_json


def copy_json_template(src: Path, dst: Path, updates: dict | None = None) -> None:
    with src.open("r", encoding="utf-8") as f:
        obj = json.load(f)
    if updates:
        obj.update(updates)
    write_json(dst, obj)


def main() -> int:
    ap = argparse.ArgumentParser(description="Initialize an AutoSCI paper-reproduction workspace.")
    ap.add_argument("workspace", type=Path)
    ap.add_argument("--mode", choices=["REPO_REPRODUCE", "PAPER_ONLY", "REPO_AUDIT"], default="REPO_REPRODUCE")
    ap.add_argument("--profile", choices=["diagnostic", "standard", "release"], default="standard")
    ap.add_argument("--force", action="store_true", help="Allow writing into a non-empty workspace without deleting existing files.")
    args = ap.parse_args()

    ws = args.workspace.resolve()
    if ws.exists() and any(ws.iterdir()) and not args.force:
        raise SystemExit(f"Refusing non-empty workspace: {ws}. Use --force to add missing scaffold files.")
    ws.mkdir(parents=True, exist_ok=True)
    for d in ["environment/source", "environment/resolved", "patches", "logs", "artifacts"]:
        (ws / d).mkdir(parents=True, exist_ok=True)

    root = Path(__file__).resolve().parent.parent
    t = root / "templates"
    created = utc_now()

    files = {
        "reproduction_contract.template.json": "reproduction_contract.json",
        "paper_manifest.template.json": "paper_manifest.json",
        "repository_manifest.template.json": "repository_manifest.json",
        "run_plan.template.json": "run_plan.json",
        "data_manifest.template.json": "data_manifest.json",
        "reproduction_assessment.template.json": "reproduction_assessment.json",
    }
    for src_name, dst_name in files.items():
        dst = ws / dst_name
        if dst.exists():
            continue
        updates = None
        if dst_name == "reproduction_contract.json":
            updates = {"mode": args.mode, "profile": args.profile, "created_at": created, "target_claims": []}
        elif dst_name == "run_plan.json":
            updates = {"created_at": created, "items": []}
        elif dst_name == "data_manifest.json":
            updates = {"datasets": []}
        elif dst_name == "reproduction_assessment.json":
            updates = {"assessments": []}
        copy_json_template(t / src_name, dst, updates)

    jsonl_files = [
        "claim_code_map.jsonl",
        "checkpoint_manifest.jsonl",
        "discrepancies.jsonl",
        "underspecifications.jsonl",
        "implementation_decisions.jsonl",
    ]
    for dst_name in jsonl_files:
        dst = ws / dst_name
        dst.touch(exist_ok=True)

    ledger = ws / "run_ledger.jsonl"
    ledger.touch(exist_ok=True)
    metrics = ws / "metrics.csv"
    if not metrics.exists():
        shutil.copyfile(t / "metrics.template.csv", metrics)

    env_diff = ws / "environment/environment_diff.json"
    if not env_diff.exists():
        write_json(env_diff, {"schema_version": "1.0", "differences": [], "notes": None})

    report = ws / "reproduction_report.md"
    if not report.exists():
        report.write_text(
            "# Reproduction Report\n\n"
            "## Target claim(s)\n\n"
            "## Paper and repository identity\n\n"
            "## Environment and external artifacts\n\n"
            "## Runs\n\n"
            "## Result reconciliation\n\n"
            "## Discrepancies and blockers\n\n"
            "## Scope and limitations\n",
            encoding="utf-8",
        )

    print(f"Initialized {ws}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
