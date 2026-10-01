#!/usr/bin/env python3
from __future__ import annotations

import argparse
import math
import sys
from copy import deepcopy

from _common import POWER_PLAN_SCHEMA_VERSION, read_json, categorical_level_key

ALLOWED_TYPES = {"welch_two_group_mean", "paired_mean", "independent_proportions", "welch_contrast"}
ALLOWED_SOLVE_FOR = {"sample_size", "prospective_power", "minimum_detectable_effect"}
ALLOWED_ALTERNATIVES = {"two-sided", "larger", "smaller"}
ALLOWED_SOURCE_KINDS = {"scientific_threshold", "external_evidence", "pilot", "scenario"}

SCENARIO_OVERRIDE_KEYS = {
    ("welch_two_group_mean", "sample_size"): {
        "mean_difference", "sd_a", "sd_b", "allocation_ratio_b_to_a",
        "attrition_rate", "alpha", "target_power", "alternative",
    },
    ("welch_two_group_mean", "prospective_power"): {
        "mean_difference", "sd_a", "sd_b", "n_a", "n_b",
        "attrition_rate", "alpha", "target_power", "alternative",
    },
    ("welch_two_group_mean", "minimum_detectable_effect"): {
        "sd_a", "sd_b", "n_a", "n_b",
        "attrition_rate", "alpha", "target_power", "alternative",
    },
    ("paired_mean", "sample_size"): {
        "mean_difference", "sd_difference", "attrition_rate", "alpha", "target_power", "alternative",
    },
    ("paired_mean", "prospective_power"): {
        "mean_difference", "sd_difference", "n_pairs", "attrition_rate", "alpha", "target_power", "alternative",
    },
    ("paired_mean", "minimum_detectable_effect"): {
        "sd_difference", "n_pairs", "attrition_rate", "alpha", "target_power", "alternative",
    },
    ("independent_proportions", "sample_size"): {
        "p_a", "p_b", "allocation_ratio_b_to_a",
        "attrition_rate", "alpha", "target_power", "alternative",
    },
    ("independent_proportions", "prospective_power"): {
        "p_a", "p_b", "n_a", "n_b",
        "attrition_rate", "alpha", "target_power", "alternative",
    },
    ("welch_contrast", "sample_size"): {
        "contrast_effect", "contrast_terms", "attrition_rate", "alpha", "target_power", "alternative",
    },
    ("welch_contrast", "prospective_power"): {
        "contrast_effect", "contrast_terms", "attrition_rate", "alpha", "target_power", "alternative",
    },
    ("welch_contrast", "minimum_detectable_effect"): {
        "contrast_terms", "attrition_rate", "alpha", "target_power", "alternative",
    },
}


def _is_finite_number(x, *, positive=False, nonnegative=False):
    if isinstance(x, bool) or not isinstance(x, (int, float)):
        return False
    v = float(x)
    if not math.isfinite(v):
        return False
    if positive and not (v > 0):
        return False
    if nonnegative and not (v >= 0):
        return False
    return True


def _is_int_at_least(x, minimum=2):
    return isinstance(x, int) and not isinstance(x, bool) and x >= minimum


def _is_level_scalar(x):
    if isinstance(x, bool):
        return True
    if isinstance(x, str):
        return bool(x.strip())
    if isinstance(x, (int, float)) and not isinstance(x, bool):
        return math.isfinite(float(x))
    return False


def _effective(item, plan, key, default=None):
    return item.get(key, plan.get(key, default))


def _validate_source(source, prefix, errors):
    if not isinstance(source, dict):
        errors.append(f"{prefix}.assumption_source must be an object")
        return
    kind = source.get("kind")
    ref = source.get("reference")
    if kind not in ALLOWED_SOURCE_KINDS:
        errors.append(f"{prefix}.assumption_source.kind must be one of {sorted(ALLOWED_SOURCE_KINDS)}")
    if not isinstance(ref, str) or not ref.strip():
        errors.append(f"{prefix}.assumption_source.reference must be a non-empty provenance note/reference")
    forbidden = {"observed_power", "posthoc_power", "current_study_observed_effect"}
    if isinstance(kind, str) and kind in forbidden:
        errors.append(f"{prefix}.assumption_source.kind must describe a prospective assumption, not post-hoc observed power")


