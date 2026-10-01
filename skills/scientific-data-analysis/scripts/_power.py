from __future__ import annotations

import json
import math
from copy import deepcopy
from typing import Any

import numpy as np
from scipy import optimize, stats
from statsmodels.stats.proportion import proportion_effectsize, power_proportions_2indep

from _common import SKILL_VERSION, POWER_PLAN_SCHEMA_VERSION, jsonable_level, level_display_labels

MAX_N_PRIMARY = 1_000_000


def _alpha(item, plan):
    return float(item.get("alpha", plan.get("alpha", 0.05)))


def _target(item, plan):
    return float(item.get("target_power", plan.get("target_power", 0.8)))


def _alternative(item, plan):
    return item.get("alternative", plan.get("alternative", "two-sided"))


def _attrition(item):
    return float(item.get("attrition_rate", 0.0))


def _inflated(n: int, attrition: float) -> int:
    if attrition <= 0:
        return int(n)
    return int(math.ceil(n / (1.0 - attrition)))


def _nct_power(ncp: float, df: float, alpha: float, alternative: str) -> float:
    if alternative == "two-sided":
        crit = stats.t.ppf(1 - alpha / 2, df)
        return float(stats.nct.cdf(-crit, df, ncp) + stats.nct.sf(crit, df, ncp))
    if alternative == "larger":
        crit = stats.t.ppf(1 - alpha, df)
        return float(stats.nct.sf(crit, df, ncp))
    if alternative == "smaller":
        crit = stats.t.ppf(alpha, df)
        return float(stats.nct.cdf(crit, df, ncp))
    raise ValueError(f"Unsupported alternative: {alternative}")


def welch_power(mean_difference: float, sd_a: float, sd_b: float, n_a: int, n_b: int, alpha: float, alternative: str) -> tuple[float, float, float]:
    if n_a < 2 or n_b < 2:
        raise ValueError("Welch planning requires n_a,n_b >= 2")
    va = sd_a ** 2 / n_a
    vb = sd_b ** 2 / n_b
    se = math.sqrt(va + vb)
    df = (va + vb) ** 2 / ((va ** 2) / (n_a - 1) + (vb ** 2) / (n_b - 1))
    ncp = mean_difference / se
    return _nct_power(ncp, df, alpha, alternative), float(df), float(se)


def paired_power(mean_difference: float, sd_difference: float, n_pairs: int, alpha: float, alternative: str) -> tuple[float, float, float]:
    if n_pairs < 2:
        raise ValueError("Paired planning requires n_pairs >= 2")
    se = sd_difference / math.sqrt(n_pairs)
    df = n_pairs - 1
    ncp = mean_difference / se
    return _nct_power(ncp, df, alpha, alternative), float(df), float(se)


def welch_contrast_power(contrast_effect: float, terms: list[dict[str, Any]], alpha: float, alternative: str) -> tuple[float, float, float]:
    """Prospective power for a prespecified heteroscedastic linear contrast.

    Each term must contain ``weight``, ``sd`` and analyzable ``n``. The
    variance estimate is sum(c_i^2 * sigma_i^2 / n_i); Welch-Satterthwaite
    degrees of freedom use the corresponding per-group variance
    contributions.
    """
    if len(terms) < 2:
        raise ValueError("Welch contrast planning requires at least two groups")
    contributions = []
    for term in terms:
        n = int(term["n"])
        if n < 2:
            raise ValueError("Welch contrast planning requires n >= 2 in every group")
        weight = float(term["weight"])
        sd = float(term["sd"])
        contributions.append((weight ** 2) * (sd ** 2) / n)
    variance = float(sum(contributions))
    if not math.isfinite(variance) or variance <= 0:
        raise ValueError("Welch contrast planning produced non-positive sampling variance")
    se = math.sqrt(variance)
    denom = sum((v ** 2) / (int(term["n"]) - 1) for v, term in zip(contributions, terms))
    if not math.isfinite(denom) or denom <= 0:
        raise ValueError("Welch contrast planning produced invalid Satterthwaite denominator")
    df = (variance ** 2) / denom
    ncp = float(contrast_effect) / se
    return _nct_power(ncp, df, alpha, alternative), float(df), float(se)


def _contrast_terms_for_sample_size(item: dict[str, Any], n_reference: int) -> tuple[list[dict[str, Any]], list[float]]:
    raw = [float(t.get("allocation_ratio", 1.0)) for t in item["contrast_terms"]]
    min_ratio = min(raw)
    normalized = [r / min_ratio for r in raw]
    terms = []
    for term, ratio in zip(item["contrast_terms"], normalized):
        t = deepcopy(term)
        t["n"] = max(2, int(math.ceil(ratio * n_reference)))
        terms.append(t)
    return terms, normalized


