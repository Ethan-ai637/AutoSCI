#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path

from common import read_csv

STRUCTURED_STAGES = {"structured", "gap"}
ITERATIVE_STAGES = {"structured", "backward", "forward", "gap", "update"}
ALLOWED_STAGES = {"seed", "structured", "backward", "forward", "gap", "update", "other"}
ALLOWED_STATUS = {"succeeded", "partial", "failed"}
TRUE_VALUES = {"1", "true", "yes", "y"}


def norm(v):
    return str(v or "").strip()


def split_tokens(v):
    return [x.strip() for x in norm(v).replace(",", ";").split(";") if x.strip()]


def as_number(v):
    s = norm(v)
    if not s:
        return None
    try:
        return float(s)
    except ValueError:
        return None


def effective_status(row):
    declared = norm(row.get("search_status")).lower()
    result_count = as_number(row.get("result_count"))
    imported = as_number(row.get("imported_count"))
    notes = norm(row.get("notes")).lower()
    if declared in ALLOWED_STATUS:
        status = declared
    elif "fail" in notes or "http 4" in notes or "http 5" in notes or "inaccessible" in notes:
        status = "failed"
    else:
        status = ""
    # A capped/sample import cannot represent complete query retrieval even if the call itself succeeded.
    if status == "succeeded" and result_count is not None and imported is not None and result_count > imported:
        status = "partial"
    return status


def source_status(rows):
    statuses = [effective_status(r) for r in rows]
    statuses = [s for s in statuses if s]
    if not rows:
        return "not_attempted"
    if not statuses:
        return "unknown"
    if all(s == "failed" for s in statuses):
        return "failed"
    if all(s == "succeeded" for s in statuses):
        return "succeeded"
    return "partial"


