#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path

from common import read_csv, write_csv

ALLOWED_DECISIONS = {"include", "exclude", "uncertain"}
DECISION_STAGE_RANK = {
    "title_abstract": 10,
    "full_text_attempted": 15,
    "full_text": 16,  # legacy ambiguous stage; does not prove full-text access
    "full_text_screened": 20,
    "adjudication": 30,
    "final": 40,
}
EVIDENCE_STAGE_RANK = {
    "title_abstract": 10,
    "full_text_attempted": 15,
    "full_text": 16,
    "full_text_screened": 20,
}
ACCESS_RANK = {"": 0, "unknown": 0, "title_only": 5, "abstract": 10, "metadata_plus_abstract": 12, "full_text": 20}
OUT_FIELDS = [
    "record_id", "title", "decision", "reason_code", "screening_stage",
    "evidence_stage", "access_level", "reviewers", "decision_basis", "conflict_status", "notes"
]


def norm(v):
    return str(v or "").strip()


def reconcile(records, events):
    by_id = defaultdict(list)
    for row in events:
        rid = norm(row.get("record_id"))
        if rid:
            by_id[rid].append(row)

    output, conflicts, warnings = [], [], []
    for rec in records:
        rid = norm(rec.get("record_id"))
        title = norm(rec.get("title"))
        all_rows = by_id.get(rid, [])
        rows = [r for r in all_rows if norm(r.get("decision")).lower() in ALLOWED_DECISIONS]
        if not rows:
            output.append({
                "record_id": rid, "title": title, "decision": "", "reason_code": "",
                "screening_stage": "", "evidence_stage": "", "access_level": "", "reviewers": "",
                "decision_basis": "", "conflict_status": "", "notes": ""
            })
            continue

        max_rank = max(DECISION_STAGE_RANK.get(norm(r.get("stage")).lower(), 0) for r in rows)
        stage_rows = [r for r in rows if DECISION_STAGE_RANK.get(norm(r.get("stage")).lower(), 0) == max_rank]
        stage = norm(stage_rows[-1].get("stage")).lower()
        decisions = sorted({norm(r.get("decision")).lower() for r in stage_rows})
        reviewers = []
        for r in stage_rows:
            rv = norm(r.get("reviewer"))
            if rv and rv not in reviewers:
                reviewers.append(rv)

        if len(decisions) == 1:
            decision = decisions[0]
            conflict_status = "resolved"
        else:
            decision = "uncertain"
            conflict_status = "unresolved"
            conflicts.append({"record_id": rid, "title": title, "stage": stage, "decisions": decisions, "reviewers": reviewers})

        reasons, bases, notes = [], [], []
        for r in stage_rows:
            for value, bucket in [
                (norm(r.get("reason_code")), reasons),
                (norm(r.get("evidence_basis")), bases),
                (norm(r.get("notes")), notes),
            ]:
                if value and value not in bucket:
                    bucket.append(value)

        evidence_rows = [r for r in all_rows if norm(r.get("stage")).lower() in EVIDENCE_STAGE_RANK]
        evidence_stage = ""
        if evidence_rows:
            evidence_stage = max(
                (norm(r.get("stage")).lower() for r in evidence_rows),
                key=lambda x: EVIDENCE_STAGE_RANK.get(x, 0),
            )
        access_level = ""
        if all_rows:
            access_level = max(
                (norm(r.get("access_level")).lower() for r in all_rows),
                key=lambda x: ACCESS_RANK.get(x, -1),
                default="",
            )
        if decision == "exclude" and not reasons:
            warnings.append(f"{rid}: final exclusion has no reason_code")
        if evidence_stage == "full_text":
            warnings.append(f"{rid}: legacy stage 'full_text' is ambiguous; migrate manually to full_text_attempted or full_text_screened")

        output.append({
            "record_id": rid,
            "title": title,
            "decision": decision,
            "reason_code": ";".join(reasons),
            "screening_stage": stage,
            "evidence_stage": evidence_stage,
            "access_level": access_level,
            "reviewers": ";".join(reviewers),
            "decision_basis": " | ".join(bases),
            "conflict_status": conflict_status,
            "notes": " | ".join(notes),
        })
    return output, conflicts, warnings


def main():
    ap = argparse.ArgumentParser(description="Reconcile append-only screening events into one final row while preserving evidence/access stage.")
    ap.add_argument("screening_log")
    ap.add_argument("--records", required=True)
    ap.add_argument("-o", "--output", required=True)
    ap.add_argument("--conflicts", required=True)
    args = ap.parse_args()

    records = read_csv(args.records)
    events = read_csv(args.screening_log)
    out, conflicts, warnings = reconcile(records, events)
    write_csv(args.output, out, OUT_FIELDS)
    report = {
        "records": len(records),
        "events": len(events),
        "resolved_records": sum(bool(norm(r.get("decision"))) for r in out),
        "unresolved_conflicts": len(conflicts),
        "full_text_screened_records": sum(norm(r.get("evidence_stage")) == "full_text_screened" for r in out),
        "full_text_attempted_records": sum(norm(r.get("evidence_stage")) == "full_text_attempted" for r in out),
        "legacy_ambiguous_full_text_records": sum(norm(r.get("evidence_stage")) == "full_text" for r in out),
        "conflicts": conflicts,
        "warnings": warnings,
    }
    Path(args.conflicts).parent.mkdir(parents=True, exist_ok=True)
    Path(args.conflicts).write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    raise SystemExit(1 if conflicts else 0)


if __name__ == "__main__":
    main()
