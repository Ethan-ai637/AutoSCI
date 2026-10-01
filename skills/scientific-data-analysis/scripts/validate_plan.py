#!/usr/bin/env python3
from __future__ import annotations

import argparse
import math
import re
import sys
from copy import deepcopy

from _common import ANALYSIS_PLAN_SCHEMA_VERSION, read_json, categorical_level_key

ALLOWED_PROFILES = {"exploratory", "standard", "confirmatory"}
ALLOWED_TYPES = {
    "independent_t", "paired_t", "mann_whitney", "wilcoxon",
    "pearson", "spearman", "linear_regression", "ancova_two_group",
    "logistic_regression", "poisson_regression", "welch_anova", "welch_contrast", "chi_square", "fisher_exact",
    "equivalence_tost_independent", "equivalence_tost_paired",
}
ALLOWED_MULT = {"none", "holm", "bonferroni", "fdr_bh"}
ALLOWED_ID_POLICIES = {"audit", "error", "allow"}
ALLOWED_LINEAR_ROBUST_SE = {"HC3", "nonrobust"}
ALLOWED_GLM_ROBUST_SE = {"HC0", "nonrobust"}
ALLOWED_ANALYSIS_ROLES = {"primary", "secondary", "exploratory"}
ALLOWED_FILTER_OPERATORS = {"eq", "ne", "in", "not_in", "isna", "notna", "lt", "le", "gt", "ge"}
ALLOWED_SENSITIVITY_OVERRIDES = {
    "type", "robust_se", "report_predictor", "covariates", "predictors",
    "equivalence_margin_lower", "equivalence_margin_upper", "equivalence_alpha", "contrast_terms",
}
ALLOWED_MISSING = {"complete_case"}
ALLOWED_ESTIMAND_RELATIONS = {"same", "different", "uncertain"}
HEX64 = re.compile(r"^[0-9a-fA-F]{64}$")




def _valid_level_scalar(value):
    if isinstance(value, bool):
        return True
    if isinstance(value, str):
        return value != ""
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return math.isfinite(float(value))
    return False


def _valid_filter_scalar(value):
    """JSON scalar allowed for typed categorical sensitivity filters.

    Boolean is intentionally allowed here because sensitivity/QC flags are
    commonly boolean. Missingness must use isna/notna rather than eq null.
    """
    if isinstance(value, bool):
        return True
    if isinstance(value, str):
        return value != ""
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return math.isfinite(float(value))
    return False


def _level_key(value):
    return categorical_level_key(value)


_ESTIMAND_FAMILY = {
    "independent_t": "independent_mean_difference",
    "equivalence_tost_independent": "independent_mean_difference",
    "paired_t": "paired_mean_difference",
    "equivalence_tost_paired": "paired_mean_difference",
    "mann_whitney": "mann_whitney_rank_separation",
    "wilcoxon": "wilcoxon_signed_rank",
    "pearson": "pearson_linear_correlation",
    "spearman": "spearman_rank_correlation",
    "linear_regression": "linear_regression_coefficient",
    "ancova_two_group": "ancova_adjusted_group_difference",
    "logistic_regression": "logistic_odds_ratio",
    "poisson_regression": "poisson_incidence_rate_ratio",
    "welch_anova": "welch_omnibus",
    "welch_contrast": "welch_planned_contrast",
    "chi_square": "cramers_v_association",
    "fisher_exact": "two_by_two_odds_ratio",
}


def _effective_report_predictor(a):
    preds = a.get("predictors") or []
    return a.get("report_predictor") or (preds[0] if preds else None)


def _contrast_map(a):
    out = {}
    for term in a.get("contrast_terms") or []:
        if not isinstance(term, dict) or "level" not in term or "weight" not in term:
            continue
        try:
            out[_level_key(term["level"])] = float(term["weight"])
        except Exception:
            continue
    return out


