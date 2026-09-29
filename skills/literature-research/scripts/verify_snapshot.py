#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def skill_digest(skill_root: Path) -> str:
    rows = []
    for p in sorted(skill_root.rglob("*")):
        if not p.is_file() or "__pycache__" in p.parts or p.name.endswith(".pyc"):
            continue
        rel = p.relative_to(skill_root).as_posix()
        rows.append((rel, sha256_file(p)))
    h = hashlib.sha256()
    for rel, digest in rows:
        h.update(f"{rel}\0{digest}\n".encode("utf-8"))
    return h.hexdigest()


def main():
    ap = argparse.ArgumentParser(description="Verify a frozen literature-research workspace snapshot.")
    ap.add_argument("manifest")
    ap.add_argument("--root", default=".")
    ap.add_argument("--ignore-skill-package", action="store_true")
    args = ap.parse_args()

    root = Path(args.root).resolve()
    manifest_path = Path(args.manifest).resolve()
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    errors, warnings = [], []

    for entry in manifest.get("artifacts", []):
        rel = entry.get("path")
        expected = entry.get("sha256")
        if not rel or not expected:
            errors.append(f"invalid manifest artifact entry: {entry}")
            continue
        p = (root / rel).resolve()
        try:
            p.relative_to(root)
        except ValueError:
            errors.append(f"artifact escapes workspace root: {rel}")
            continue
        if not p.exists():
            errors.append(f"missing artifact: {rel}")
            continue
        actual = sha256_file(p)
        if actual != expected:
            errors.append(f"changed artifact: {rel}")
        expected_size = entry.get("size")
        if isinstance(expected_size, int) and p.stat().st_size != expected_size:
            warnings.append(f"size changed for {rel}: {expected_size} -> {p.stat().st_size}")

    expected_workspace_schema = manifest.get("workspace_schema")
    meta_path = root / "review/workspace_meta.json"
    if expected_workspace_schema and expected_workspace_schema != "legacy-unversioned":
        if not meta_path.exists():
            errors.append("snapshot expects a versioned workspace but review/workspace_meta.json is missing")
        else:
            try:
                actual_workspace_schema = json.loads(meta_path.read_text(encoding="utf-8")).get("workspace_schema")
                if actual_workspace_schema != expected_workspace_schema:
                    errors.append(f"workspace schema differs from snapshot: {expected_workspace_schema!r} -> {actual_workspace_schema!r}")
            except Exception as exc:
                errors.append(f"could not parse review/workspace_meta.json: {exc}")

    if not args.ignore_skill_package:
        expected_pkg = ((manifest.get("skill") or {}).get("package_sha256"))
        if expected_pkg:
            actual_pkg = skill_digest(Path(__file__).resolve().parent.parent)
            if actual_pkg != expected_pkg:
                errors.append("literature-research skill package differs from the package used to create the snapshot")

    result = {
        "manifest": str(manifest_path),
        "checked_artifacts": len(manifest.get("artifacts", [])),
        "errors": errors,
        "warnings": warnings,
        "passed": not errors,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    raise SystemExit(1 if errors else 0)


if __name__ == "__main__":
    main()
