#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
from pathlib import Path
from typing import Any

from _util import load_json, read_jsonl, utc_now, write_json


def _number(v: Any) -> float | None:
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def _variation_bounds(reported: dict) -> tuple[float, float] | None:
    center = _number(reported.get("value"))
    variation = reported.get("variation") or {}
    if center is None or not isinstance(variation, dict):
        return None
    if _number(variation.get("lower")) is not None and _number(variation.get("upper")) is not None:
        return float(variation["lower"]), float(variation["upper"])
    width = _number(variation.get("value"))
    if width is not None:
        multiplier = _number(variation.get("multiplier")) or 1.0
        return center - multiplier * width, center + multiplier * width
    return None


def compare(claim: dict, observed: float) -> tuple[str | None, dict]:
    reported = claim.get("reported") or {}
    expected = _number(reported.get("value"))
    rule = claim.get("comparison_rule") or {}
    kind = rule.get("kind")
    params = rule.get("parameters") or {}
    details = {"kind": kind, "expected": expected, "observed": observed, "parameters": params}
    if expected is None:
        return None, details
    if kind in {"exact", "deterministic_equality"}:
        return ("exact_reproduction" if observed == expected else "numerically_different"), details
    if kind == "absolute_tolerance":
        tol = _number(params.get("tolerance"))
        if tol is None:
            return None, details
        details["absolute_error"] = abs(observed - expected)
        return ("within_reported_variation" if abs(observed - expected) <= tol else "numerically_different"), details
    if kind == "relative_tolerance":
        tol = _number(params.get("tolerance"))
        if tol is None or expected == 0:
            return None, details
        err = abs(observed - expected) / abs(expected)
        details["relative_error"] = err
        return ("within_reported_variation" if err <= tol else "numerically_different"), details
    if kind == "reported_variation":
        bounds = _variation_bounds(reported)
        if not bounds:
            return None, details
        details["bounds"] = list(bounds)
        return ("within_reported_variation" if bounds[0] <= observed <= bounds[1] else "numerically_different"), details
    return None, details


def main() -> int:
    ap = argparse.ArgumentParser(description="Deterministically reconcile scalar claim metrics using predeclared comparison rules.")
    ap.add_argument("workspace", type=Path)
    ap.add_argument("--output", type=Path)
    args = ap.parse_args()
    ws = args.workspace.resolve()
    contract = load_json(ws / "reproduction_contract.json")
    claims = {c["claim_id"]: c for c in contract.get("target_claims") or [] if c.get("claim_id")}
    runs = {r.get("run_id"): r for r in read_jsonl(ws / "run_ledger.jsonl") if r.get("run_id")}

    rows = []
    with (ws / "metrics.csv").open("r", encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            if not any((v or "").strip() for v in row.values()):
                continue
            rows.append(row)

    results = []
    for row in rows:
        cid = row.get("claim_id")
        rid = row.get("run_id")
        claim = claims.get(cid)
        run = runs.get(rid)
        observed = _number(row.get("value"))
        if not claim or not run or observed is None or run.get("exit_code") != 0 or run.get("run_kind") != "target":
            continue
        expected_metric = claim.get("metric")
        actual_metric = row.get("metric")
        if expected_metric and (actual_metric or "").strip().casefold() != expected_metric.strip().casefold():
            continue
        state, details = compare(claim, observed)
        if state:
            results.append({
                "claim_id": cid,
                "state": state,
                "supporting_run_ids": [rid],
                "comparison_rule": claim.get("comparison_rule"),
                "reported": claim.get("reported"),
                "observed": {"value": observed, "metric": row.get("metric"), "unit": row.get("unit"), "run_id": rid},
                "material_deviations": [],
                "limitations": [],
                "reconciliation": {"method": "deterministic_scalar_rule", **details},
                "notes": None,
            })

    out_obj = {"schema_version": "1.1", "generated_at": utc_now(), "assessments": results}
    out = args.output.resolve() if args.output else ws / "reproduction_assessment.candidate.json"
    write_json(out, out_obj)
    print(f"wrote {len(results)} deterministic candidate assessment(s) -> {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