def same_estimand_structural_conflicts(base, candidate):
    """Return mechanically provable conflicts with an estimand_relation='same' claim.

    This deliberately does not judge whether a data subset changes the scientific
    target population. It only rejects plan changes that alter the statistical
    quantity being estimated in ways the plan itself makes explicit.
    """
    conflicts = []
    base_type = base.get("type")
    cand_type = candidate.get("type")
    base_family = _ESTIMAND_FAMILY.get(base_type, base_type)
    cand_family = _ESTIMAND_FAMILY.get(cand_type, cand_type)
    if base_family != cand_family:
        conflicts.append(f"estimand family changes from {base_family} to {cand_family}")
        return conflicts

    if base_family in {"linear_regression_coefficient", "logistic_odds_ratio", "poisson_incidence_rate_ratio"}:
        bp = _effective_report_predictor(base)
        cp = _effective_report_predictor(candidate)
        if bp != cp:
            conflicts.append(f"reported predictor changes from {bp!r} to {cp!r}")
        if set(base.get("predictors") or []) != set(candidate.get("predictors") or []):
            conflicts.append("predictor/adjustment set changes")

    if base_family == "ancova_adjusted_group_difference":
        if set(base.get("covariates") or []) != set(candidate.get("covariates") or []):
            conflicts.append("ANCOVA covariate adjustment set changes")

    if base_family == "welch_planned_contrast":
        bm = _contrast_map(base)
        cm = _contrast_map(candidate)
        if set(bm) != set(cm) or any(not math.isclose(bm[k], cm[k], rel_tol=0.0, abs_tol=1e-12) for k in set(bm) & set(cm)):
            conflicts.append("planned contrast levels or weight scale changes")

    return conflicts


def _need(errors, obj, keys, prefix):
    for k in keys:
        if obj.get(k) in (None, "", []):
            errors.append(f"{prefix} missing {k}")


def _validate_predictors(errors, a, i, prefix, key="predictors"):
    preds = a.get(key)
    if preds is not None and (not isinstance(preds, list) or not preds or not all(isinstance(x, str) and x for x in preds)):
        errors.append(f"{prefix}[{i}] {key} must be a non-empty list of column names")
    elif isinstance(preds, list) and len(preds) != len(set(preds)):
        errors.append(f"{prefix}[{i}] {key} must be unique")
    return preds


def _validate_equivalence(errors, warnings, a, i, prefix):
    lo = a.get("equivalence_margin_lower")
    hi = a.get("equivalence_margin_upper")
    if not isinstance(lo, (int, float)) or not isinstance(hi, (int, float)):
        errors.append(f"{prefix}[{i}] equivalence analyses require numeric equivalence_margin_lower/upper")
    elif not lo < hi:
        errors.append(f"{prefix}[{i}] equivalence_margin_lower must be < equivalence_margin_upper")
    elif not (lo < 0 < hi):
        warnings.append(f"{prefix}[{i}] equivalence interval does not contain 0; verify that this is the intended raw-scale equivalence region")
    alpha = a.get("equivalence_alpha", 0.05)
    if not isinstance(alpha, (int, float)) or not (0 < alpha < 0.5):
        errors.append(f"{prefix}[{i}] equivalence_alpha must be in (0, 0.5)")