def _contrast_signature(terms):
    sig = []
    for t in terms or []:
        if not isinstance(t, dict):
            return None
        try:
            sig.append((categorical_level_key(t.get("level")), float(t.get("weight"))))
        except Exception:
            return None
    return sig


def _validate_contrast_terms(item, label, solve_for, errors, warnings):
    terms = item.get("contrast_terms")
    if not isinstance(terms, list) or len(terms) < 2:
        errors.append(f"{label}.contrast_terms must contain at least two group terms")
        return
    level_keys = []
    weights = []
    for j, term in enumerate(terms):
        tlabel = f"{label}.contrast_terms[{j}]"
        if not isinstance(term, dict):
            errors.append(f"{tlabel} must be an object")
            continue
        level = term.get("level")
        if not _is_level_scalar(level):
            errors.append(f"{tlabel}.level must be a boolean, finite numeric, or non-empty string scalar")
        else:
            level_keys.append(categorical_level_key(level))
        weight = term.get("weight")
        if not _is_finite_number(weight) or float(weight) == 0:
            errors.append(f"{tlabel}.weight must be a finite non-zero number")
        else:
            weights.append(float(weight))
        if not _is_finite_number(term.get("sd"), positive=True):
            errors.append(f"{tlabel}.sd must be > 0")
        if solve_for == "sample_size":
            if "n" in term:
                errors.append(f"{tlabel}.n is not allowed for solve_for='sample_size'; the planner solves group n from allocation_ratio")
            if not _is_finite_number(term.get("allocation_ratio", 1.0), positive=True):
                errors.append(f"{tlabel}.allocation_ratio must be > 0")
        else:
            if "allocation_ratio" in term:
                errors.append(f"{tlabel}.allocation_ratio is not allowed for fixed-n solve_for='{solve_for}'; declare n directly")
            if not _is_int_at_least(term.get("n")):
                errors.append(f"{tlabel}.n must be an integer >= 2 for solve_for='{solve_for}'")
    if len(level_keys) != len(set(level_keys)):
        errors.append(f"{label}.contrast_terms levels must be unique under typed categorical identity")
    if weights:
        if not any(w > 0 for w in weights) or not any(w < 0 for w in weights):
            errors.append(f"{label}.contrast_terms weights must contain at least one positive and one negative value")
        if not math.isclose(sum(weights), 0.0, rel_tol=1e-10, abs_tol=1e-10):
            errors.append(f"{label}.contrast_terms weights must sum to zero")
    if solve_for == "minimum_detectable_effect" and "contrast_effect" in item:
        warnings.append(f"{label}.contrast_effect is ignored for solve_for='minimum_detectable_effect'; the planner solves the contrast effect")


