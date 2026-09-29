#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path

SKILL_ROOT = Path(__file__).resolve().parent.parent
CURRENT_SCHEMA = SKILL_ROOT / "schemas/workspace-v2.json"
SUPPORTED_FROM = {"", "legacy-unversioned", "autosci-literature-research-workspace-v1", "autosci-literature-research-workspace-v2"}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def read_header_rows(path: Path):
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        r = csv.DictReader(f)
        return list(r.fieldnames or []), [dict(x) for x in r]


def write_csv(path: Path, fields: list[str], rows: list[dict]):
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        for row in rows:
            w.writerow({k: row.get(k, "") for k in fields})


def main():
    ap = argparse.ArgumentParser(description="Conservatively migrate a literature-research workspace to the current v2 structural contract.")
    ap.add_argument("--root", default=".")
    ap.add_argument("--schema", default=str(CURRENT_SCHEMA))
    ap.add_argument("--apply", action="store_true", help="Apply the migration; default is preview only.")
    ap.add_argument("--report", help="Optional report path. Apply mode defaults to review/migration_report.json.")
    args = ap.parse_args()

    root = Path(args.root).resolve()
    contract = json.loads(Path(args.schema).resolve().read_text(encoding="utf-8"))
    version = (SKILL_ROOT / "VERSION").read_text(encoding="utf-8").strip()
    actions = []
    errors = []
    manual_followup = []

    meta_path = root / "review/workspace_meta.json"
    if meta_path.exists():
        try:
            meta = json.loads(meta_path.read_text(encoding="utf-8"))
        except Exception as exc:
            errors.append(f"cannot parse existing workspace metadata: {exc}")
            meta = {}
        declared = str(meta.get("workspace_schema") or "").strip()
    else:
        meta = {}
        declared = "legacy-unversioned"
        actions.append({"action": "create_workspace_meta", "path": "review/workspace_meta.json"})

    if declared not in SUPPORTED_FROM:
        errors.append(f"workspace declares unsupported schema {declared!r}; automatic migration path is not defined")

    csv_changes = []
    for rel, spec in (contract.get("artifacts") or {}).items():
        if spec.get("kind") != "csv":
            continue
        p = root / rel
        if not p.exists() or not p.is_file():
            continue
        try:
            fields, rows = read_header_rows(p)
        except Exception as exc:
            errors.append(f"cannot read {rel}: {exc}")
            continue
        missing = [x for x in spec.get("required_columns", []) if x not in fields]
        if missing:
            actions.append({"action": "append_blank_columns", "path": rel, "columns": missing})
            csv_changes.append((rel, p, fields, rows, missing))
        if rel == "review/screening_log.csv" and any(str(r.get("stage") or "").strip().lower() == "full_text" for r in rows):
            manual_followup.append(
                "review/screening_log.csv contains legacy stage=full_text. v1.6 does not infer whether full text was actually accessed; manually relabel each relevant event as full_text_attempted or full_text_screened and set access_level."
            )

    protocol_path = root / "protocol.json"
    protocol_change = None
    if protocol_path.exists():
        try:
            protocol = json.loads(protocol_path.read_text(encoding="utf-8"))
            if "deterministic_exclusion_rules" not in protocol:
                protocol_change = protocol
                actions.append({"action": "add_empty_protocol_key", "path": "protocol.json", "key": "deterministic_exclusion_rules"})
        except Exception as exc:
            errors.append(f"cannot parse protocol.json: {exc}")

    applied = False
    backup_root = None
    if args.apply and not errors:
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        backup_root = root / "review" / "migration_backup" / stamp
        for rel, p, fields, rows, missing in csv_changes:
            dst = backup_root / rel
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(p, dst)
            write_csv(p, fields + missing, rows)
        if protocol_change is not None:
            dst = backup_root / "protocol.json"
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(protocol_path, dst)
            protocol_change["deterministic_exclusion_rules"] = []
            protocol_path.write_text(json.dumps(protocol_change, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

        if meta_path.exists():
            dst = backup_root / "review/workspace_meta.json"
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(meta_path, dst)
        history = list(meta.get("migration_history") or [])
        history.append({
            "migrated_at": utc_now(),
            "from_workspace_schema": declared,
            "to_workspace_schema": contract.get("schema_id"),
            "skill_version": version,
            "actions": actions,
            "manual_followup": manual_followup,
            "note": "Structural migration only; no scientific judgments or legacy full-text access claims were inferred or changed."
        })
        meta = {
            **meta,
            "workspace_schema": contract.get("schema_id"),
            "created_by_skill_version": meta.get("created_by_skill_version") or "legacy-unversioned",
            "created_at": meta.get("created_at") or utc_now(),
            "last_migrated_by_skill_version": version,
            "migration_history": history,
        }
        meta_path.parent.mkdir(parents=True, exist_ok=True)
        meta_path.write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
        applied = True

    result = {
        "from_schema": declared,
        "target_schema": contract.get("schema_id"),
        "mode": "apply" if args.apply else "preview",
        "actions": actions,
        "manual_followup": manual_followup,
        "errors": errors,
        "applied": applied,
        "backup_dir": str(backup_root.relative_to(root)) if backup_root else None,
        "scientific_content_changed": False,
    }
    report_arg = args.report or ("review/migration_report.json" if args.apply else None)
    if report_arg:
        report = Path(report_arg)
        if not report.is_absolute():
            report = root / report
        report.parent.mkdir(parents=True, exist_ok=True)
        report.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    raise SystemExit(1 if errors else 0)


if __name__ == "__main__":
    main()
