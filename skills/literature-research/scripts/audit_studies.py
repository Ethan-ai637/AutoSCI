#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
from collections import defaultdict
from pathlib import Path

from common import read_csv

ALLOWED_ROLES = {
    "primary_or_only_report", "primary_report", "secondary_analysis", "follow_up",
    "protocol", "preprint_version", "conference_version", "journal_version",
    "supplement", "correction", "companion", "unknown"
}
ALLOWED_VERIFICATION = {"provisional", "verified", "partial", "unverified"}


def norm(v):
    return str(v or "").strip()


def write_summary(path, rows):
    fields = [
        "study_id", "report_count", "included_report_count", "report_roles",
        "verification_statuses", "record_ids", "years", "titles"
    ]
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)


def main():
    ap = argparse.ArgumentParser(description="Audit report-to-study mapping and summarize underlying studies.")
    ap.add_argument("--records", required=True)
    ap.add_argument("--study-map", required=True)
    ap.add_argument("--screening")
    ap.add_argument("--citation-trail")
    ap.add_argument("--evidence")
    ap.add_argument("--profile", choices=["exploratory", "standard", "systematic"], default="standard")
    ap.add_argument("--summary")
    ap.add_argument("--report")
    args = ap.parse_args()

    records = read_csv(args.records)
    record_by_id = {norm(r.get("record_id")): r for r in records if norm(r.get("record_id"))}
    ids = set(record_by_id)
    study_map = read_csv(args.study_map)
    errors, warnings = [], []

    map_by_record = {}
    groups = defaultdict(list)
    for idx, row in enumerate(study_map, 2):
        rid = norm(row.get("record_id"))
        sid = norm(row.get("study_id"))
        role = norm(row.get("report_role")).lower()
        status = norm(row.get("verification_status")).lower()
        basis = norm(row.get("linkage_basis"))
        if not rid:
            errors.append(f"study_map row {idx}: missing record_id")
            continue
        if rid not in ids:
            errors.append(f"study_map row {idx}: unknown record_id {rid}")
        if rid in map_by_record:
            errors.append(f"study_map row {idx}: duplicate mapping for record_id {rid}")
        map_by_record[rid] = row
        if not sid:
            errors.append(f"study_map row {idx}: missing study_id for {rid}")
        else:
            groups[sid].append(row)
        if role and role not in ALLOWED_ROLES:
            errors.append(f"study_map row {idx}: invalid report_role {role!r}")
        if status and status not in ALLOWED_VERIFICATION:
            errors.append(f"study_map row {idx}: invalid verification_status {status!r}")
        if not status:
            warnings.append(f"study_map row {idx}: missing verification_status")

    missing_map = ids - set(map_by_record)
    if missing_map:
        msg = f"study_map missing {len(missing_map)} record(s)"
        (errors if args.profile in {"standard", "systematic"} else warnings).append(msg)

    for sid, rows in groups.items():
        if len(rows) <= 1:
            continue
        for row in rows:
            rid = norm(row.get("record_id"))
            status = norm(row.get("verification_status")).lower()
            basis = norm(row.get("linkage_basis"))
            if not basis:
                msg = f"study {sid}: multi-report grouping lacks linkage_basis for {rid}"
                (errors if args.profile == "systematic" else warnings).append(msg)
            if status in {"provisional", "unverified", ""}:
                msg = f"study {sid}: multi-report grouping is not sufficiently verified for {rid} ({status or 'blank'})"
                (errors if args.profile == "systematic" else warnings).append(msg)

    decision_by_id = {}
    if args.screening:
        for row in read_csv(args.screening):
            decision_by_id[norm(row.get("record_id"))] = norm(row.get("decision")).lower()

    trail = read_csv(args.citation_trail) if args.citation_trail else []
    for idx, row in enumerate(trail, 2):
        if norm(row.get("relation")).lower() != "same_study_version":
            continue
        a, b = norm(row.get("source_id")), norm(row.get("target_id"))
        if a in map_by_record and b in map_by_record:
            sa = norm(map_by_record[a].get("study_id"))
            sb = norm(map_by_record[b].get("study_id"))
            if sa and sb and sa != sb:
                errors.append(
                    f"citation row {idx}: same_study_version edge {a}->{b} conflicts with study_map ({sa} != {sb})"
                )

    if args.evidence:
        for idx, row in enumerate(read_csv(args.evidence), 2):
            rid = norm(row.get("source_id"))
            evid_sid = norm(row.get("study_id"))
            mapped = norm(map_by_record.get(rid, {}).get("study_id"))
            if rid and rid in map_by_record:
                if args.profile in {"standard", "systematic"} and not evid_sid:
                    errors.append(f"evidence row {idx}: missing study_id for source {rid}")
                elif evid_sid and mapped and evid_sid != mapped:
                    errors.append(
                        f"evidence row {idx}: study_id {evid_sid} disagrees with study_map {mapped} for source {rid}"
                    )

    summary_rows = []
    for sid in sorted(groups):
        rows = groups[sid]
        rids = [norm(r.get("record_id")) for r in rows]
        recs = [record_by_id[rid] for rid in rids if rid in record_by_id]
        summary_rows.append({
            "study_id": sid,
            "report_count": len(rows),
            "included_report_count": sum(decision_by_id.get(rid) == "include" for rid in rids),
            "report_roles": ";".join(sorted({norm(r.get("report_role")) for r in rows if norm(r.get("report_role"))})),
            "verification_statuses": ";".join(sorted({norm(r.get("verification_status")) for r in rows if norm(r.get("verification_status"))})),
            "record_ids": ";".join(rids),
            "years": ";".join(sorted({norm(r.get("year")) for r in recs if norm(r.get("year"))})),
            "titles": " | ".join(norm(r.get("title")) for r in recs if norm(r.get("title"))),
        })

    result = {
        "records": len(records),
        "mapped_records": len(map_by_record),
        "studies": len(groups),
        "multi_report_studies": sum(len(rows) > 1 for rows in groups.values()),
        "included_reports": sum(v == "include" for v in decision_by_id.values()),
        "included_studies": len({
            norm(map_by_record[rid].get("study_id"))
            for rid, dec in decision_by_id.items()
            if dec == "include" and rid in map_by_record and norm(map_by_record[rid].get("study_id"))
        }),
        "errors": errors,
        "warnings": warnings,
        "passed": not errors,
    }
    if args.summary:
        write_summary(args.summary, summary_rows)
    if args.report:
        Path(args.report).parent.mkdir(parents=True, exist_ok=True)
        Path(args.report).write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    raise SystemExit(1 if errors else 0)


if __name__ == "__main__":
    main()