def main():
    ap = argparse.ArgumentParser(description="Audit search execution, coverage, and marginal-yield evidence against the protocol.")
    ap.add_argument("--protocol", required=True)
    ap.add_argument("--search-log", required=True)
    ap.add_argument("--report")
    args = ap.parse_args()

    protocol = json.loads(Path(args.protocol).read_text(encoding="utf-8"))
    profile = norm(protocol.get("profile", "standard")).lower()
    rows = read_csv(args.search_log)
    errors, warnings = [], []

    qids = []
    concept_names = {norm(c.get("name")) for c in protocol.get("concepts", []) if norm(c.get("name"))}
    concepts_seen = set()
    stage_counts = {}
    source_rows = defaultdict(list)
    yield_missing_rows = []
    stopping_rows = []

    for idx, row in enumerate(rows, 2):
        qid = norm(row.get("query_id"))
        source = norm(row.get("source"))
        query = norm(row.get("query"))
        stage = norm(row.get("search_stage")).lower() or "other"
        status = effective_status(row)
        stage_counts[stage] = stage_counts.get(stage, 0) + 1
        if qid:
            qids.append(qid)
        else:
            errors.append(f"search row {idx}: missing query_id")
        if not source or not query:
            errors.append(f"search row {idx}: missing source/query")
        if source:
            source_rows[source.casefold()].append(row)
        if stage not in ALLOWED_STAGES:
            warnings.append(f"search row {idx}: unrecognized search_stage {stage!r}")
        blocks = set(split_tokens(row.get("concept_blocks")))
        concepts_seen |= blocks
        unknown = sorted(blocks - concept_names)
        if unknown:
            warnings.append(f"search row {idx}: unknown concept_blocks {unknown}")
        if stage in STRUCTURED_STAGES and concept_names and not blocks:
            warnings.append(f"search row {idx}: {stage} search has no concept_blocks")

        declared = norm(row.get("search_status")).lower()
        if declared and declared not in ALLOWED_STATUS:
            errors.append(f"search row {idx}: invalid search_status {declared!r}")
        if profile in {"standard", "systematic"} and not declared:
            msg = f"search row {idx}: search_status is required to distinguish successful, partial, and failed retrieval"
            (errors if profile == "systematic" else warnings).append(msg)
        if status == "failed":
            imported = as_number(row.get("imported_count"))
            if imported not in (None, 0):
                errors.append(f"search row {idx}: failed search cannot import {imported:g} records")
        if declared == "succeeded":
            rc, ic = as_number(row.get("result_count")), as_number(row.get("imported_count"))
            if rc is not None and ic is not None and rc > ic:
                warnings.append(f"search row {idx}: declared succeeded but imported {ic:g}/{rc:g}; effective coverage is partial")

        imported = as_number(row.get("imported_count"))
        if stage in ITERATIVE_STAGES and status != "failed" and imported is not None and imported > 0:
            missing = [f for f in ("new_unique_count", "new_screened_count", "new_included_count") if as_number(row.get(f)) is None]
            if missing:
                yield_missing_rows.append({"row": idx, "query_id": qid, "missing": missing})
        if norm(row.get("stopping_evidence")).lower() in TRUE_VALUES:
            stopping_rows.append((idx, row))

        if profile == "systematic":
            if not norm(row.get("searched_at")):
                errors.append(f"search row {idx}: systematic profile requires searched_at")
            if not norm(row.get("interface")):
                warnings.append(f"search row {idx}: systematic profile should record interface/version when available")
            if status in {"succeeded", "partial"} and as_number(row.get("result_count")) is None:
                warnings.append(f"search row {idx}: successful/partial query has missing/non-numeric result_count")

    dup_qids = sorted({x for x in qids if qids.count(x) > 1})
    if dup_qids:
        errors.append(f"duplicate query_id values: {dup_qids}")

    target_sources = [norm(x) for x in protocol.get("target_sources", []) if norm(x)]
    coverage = {}
    for source in target_sources:
        coverage[source] = source_status(source_rows.get(source.casefold(), []))
    not_attempted = [s for s, status in coverage.items() if status == "not_attempted"]
    failed = [s for s, status in coverage.items() if status == "failed"]
    partial = [s for s, status in coverage.items() if status in {"partial", "unknown"}]
    succeeded = [s for s, status in coverage.items() if status == "succeeded"]

    if not_attempted:
        msg = f"protocol target_sources not attempted: {not_attempted}"
        (errors if profile == "systematic" else warnings).append(msg)
    if failed:
        msg = f"protocol target_sources attempted but retrieval failed: {failed}"
        (errors if profile == "systematic" else warnings).append(msg)
    if partial:
        warnings.append(f"protocol target_sources only partially/unclearly covered: {partial}")

    missing_concepts = sorted(concept_names - concepts_seen)
    if missing_concepts and rows:
        warnings.append(f"protocol concepts never tagged in search_log concept_blocks: {missing_concepts}")

    if profile in {"standard", "systematic"} and not rows:
        errors.append("search_log is empty")
    if profile == "systematic" and stage_counts.get("structured", 0) == 0:
        errors.append("systematic profile has no structured search row")

    # Stopping-rule verifiability is deliberately separate from general search-log validity.
    if stopping_rows:
        incomplete = []
        for idx, row in stopping_rows:
            status = effective_status(row)
            missing = [f for f in ("new_unique_count", "new_screened_count", "new_included_count") if as_number(row.get(f)) is None]
            if status not in {"succeeded", "partial"} or missing:
                incomplete.append({"row": idx, "query_id": norm(row.get("query_id")), "status": status or "unknown", "missing": missing})
        stopping_status = "verifiable" if not incomplete else "not_assessable"
        stopping_basis = "explicit_stopping_evidence_rows"
    else:
        # Without explicit tagging, iterative rows can document marginal yield but cannot prove which rows justified stopping.
        incomplete = list(yield_missing_rows)
        stopping_status = "not_assessable" if protocol.get("stopping_rule") else "not_applicable"
        stopping_basis = "no_explicit_stopping_evidence"

    if yield_missing_rows:
        msg = f"{len(yield_missing_rows)} successful/partial iterative search row(s) imported records without complete marginal-yield counts"
        (errors if profile == "systematic" else warnings).append(msg)
    if protocol.get("stopping_rule") and stopping_status != "verifiable":
        msg = "stopping rule is recorded but cannot be mechanically verified from tagged, complete marginal-yield evidence"
        (errors if profile == "systematic" else warnings).append(msg)

    result = {
        "profile": profile,
        "search_rows": len(rows),
        "stage_counts": stage_counts,
        "target_sources": target_sources,
        "source_coverage": coverage,
        "not_attempted_target_sources": not_attempted,
        "failed_target_sources": failed,
        "partial_target_sources": partial,
        "succeeded_target_sources": succeeded,
        "protocol_concepts": sorted(concept_names),
        "concepts_seen": sorted(concepts_seen),
        "missing_concepts": missing_concepts,
        "marginal_yield_complete": not yield_missing_rows,
        "marginal_yield_missing_rows": yield_missing_rows,
        "stopping_rule_status": stopping_status,
        "stopping_rule_basis": stopping_basis,
        "stopping_rule_incomplete_rows": incomplete,
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
