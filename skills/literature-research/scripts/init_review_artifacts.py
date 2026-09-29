#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

from common import read_csv, stable_study_id, write_csv

SCREEN_FIELDS = [
    "record_id", "title", "decision", "reason_code", "screening_stage",
    "evidence_stage", "access_level", "reviewers", "decision_basis", "conflict_status", "notes"
]
SCREEN_LOG_FIELDS = [
    "record_id", "title", "stage", "access_level", "reviewer", "decision", "reason_code",
    "criterion_id", "evidence_basis", "decided_at", "notes"
]
STUDY_MAP_FIELDS = [
    "record_id", "study_id", "report_role", "linkage_basis", "verification_status", "notes"
]
EVIDENCE_FIELDS = [
    "source_id", "study_id", "source_version", "claim_id", "research_question_component",
    "study_design_or_method", "population_dataset_context", "intervention_or_method",
    "comparator_or_baseline", "outcome_metric", "reported_result",
    "uncertainty_or_variance", "authors_interpretation", "reviewer_interpretation",
    "limitations", "evidence_location", "support_level", "verification_status",
    "evidence_strength_note"
]
TRAIL_FIELDS = ["source_id", "target_id", "relation", "verification_source", "verification_url", "verified_at", "notes"]
SYNTHESIS_CLAIM_FIELDS = [
    "synthesis_id", "statement", "research_question_component", "evidence_state",
    "verification_coverage", "verified_evidence_count", "partial_evidence_count",
    "eligible_support_unit_count", "eligible_contradict_unit_count",
    "scope", "caveat", "notes"
]
SYNTHESIS_LINK_FIELDS = ["synthesis_id", "claim_id", "relation", "notes"]


def main():
    ap = argparse.ArgumentParser(description="Initialize review artifacts from deduplicated records.")
    ap.add_argument("records")
    ap.add_argument("--outdir", default="review")
    args = ap.parse_args()

    rows = read_csv(args.records)
    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    screening = [{
        "record_id": r.get("record_id", ""),
        "title": r.get("title", ""),
        "decision": "",
        "reason_code": "",
        "screening_stage": "",
        "evidence_stage": "",
        "access_level": "",
        "reviewers": "",
        "decision_basis": "",
        "conflict_status": "",
        "notes": "",
    } for r in rows]
    screening_log = [{
        "record_id": r.get("record_id", ""),
        "title": r.get("title", ""),
        "stage": "title_abstract",
        "access_level": "",
        "reviewer": "",
        "decision": "",
        "reason_code": "",
        "criterion_id": "",
        "evidence_basis": "title/abstract",
        "decided_at": "",
        "notes": "",
    } for r in rows]
    study_map = [{
        "record_id": r.get("record_id", ""),
        "study_id": stable_study_id(r.get("record_id", "")),
        "report_role": "primary_or_only_report",
        "linkage_basis": "",
        "verification_status": "provisional",
        "notes": "Initialized one report per provisional study; merge study_id values only after verified linkage.",
    } for r in rows]
    write_csv(outdir / "screening.csv", screening, SCREEN_FIELDS)
    write_csv(outdir / "screening_log.csv", screening_log, SCREEN_LOG_FIELDS)
    write_csv(outdir / "study_map.csv", study_map, STUDY_MAP_FIELDS)
    write_csv(outdir / "evidence_table.csv", [], EVIDENCE_FIELDS)
    write_csv(outdir / "citation_trail.csv", [], TRAIL_FIELDS)
    write_csv(outdir / "synthesis_claims.csv", [], SYNTHESIS_CLAIM_FIELDS)
    write_csv(outdir / "synthesis_evidence.csv", [], SYNTHESIS_LINK_FIELDS)
    skill_root = Path(__file__).resolve().parent.parent
    version_path = skill_root / "VERSION"
    skill_version = version_path.read_text(encoding="utf-8").strip() if version_path.exists() else None
    workspace_meta = {
        "workspace_schema": "autosci-literature-research-workspace-v2",
        "created_by_skill_version": skill_version,
        "created_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "migration_history": [],
    }
    (outdir / "workspace_meta.json").write_text(json.dumps(workspace_meta, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"initialized={outdir} records={len(rows)} schema={workspace_meta['workspace_schema']}")


if __name__ == "__main__":
    main()
