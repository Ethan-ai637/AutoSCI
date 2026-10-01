#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from copy import deepcopy
from pathlib import Path

import numpy as np
import pandas as pd

from _common import (
    read_json, read_table, read_artifact_csv, sha256_file, write_json, stable_seed, SKILL_VERSION,
    categorical_level_mask, categorical_levels_mask,
)
from run_stats import run_item
from validate_plan import validate


def _mask_rule(df, rule):
    col = rule["column"]
    if col not in df.columns:
        raise KeyError(f"Sensitivity filter column not found: {col}")
    s = df[col]
    op = rule["operator"]
    # Categorical equality filters use the same typed scalar identity as
    # cleaning and inference. This prevents Python/pandas equality aliases
    # such as boolean True and numeric 1 from changing the intended subset.
    if op == "eq":
        return categorical_level_mask(s, rule.get("value"))
    if op == "ne":
        return ~categorical_level_mask(s, rule.get("value"))
    if op == "in":
        return categorical_levels_mask(s, rule.get("values", []))
    if op == "not_in":
        return ~categorical_levels_mask(s, rule.get("values", []))
    if op == "isna":
        return s.isna()
    if op == "notna":
        return s.notna()
    numeric = pd.to_numeric(s, errors="coerce")
    value = float(rule["value"])
    if op == "lt": return numeric < value
    if op == "le": return numeric <= value
    if op == "gt": return numeric > value
    if op == "ge": return numeric >= value
    raise ValueError(f"Unsupported sensitivity filter operator: {op}")


def apply_filter(df, filter_spec):
    rules = (filter_spec or {}).get("exclude_if", [])
    if not rules:
        return df.copy(), pd.Series(False, index=df.index)
    exclude = pd.Series(False, index=df.index)
    for rule in rules:
        exclude |= _mask_rule(df, rule).fillna(False)
    return df.loc[~exclude].copy(), exclude


def null_relation(lo, hi, null):
    if lo is None or hi is None or pd.isna(lo) or pd.isna(hi) or null is None or pd.isna(null):
        return "not_available"
    return "includes_null" if float(lo) <= float(null) <= float(hi) else "excludes_null"


def direction_from_estimate(est, null):
    if est is None or pd.isna(est) or null is None or pd.isna(null):
        return "not_available"
    delta = float(est) - float(null)
    if delta > 0: return "above_null"
    if delta < 0: return "below_null"
    return "at_null"