def validate_planning_item(item, plan, index=0, *, prefix="planning_items", validate_scenarios=True):
    errors, warnings = [], []
    label = f"{prefix}[{index}]"
    if not isinstance(item, dict):
        return [f"{label} must be an object"], []
    for key in ["planning_item_id", "type", "solve_for", "assumption_source"]:
        if key not in item:
            errors.append(f"{label} missing required field '{key}'")
    typ = item.get("type")
    solve_for = item.get("solve_for")
    if typ not in ALLOWED_TYPES:
        errors.append(f"{label}.type must be one of {sorted(ALLOWED_TYPES)}")
        return errors, warnings
    if solve_for not in ALLOWED_SOLVE_FOR:
        errors.append(f"{label}.solve_for must be one of {sorted(ALLOWED_SOLVE_FOR)}")
    if typ == "independent_proportions" and solve_for == "minimum_detectable_effect":
        errors.append(f"{label}: minimum_detectable_effect is not supported for independent_proportions in the v1.6 core")

    _validate_source(item.get("assumption_source"), label, errors)

    alpha = _effective(item, plan, "alpha")
    power = _effective(item, plan, "target_power")
    alternative = _effective(item, plan, "alternative", "two-sided")
    if not _is_finite_number(alpha) or not (0 < float(alpha) < 0.5):
        errors.append(f"{label}: alpha must be a finite number in (0, 0.5)")
    if solve_for in {"sample_size", "minimum_detectable_effect"}:
        if not _is_finite_number(power) or not (float(alpha or 0) < float(power) < 1):
            errors.append(f"{label}: target_power must be finite, greater than alpha, and < 1")
    elif power is not None and (not _is_finite_number(power) or not (0 < float(power) < 1)):
        errors.append(f"{label}: target_power, when supplied, must be in (0,1)")
    if alternative not in ALLOWED_ALTERNATIVES:
        errors.append(f"{label}: alternative must be one of {sorted(ALLOWED_ALTERNATIVES)}")

    attrition = item.get("attrition_rate", 0.0)
    if not _is_finite_number(attrition, nonnegative=True) or not (0 <= float(attrition) < 1):
        errors.append(f"{label}.attrition_rate must be in [0,1)")

    if typ in {"welch_two_group_mean", "independent_proportions"}:
        ratio = item.get("allocation_ratio_b_to_a", 1.0)
        if not _is_finite_number(ratio, positive=True):
            errors.append(f"{label}.allocation_ratio_b_to_a must be > 0")
        if solve_for in {"prospective_power", "minimum_detectable_effect"} and "allocation_ratio_b_to_a" in item:
            warnings.append(
                f"{label}.allocation_ratio_b_to_a does not determine fixed-n calculations; "
                "actual allocation is determined by n_a and n_b. Scenario overrides of this field are rejected."
            )

    if typ == "welch_two_group_mean":
        if not _is_finite_number(item.get("sd_a"), positive=True):
            errors.append(f"{label}.sd_a must be > 0")
        if not _is_finite_number(item.get("sd_b"), positive=True):
            errors.append(f"{label}.sd_b must be > 0")
        if solve_for in {"sample_size", "prospective_power"}:
            d = item.get("mean_difference")
            if not _is_finite_number(d) or float(d) == 0:
                errors.append(f"{label}.mean_difference must be a finite non-zero raw difference (group B minus group A)")
            elif alternative == "larger" and float(d) <= 0:
                errors.append(f"{label}.mean_difference must be > 0 for alternative='larger'")
            elif alternative == "smaller" and float(d) >= 0:
                errors.append(f"{label}.mean_difference must be < 0 for alternative='smaller'")
        if solve_for in {"prospective_power", "minimum_detectable_effect"}:
            if not _is_int_at_least(item.get("n_a")) or not _is_int_at_least(item.get("n_b")):
                errors.append(f"{label}: n_a and n_b must be integers >= 2 for solve_for='{solve_for}'")

    elif typ == "welch_contrast":
        _validate_contrast_terms(item, label, solve_for, errors, warnings)
        if solve_for in {"sample_size", "prospective_power"}:
            d = item.get("contrast_effect")
            if not _is_finite_number(d) or float(d) == 0:
                errors.append(f"{label}.contrast_effect must be a finite non-zero raw planned-contrast value")
            elif alternative == "larger" and float(d) <= 0:
                errors.append(f"{label}.contrast_effect must be > 0 for alternative='larger'")
            elif alternative == "smaller" and float(d) >= 0:
                errors.append(f"{label}.contrast_effect must be < 0 for alternative='smaller'")

    elif typ == "paired_mean":
        if not _is_finite_number(item.get("sd_difference"), positive=True):
            errors.append(f"{label}.sd_difference must be > 0")
        if solve_for in {"sample_size", "prospective_power"}:
            d = item.get("mean_difference")
            if not _is_finite_number(d) or float(d) == 0:
                errors.append(f"{label}.mean_difference must be a finite non-zero paired mean difference")
            elif alternative == "larger" and float(d) <= 0:
                errors.append(f"{label}.mean_difference must be > 0 for alternative='larger'")
            elif alternative == "smaller" and float(d) >= 0:
                errors.append(f"{label}.mean_difference must be < 0 for alternative='smaller'")
        if solve_for in {"prospective_power", "minimum_detectable_effect"} and not _is_int_at_least(item.get("n_pairs")):
            errors.append(f"{label}.n_pairs must be an integer >= 2 for solve_for='{solve_for}'")

    elif typ == "independent_proportions":
        for key in ["p_a", "p_b"]:
            v = item.get(key)
            if not _is_finite_number(v) or not (0 < float(v) < 1):
                errors.append(f"{label}.{key} must be in (0,1)")
        if _is_finite_number(item.get("p_a")) and _is_finite_number(item.get("p_b")):
            diff = float(item["p_b"]) - float(item["p_a"])
            if diff == 0:
                errors.append(f"{label}: p_a and p_b must differ")
            elif alternative == "larger" and diff <= 0:
                errors.append(f"{label}: p_b - p_a must be > 0 for alternative='larger'")
            elif alternative == "smaller" and diff >= 0:
                errors.append(f"{label}: p_b - p_a must be < 0 for alternative='smaller'")
        if solve_for == "prospective_power":
            if not _is_int_at_least(item.get("n_a")) or not _is_int_at_least(item.get("n_b")):
                errors.append(f"{label}: n_a and n_b must be integers >= 2 for prospective_power")

    # Warn about explicit fields that are accepted for compatibility but do not enter the selected solve mode.
    if typ == "welch_two_group_mean":
        if solve_for == "sample_size" and any(k in item for k in ("n_a", "n_b")):
            warnings.append(f"{label}: n_a/n_b are ignored for solve_for='sample_size'; the planner solves them.")
        if solve_for == "minimum_detectable_effect" and "mean_difference" in item:
            warnings.append(f"{label}.mean_difference is ignored for solve_for='minimum_detectable_effect'; the planner solves the effect.")
    elif typ == "paired_mean":
        if solve_for == "sample_size" and "n_pairs" in item:
            warnings.append(f"{label}.n_pairs is ignored for solve_for='sample_size'; the planner solves it.")
        if solve_for == "minimum_detectable_effect" and "mean_difference" in item:
            warnings.append(f"{label}.mean_difference is ignored for solve_for='minimum_detectable_effect'; the planner solves the effect.")
    elif typ == "independent_proportions":
        if solve_for == "sample_size" and any(k in item for k in ("n_a", "n_b")):
            warnings.append(f"{label}: n_a/n_b are ignored for solve_for='sample_size'; the planner solves them.")

    if validate_scenarios:
        scenarios = item.get("scenarios", [])
        if scenarios is not None and not isinstance(scenarios, list):
            errors.append(f"{label}.scenarios must be a list")
            scenarios = []
        seen = set()
        for j, scenario in enumerate(scenarios or []):
            slabel = f"{label}.scenarios[{j}]"
            if not isinstance(scenario, dict):
                errors.append(f"{slabel} must be an object")
                continue
            sid = scenario.get("scenario_id")
            overrides = scenario.get("overrides")
            if not isinstance(sid, str) or not sid.strip():
                errors.append(f"{slabel}.scenario_id must be a non-empty string")
            elif sid in seen or sid == "base":
                errors.append(f"{slabel}.scenario_id must be unique and cannot be 'base'")
            else:
                seen.add(sid)
            if not isinstance(overrides, dict) or not overrides:
                errors.append(f"{slabel}.overrides must be a non-empty object")
                continue
            allowed_overrides = SCENARIO_OVERRIDE_KEYS.get((typ, solve_for), set())
            unknown = set(overrides) - allowed_overrides
            if unknown:
                errors.append(
                    f"{slabel}.overrides contains keys that are unsupported or have no effect for "
                    f"{typ} with solve_for={solve_for!r}: {sorted(unknown)}"
                )
                continue
            if typ == "welch_contrast" and "contrast_terms" in overrides:
                base_sig = _contrast_signature(item.get("contrast_terms"))
                new_sig = _contrast_signature(overrides.get("contrast_terms"))
                if base_sig is None or new_sig is None or len(base_sig) != len(new_sig):
                    errors.append(f"{slabel}.contrast_terms must preserve the base contrast levels and weights; only SD/allocation/n assumptions may change")
                    continue
                same = all(a[0] == b[0] and math.isclose(a[1], b[1], rel_tol=1e-12, abs_tol=1e-12) for a, b in zip(base_sig, new_sig))
                if not same:
                    errors.append(f"{slabel}.contrast_terms must preserve the exact typed levels, order, and contrast weights; changing the estimand is not a planning scenario")
                    continue
            merged = deepcopy(item)
            merged.pop("scenarios", None)
            merged.update(overrides)
            e, w = validate_planning_item(merged, plan, j, prefix=f"{label}.scenario_expansions", validate_scenarios=False)
            errors.extend(e); warnings.extend(w)

    return errors, warnings