def _contrast_terms_json(terms: list[dict[str, Any]]) -> str:
    payload = []
    for term in terms:
        x = {
            "level": jsonable_level(term.get("level")),
            "weight": float(term["weight"]),
            "sd": float(term["sd"]),
        }
        if "allocation_ratio" in term:
            x["allocation_ratio"] = float(term["allocation_ratio"])
        if "n" in term:
            x["n"] = int(term["n"])
        payload.append(x)
    return json.dumps(payload, ensure_ascii=False, separators=(",", ":"))


def _contrast_group_n_json(terms: list[dict[str, Any]], *, attrition: float | None = None) -> str:
    payload = []
    for term in terms:
        n = int(term["n"])
        if attrition is not None:
            n = _inflated(n, attrition)
        payload.append({"level": jsonable_level(term.get("level")), "n": n})
    return json.dumps(payload, ensure_ascii=False, separators=(",", ":"))


def _contrast_orientation(terms: list[dict[str, Any]]) -> str:
    labels = level_display_labels([t.get("level") for t in terms])
    return " + ".join(f"{float(t['weight']):g}*{lab}" for t, lab in zip(terms, labels))


def _solve_integer_power(power_fn, target: float, *, low: int = 2, high_cap: int = MAX_N_PRIMARY) -> int:
    low = max(2, int(low))
    if power_fn(low) >= target:
        return low
    hi = max(low + 1, 4)
    while hi <= high_cap and power_fn(hi) < target:
        hi *= 2
    if hi > high_cap:
        hi = high_cap
        if power_fn(hi) < target:
            raise ValueError(f"Target power not reached before planning cap n={high_cap}")
    lo = low
    while lo < hi:
        mid = (lo + hi) // 2
        if power_fn(mid) >= target:
            hi = mid
        else:
            lo = mid + 1
    return int(lo)


def _solve_mde(power_fn_from_signed_effect, target: float, alternative: str, scale: float) -> float:
    sign = -1.0 if alternative == "smaller" else 1.0
    def f(mag):
        effect = sign * mag
        return power_fn_from_signed_effect(effect) - target
    lo = 0.0
    hi = max(float(scale), 1e-12)
    while f(hi) < 0 and hi < max(1.0, scale) * 1e6:
        hi *= 2.0
    if f(hi) < 0:
        raise ValueError("Could not bracket a minimum detectable effect under the declared assumptions")
    root = optimize.brentq(f, lo, hi, xtol=1e-12, rtol=1e-10, maxiter=200)
    return float(sign * root if alternative != "two-sided" else root)




def proportion_normal_approximation_diagnostics(p_a: float, p_b: float, n_a: int, n_b: int) -> dict[str, float | str]:
    """Return transparent cell-count diagnostics for the two-proportion normal approximation.

    The core planner uses a normal approximation.  We therefore expose the
    smallest expected event/non-event count under the declared alternative
    rates instead of silently treating every finite solution as equally
    trustworthy.  The adequacy labels are conservative QA heuristics rather
    than mathematical guarantees.
    """
    counts = {
        "expected_events_a": float(n_a * p_a),
        "expected_nonevents_a": float(n_a * (1.0 - p_a)),
        "expected_events_b": float(n_b * p_b),
        "expected_nonevents_b": float(n_b * (1.0 - p_b)),
    }
    m = min(counts.values())
    if m < 1.0:
        adequacy = "poor_extreme_sparsity"
    elif m < 5.0:
        adequacy = "caution_sparse"
    else:
        adequacy = "adequate_by_conservative_count_rule"
    counts["min_expected_cell_count"] = float(m)
    counts["normal_approximation_adequacy"] = adequacy
    counts["normal_approximation_count_rule"] = "min_expected_event_or_nonevent_count_under_declared_rates"
    return counts

def _common_row(plan, item, scenario_id, scenario_overrides):
    return {
        "skill_version": SKILL_VERSION,
        "power_plan_schema_version": POWER_PLAN_SCHEMA_VERSION,
        "planning_id": plan.get("planning_id"),
        "unit_of_analysis": plan.get("unit_of_analysis"),
        "planning_item_id": item["planning_item_id"],
        "scenario_id": scenario_id,
        "type": item["type"],
        "solve_for": item["solve_for"],
        "alpha": _alpha(item, plan),
        "target_power": _target(item, plan),
        "alternative": _alternative(item, plan),
        "attrition_rate": _attrition(item),
        "assumption_source_json": json.dumps(item.get("assumption_source", {}), ensure_ascii=False, sort_keys=True, separators=(",", ":")),
        "scenario_overrides_json": json.dumps(scenario_overrides or {}, ensure_ascii=False, sort_keys=True, separators=(",", ":")),
    }


