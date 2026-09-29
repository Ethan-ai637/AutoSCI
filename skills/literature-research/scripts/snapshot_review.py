#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path


DEFAULT_ARTIFACTS = [
    ("protocol", "protocol.json"),
    ("workspace_meta", "review/workspace_meta.json"),
    ("schema_audit", "review/schema_audit.json"),
    ("search_log", "search_log.csv"),
    ("normalized_records", "records.normalized.csv"),
    ("canonical_records", "records.deduped.csv"),
    ("dedup_report", "dedup_report.json"),
    ("search_audit", "review/search_audit.json"),
    ("screening_log", "review/screening_log.csv"),
    ("screening", "review/screening.csv"),
    ("screening_conflicts", "review/screening_conflicts.json"),
    ("study_map", "review/study_map.csv"),
    ("study_summary", "review/study_summary.csv"),
    ("study_audit", "review/study_audit.json"),
    ("clusters", "review/clusters.csv"),
    ("cluster_summary", "review/cluster_summary.md"),
    ("evidence", "review/evidence_table.csv"),
    ("citation_trail", "review/citation_trail.csv"),
    ("citation_trail_audit", "review/citation_trail_audit.json"),
    ("synthesis_claims", "review/synthesis_claims.csv"),
    ("synthesis_evidence", "review/synthesis_evidence.csv"),
    ("synthesis_audit", "review/synthesis_audit.json"),
    ("evidence_graph", "review/evidence_graph.json"),
    ("synthesis_brief", "review/synthesis_brief.md"),
    ("flow_report", "review/flow_report.json"),
    ("preflight", "review/preflight.json"),
]


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def skill_digest(skill_root: Path) -> tuple[str, list[dict]]:
    members = []
    for p in sorted(skill_root.rglob("*")):
        if not p.is_file() or "__pycache__" in p.parts or p.name.endswith(".pyc"):
            continue
        # Avoid self-referential or generated files outside the skill source tree; this package stores none by default.
        rel = p.relative_to(skill_root).as_posix()
        digest = sha256_file(p)
        members.append({"path": rel, "sha256": digest, "size": p.stat().st_size})
    h = hashlib.sha256()
    for x in members:
        h.update(f"{x['path']}\0{x['sha256']}\n".encode("utf-8"))
    return h.hexdigest(), members


def main():
    ap = argparse.ArgumentParser(description="Freeze a literature-research workspace into a hash-verified manifest.")
    ap.add_argument("--root", default=".", help="Workspace root containing protocol.json/search_log.csv/review/")
    ap.add_argument("--manifest", default="review/review_manifest.json")
    ap.add_argument("--require-preflight", action="store_true", help="Require review/preflight.json with passed=true")
    ap.add_argument("--include", action="append", default=[], help="Additional workspace-relative file to fingerprint; may be repeated")
    args = ap.parse_args()

    root = Path(args.root).resolve()
    manifest_path = (root / args.manifest).resolve() if not Path(args.manifest).is_absolute() else Path(args.manifest).resolve()
    skill_root = Path(__file__).resolve().parent.parent

    preflight_path = root / "review/preflight.json"
    if args.require_preflight:
        if not preflight_path.exists():
            raise SystemExit("required preflight file is missing: review/preflight.json")
        try:
            pf = json.loads(preflight_path.read_text(encoding="utf-8"))
        except Exception as exc:
            raise SystemExit(f"could not parse preflight: {exc}")
        if pf.get("passed") is not True:
            raise SystemExit("preflight did not pass; refusing to freeze snapshot")
        workspace_meta_path = root / "review/workspace_meta.json"
        if workspace_meta_path.exists():
            schema_audit_path = root / "review/schema_audit.json"
            if not schema_audit_path.exists():
                raise SystemExit("versioned workspace is missing review/schema_audit.json; validate the workspace before freezing")
            try:
                schema_audit = json.loads(schema_audit_path.read_text(encoding="utf-8"))
            except Exception as exc:
                raise SystemExit(f"could not parse schema audit: {exc}")
            if schema_audit.get("passed") is not True:
                raise SystemExit("workspace schema audit did not pass; refusing to freeze snapshot")

    artifacts = []
    seen = set()
    for role, rel in DEFAULT_ARTIFACTS + [("extra", x) for x in args.include]:
        p = (root / rel).resolve()
        try:
            rel_norm = p.relative_to(root).as_posix()
        except ValueError:
            raise SystemExit(f"artifact is outside workspace root: {p}")
        if rel_norm in seen or p == manifest_path:
            continue
        seen.add(rel_norm)
        if not p.exists():
            continue
        if not p.is_file():
            continue
        artifacts.append({
            "role": role,
            "path": rel_norm,
            "sha256": sha256_file(p),
            "size": p.stat().st_size,
        })

    protocol_meta = {}
    protocol_path = root / "protocol.json"
    if protocol_path.exists():
        try:
            p = json.loads(protocol_path.read_text(encoding="utf-8"))
            protocol_meta = {
                "protocol_id": p.get("protocol_id"),
                "protocol_version": p.get("protocol_version"),
                "profile": p.get("profile"),
                "research_question": p.get("research_question"),
                "synthesis_unit": p.get("synthesis_unit"),
            }
        except Exception:
            protocol_meta = {"parse_error": True}

    version_path = skill_root / "VERSION"
    skill_version = version_path.read_text(encoding="utf-8").strip() if version_path.exists() else None
    package_digest, package_members = skill_digest(skill_root)

    workspace_schema = None
    workspace_meta_path = root / "review/workspace_meta.json"
    if workspace_meta_path.exists():
        try:
            workspace_schema = json.loads(workspace_meta_path.read_text(encoding="utf-8")).get("workspace_schema")
        except Exception:
            workspace_schema = "unparseable"

    manifest = {
        "manifest_schema": "autosci-literature-research-snapshot-v1",
        "workspace_schema": workspace_schema or "legacy-unversioned",
        "created_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "workspace_root_label": root.name,
        "skill": {
            "name": "literature-research",
            "version": skill_version,
            "package_sha256": package_digest,
            "package_files": len(package_members),
        },
        "protocol": protocol_meta,
        "artifacts": artifacts,
        "artifact_count": len(artifacts),
        "limitations": [
            "A valid snapshot proves file identity and package identity, not scientific correctness or search completeness.",
            "External databases and web interfaces can change after the snapshot; exact query/date/source logs remain necessary.",
        ],
    }
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({
        "manifest": str(manifest_path),
        "artifact_count": len(artifacts),
        "skill_version": skill_version,
        "skill_package_sha256": package_digest,
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