def validate(plan):
    errors, warnings = [], []
    if not isinstance(plan, dict):
        return ["Power plan must be a JSON object"], []
    if plan.get("power_plan_schema_version") != POWER_PLAN_SCHEMA_VERSION:
        errors.append(f"power_plan_schema_version must be '{POWER_PLAN_SCHEMA_VERSION}'")
    for key in ["planning_id", "plan_version", "research_question", "unit_of_analysis", "planning_items"]:
        if key not in plan:
            errors.append(f"Missing required top-level field '{key}'")
    for key in ["planning_id", "plan_version", "research_question", "unit_of_analysis"]:
        if key in plan and (not isinstance(plan[key], str) or not plan[key].strip()):
            errors.append(f"{key} must be a non-empty string")
    forbidden_top = [k for k in ["input", "analyses", "results"] if k in plan]
    if forbidden_top:
        errors.append(f"Power planning is a separate prospective workflow; remove current-study data/inference fields: {forbidden_top}")

    alpha = plan.get("alpha", 0.05)
    target = plan.get("target_power", 0.8)
    alternative = plan.get("alternative", "two-sided")
    if not _is_finite_number(alpha) or not (0 < float(alpha) < 0.5):
        errors.append("alpha must be a finite number in (0,0.5)")
    if not _is_finite_number(target) or not (float(alpha or 0) < float(target) < 1):
        errors.append("target_power must be finite, greater than alpha, and < 1")
    if alternative not in ALLOWED_ALTERNATIVES:
        errors.append(f"alternative must be one of {sorted(ALLOWED_ALTERNATIVES)}")

    items = plan.get("planning_items")
    if not isinstance(items, list) or not items:
        errors.append("planning_items must contain at least one item")
        items = []
    ids = []
    for i, item in enumerate(items):
        e, w = validate_planning_item(item, plan, i)
        errors.extend(e); warnings.extend(w)
        if isinstance(item, dict) and item.get("planning_item_id"):
            ids.append(item["planning_item_id"])
    if len(ids) != len(set(ids)):
        errors.append("planning_item_id values must be unique")
    return errors, warnings


def main():
    ap = argparse.ArgumentParser(description="Validate a prospective power/sample-size planning contract")
    ap.add_argument("plan")
    args = ap.parse_args()
    plan = read_json(args.plan)
    errors, warnings = validate(plan)
    for w in warnings:
        print(f"WARNING: {w}")
    for e in errors:
        print(f"ERROR: {e}")
    if errors:
        sys.exit(1)
    print("Power plan validation: PASS")


if __name__ == "__main__":
    main()