def compute_sensitivity_rows(df, plan, base_results, *, data_hash=None, plan_hash=None):
    """Deterministically compute every declared sensitivity result.

    `base_results` must represent the exact base analyses whose values are copied
    into the sensitivity artifact. Callers that need an independent audit should
    pass freshly recomputed base results rather than trusting an artifact file.
    """
    sensitivities = plan.get("sensitivity_analyses", [])
    by_analysis = {a["analysis_item_id"]: a for a in plan["analyses"]}
    by_result = {str(r["analysis_item_id"]): r for _, r in base_results.iterrows()}
    level = float(plan.get("confidence_level", 0.95))
    seed = int(plan.get("random_seed", 0))
    n_resamples = int(plan.get("resampling", {}).get("n_resamples", 2000))
    missing_strategy = plan.get("missing_data", {}).get("strategy", "complete_case")

    rows = []
    for spec in sensitivities:
        sid = spec["sensitivity_id"]
        base_id = spec["base_analysis_item_id"]
        if base_id not in by_result:
            raise ValueError(f"{sid}: base result '{base_id}' is missing")
        subset, excluded_mask = apply_filter(df, spec.get("data_filter"))
        analysis = deepcopy(by_analysis[base_id])
        analysis.update(spec.get("analysis_overrides") or {})
        analysis["analysis_item_id"] = f"sensitivity::{sid}"
        analysis["multiplicity_family"] = ""
        result = run_item(
            subset, analysis, level, stable_seed(seed, f"sensitivity::{sid}"),
            n_resamples=n_resamples, missing_strategy=missing_strategy,
        )
        base = by_result[base_id]

        estimand_relation = spec.get("estimand_relation", "uncertain")
        same_estimand = estimand_relation == "same"
        result.update({
            "sensitivity_id": sid,
            "base_analysis_item_id": base_id,
            "rationale": spec.get("rationale", ""),
            "rows_before": int(len(df)),
            "rows_after": int(len(subset)),
            "rows_excluded": int(excluded_mask.sum()),
            "data_filter_json": json.dumps(spec.get("data_filter") or {}, sort_keys=True),
            "analysis_overrides_json": json.dumps(spec.get("analysis_overrides") or {}, sort_keys=True),
            "base_type": by_analysis[base_id]["type"],
            "base_estimate": base.get("estimate"),
            "base_estimate_name": base.get("estimate_name"),
            "base_ci_low": base.get("ci_low"),
            "base_ci_high": base.get("ci_high"),
            "base_p_value": base.get("p_value"),
            "base_p_adjusted": base.get("p_adjusted"),
            "estimand_relation": estimand_relation,
            "same_estimand_as_base": bool(same_estimand),
            "base_null_relation": null_relation(base.get("ci_low"), base.get("ci_high"), base.get("null_value")),
            "sensitivity_null_relation": null_relation(result.get("ci_low"), result.get("ci_high"), result.get("null_value")),
            "base_direction": direction_from_estimate(base.get("estimate"), base.get("null_value")),
            "sensitivity_direction": direction_from_estimate(result.get("estimate"), result.get("null_value")),
            "data_sha256": data_hash,
            "plan_sha256": plan_hash,
            "skill_version": SKILL_VERSION,
        })
        if same_estimand and pd.notna(base.get("estimate")) and result.get("estimate") is not None:
            delta = float(result["estimate"]) - float(base["estimate"])
            result["estimate_change_from_base"] = delta
            b = float(base["estimate"])
            result["relative_estimate_change_from_base"] = (delta / abs(b)) if b != 0 else None
        else:
            result["estimate_change_from_base"] = None
            result["relative_estimate_change_from_base"] = None
        rows.append(result)
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", required=True)
    ap.add_argument("--plan", required=True)
    ap.add_argument("--base-results", required=True)
    ap.add_argument("--out-csv", required=True)
    ap.add_argument("--out-json", required=True)
    args = ap.parse_args()

    plan = read_json(args.plan)
    errors, warnings = validate(plan)
    if errors:
        raise ValueError("Invalid analysis plan: " + "; ".join(errors))
    for w in warnings:
        print(f"WARNING: {w}")

    df = read_table(args.data)
    base_results = read_artifact_csv(args.base_results)
    by_analysis = {a["analysis_item_id"]: a for a in plan["analyses"]}
    data_hash = sha256_file(args.data)
    plan_hash = sha256_file(args.plan)

    # A sensitivity analysis is only interpretable relative to the exact base
    # analysis it perturbs. Reject stale or ambiguous base-result artifacts
    # before copying their estimates into a newly stamped sensitivity file.
    if "analysis_item_id" not in base_results.columns:
        raise ValueError("--base-results is missing analysis_item_id")
    if base_results["analysis_item_id"].astype(str).duplicated().any():
        dup = sorted(base_results.loc[base_results["analysis_item_id"].astype(str).duplicated(keep=False), "analysis_item_id"].astype(str).unique())
        raise ValueError(f"--base-results contains duplicate analysis_item_id values: {dup}")
    if "data_sha256" not in base_results.columns or set(base_results["data_sha256"].dropna().astype(str).unique()) != {data_hash}:
        raise ValueError("--base-results data_sha256 does not uniquely match the current analysis-ready data")
    if "plan_sha256" not in base_results.columns or set(base_results["plan_sha256"].dropna().astype(str).unique()) != {plan_hash}:
        raise ValueError("--base-results plan_sha256 does not uniquely match the current analysis plan")
    if "skill_version" not in base_results.columns or set(base_results["skill_version"].dropna().astype(str).unique()) != {SKILL_VERSION}:
        raise ValueError(f"--base-results skill_version does not uniquely match current skill version {SKILL_VERSION}; rerun base statistics")
    missing_base_ids = sorted(set(by_analysis) - set(base_results["analysis_item_id"].astype(str)))
    if missing_base_ids:
        raise ValueError(f"--base-results is missing planned analysis result(s): {missing_base_ids}")

    rows = compute_sensitivity_rows(
        df, plan, base_results, data_hash=data_hash, plan_hash=plan_hash,
    )
    out_df = pd.DataFrame(rows)
    Path(args.out_csv).parent.mkdir(parents=True, exist_ok=True)
    out_df.to_csv(args.out_csv, index=False)
    write_json({
        "skill_version": SKILL_VERSION,
        "analysis_id": plan.get("analysis_id"),
        "data_sha256": data_hash,
        "plan_sha256": plan_hash,
        "sensitivity_results": rows,
    }, args.out_json)
    print(f"Wrote {len(rows)} sensitivity results")


if __name__ == "__main__":
    main()
