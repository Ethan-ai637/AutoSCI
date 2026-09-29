#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
from collections import Counter, defaultdict
from pathlib import Path

from common import read_csv

ALLOWED_STATES = {"consistent", "mixed", "single_source", "single_study", "gap", "descriptive"}
ALLOWED_RELATIONS = {"supports", "contradicts", "qualifies", "context"}
ELIGIBLE_SUPPORT_LEVELS = {"direct", "derived"}
ELIGIBLE_VERIFICATION = {"verified", "partial"}


def norm(v):
    return str(v or "").strip()


def verification_coverage(counts: Counter) -> str:
    substantive = counts.get("verified", 0) + counts.get("partial", 0)
    if substantive == 0:
        return "not_applicable"
    if counts.get("partial", 0) == 0:
        return "complete"
    if counts.get("verified", 0) == 0:
        return "partial_only"
    return "mixed"


def main():
    ap = argparse.ArgumentParser(description="Audit claim-level provenance and verification coverage for cross-paper synthesis claims.")
    ap.add_argument("--evidence", required=True)
    ap.add_argument("--claims", required=True)
    ap.add_argument("--links", required=True)
    ap.add_argument("--study-map")
    ap.add_argument("--unit", choices=["auto", "study", "report"], default="auto")
    ap.add_argument("--report")
    ap.add_argument("--update-claims", action="store_true", help="After a passing audit, persist derived verification/support counts into synthesis_claims.csv")
    args = ap.parse_args()

    evidence = read_csv(args.evidence)
    claims = read_csv(args.claims)
    links = read_csv(args.links)
    errors, warnings = [], []

    study_by_record = {}
    if args.study_map:
        for idx, row in enumerate(read_csv(args.study_map), 2):
            rid, sid = norm(row.get("record_id")), norm(row.get("study_id"))
            if rid in study_by_record and sid != study_by_record[rid]:
                errors.append(f"study_map row {idx}: conflicting study_id for {rid}")
            if rid:
                study_by_record[rid] = sid

    evidence_by_claim = {}
    for idx, row in enumerate(evidence, 2):
        cid = norm(row.get("claim_id"))
        if not cid:
            errors.append(f"evidence row {idx}: missing claim_id")
        elif cid in evidence_by_claim:
            errors.append(f"duplicate evidence claim_id: {cid}")
        else:
            evidence_by_claim[cid] = row
        rid = norm(row.get("source_id"))
        explicit_sid = norm(row.get("study_id"))
        mapped_sid = study_by_record.get(rid, "")
        if args.study_map and explicit_sid and mapped_sid and explicit_sid != mapped_sid:
            errors.append(f"evidence row {idx}: study_id {explicit_sid} conflicts with study_map {mapped_sid} for {rid}")

    claim_by_id = {}
    for idx, row in enumerate(claims, 2):
        sid = norm(row.get("synthesis_id"))
        state = norm(row.get("evidence_state")).lower()
        if not sid:
            errors.append(f"synthesis row {idx}: missing synthesis_id")
            continue
        if sid in claim_by_id:
            errors.append(f"duplicate synthesis_id: {sid}")
        claim_by_id[sid] = row
        if not norm(row.get("statement")):
            errors.append(f"synthesis row {idx}: missing statement")
        if state and state not in ALLOWED_STATES:
            errors.append(f"synthesis row {idx}: invalid evidence_state {state!r}")

    by_synth = defaultdict(list)
    for idx, row in enumerate(links, 2):
        sid = norm(row.get("synthesis_id"))
        cid = norm(row.get("claim_id"))
        rel = norm(row.get("relation")).lower()
        if sid not in claim_by_id:
            errors.append(f"link row {idx}: unknown synthesis_id {sid}")
        if cid not in evidence_by_claim:
            errors.append(f"link row {idx}: unknown claim_id {cid}")
        if rel not in ALLOWED_RELATIONS:
            errors.append(f"link row {idx}: invalid relation {rel!r}")
        by_synth[sid].append(row)

    has_study_ids = any(norm(r.get("study_id")) for r in evidence) or bool(study_by_record)
    synthesis_unit = args.unit
    if synthesis_unit == "auto":
        synthesis_unit = "study" if has_study_ids else "report"
    if synthesis_unit == "study" and not has_study_ids:
        errors.append("study-level synthesis requested but no study IDs are available")

    claim_metrics = {}
    for sid, row in claim_by_id.items():
        state = norm(row.get("evidence_state")).lower()
        slinks = by_synth.get(sid, [])
        sources, studies = set(), set()
        eligible_support_sources, eligible_support_studies = set(), set()
        eligible_contradict_sources, eligible_contradict_studies = set(), set()
        ineligible_substantive_links = []
        verification_counts = Counter()
        eligible_claim_ids = []
        for x in slinks:
            cid = norm(x.get("claim_id"))
            erow = evidence_by_claim.get(cid, {})
            rid = norm(erow.get("source_id"))
            stid = norm(erow.get("study_id")) or study_by_record.get(rid, "")
            if rid:
                sources.add(rid)
            if stid:
                studies.add(stid)
            rel = norm(x.get("relation")).lower()
            support_level = norm(erow.get("support_level")).lower()
            verification = norm(erow.get("verification_status")).lower()
            eligible = support_level in ELIGIBLE_SUPPORT_LEVELS and verification in ELIGIBLE_VERIFICATION
            if rel in {"supports", "contradicts"}:
                if not eligible:
                    ineligible_substantive_links.append({
                        "claim_id": cid,
                        "relation": rel,
                        "support_level": support_level,
                        "verification_status": verification,
                    })
                else:
                    verification_counts[verification] += 1
                    eligible_claim_ids.append(cid)
                    if rel == "supports":
                        if rid:
                            eligible_support_sources.add(rid)
                        if stid:
                            eligible_support_studies.add(stid)
                    elif rel == "contradicts":
                        if rid:
                            eligible_contradict_sources.add(rid)
                        if stid:
                            eligible_contradict_studies.add(stid)
        if synthesis_unit == "study":
            support_units = eligible_support_studies
            contradict_units = eligible_contradict_studies
            unit_label = "studies"
        else:
            support_units = eligible_support_sources
            contradict_units = eligible_contradict_sources
            unit_label = "source records"

        coverage = verification_coverage(verification_counts)
        claim_metrics[sid] = {
            "source_records": len(sources),
            "studies": len(studies),
            "eligible_support_units": len(support_units),
            "eligible_contradict_units": len(contradict_units),
            "eligible_substantive_claims": len(eligible_claim_ids),
            "verification_counts": dict(verification_counts),
            "verification_coverage": coverage,
            "ineligible_substantive_links": ineligible_substantive_links,
        }
        if coverage in {"mixed", "partial_only"} and state not in {"gap"}:
            warnings.append(f"{sid}: substantive synthesis evidence has verification_coverage={coverage}; preserve this limitation in narrative output")
        if ineligible_substantive_links:
            warnings.append(
                f"{sid}: {len(ineligible_substantive_links)} supports/contradicts link(s) do not count as substantive evidence "
                "because support_level is not direct/derived or verification_status is not verified/partial"
            )
        if state == "gap":
            if support_units or contradict_units:
                errors.append(f"{sid}: gap claim has substantive supporting/contradicting evidence")
            elif slinks:
                warnings.append(f"{sid}: gap claim has contextual/qualifying links; ensure they describe the gap rather than fill it")
            continue
        if not slinks:
            errors.append(f"{sid}: synthesis claim has no evidence links")
            continue
        if state == "consistent":
            if len(support_units) < 2:
                errors.append(f"{sid}: consistent evidence requires >=2 distinct eligible supporting {unit_label}")
            if contradict_units:
                errors.append(f"{sid}: consistent evidence has {len(contradict_units)} eligible contradicting {unit_label}")
        if state == "mixed":
            if not support_units or not contradict_units:
                errors.append(f"{sid}: mixed evidence requires eligible supports and contradicts evidence")
        if state == "single_study":
            substantive_studies = eligible_support_studies | eligible_contradict_studies
            if len(substantive_studies) != 1:
                errors.append(f"{sid}: single_study requires substantive evidence from exactly 1 study")
            if synthesis_unit == "report":
                warnings.append(f"{sid}: single_study state is being used while synthesis unit is report")
        if state == "single_source":
            substantive_sources = eligible_support_sources | eligible_contradict_sources
            if len(substantive_sources) != 1:
                errors.append(f"{sid}: single_source requires substantive evidence from exactly 1 source record")
            if studies:
                warnings.append(f"{sid}: prefer evidence_state=single_study when a study_map is available")

    if args.update_claims and not errors:
        derived_fields = [
            "verification_coverage", "verified_evidence_count", "partial_evidence_count",
            "eligible_support_unit_count", "eligible_contradict_unit_count"
        ]
        existing_fields = list(claims[0].keys()) if claims else []
        canonical = [
            "synthesis_id", "statement", "research_question_component", "evidence_state",
            *derived_fields, "scope", "caveat", "notes"
        ]
        fieldnames = []
        for name in canonical + existing_fields:
            if name not in fieldnames:
                fieldnames.append(name)
        for row in claims:
            sid = norm(row.get("synthesis_id"))
            metrics = claim_metrics.get(sid, {})
            vcounts = metrics.get("verification_counts", {})
            row["verification_coverage"] = metrics.get("verification_coverage", "not_applicable")
            row["verified_evidence_count"] = str(vcounts.get("verified", 0))
            row["partial_evidence_count"] = str(vcounts.get("partial", 0))
            row["eligible_support_unit_count"] = str(metrics.get("eligible_support_units", 0))
            row["eligible_contradict_unit_count"] = str(metrics.get("eligible_contradict_units", 0))
        with Path(args.claims).open("w", encoding="utf-8", newline="") as f:
            w = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
            w.writeheader()
            w.writerows([{k: r.get(k, "") for k in fieldnames} for r in claims])

    result = {
        "evidence_claims": len(evidence_by_claim),
        "synthesis_claims": len(claim_by_id),
        "links": len(links),
        "study_aware": bool(has_study_ids),
        "synthesis_unit": synthesis_unit,
        "claim_metrics": claim_metrics,
        "errors": errors,
        "warnings": warnings,
        "passed": not errors,
    }
    if args.report:
        Path(args.report).parent.mkdir(parents=True, exist_ok=True)
        Path(args.report).write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    raise SystemExit(1 if errors else 0)


if __name__ == "__main__":
    main()