def calculate_item(plan: dict[str, Any], item: dict[str, Any], *, scenario_id="base", scenario_overrides=None) -> dict[str, Any]:
    typ = item["type"]
    solve_for = item["solve_for"]
    alpha = _alpha(item, plan)
    target = _target(item, plan)
    alternative = _alternative(item, plan)
    attrition = _attrition(item)
    row = _common_row(plan, item, scenario_id, scenario_overrides)

    if typ == "welch_two_group_mean":
        sd_a = float(item["sd_a"]); sd_b = float(item["sd_b"])
        ratio = float(item.get("allocation_ratio_b_to_a", 1.0))
        row.update({
            "effect_metric": "raw_mean_difference_b_minus_a",
            "sd_a": sd_a, "sd_b": sd_b, "allocation_ratio_b_to_a": ratio,
            "method": "noncentral_t_welch_satterthwaite_approximation",
        })
        if solve_for == "sample_size":
            delta = float(item["mean_difference"])
            def p_from_na(na):
                nb = max(2, int(math.ceil(ratio * na)))
                return welch_power(delta, sd_a, sd_b, na, nb, alpha, alternative)[0]
            n_a = _solve_integer_power(p_from_na, target)
            n_b = max(2, int(math.ceil(ratio * n_a)))
            power, df, se = welch_power(delta, sd_a, sd_b, n_a, n_b, alpha, alternative)
            row.update({"assumed_effect": delta, "n_a_analyzable": n_a, "n_b_analyzable": n_b, "actual_allocation_ratio_b_to_a": n_b/n_a, "n_total_analyzable": n_a+n_b,
                        "n_a_enroll": _inflated(n_a, attrition), "n_b_enroll": _inflated(n_b, attrition),
                        "n_total_enroll": _inflated(n_a, attrition)+_inflated(n_b, attrition), "achieved_power": power,
                        "welch_df_at_solution": df, "standard_error_at_solution": se, "minimum_detectable_effect": None})
        elif solve_for == "prospective_power":
            n_a = int(item["n_a"]); n_b = int(item["n_b"]); delta = float(item["mean_difference"])
            power, df, se = welch_power(delta, sd_a, sd_b, n_a, n_b, alpha, alternative)
            row.update({"assumed_effect": delta, "n_a_analyzable": n_a, "n_b_analyzable": n_b, "actual_allocation_ratio_b_to_a": n_b/n_a, "n_total_analyzable": n_a+n_b,
                        "n_a_enroll": _inflated(n_a, attrition), "n_b_enroll": _inflated(n_b, attrition),
                        "n_total_enroll": _inflated(n_a, attrition)+_inflated(n_b, attrition), "achieved_power": power,
                        "welch_df_at_solution": df, "standard_error_at_solution": se, "minimum_detectable_effect": None})
        elif solve_for == "minimum_detectable_effect":
            n_a = int(item["n_a"]); n_b = int(item["n_b"])
            mde = _solve_mde(lambda d: welch_power(d, sd_a, sd_b, n_a, n_b, alpha, alternative)[0], target, alternative, math.sqrt(sd_a*sd_b))
            power, df, se = welch_power(mde, sd_a, sd_b, n_a, n_b, alpha, alternative)
            row.update({"assumed_effect": None, "n_a_analyzable": n_a, "n_b_analyzable": n_b, "actual_allocation_ratio_b_to_a": n_b/n_a, "n_total_analyzable": n_a+n_b,
                        "n_a_enroll": _inflated(n_a, attrition), "n_b_enroll": _inflated(n_b, attrition),
                        "n_total_enroll": _inflated(n_a, attrition)+_inflated(n_b, attrition), "achieved_power": power,
                        "welch_df_at_solution": df, "standard_error_at_solution": se, "minimum_detectable_effect": mde})
        else:
            raise ValueError(solve_for)


    elif typ == "welch_contrast":
        base_terms = deepcopy(item["contrast_terms"])
        row.update({
            "effect_metric": "planned_linear_contrast_raw_scale",
            "method": "noncentral_t_generalized_welch_satterthwaite_contrast",
            "contrast_terms_json": _contrast_terms_json(base_terms),
            "contrast_orientation": _contrast_orientation(base_terms),
            "contrast_weight_sum": float(sum(float(t["weight"]) for t in base_terms)),
            "n_groups": int(len(base_terms)),
        })
        if solve_for == "sample_size":
            effect = float(item["contrast_effect"])
            def p_from_reference(nref):
                terms, _ = _contrast_terms_for_sample_size(item, nref)
                return welch_contrast_power(effect, terms, alpha, alternative)[0]
            nref = _solve_integer_power(p_from_reference, target)
            terms, normalized = _contrast_terms_for_sample_size(item, nref)
            power, df, se = welch_contrast_power(effect, terms, alpha, alternative)
            n_total = sum(int(t["n"]) for t in terms)
            enroll_total = sum(_inflated(int(t["n"]), attrition) for t in terms)
            row.update({
                "assumed_effect": effect,
                "minimum_detectable_effect": None,
                "n_reference_analyzable": int(nref),
                "n_total_analyzable": int(n_total),
                "n_total_enroll": int(enroll_total),
                "group_n_analyzable_json": _contrast_group_n_json(terms),
                "group_n_enroll_json": _contrast_group_n_json(terms, attrition=attrition),
                "normalized_allocation_ratios_json": json.dumps([
                    {"level": jsonable_level(t.get("level")), "ratio": float(r)}
                    for t, r in zip(terms, normalized)
                ], ensure_ascii=False, separators=(",", ":")),
                "achieved_power": power,
                "welch_df_at_solution": df,
                "standard_error_at_solution": se,
            })
        elif solve_for == "prospective_power":
            effect = float(item["contrast_effect"])
            terms = deepcopy(item["contrast_terms"])
            power, df, se = welch_contrast_power(effect, terms, alpha, alternative)
            n_total = sum(int(t["n"]) for t in terms)
            enroll_total = sum(_inflated(int(t["n"]), attrition) for t in terms)
            row.update({
                "assumed_effect": effect,
                "minimum_detectable_effect": None,
                "n_total_analyzable": int(n_total),
                "n_total_enroll": int(enroll_total),
                "group_n_analyzable_json": _contrast_group_n_json(terms),
                "group_n_enroll_json": _contrast_group_n_json(terms, attrition=attrition),
                "achieved_power": power,
                "welch_df_at_solution": df,
                "standard_error_at_solution": se,
            })
        elif solve_for == "minimum_detectable_effect":
            terms = deepcopy(item["contrast_terms"])
            scale = math.sqrt(sum((float(t["weight"]) * float(t["sd"])) ** 2 for t in terms))
            mde = _solve_mde(lambda d: welch_contrast_power(d, terms, alpha, alternative)[0], target, alternative, scale)
            power, df, se = welch_contrast_power(mde, terms, alpha, alternative)
            n_total = sum(int(t["n"]) for t in terms)
            enroll_total = sum(_inflated(int(t["n"]), attrition) for t in terms)
            row.update({
                "assumed_effect": None,
                "minimum_detectable_effect": mde,
                "n_total_analyzable": int(n_total),
                "n_total_enroll": int(enroll_total),
                "group_n_analyzable_json": _contrast_group_n_json(terms),
                "group_n_enroll_json": _contrast_group_n_json(terms, attrition=attrition),
                "achieved_power": power,
                "welch_df_at_solution": df,
                "standard_error_at_solution": se,
            })
        else:
            raise ValueError(solve_for)

    elif typ == "paired_mean":
        sd = float(item["sd_difference"])
        row.update({"effect_metric": "paired_mean_difference", "sd_difference": sd, "method": "noncentral_t_paired"})
        if solve_for == "sample_size":
            delta = float(item["mean_difference"])
            n = _solve_integer_power(lambda nn: paired_power(delta, sd, nn, alpha, alternative)[0], target)
            power, df, se = paired_power(delta, sd, n, alpha, alternative)
            row.update({"assumed_effect": delta, "n_pairs_analyzable": n, "n_total_analyzable": n,
                        "n_pairs_enroll": _inflated(n, attrition), "n_total_enroll": _inflated(n, attrition),
                        "achieved_power": power, "df_at_solution": df, "standard_error_at_solution": se, "minimum_detectable_effect": None})
        elif solve_for == "prospective_power":
            n = int(item["n_pairs"]); delta = float(item["mean_difference"])
            power, df, se = paired_power(delta, sd, n, alpha, alternative)
            row.update({"assumed_effect": delta, "n_pairs_analyzable": n, "n_total_analyzable": n,
                        "n_pairs_enroll": _inflated(n, attrition), "n_total_enroll": _inflated(n, attrition),
                        "achieved_power": power, "df_at_solution": df, "standard_error_at_solution": se, "minimum_detectable_effect": None})
        elif solve_for == "minimum_detectable_effect":
            n = int(item["n_pairs"])
            mde = _solve_mde(lambda d: paired_power(d, sd, n, alpha, alternative)[0], target, alternative, sd)
            power, df, se = paired_power(mde, sd, n, alpha, alternative)
            row.update({"assumed_effect": None, "n_pairs_analyzable": n, "n_total_analyzable": n,
                        "n_pairs_enroll": _inflated(n, attrition), "n_total_enroll": _inflated(n, attrition),
                        "achieved_power": power, "df_at_solution": df, "standard_error_at_solution": se, "minimum_detectable_effect": mde})
        else:
            raise ValueError(solve_for)

    elif typ == "independent_proportions":
        p_a = float(item["p_a"]); p_b = float(item["p_b"])
        ratio = float(item.get("allocation_ratio_b_to_a", 1.0))
        h = float(proportion_effectsize(p_b, p_a))
        diff = p_b - p_a
        def prop_power(n_a, n_b):
            # statsmodels defines group 1 as p_b and group 2 as p_a here so
            # the signed alternative remains oriented B minus A.
            return float(power_proportions_2indep(
                diff=diff, prop2=p_a, nobs1=n_b, ratio=n_a / n_b,
                alpha=alpha, alternative=alternative, return_results=False,
            ))
        row.update({"effect_metric": "risk_difference_b_minus_a", "p_a": p_a, "p_b": p_b,
                    "assumed_effect": diff, "cohen_h": h, "allocation_ratio_b_to_a": ratio,
                    "method": "two_proportion_z_pooled_null_nonpooled_alternative"})
        if solve_for == "sample_size":
            def p_from_na(na):
                nb = max(2, int(math.ceil(ratio * na)))
                return prop_power(na, nb)
            n_a = _solve_integer_power(p_from_na, target)
            n_b = max(2, int(math.ceil(ratio*n_a)))
            power = prop_power(n_a, n_b)
            row.update({"n_a_analyzable": n_a, "n_b_analyzable": n_b, "actual_allocation_ratio_b_to_a": n_b/n_a, "n_total_analyzable": n_a+n_b,
                        "n_a_enroll": _inflated(n_a, attrition), "n_b_enroll": _inflated(n_b, attrition),
                        "n_total_enroll": _inflated(n_a, attrition)+_inflated(n_b, attrition), "achieved_power": power,
                        "minimum_detectable_effect": None})
            row.update(proportion_normal_approximation_diagnostics(p_a, p_b, n_a, n_b))
        elif solve_for == "prospective_power":
            n_a = int(item["n_a"]); n_b = int(item["n_b"])
            power = prop_power(n_a, n_b)
            row.update({"n_a_analyzable": n_a, "n_b_analyzable": n_b, "actual_allocation_ratio_b_to_a": n_b/n_a, "n_total_analyzable": n_a+n_b,
                        "n_a_enroll": _inflated(n_a, attrition), "n_b_enroll": _inflated(n_b, attrition),
                        "n_total_enroll": _inflated(n_a, attrition)+_inflated(n_b, attrition), "achieved_power": power,
                        "minimum_detectable_effect": None})
            row.update(proportion_normal_approximation_diagnostics(p_a, p_b, n_a, n_b))
        else:
            raise ValueError("minimum_detectable_effect is not supported for independent_proportions in the v1.6 core")
    else:
        raise ValueError(f"Unsupported planning type: {typ}")

    # target_power always has an effective value (item override -> plan -> default 0.8),
    # so the target-status field should be deterministic for every solve mode.
    row["meets_target_power"] = bool(float(row["achieved_power"]) >= target - 1e-9)
    return row


def expand_and_calculate(plan: dict[str, Any]) -> list[dict[str, Any]]:
    rows = []
    for item in plan.get("planning_items", []):
        rows.append(calculate_item(plan, item, scenario_id="base", scenario_overrides={}))
        for scenario in item.get("scenarios", []) or []:
            overrides = scenario.get("overrides", {})
            merged = deepcopy(item)
            merged.pop("scenarios", None)
            merged.update(overrides)
            rows.append(calculate_item(plan, merged, scenario_id=scenario["scenario_id"], scenario_overrides=overrides))
    return rows
