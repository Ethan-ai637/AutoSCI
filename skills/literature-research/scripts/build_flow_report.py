#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

from common import read_csv


def norm(v):
    return str(v or "").strip()


def maybe_int(v):
    s = norm(v)
    if not s:
        return None
    try:
        return int(float(s))
    except ValueError:
        return None


def sum_known(rows, field):
    vals = [maybe_int(r.get(field)) for r in rows]
    known = [v for v in vals if v is not None]
    return (sum(known), len(known), len(vals) - len(known))


def main():
    ap = argparse.ArgumentParser(description="Build a count-reconciliation report for a literature-research workspace.")
    ap.add_argument("--search-log", required=True)
    ap.add_argument("--records", required=True, help="Deduplicated canonical records CSV")
    ap.add_argument("--dedup-report")
    ap.add_argument("--screening", required=True)
    ap.add_argument("--screening-log")
    ap.add_argument("--study-map")
    ap.add_argument("--evidence")
    ap.add_argument("--synthesis-claims")
    ap.add_argument("--synthesis-evidence")
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    warnings, errors = [], []
    search = read_csv(args.search_log)
    records = read_csv(args.records)
    screening = read_csv(args.screening)
    screening_log = read_csv(args.screening_log) if args.screening_log else []
    study_map = read_csv(args.study_map) if args.study_map else []
    evidence = read_csv(args.evidence) if args.evidence else []
    synth_claims = read_csv(args.synthesis_claims) if args.synthesis_claims else []
    synth_links = read_csv(args.synthesis_evidence) if args.synthesis_evidence else []

    result_sum, result_known, result_missing = sum_known(search, "result_count")
    imported_sum, imported_known, imported_missing = sum_known(search, "imported_count")
    new_unique_sum, new_unique_known, new_unique_missing = sum_known(search, "new_unique_count")
    new_screened_sum, new_screened_known, new_screened_missing = sum_known(search, "new_screened_count")
    new_included_sum, new_included_known, new_included_missing = sum_known(search, "new_included_count")

    dedup = {}
    if args.dedup_report:
        p = Path(args.dedup_report)
        if not p.exists():
            errors.append(f"dedup report not found: {p}")
        else:
            try:
                dedup = json.loads(p.read_text(encoding="utf-8"))
            except Exception as exc:
                errors.append(f"could not parse dedup report: {exc}")

    decision_counts = Counter(norm(r.get("decision")).lower() or "blank" for r in screening)
    stage_counts = Counter(norm(r.get("screening_stage")).lower() or "blank" for r in screening)
    event_stage_counts = Counter(norm(r.get("stage")).lower() or "blank" for r in screening_log)
    access_counts = Counter(norm(r.get("access_level")).lower() or "blank" for r in screening)
    evidence_stage_counts = Counter(norm(r.get("evidence_stage")).lower() or "blank" for r in screening)
    search_status_counts = Counter(norm(r.get("search_status")).lower() or "blank" for r in search)

    study_by_record = {norm(r.get("record_id")): norm(r.get("study_id")) for r in study_map if norm(r.get("record_id"))}
    included_ids = {norm(r.get("record_id")) for r in screening if norm(r.get("decision")).lower() == "include"}
    included_studies = {study_by_record[rid] for rid in included_ids if study_by_record.get(rid)}

    unique_record_ids = {norm(r.get("record_id")) for r in records if norm(r.get("record_id"))}
    if len(unique_record_ids) != len(records):
        errors.append("records CSV contains missing or duplicate record_id values")
    screened_ids = {norm(r.get("record_id")) for r in screening if norm(r.get("record_id"))}
    if screened_ids - unique_record_ids:
        errors.append("screening contains record IDs absent from canonical records")
    if unique_record_ids - screened_ids:
        warnings.append(f"{len(unique_record_ids-screened_ids)} canonical record(s) have no final screening row")

    if dedup:
        out_n = dedup.get("output_records")
        if isinstance(out_n, int) and out_n != len(records):
            errors.append(f"dedup report output_records={out_n} but records CSV has {len(records)} rows")
        in_n = dedup.get("input_records")
        removed = dedup.get("duplicates_removed")
        if isinstance(in_n, int) and isinstance(out_n, int) and isinstance(removed, int):
            if in_n - out_n != removed:
                errors.append("dedup report counts do not reconcile: input - output != duplicates_removed")

    if imported_known == len(search) and dedup.get("input_records") is not None:
        # This is only a warning because imported_count can legitimately count records later rejected before normalization.
        if imported_sum < int(dedup.get("input_records", 0)):
            warnings.append("sum(imported_count) is smaller than dedup input_records; check for unlogged imports or differing count definitions")

    flow = {
        "search": {
            "query_rows": len(search),
            "reported_result_count_sum": result_sum,
            "reported_result_count_rows_known": result_known,
            "reported_result_count_rows_missing": result_missing,
            "imported_count_sum": imported_sum,
            "imported_count_rows_known": imported_known,
            "imported_count_rows_missing": imported_missing,
            "new_unique_count_sum": new_unique_sum,
            "new_unique_count_rows_known": new_unique_known,
            "new_unique_count_rows_missing": new_unique_missing,
            "new_screened_count_sum": new_screened_sum,
            "new_screened_count_rows_known": new_screened_known,
            "new_screened_count_rows_missing": new_screened_missing,
            "new_included_count_sum": new_included_sum,
            "new_included_count_rows_known": new_included_known,
            "new_included_count_rows_missing": new_included_missing,
            "search_status_counts": dict(sorted(search_status_counts.items())),
        },
        "deduplication": {
            "input_records": dedup.get("input_records"),
            "canonical_records": len(records),
            "duplicates_removed": dedup.get("duplicates_removed"),
        },
        "screening": {
            "final_rows": len(screening),
            "final_decisions": dict(sorted(decision_counts.items())),
            "final_stage_counts": dict(sorted(stage_counts.items())),
            "screening_events": len(screening_log),
            "event_stage_counts": dict(sorted(event_stage_counts.items())),
            "evidence_stage_counts": dict(sorted(evidence_stage_counts.items())),
            "access_level_counts": dict(sorted(access_counts.items())),
        },
        "study_identity": {
            "mapped_reports": len(study_by_record),
            "distinct_studies": len({x for x in study_by_record.values() if x}),
            "included_reports": len(included_ids),
            "included_studies": len(included_studies),
        },
        "evidence_and_synthesis": {
            "evidence_claims": len(evidence),
            "synthesis_claims": len(synth_claims),
            "synthesis_links": len(synth_links),
        },
    }

    out = {
        "flow": flow,
        "notes": [
            "Reported search-hit totals are sums across query rows and may contain overlap.",
            "This report reconciles workspace counts; it is not by itself a PRISMA-compliant flow diagram or proof of exhaustive search coverage.",
        ],
        "errors": errors,
        "warnings": warnings,
        "passed": not errors,
    }
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out).write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(out, ensure_ascii=False, indent=2))
    raise SystemExit(1 if errors else 0)


if __name__ == "__main__":
    main()
