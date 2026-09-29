#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

SKILL_ROOT = Path(__file__).resolve().parent.parent
CURRENT_SCHEMA = SKILL_ROOT / "schemas/workspace-v2.json"
SCHEMA_BY_ID = {
    "autosci-literature-research-workspace-v1": SKILL_ROOT / "schemas/workspace-v1.json",
    "autosci-literature-research-workspace-v2": CURRENT_SCHEMA,
}


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def csv_header(path: Path) -> list[str]:
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        row = next(csv.reader(f), [])
    return [str(x).strip() for x in row]


def choose_schema(root: Path, explicit: str | None) -> Path:
    if explicit:
        return Path(explicit).resolve()
    meta_path = root / "review/workspace_meta.json"
    if meta_path.exists():
        try:
            declared = str(load_json(meta_path).get("workspace_schema") or "").strip()
            if declared in SCHEMA_BY_ID:
                return SCHEMA_BY_ID[declared]
        except Exception:
            pass
    return CURRENT_SCHEMA


def main():
    ap = argparse.ArgumentParser(description="Validate the structural contract of a literature-research workspace.")
    ap.add_argument("--root", default=".")
    ap.add_argument("--schema", help="Explicit schema contract. Default auto-selects from workspace_meta; legacy workspaces use current schema.")
    ap.add_argument("--require-final", action="store_true", help="Require the standard final artifact surface.")
    ap.add_argument("--report")
    args = ap.parse_args()

    root = Path(args.root).resolve()
    schema_path = choose_schema(root, args.schema)
    contract = load_json(schema_path)
    errors: list[str] = []
    warnings: list[str] = []
    checked: list[str] = []

    meta_path = root / "review/workspace_meta.json"
    if meta_path.exists():
        try:
            meta = load_json(meta_path)
            workspace_schema = str(meta.get("workspace_schema") or "").strip()
        except Exception as exc:
            meta = {}
            workspace_schema = "invalid"
            errors.append(f"could not parse review/workspace_meta.json: {exc}")
        if workspace_schema and workspace_schema != contract.get("schema_id"):
            errors.append(f"workspace schema {workspace_schema!r} is not supported by selected contract {contract.get('schema_id')!r}")
        elif not workspace_schema:
            errors.append("review/workspace_meta.json missing workspace_schema")
        status = "versioned"
    else:
        meta = {}
        workspace_schema = "legacy-unversioned"
        status = "legacy-unversioned"
        warnings.append("review/workspace_meta.json is missing; treating workspace as legacy-unversioned")

    required_final = set(contract.get("final_required", [])) if args.require_final else set()
    for rel, spec in (contract.get("artifacts") or {}).items():
        p = root / rel
        if not p.exists():
            if rel in required_final:
                errors.append(f"missing required final artifact: {rel}")
            continue
        if not p.is_file():
            errors.append(f"artifact is not a file: {rel}")
            continue
        checked.append(rel)
        kind = spec.get("kind")
        if kind == "csv":
            try:
                header = csv_header(p)
            except Exception as exc:
                errors.append(f"could not read CSV header for {rel}: {exc}")
                continue
            missing = [x for x in spec.get("required_columns", []) if x not in header]
            if missing:
                errors.append(f"{rel} missing required columns: {missing}")
        elif kind == "json_object":
            try:
                data = load_json(p)
            except Exception as exc:
                errors.append(f"could not parse JSON {rel}: {exc}")
                continue
            if not isinstance(data, dict):
                errors.append(f"{rel} must contain a JSON object")
                continue
            missing = [x for x in spec.get("required_keys", []) if x not in data]
            if missing:
                errors.append(f"{rel} missing required keys: {missing}")
            for key, allowed in (spec.get("enums") or {}).items():
                if key in data and str(data.get(key)) not in {str(x) for x in allowed}:
                    errors.append(f"{rel} has unsupported {key}={data.get(key)!r}; allowed={allowed}")
        else:
            warnings.append(f"schema contract has unknown artifact kind {kind!r} for {rel}")

    result = {
        "schema_contract": contract.get("schema_id"),
        "schema_version": contract.get("schema_version"),
        "schema_path": str(schema_path),
        "workspace_schema": workspace_schema,
        "workspace_status": status,
        "require_final": args.require_final,
        "checked_artifacts": sorted(checked),
        "errors": errors,
        "warnings": warnings,
        "passed": not errors,
    }
    if args.report:
        out = Path(args.report)
        if not out.is_absolute():
            out = root / out
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    raise SystemExit(1 if errors else 0)


if __name__ == "__main__":
    main()
