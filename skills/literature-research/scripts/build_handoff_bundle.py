#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path

CORE = [
    "protocol.json",
    "review/workspace_meta.json",
    "review/schema_audit.json",
    "records.deduped.csv",
    "review/screening.csv",
    "review/study_map.csv",
    "review/study_summary.csv",
    "review/clusters.csv",
    "review/cluster_summary.md",
    "review/evidence_table.csv",
    "review/citation_trail.csv",
    "review/synthesis_claims.csv",
    "review/synthesis_evidence.csv",
    "review/synthesis_audit.json",
    "review/evidence_graph.json",
    "review/synthesis_brief.md",
    "review/flow_report.json",
    "review/preflight.json",
    "review/review_manifest.json",
]


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
        rows.append((p.relative_to(skill_root).as_posix(), sha256_file(p)))
    h = hashlib.sha256()
    for rel, digest in rows:
        h.update(f"{rel}\0{digest}\n".encode("utf-8"))
    return h.hexdigest()


def verify_frozen_snapshot(root: Path, manifest_path: Path) -> list[str]:
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    errors = []
    for entry in manifest.get("artifacts", []):
        rel, expected = entry.get("path"), entry.get("sha256")
        if not rel or not expected:
            errors.append("invalid frozen artifact entry")
            continue
        p = (root / rel).resolve()
        try:
            p.relative_to(root)
        except ValueError:
            errors.append(f"frozen artifact escapes root: {rel}")
            continue
        if not p.exists():
            errors.append(f"missing frozen artifact: {rel}")
        elif sha256_file(p) != expected:
            errors.append(f"changed frozen artifact: {rel}")
    expected_pkg = ((manifest.get("skill") or {}).get("package_sha256"))
    if expected_pkg and skill_digest(Path(__file__).resolve().parent.parent) != expected_pkg:
        errors.append("skill package differs from the frozen snapshot")
    return errors


def main():
    ap = argparse.ArgumentParser(description="Build a compact downstream handoff bundle from an audited literature-review workspace.")
    ap.add_argument("--root", default=".")
    ap.add_argument("--outdir", required=True)
    ap.add_argument("--target", choices=["generic", "scientific-figure", "academic-research-presentation"], default="generic")
    ap.add_argument("--allow-unfrozen", action="store_true", help="Allow handoff without a frozen review_manifest.json")
    args = ap.parse_args()

    root = Path(args.root).resolve()
    out = Path(args.outdir).resolve()
    preflight_path = root / "review/preflight.json"
    if not preflight_path.exists():
        raise SystemExit("missing review/preflight.json; run preflight before handoff")
    pf = json.loads(preflight_path.read_text(encoding="utf-8"))
    if pf.get("passed") is not True:
        raise SystemExit("preflight did not pass; refusing downstream handoff")
    workspace_meta_path = root / "review/workspace_meta.json"
    if workspace_meta_path.exists():
        schema_audit_path = root / "review/schema_audit.json"
        if not schema_audit_path.exists():
            raise SystemExit("versioned workspace is missing review/schema_audit.json; validate the workspace before handoff")
        try:
            schema_audit = json.loads(schema_audit_path.read_text(encoding="utf-8"))
        except Exception as exc:
            raise SystemExit(f"could not parse schema audit: {exc}")
        if schema_audit.get("passed") is not True:
            raise SystemExit("workspace schema audit did not pass; refusing downstream handoff")
    frozen_manifest = root / "review/review_manifest.json"
    if not args.allow_unfrozen:
        if not frozen_manifest.exists():
            raise SystemExit("missing review/review_manifest.json; freeze the workspace first or pass --allow-unfrozen")
        frozen_errors = verify_frozen_snapshot(root, frozen_manifest)
        if frozen_errors:
            raise SystemExit("frozen snapshot verification failed before handoff: " + "; ".join(frozen_errors))

    for required in ("review/evidence_graph.json", "review/synthesis_brief.md"):
        if not (root / required).exists():
            raise SystemExit(f"missing {required}; build structured downstream views before handoff")
    graph = json.loads((root / "review/evidence_graph.json").read_text(encoding="utf-8"))
    if graph.get("passed") is not True:
        raise SystemExit("review/evidence_graph.json did not pass; refusing downstream handoff")

    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)
    copied = []
    for rel in CORE:
        src = root / rel
        if not src.exists() or not src.is_file():
            continue
        dst = out / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
        copied.append({"path": rel, "sha256": sha256_file(dst), "size": dst.stat().st_size})

    target_notes = {
        "generic": [
            "Start with review/synthesis_brief.md for orientation, then inspect evidence_table.csv and evidence_graph.json for provenance.",
        ],
        "scientific-figure": [
            "Use evidence_graph.json and synthesis_claims.csv to identify source-grounded conceptual relationships.",
            "Do not convert extracted narrative evidence into quantitative plots unless authoritative numeric data are separately available.",
        ],
        "academic-research-presentation": [
            "Use synthesis_brief.md for narrative planning and evidence_table.csv for claim-to-source verification.",
            "Prefer original source figures/tables from the cited reports when explaining empirical results; this bundle is provenance, not a replacement for source visuals.",
        ],
    }
    workspace_schema = "legacy-unversioned"
    meta_path = root / "review/workspace_meta.json"
    if meta_path.exists():
        try:
            workspace_schema = json.loads(meta_path.read_text(encoding="utf-8")).get("workspace_schema") or workspace_schema
        except Exception:
            workspace_schema = "unparseable"

    manifest = {
        "schema": "autosci-literature-handoff-v1",
        "workspace_schema": workspace_schema,
        "created_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "target": args.target,
        "source_workspace": root.name,
        "frozen": (root / "review/review_manifest.json").exists(),
        "files": copied,
        "routing_notes": target_notes[args.target],
        "limitations": [
            "The bundle preserves review provenance but does not grant permission to reproduce copyrighted source figures or full text.",
            "Downstream artifacts must preserve caveats, scope, evidence-state distinctions, and source traceability.",
        ],
    }
    (out / "handoff_manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    readme = [
        "# AutoSCI literature-research handoff",
        "",
        f"Target: `{args.target}`",
        "",
        "Start with `review/synthesis_brief.md`; use `review/evidence_graph.json` for machine-readable provenance and `review/evidence_table.csv` for claim-level inspection.",
        "",
        *[f"- {x}" for x in target_notes[args.target]],
        "",
        "This handoff does not create new scientific claims. Preserve the recorded scope, caveats, evidence states, and source provenance in downstream work.",
        "",
    ]
    (out / "HANDOFF.md").write_text("\n".join(readme), encoding="utf-8")
    print(json.dumps({"outdir": str(out), "target": args.target, "files": len(copied), "frozen": manifest["frozen"]}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