def validate_analysis_item(a, i="?", *, prefix="analyses"):
    errors, warnings = [], []
    aid = a.get("analysis_item_id")
    typ = a.get("type")
    if not aid:
        errors.append(f"{prefix}[{i}] missing analysis_item_id")
    if typ not in ALLOWED_TYPES:
        errors.append(f"{prefix}[{i}] unsupported type: {typ}")
        return errors, warnings
    role = a.get("analysis_role")
    if role is not None and role not in ALLOWED_ANALYSIS_ROLES:
        errors.append(f"{prefix}[{i}] analysis_role must be one of {sorted(ALLOWED_ANALYSIS_ROLES)}")
    if a.get("alternative") not in (None, "two-sided"):
        errors.append(f"{prefix}[{i}] core inference supports only two-sided difference tests; TOST defines its own two one-sided tests")

    if typ in {"independent_t", "mann_whitney", "equivalence_tost_independent"}:
        _need(errors, a, ["outcome", "group", "group_a", "group_b"], f"{prefix}[{i}] {typ}")
        for key in ["group_a", "group_b"]:
            if a.get(key) is not None and not _valid_level_scalar(a.get(key)):
                errors.append(f"{prefix}[{i}] {key} must be a boolean, finite numeric, or non-empty string level")
        if a.get("group_a") is not None and a.get("group_b") is not None and _level_key(a.get("group_a")) == _level_key(a.get("group_b")):
            errors.append(f"{prefix}[{i}] group_a and group_b must differ")
        if typ == "equivalence_tost_independent":
            _validate_equivalence(errors, warnings, a, i, prefix)

    elif typ in {"paired_t", "wilcoxon", "equivalence_tost_paired"}:
        wide_ok = bool(a.get("outcome_a") and a.get("outcome_b"))
        long_ok = all(a.get(k) not in (None, "") for k in ["outcome", "pair_id", "condition", "condition_a", "condition_b"])
        if not (wide_ok or long_ok):
            errors.append(f"{prefix}[{i}] {typ} needs outcome_a/outcome_b or long-format pairing fields")
        if wide_ok and a.get("outcome_a") == a.get("outcome_b"):
            errors.append(f"{prefix}[{i}] outcome_a and outcome_b must differ")
        if long_ok:
            for key in ["condition_a", "condition_b"]:
                if not _valid_level_scalar(a.get(key)):
                    errors.append(f"{prefix}[{i}] {key} must be a boolean, finite numeric, or non-empty string level")
            if _level_key(a.get("condition_a")) == _level_key(a.get("condition_b")):
                errors.append(f"{prefix}[{i}] condition_a and condition_b must differ")
        if wide_ok and long_ok:
            warnings.append(f"{prefix}[{i}] supplies both wide- and long-format pairing fields; wide-format fields take precedence")
        if typ == "equivalence_tost_paired":
            _validate_equivalence(errors, warnings, a, i, prefix)

    elif typ in {"pearson", "spearman"}:
        _need(errors, a, ["x", "y"], f"{prefix}[{i}] {typ}")
        if a.get("x") == a.get("y") and a.get("x") is not None:
            warnings.append(f"{prefix}[{i}] x and y are the same column; correlation is not scientifically informative")

    elif typ == "linear_regression":
        _need(errors, a, ["outcome", "predictors"], f"{prefix}[{i}] linear_regression")
        preds = _validate_predictors(errors, a, i, prefix)
        if isinstance(preds, list) and a.get("outcome") in preds:
            errors.append(f"{prefix}[{i}] outcome cannot also be a predictor")
        robust = a.get("robust_se", "HC3")
        if robust not in ALLOWED_LINEAR_ROBUST_SE:
            errors.append(f"{prefix}[{i}] robust_se must be one of {sorted(ALLOWED_LINEAR_ROBUST_SE)}")
        target = a.get("report_predictor")
        if target and isinstance(preds, list) and target not in preds:
            errors.append(f"{prefix}[{i}] report_predictor must be included in predictors")

    elif typ == "ancova_two_group":
        _need(errors, a, ["outcome", "group", "group_a", "group_b", "covariates"], f"{prefix}[{i}] ancova_two_group")
        for key in ["group_a", "group_b"]:
            if a.get(key) is not None and not _valid_level_scalar(a.get(key)):
                errors.append(f"{prefix}[{i}] {key} must be a boolean, finite numeric, or non-empty string level")
        if a.get("group_a") is not None and a.get("group_b") is not None and _level_key(a.get("group_a")) == _level_key(a.get("group_b")):
            errors.append(f"{prefix}[{i}] group_a and group_b must differ")
        covs = a.get("covariates")
        if not isinstance(covs, list) or not covs or not all(isinstance(x, str) and x for x in covs):
            errors.append(f"{prefix}[{i}] covariates must be a non-empty list of numeric column names")
        elif len(covs) != len(set(covs)):
            errors.append(f"{prefix}[{i}] covariates must be unique")
        if isinstance(covs, list) and a.get("outcome") in covs:
            errors.append(f"{prefix}[{i}] outcome cannot also be a covariate")
        robust = a.get("robust_se", "HC3")
        if robust not in ALLOWED_LINEAR_ROBUST_SE:
            errors.append(f"{prefix}[{i}] robust_se must be one of {sorted(ALLOWED_LINEAR_ROBUST_SE)}")
        if a.get("include_interactions") not in (None, False):
            errors.append(f"{prefix}[{i}] v1.4 ancova_two_group does not auto-fit group×covariate interactions; use a specialist/general model handoff when interactions are part of the estimand")

    elif typ == "logistic_regression":
        _need(errors, a, ["outcome", "event_level", "nonevent_level", "predictors"], f"{prefix}[{i}] logistic_regression")
        for key in ["event_level", "nonevent_level"]:
            if a.get(key) is not None and not _valid_level_scalar(a.get(key)):
                errors.append(f"{prefix}[{i}] {key} must be a boolean, finite numeric, or non-empty string level")
        if a.get("event_level") is not None and a.get("nonevent_level") is not None and _level_key(a.get("event_level")) == _level_key(a.get("nonevent_level")):
            errors.append(f"{prefix}[{i}] event_level and nonevent_level must differ")
        preds = _validate_predictors(errors, a, i, prefix)
        if isinstance(preds, list) and a.get("outcome") in preds:
            errors.append(f"{prefix}[{i}] outcome cannot also be a predictor")
        target = a.get("report_predictor")
        if target and isinstance(preds, list) and target not in preds:
            errors.append(f"{prefix}[{i}] report_predictor must be included in predictors")
        robust = a.get("robust_se", "HC0")
        if robust not in ALLOWED_GLM_ROBUST_SE:
            errors.append(f"{prefix}[{i}] robust_se must be one of {sorted(ALLOWED_GLM_ROBUST_SE)}")

    elif typ == "welch_anova":
        _need(errors, a, ["outcome", "group", "group_levels"], f"{prefix}[{i}] welch_anova")
        levels = a.get("group_levels")
        if not isinstance(levels, list) or len(levels) < 3:
            errors.append(f"{prefix}[{i}] welch_anova group_levels must contain at least three declared levels")
        elif not all(_valid_level_scalar(x) for x in levels):
            errors.append(f"{prefix}[{i}] welch_anova group_levels must contain only boolean, finite numeric, or non-empty string levels")
        elif len({_level_key(x) for x in levels}) != len(levels):
            errors.append(f"{prefix}[{i}] welch_anova group_levels must be distinct under scalar data equality")

    elif typ == "welch_contrast":
        _need(errors, a, ["outcome", "group", "contrast_terms"], f"{prefix}[{i}] welch_contrast")
        terms = a.get("contrast_terms")
        if not isinstance(terms, list) or len(terms) < 2:
            errors.append(f"{prefix}[{i}] welch_contrast contrast_terms must contain at least two level/weight terms")
        else:
            levels = []
            level_keys = []
            weights = []
            for j, term in enumerate(terms):
                if not isinstance(term, dict):
                    errors.append(f"{prefix}[{i}] welch_contrast contrast_terms[{j}] must be an object")
                    continue
                if "level" not in term or "weight" not in term:
                    errors.append(f"{prefix}[{i}] welch_contrast contrast_terms[{j}] requires level and weight")
                    continue
                level = term.get("level")
                weight = term.get("weight")
                if not _valid_level_scalar(level):
                    errors.append(f"{prefix}[{i}] welch_contrast contrast_terms[{j}].level must be a boolean, finite numeric, or non-empty string scalar")
                if not isinstance(weight, (int, float)) or isinstance(weight, bool) or not math.isfinite(float(weight)):
                    errors.append(f"{prefix}[{i}] welch_contrast contrast_terms[{j}].weight must be finite numeric")
                elif abs(float(weight)) <= 1e-15:
                    errors.append(f"{prefix}[{i}] welch_contrast contrast_terms[{j}].weight must be nonzero; omit unused groups")
                levels.append(level)
                level_keys.append(_level_key(level))
                if isinstance(weight, (int, float)) and not isinstance(weight, bool) and math.isfinite(float(weight)):
                    weights.append(float(weight))
            if len(level_keys) == len(terms) and len(set(level_keys)) != len(level_keys):
                errors.append(f"{prefix}[{i}] welch_contrast levels must be distinct under scalar data equality")
            if len(weights) == len(terms):
                tol = 1e-10 * max(1.0, sum(abs(w) for w in weights))
                if abs(sum(weights)) > tol:
                    errors.append(f"{prefix}[{i}] welch_contrast weights must sum to zero (within numerical tolerance); got {sum(weights):.12g}")
                if not (any(w > 0 for w in weights) and any(w < 0 for w in weights)):
                    errors.append(f"{prefix}[{i}] welch_contrast requires at least one positive and one negative weight")

    elif typ == "poisson_regression":
        _need(errors, a, ["outcome", "predictors"], f"{prefix}[{i}] poisson_regression")
        preds = _validate_predictors(errors, a, i, prefix)
        if isinstance(preds, list) and a.get("outcome") in preds:
            errors.append(f"{prefix}[{i}] outcome cannot also be a predictor")
        target = a.get("report_predictor")
        if target and isinstance(preds, list) and target not in preds:
            errors.append(f"{prefix}[{i}] report_predictor must be included in predictors")
        robust = a.get("robust_se", "HC0")
        if robust not in ALLOWED_GLM_ROBUST_SE:
            errors.append(f"{prefix}[{i}] robust_se must be one of {sorted(ALLOWED_GLM_ROBUST_SE)}")
        exposure = a.get("exposure")
        offset = a.get("offset")
        if exposure not in (None, "") and offset not in (None, ""):
            errors.append(f"{prefix}[{i}] poisson_regression may declare exposure or offset, not both")
        if exposure is not None and not isinstance(exposure, str):
            errors.append(f"{prefix}[{i}] exposure must be a column name or null")
        if offset is not None and not isinstance(offset, str):
            errors.append(f"{prefix}[{i}] offset must be a column name or null")

    elif typ in {"chi_square", "fisher_exact"}:
        _need(errors, a, ["row", "column"], f"{prefix}[{i}] {typ}")
        if a.get("row") == a.get("column") and a.get("row") is not None:
            errors.append(f"{prefix}[{i}] row and column must differ")
        if typ == "fisher_exact":
            for key in ["row_levels", "column_levels"]:
                levels = a.get(key)
                if levels is not None and (not isinstance(levels, list) or len(levels) != 2 or not all(_valid_level_scalar(x) for x in levels) or len({_level_key(x) for x in levels}) != 2):
                    errors.append(f"{prefix}[{i}] {key} must contain exactly two distinct boolean/finite numeric/non-empty string levels when supplied")
    return errors, warnings


