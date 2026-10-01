#!/usr/bin/env python3
from __future__ import annotations

import argparse
import math
from pathlib import Path
import numpy as np
import pandas as pd

from _common import read_json, read_artifact_csv, sha256_file, write_json, SKILL_VERSION, POWER_PLAN_SCHEMA_VERSION
from validate_power_plan import validate
from _power import expand_and_calculate


def _truthy(v):
    if isinstance(v, bool):
        return v
    return str(v).strip().lower() in {"true", "1", "yes"}


def _values_match(actual, expected, *, rtol=1e-10, atol=1e-12):
    if expected is None:
        return pd.isna(actual)
    try:
        if pd.isna(expected):
            return pd.isna(actual)
    except Exception:
        pass
    if isinstance(expected, str) and expected == "" and pd.isna(actual):
        return True
    if isinstance(expected, (bool, np.bool_)):
        return _truthy(actual) == bool(expected)
    if isinstance(expected, (int, float, np.integer, np.floating)) and not isinstance(expected, (bool, np.bool_)):
        try:
            av = float(actual); ev = float(expected)
        except Exception:
            return False
        if not (math.isfinite(av) and math.isfinite(ev)):
            return av == ev
        return math.isclose(av, ev, rel_tol=rtol, abs_tol=atol)
    return str(actual) == str(expected)


def main():
    ap = argparse.ArgumentParser(description="Deterministically audit a power/sample-size planning artifact")
    ap.add_argument("--plan", required=True)
    ap.add_argument("--results", required=True)
    ap.add_argument("--report", required=True)
    args = ap.parse_args()

    plan = read_json(args.plan)
    actual = read_artifact_csv(args.results)
    errors, warnings = validate(plan)
    plan_hash = sha256_file(args.plan)

    expected_rows = expand_and_calculate(plan)
    for row in expected_rows:
        row["plan_sha256"] = plan_hash
        row["skill_version"] = SKILL_VERSION
        row["power_plan_schema_version"] = POWER_PLAN_SCHEMA_VERSION

    # The binary-proportion core uses a normal approximation.  Treat very
    # sparse expected event/non-event counts as a release-level adequacy issue
    # rather than silently presenting an exact-looking integer recommendation.
    for row in expected_rows:
        if row.get("type") != "independent_proportions":
            continue
        key = f"{row.get('planning_item_id')}::{row.get('scenario_id')}"
        adequacy = row.get("normal_approximation_adequacy")
        m = row.get("min_expected_cell_count")
        if adequacy == "poor_extreme_sparsity":
            errors.append(
                f"{key}: two-proportion normal approximation has extreme sparsity "
                f"(minimum expected event/non-event count={float(m):.6g} < 1); "
                "do not release this planning result as reliable—use an exact, simulation-based, or other design-specific method"
            )
        elif adequacy == "caution_sparse":
            warnings.append(
                f"{key}: two-proportion normal approximation is sparse "
                f"(minimum expected event/non-event count={float(m):.6g} < 5); "
                "treat the result as approximate and consider exact/simulation-based planning"
            )

    duplicate_keys = False
    if "planning_item_id" not in actual.columns or "scenario_id" not in actual.columns:
        errors.append("power results must contain planning_item_id and scenario_id")
        actual_keys = set()
    else:
        key_series = actual["planning_item_id"].astype(str) + "::" + actual["scenario_id"].astype(str)
        duplicate_keys = bool(key_series.duplicated().any())
        if duplicate_keys:
            errors.append("power results contain duplicate planning_item_id/scenario_id rows")
        actual_keys = set(key_series)

    expected_keys = {str(r["planning_item_id"]) + "::" + str(r["scenario_id"]) for r in expected_rows}
    if actual_keys != expected_keys:
        errors.append(f"Power result keys mismatch. missing={sorted(expected_keys-actual_keys)} extra={sorted(actual_keys-expected_keys)}")

    actual_by_key = {}
    if "planning_item_id" in actual.columns and "scenario_id" in actual.columns:
        for _, r in actual.iterrows():
            actual_by_key[str(r["planning_item_id"]) + "::" + str(r["scenario_id"])] = r

    mismatch_count = 0
    for exp in expected_rows:
        key = str(exp["planning_item_id"]) + "::" + str(exp["scenario_id"])
        act = actual_by_key.get(key)
        if act is None:
            continue
        for field, ev in exp.items():
            if field not in actual.columns:
                errors.append(f"{key}: results missing recomputable field {field}")
                mismatch_count += 1
                continue
            if not _values_match(act.get(field), ev):
                errors.append(f"{key}: deterministic power reconciliation mismatch for {field} (artifact={act.get(field)!r}, recomputed={ev!r})")
                mismatch_count += 1
            if mismatch_count >= 25:
                errors.append("Deterministic power reconciliation stopped after 25 mismatches")
                break
        if mismatch_count >= 25:
            break

    for _, r in actual.iterrows():
        if "achieved_power" in r and pd.notna(r.get("achieved_power")):
            p = float(r["achieved_power"])
            if not (0 <= p <= 1):
                errors.append(f"{r.get('planning_item_id')}::{r.get('scenario_id')}: achieved_power outside [0,1]")
        for col in ["n_a_analyzable", "n_b_analyzable", "n_pairs_analyzable", "n_reference_analyzable", "n_total_analyzable", "n_total_enroll"]:
            if col in r.index and pd.notna(r.get(col)) and float(r.get(col)) < 0:
                errors.append(f"{r.get('planning_item_id')}::{r.get('scenario_id')}: {col} is negative")

    status = "PASS" if not errors else "FAIL"
    report = {
        "status": status,
        "skill_version": SKILL_VERSION,
        "power_plan_schema_version": POWER_PLAN_SCHEMA_VERSION,
        "planning_id": plan.get("planning_id"),
        "plan_sha256": plan_hash,
        "deterministic_power_reconciliation": "PASS" if mismatch_count == 0 and actual_keys == expected_keys and not duplicate_keys and len(actual) == len(expected_rows) else "FAIL",
        "n_planning_rows": len(expected_rows),
        "n_result_rows": len(actual),
        "warnings": warnings,
        "errors": errors,
    }
    write_json(report, args.report)
    print(f"Power preflight: {status} ({len(errors)} errors, {len(warnings)} warnings)")
    if errors:
        for e in errors:
            print(f"ERROR: {e}")
        raise SystemExit(1)


if __name__ == "__main__":
    main()