def validate(plan):
    errors, warnings = [], []
    required = [
        "analysis_id", "plan_version", "profile", "research_question", "unit_of_analysis",
        "confidence_level", "random_seed", "input", "variables", "cleaning", "missing_data",
        "resampling", "analyses", "multiplicity",
    ]
    for k in required:
        if k not in plan:
            errors.append(f"Missing required field: {k}")

    schema = plan.get("analysis_plan_schema_version")
    if schema is None:
        errors.append("analysis_plan_schema_version is required in v1.4")
    elif str(schema) != ANALYSIS_PLAN_SCHEMA_VERSION:
        errors.append(f"analysis_plan_schema_version must be '{ANALYSIS_PLAN_SCHEMA_VERSION}' for this skill version")

    if not isinstance(plan.get("analysis_id"), str) or not str(plan.get("analysis_id", "")).strip():
        errors.append("analysis_id must be a non-empty string")
    if not isinstance(plan.get("research_question"), str) or not str(plan.get("research_question", "")).strip():
        errors.append("research_question must be a non-empty string")
    if not isinstance(plan.get("unit_of_analysis"), str) or not str(plan.get("unit_of_analysis", "")).strip():
        errors.append("unit_of_analysis must be a non-empty string")
    if plan.get("profile") not in ALLOWED_PROFILES:
        errors.append(f"profile must be one of {sorted(ALLOWED_PROFILES)}")
    if not isinstance(plan.get("random_seed"), int):
        errors.append("random_seed must be an integer")
    cl = plan.get("confidence_level")
    if not isinstance(cl, (int, float)) or not (0 < cl < 1):
        errors.append("confidence_level must be a number in (0,1)")

    inp = plan.get("input")
    if not isinstance(inp, dict):
        errors.append("input must be an object")
    else:
        if not isinstance(inp.get("path"), str) or not inp.get("path", "").strip():
            errors.append("input.path must be a non-empty string")
        sha = inp.get("sha256", "")
        if sha and not HEX64.match(str(sha)):
            errors.append("input.sha256 must be blank or a 64-character SHA-256 hex digest")
        if plan.get("profile") == "confirmatory" and not sha:
            errors.append("confirmatory profile requires input.sha256 to lock the raw input identity")
        elif plan.get("profile") == "standard" and not sha:
            warnings.append("input.sha256 is blank; fill it before freezing a standard analysis")

    variables = plan.get("variables")
    if not isinstance(variables, dict):
        errors.append("variables must be an object")
    elif not variables.get("id"):
        warnings.append("variables.id is empty; independent-unit traceability may be reduced")

    missing = plan.get("missing_data")
    if not isinstance(missing, dict):
        errors.append("missing_data must be an object")
    else:
        strategy = missing.get("strategy")
        if strategy not in ALLOWED_MISSING:
            errors.append(f"missing_data.strategy must be one of {sorted(ALLOWED_MISSING)} in v1.3")
        if missing.get("report_per_analysis", True) is not True:
            warnings.append("missing_data.report_per_analysis=false reduces auditability; v1.3 still records core analyzed-unit counts")
        if missing.get("imputation") not in (None, "none"):
            errors.append("v1.3 core does not perform imputation; use imputation='none' or a specialist/multiple-imputation workflow")

    resampling = plan.get("resampling")
    if not isinstance(resampling, dict):
        errors.append("resampling must be an object")
    else:
        nr = resampling.get("n_resamples")
        if not isinstance(nr, int) or not (200 <= nr <= 100000):
            errors.append("resampling.n_resamples must be an integer between 200 and 100000")
        if resampling.get("method", "percentile") != "percentile":
            errors.append("v1.3 supports only percentile bootstrap in the deterministic core")

    cleaning = plan.get("cleaning")
    if not isinstance(cleaning, dict):
        errors.append("cleaning must be an object")
        cleaning = {}
    for key in ["missing_tokens", "require_nonmissing", "require_numeric"]:
        if key in cleaning and not isinstance(cleaning.get(key), list):
            errors.append(f"cleaning.{key} must be a list")
    if cleaning.get("id_duplicate_policy", "audit") not in ALLOWED_ID_POLICIES:
        errors.append(f"cleaning.id_duplicate_policy must be one of {sorted(ALLOWED_ID_POLICIES)}")
    ranges = cleaning.get("numeric_ranges", {})
    if not isinstance(ranges, dict):
        errors.append("cleaning.numeric_ranges must be an object")
    else:
        for col, bounds in ranges.items():
            if not isinstance(bounds, dict):
                errors.append(f"cleaning.numeric_ranges.{col} must be an object")
                continue
            mn, mx = bounds.get("min"), bounds.get("max")
            for label, value in [("min", mn), ("max", mx)]:
                if value is not None and not isinstance(value, (int, float)):
                    errors.append(f"cleaning.numeric_ranges.{col}.{label} must be numeric or null")
            if isinstance(mn, (int, float)) and isinstance(mx, (int, float)) and mn > mx:
                errors.append(f"cleaning.numeric_ranges.{col}: min cannot exceed max")
    levels = cleaning.get("allowed_levels", {})
    if not isinstance(levels, dict):
        errors.append("cleaning.allowed_levels must be an object")
    else:
        for col, vals in levels.items():
            if not isinstance(vals, list) or not vals:
                errors.append(f"cleaning.allowed_levels.{col} must be a non-empty list")
            elif not all(_valid_level_scalar(x) for x in vals):
                errors.append(f"cleaning.allowed_levels.{col} must contain only boolean, finite numeric, or non-empty string levels")
            elif len({_level_key(x) for x in vals}) != len(vals):
                errors.append(f"cleaning.allowed_levels.{col} contains duplicate levels under scalar data equality")

    tech = cleaning.get("technical_replicates")
    if tech is not None:
        if not isinstance(tech, dict):
            errors.append("cleaning.technical_replicates must be null or an object")
        else:
            keys = tech.get("group_by") or []
            values = tech.get("value_columns") or []
            if not isinstance(keys, list) or not keys:
                errors.append("technical_replicates.group_by must be a non-empty list")
            if not isinstance(values, list) or not values:
                errors.append("technical_replicates.value_columns must be a non-empty list")
            if set(keys) & set(values):
                errors.append("technical_replicates.group_by and value_columns must not overlap")
            if tech.get("method", "mean") not in {"mean", "median"}:
                errors.append("technical_replicates.method must be mean or median")
            carry = tech.get("carry_columns")
            if carry is not None and not isinstance(carry, list):
                errors.append("technical_replicates.carry_columns must be null or a list")

    analyses = plan.get("analyses")
    if not isinstance(analyses, list) or not analyses:
        errors.append("analyses must contain at least one analysis item")
        analyses = []
    ids = []
    for i, a in enumerate(analyses):
        if not isinstance(a, dict):
            errors.append(f"analyses[{i}] must be an object")
            continue
        e, w = validate_analysis_item(a, i)
        errors.extend(e); warnings.extend(w)
        if a.get("analysis_item_id"):
            ids.append(a["analysis_item_id"])
        if plan.get("profile") == "confirmatory" and not a.get("analysis_role"):
            errors.append(f"analyses[{i}] confirmatory analyses require analysis_role")
    if len(ids) != len(set(ids)):
        errors.append("analysis_item_id values must be unique")

    mult = plan.get("multiplicity", {})
    if not isinstance(mult, dict):
        errors.append("multiplicity must be an object")
        mult = {}
    families_used = {a.get("multiplicity_family") for a in analyses if isinstance(a, dict) and a.get("multiplicity_family")}
    for fam in families_used:
        if fam not in mult:
            errors.append(f"Missing multiplicity definition for family '{fam}'")
        elif not isinstance(mult[fam], dict):
            errors.append(f"Multiplicity definition for family '{fam}' must be an object")
        else:
            method = mult[fam].get("method", "none")
            if method not in ALLOWED_MULT:
                errors.append(f"Unsupported multiplicity method '{method}' for family '{fam}'")
    for fam, spec in mult.items():
        if not isinstance(spec, dict):
            continue
        if spec.get("method", "none") not in ALLOWED_MULT:
            errors.append(f"Unsupported multiplicity method '{spec.get('method')}' for family '{fam}'")
            continue
        if spec.get("method") == "none":
            n = sum(isinstance(a, dict) and a.get("multiplicity_family") == fam for a in analyses)
            if n > 1 and not spec.get("justification"):
                msg = f"Family '{fam}' has {n} tests, method=none, and no justification"
                (errors if plan.get("profile") == "confirmatory" else warnings).append(msg)

    plots = plan.get("plots", [])
    if plots is not None and not isinstance(plots, list):
        errors.append("plots must be a list")
        plots = []
    plot_ids = []
    analysis_type_by_id = {a.get("analysis_item_id"): a.get("type") for a in analyses if isinstance(a, dict)}
    allowed_plot_types = {
        "group_comparison": {"independent_t", "mann_whitney", "equivalence_tost_independent", "ancova_two_group", "welch_anova", "welch_contrast"},
        "paired_comparison": {"paired_t", "wilcoxon", "equivalence_tost_paired"},
        "correlation": {"pearson", "spearman"},
        "regression": {"linear_regression"},
        "count_regression": {"poisson_regression"},
    }
    for i, p in enumerate(plots or []):
        if not isinstance(p, dict):
            errors.append(f"plots[{i}] must be an object")
            continue
        _need(errors, p, ["plot_id", "analysis_item_id", "kind"], f"plots[{i}]")
        if p.get("plot_id"):
            plot_ids.append(p["plot_id"])
        if p.get("analysis_item_id") and p.get("analysis_item_id") not in set(ids):
            errors.append(f"plots[{i}] references unknown analysis_item_id '{p.get('analysis_item_id')}'")
        elif p.get("analysis_item_id") and p.get("kind"):
            kind = p.get("kind")
            typ = analysis_type_by_id.get(p.get("analysis_item_id"))
            if kind not in allowed_plot_types:
                errors.append(f"plots[{i}] unsupported kind '{kind}'")
            elif typ not in allowed_plot_types[kind]:
                errors.append(f"plots[{i}] kind '{kind}' is not compatible with analysis type '{typ}'")
    if len(plot_ids) != len(set(plot_ids)):
        errors.append("plot_id values must be unique")

    sensitivities = plan.get("sensitivity_analyses", [])
    if not isinstance(sensitivities, list):
        errors.append("sensitivity_analyses must be a list")
        sensitivities = []
    sids = []
    by_id = {a.get("analysis_item_id"): a for a in analyses if isinstance(a, dict)}
    for i, s in enumerate(sensitivities):
        if not isinstance(s, dict):
            errors.append(f"sensitivity_analyses[{i}] must be an object")
            continue
        _need(errors, s, ["sensitivity_id", "base_analysis_item_id", "rationale", "estimand_relation"], f"sensitivity_analyses[{i}]")
        if s.get("estimand_relation") not in ALLOWED_ESTIMAND_RELATIONS:
            errors.append(f"sensitivity_analyses[{i}].estimand_relation must be one of {sorted(ALLOWED_ESTIMAND_RELATIONS)}")
        sid = s.get("sensitivity_id")
        if sid:
            sids.append(sid)
        base_id = s.get("base_analysis_item_id")
        if base_id not in by_id:
            errors.append(f"sensitivity_analyses[{i}] references unknown base_analysis_item_id '{base_id}'")
            continue
        filt = s.get("data_filter", {})
        if filt is not None and not isinstance(filt, dict):
            errors.append(f"sensitivity_analyses[{i}].data_filter must be an object")
        else:
            rules = (filt or {}).get("exclude_if", [])
            if rules and not isinstance(rules, list):
                errors.append(f"sensitivity_analyses[{i}].data_filter.exclude_if must be a list")
            for j, rule in enumerate(rules or []):
                if not isinstance(rule, dict):
                    errors.append(f"sensitivity_analyses[{i}].exclude_if[{j}] must be an object")
                    continue
                _need(errors, rule, ["column", "operator"], f"sensitivity_analyses[{i}].exclude_if[{j}]")
                op = rule.get("operator")
                if op not in ALLOWED_FILTER_OPERATORS:
                    errors.append(f"sensitivity_analyses[{i}].exclude_if[{j}] unsupported operator '{op}'")
                if op in {"eq", "ne", "lt", "le", "gt", "ge"} and "value" not in rule:
                    errors.append(f"sensitivity_analyses[{i}].exclude_if[{j}] operator {op} requires value")
                if op in {"eq", "ne"} and "value" in rule and not _valid_filter_scalar(rule.get("value")):
                    errors.append(f"sensitivity_analyses[{i}].exclude_if[{j}] operator {op} requires a finite numeric, boolean, or non-empty string scalar; use isna/notna for missingness")
                if op in {"lt", "le", "gt", "ge"} and "value" in rule:
                    value = rule.get("value")
                    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(float(value)):
                        errors.append(f"sensitivity_analyses[{i}].exclude_if[{j}] operator {op} requires a finite numeric value")
                if op in {"in", "not_in"}:
                    vals = rule.get("values")
                    if not isinstance(vals, list) or not vals:
                        errors.append(f"sensitivity_analyses[{i}].exclude_if[{j}] operator {op} requires a non-empty values list")
                    elif not all(_valid_filter_scalar(x) for x in vals):
                        errors.append(f"sensitivity_analyses[{i}].exclude_if[{j}] operator {op} values must be finite numeric, boolean, or non-empty string scalars; use isna/notna for missingness")
                    elif len({_level_key(x) for x in vals}) != len(vals):
                        errors.append(f"sensitivity_analyses[{i}].exclude_if[{j}] operator {op} values contain duplicate typed levels")
        overrides = s.get("analysis_overrides", {})
        if overrides is not None and not isinstance(overrides, dict):
            errors.append(f"sensitivity_analyses[{i}].analysis_overrides must be an object")
        else:
            unknown = set((overrides or {}).keys()) - ALLOWED_SENSITIVITY_OVERRIDES
            if unknown:
                errors.append(f"sensitivity_analyses[{i}] unsupported analysis_overrides keys: {sorted(unknown)}")
            merged = deepcopy(by_id[base_id]); merged.update(overrides or {}); merged["analysis_item_id"] = f"sensitivity::{sid or i}"
            e, w = validate_analysis_item(merged, i, prefix="sensitivity_analyses")
            errors.extend(e); warnings.extend(w)
            if s.get("estimand_relation") == "same":
                for reason in same_estimand_structural_conflicts(by_id[base_id], merged):
                    errors.append(
                        f"sensitivity_analyses[{i}] estimand_relation='same' is structurally incompatible with analysis_overrides: {reason}; "
                        "use 'different' or 'uncertain', or revise the override"
                    )
    if len(sids) != len(set(sids)):
        errors.append("sensitivity_id values must be unique")

    return errors, warnings


def main():
    ap = argparse.ArgumentParser()
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
    print("Plan validation: PASS")


if __name__ == "__main__":
    main()
