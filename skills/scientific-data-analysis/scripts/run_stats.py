#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import math
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats
import statsmodels.api as sm
from statsmodels.stats.multitest import multipletests
from statsmodels.stats.oneway import anova_oneway, effectsize_oneway
from statsmodels.tools.sm_exceptions import PerfectSeparationWarning

from _common import (
    read_table, read_json, write_json, bootstrap_ci, sha256_file, stable_seed, SKILL_VERSION,
    categorical_level_key, categorical_level_mask, categorical_levels_mask, jsonable_level, level_display_labels,
    assert_no_equality_colliding_levels, typed_scalar_key,
)
from validate_plan import validate


def tcrit_ci(est, se, df, level):
    if se is None or not np.isfinite(se) or df is None or df <= 0:
        return (None, None)
    q = stats.t.ppf((1 + level) / 2, df)
    return float(est - q * se), float(est + q * se)


def hedges_g(a, b):
    """Hedges g oriented as group b minus group a."""
    a, b = np.asarray(a, float), np.asarray(b, float)
    n1, n2 = len(a), len(b)
    if n1 < 2 or n2 < 2:
        return None
    s1, s2 = np.var(a, ddof=1), np.var(b, ddof=1)
    sp2 = ((n1 - 1) * s1 + (n2 - 1) * s2) / (n1 + n2 - 2)
    if not np.isfinite(sp2) or sp2 <= 0:
        return None
    d = (np.mean(b) - np.mean(a)) / math.sqrt(sp2)
    df = n1 + n2 - 2
    j = 1 - 3 / (4 * df - 1) if df > 1 else 1
    return float(j * d)


def matched_rank_biserial(diffs):
    d = np.asarray(diffs, float)
    d = d[np.isfinite(d) & (d != 0)]
    if len(d) == 0:
        return None
    ranks = stats.rankdata(np.abs(d))
    pos = ranks[d > 0].sum()
    neg = ranks[d < 0].sum()
    den = pos + neg
    return float((pos - neg) / den) if den else None


def _require_columns(df, columns, aid):
    missing = [c for c in columns if c not in df.columns]
    if missing:
        raise KeyError(f"{aid}: missing data column(s) {missing}")


def _paired_arrays_with_counts(df, a):
    aid = a["analysis_item_id"]
    if a.get("outcome_a") and a.get("outcome_b"):
        _require_columns(df, [a["outcome_a"], a["outcome_b"]], aid)
        raw = df[[a["outcome_a"], a["outcome_b"]]].copy()
        pair = raw.apply(pd.to_numeric, errors="coerce").dropna()
        return pair.iloc[:, 0].to_numpy(float), pair.iloc[:, 1].to_numpy(float), int(len(raw)), "pairs", {"n_rows_missing_pair_id": 0}

    cols = [a["pair_id"], a["condition"], a["outcome"]]
    _require_columns(df, cols, aid)
    p = df[cols].copy()
    p[a["outcome"]] = pd.to_numeric(p[a["outcome"]], errors="coerce")
    cond_a = a["condition_a"]
    cond_b = a["condition_b"]
    mask_a = categorical_level_mask(p[a["condition"]], cond_a)
    mask_b = categorical_level_mask(p[a["condition"]], cond_b)
    p = p[mask_a | mask_b].copy()
    p["__condition_code"] = np.where(categorical_level_mask(p[a["condition"]], cond_a), 0, 1)
    missing_pair_id_rows = int(p[a["pair_id"]].isna().sum())
    # A missing subject/pair identifier cannot define an analysis unit. Never let
    # pandas group all missing IDs into one synthetic pair.
    p = p.loc[p[a["pair_id"]].notna()].copy()
    p["__pair_key"] = p[a["pair_id"]].map(typed_scalar_key)
    pair_value_by_key = {}
    for raw_id, key in zip(p[a["pair_id"]].tolist(), p["__pair_key"].tolist()):
        pair_value_by_key.setdefault(key, raw_id)
    candidate_pairs = int(len(pair_value_by_key))

    counts = p.groupby(["__pair_key", "__condition_code"], dropna=False).size()
    dup = counts[counts > 1]
    if len(dup):
        examples = []
        for idx, n in dup.head(10).items():
            pair_key, condition_code = idx if isinstance(idx, tuple) else (idx, None)
            condition_value = cond_a if condition_code == 0 else cond_b if condition_code == 1 else condition_code
            pair_value = pair_value_by_key.get(pair_key, pair_key)
            examples.append({"pair_id": jsonable_level(pair_value), "condition": jsonable_level(condition_value), "n": int(n)})
        raise ValueError(
            f"{aid}: multiple observations exist for the same pair×condition cell; "
            "aggregate declared technical replicates first or use an appropriate repeated/multilevel model. "
            f"examples={examples}"
        )

    wide = p.pivot(index="__pair_key", columns="__condition_code", values=a["outcome"])
    missing_conditions = []
    if 0 not in wide.columns: missing_conditions.append(jsonable_level(cond_a))
    if 1 not in wide.columns: missing_conditions.append(jsonable_level(cond_b))
    if missing_conditions:
        raise ValueError(f"{aid}: condition level(s) absent from data: {missing_conditions}")
    wide = wide[[0, 1]].dropna()
    return wide.iloc[:, 0].to_numpy(float), wide.iloc[:, 1].to_numpy(float), candidate_pairs, "pairs", {"n_rows_missing_pair_id": missing_pair_id_rows}


def _paired_arrays(df, a):
    xa, xb, _, _, _ = _paired_arrays_with_counts(df, a)
    return xa, xb


def _nonnull_numeric(series):
    return pd.to_numeric(series, errors="coerce").dropna().to_numpy(float)


def _finite_or_error(value, label, aid):
    if value is None or not np.isfinite(float(value)):
        raise ValueError(f"{aid}: {label} is not finite/estimable under the declared analysis")
    return float(value)


def _level_equal(observed, declared):
    """Compare categorical levels using the skill's typed scalar identity.

    Numeric 1 and 1.0 remain the same level, but equality-colliding encodings
    such as True and 1, or string "1" and numeric 1, stay distinct.
    """
    try:
        if pd.isna(observed) or pd.isna(declared):
            return False
    except Exception:
        return False
    return categorical_level_key(observed) == categorical_level_key(declared)


def _describe_array(x):
    x = np.asarray(x, float)
    x = x[np.isfinite(x)]
    if not len(x):
        return {}
    return {
        "mean": float(np.mean(x)),
        "sd": float(np.std(x, ddof=1)) if len(x) > 1 else None,
        "median": float(np.median(x)),
        "q1": float(np.quantile(x, 0.25)),
        "q3": float(np.quantile(x, 0.75)),
    }


def _stamp_missingness(r, candidate, analyzed, unit="rows", strategy="complete_case"):
    r["missing_data_strategy"] = strategy
    r["missingness_unit"] = unit
    r["n_candidate_units"] = int(candidate)
    r["n_analyzed_units"] = int(analyzed)
    r["n_missing_or_invalid_excluded"] = int(max(0, candidate - analyzed))


def _welch_components(x1, x2, aid):
    if len(x1) < 2 or len(x2) < 2:
        raise ValueError(f"{aid}: need >=2 numeric observations per group")
    m1, m2 = np.mean(x1), np.mean(x2)
    v1, v2 = np.var(x1, ddof=1), np.var(x2, ddof=1)
    se2 = v1 / len(x1) + v2 / len(x2)
    denom = (v1 / len(x1)) ** 2 / (len(x1) - 1) + (v2 / len(x2)) ** 2 / (len(x2) - 1)
    if not np.isfinite(se2) or se2 <= 0 or not np.isfinite(denom) or denom <= 0:
        raise ValueError(f"{aid}: Welch mean comparison is not estimable because within-group variance is zero/degenerate")
    est = float(m2 - m1)
    se = math.sqrt(se2)
    dfw = se2 ** 2 / denom
    vr = max(v1, v2) / min(v1, v2) if min(v1, v2) > 0 else None
    return est, se, dfw, m1, m2, v1, v2, vr


def _ols_diagnostics(fit, X):
    out = {"condition_number": float(np.linalg.cond(np.asarray(X, float)))}
    try:
        infl = fit.get_influence()
        hat = np.asarray(infl.hat_matrix_diag, float)
        cooks = np.asarray(infl.cooks_distance[0], float)
        out["max_leverage"] = float(np.nanmax(hat)) if len(hat) else None
        out["max_cooks_distance"] = float(np.nanmax(cooks)) if len(cooks) else None
    except Exception:
        out["max_leverage"] = None
        out["max_cooks_distance"] = None
    return out



def _fisher_exact_two_sided_2x2(cells):
    """Deterministic two-sided Fisher exact p-value for a 2x2 integer table.

    Uses the standard fixed-margin hypergeometric definition: sum probabilities
    of all tables with probability <= the observed table probability.
    """
    t = np.asarray(cells, dtype=int)
    if t.shape != (2, 2) or np.any(t < 0):
        raise ValueError("Fisher exact helper requires a nonnegative 2x2 table")
    a, b, c, d = map(int, t.ravel())
    total = a + b + c + d
    row1 = a + b
    col1 = a + c
    lo = max(0, row1 - (total - col1))
    hi = min(row1, col1)
    support = np.arange(lo, hi + 1, dtype=int)
    probs = stats.hypergeom.pmf(support, total, col1, row1)
    p_obs = float(stats.hypergeom.pmf(a, total, col1, row1))
    p = float(np.clip(probs[probs <= p_obs * (1 + 1e-12)].sum(), 0.0, 1.0))
    numerator = a * d
    denominator = b * c
    if denominator == 0:
        raw_or = math.inf if numerator > 0 else None
    else:
        raw_or = float(numerator / denominator)
    return raw_or, p

def _coeff_json(fit, level, exp_label=None):
    cis = fit.conf_int(alpha=1 - level)
    coeffs = {}
    for name in fit.params.index:
        beta = float(fit.params[name])
        low = float(cis.loc[name].iloc[0]); high = float(cis.loc[name].iloc[1])
        entry = {
            "estimate": beta,
            "se": float(fit.bse[name]),
            "ci_low": low,
            "ci_high": high,
            "p_value": float(fit.pvalues[name]),
        }
        if exp_label:
            entry.update({
                exp_label: float(math.exp(beta)),
                f"{exp_label}_ci_low": float(math.exp(low)),
                f"{exp_label}_ci_high": float(math.exp(high)),
            })
        coeffs[str(name)] = entry
    return json.dumps(coeffs, sort_keys=True)


def _categorical_codes(series, observed_levels, aid, axis_name):
    """Encode categorical values with the same typed identity used in metadata.

    Pandas may merge Python-equal values such as True and 1 inside a crosstab.
    If typed identities in the source series cannot be represented by the
    observed crosstab levels, fail explicitly rather than silently recoding.
    """
    mapping = {categorical_level_key(v): i for i, v in enumerate(observed_levels)}
    keys = [categorical_level_key(v) for v in series.tolist()]
    missing = []
    for key in keys:
        if key not in mapping and key not in missing:
            missing.append(key)
    if missing:
        raise ValueError(
            f"{aid}: {axis_name} contains categorical values whose typed identity is ambiguous after contingency-table construction; "
            "normalize mixed boolean/numeric or otherwise equality-colliding category encodings before analysis"
        )
    return np.asarray([mapping[k] for k in keys], dtype=int), mapping


def result_base(a):
    return {
        "analysis_item_id": a["analysis_item_id"],
        "analysis_role": a.get("analysis_role", ""),
        "type": a["type"],
        "multiplicity_family": a.get("multiplicity_family", ""),
        "estimand": a.get("estimand", ""),
        "notes": a.get("notes", ""),
    }


def run_item(df, a, level, seed, n_resamples=2000, missing_strategy="complete_case"):
    typ = a["type"]
    aid = a["analysis_item_id"]
    r = result_base(a)
    r["resampling_n_resamples"] = int(n_resamples)

    if typ in {"independent_t", "equivalence_tost_independent"}:
        y, g = a["outcome"], a["group"]
        ga, gb = a["group_a"], a["group_b"]
        _require_columns(df, [y, g], aid)
        mask_a = categorical_level_mask(df[g], ga)
        mask_b = categorical_level_mask(df[g], gb)
        target = mask_a | mask_b
        candidate = int(target.sum())
        x1 = _nonnull_numeric(df.loc[mask_a, y])
        x2 = _nonnull_numeric(df.loc[mask_b, y])
        est, se, dfw, m1, m2, v1, v2, vr = _welch_components(x1, x2, aid)
        d1, d2 = _describe_array(x1), _describe_array(x2)
        base = dict(
            n_a=len(x1), n_b=len(x2), group_a=ga, group_b=gb,
            group_a_json=json.dumps(jsonable_level(ga)), group_b_json=json.dumps(jsonable_level(gb)),
            estimate=est, estimate_name="mean_difference_b_minus_a", null_value=0.0,
            effect_size=hedges_g(x1, x2), effect_size_name="Hedges_g_b_minus_a",
            df=float(dfw), mean_a=d1["mean"], mean_b=d2["mean"], sd_a=d1["sd"], sd_b=d2["sd"],
            median_a=d1["median"], median_b=d2["median"], variance_ratio_max_to_min=vr,
        )
        if typ == "independent_t":
            test = stats.ttest_ind(x2, x1, equal_var=False)
            p = _finite_or_error(test.pvalue, "p_value", aid)
            lo, hi = tcrit_ci(est, se, dfw, level)
            base.update(ci_low=lo, ci_high=hi, ci_level=level, ci_method="Welch-t", statistic=float(test.statistic), p_value=p)
        else:
            lo_m = float(a["equivalence_margin_lower"]); hi_m = float(a["equivalence_margin_upper"])
            alpha = float(a.get("equivalence_alpha", 0.05))
            t_lower = (est - lo_m) / se
            t_upper = (est - hi_m) / se
            p_lower = float(stats.t.sf(t_lower, dfw))
            p_upper = float(stats.t.cdf(t_upper, dfw))
            p = max(p_lower, p_upper)
            eq_level = 1 - 2 * alpha
            lo, hi = tcrit_ci(est, se, dfw, eq_level)
            base.update(
                ci_low=lo, ci_high=hi, ci_level=eq_level, ci_method="TOST_Welch_equivalence_CI",
                statistic=float(min(t_lower, -t_upper)), p_value=float(p),
                equivalence_margin_lower=lo_m, equivalence_margin_upper=hi_m, equivalence_alpha=alpha,
                tost_p_lower=p_lower, tost_p_upper=p_upper,
                equivalence_conclusion=bool(p_lower < alpha and p_upper < alpha),
                estimand_note="Equivalence is tested against prespecified raw-scale margins using two one-sided Welch tests; p_value is max(p_lower, p_upper).",
            )
        r.update(base)
        _stamp_missingness(r, candidate, len(x1) + len(x2), "rows", missing_strategy)

    elif typ in {"paired_t", "equivalence_tost_paired"}:
        xa, xb, candidate, unit, pair_diag = _paired_arrays_with_counts(df, a)
        d = xb - xa
        if len(d) < 2:
            raise ValueError(f"{aid}: need >=2 complete pairs")
        sd = float(np.std(d, ddof=1))
        if not np.isfinite(sd) or sd <= 0:
            raise ValueError(f"{aid}: paired mean comparison is not estimable because all paired differences are identical")
        est = float(np.mean(d)); se = float(stats.sem(d)); dfp = len(d) - 1
        base = dict(
            n_pairs=len(d), estimate=est, estimate_name="paired_mean_difference_b_minus_a", null_value=0.0,
            effect_size=float(est / sd), effect_size_name="paired_dz", df=dfp,
            mean_a=float(np.mean(xa)), mean_b=float(np.mean(xb)), sd_difference=sd,
            difference_skewness=float(stats.skew(d, bias=False)) if len(d) >= 3 else None,
        )
        if not (a.get("outcome_a") and a.get("outcome_b")):
            cond_labels = level_display_labels([a["condition_a"], a["condition_b"]])
            base.update(
                condition_a_json=json.dumps(jsonable_level(a["condition_a"])),
                condition_b_json=json.dumps(jsonable_level(a["condition_b"])),
                condition_orientation=f"{cond_labels[1]} minus {cond_labels[0]}",
            )
        if typ == "paired_t":
            test = stats.ttest_rel(xb, xa)
            p = _finite_or_error(test.pvalue, "p_value", aid)
            lo, hi = tcrit_ci(est, se, dfp, level)
            base.update(ci_low=lo, ci_high=hi, ci_level=level, ci_method="paired-t", statistic=float(test.statistic), p_value=p)
        else:
            lo_m = float(a["equivalence_margin_lower"]); hi_m = float(a["equivalence_margin_upper"])
            alpha = float(a.get("equivalence_alpha", 0.05))
            t_lower = (est - lo_m) / se
            t_upper = (est - hi_m) / se
            p_lower = float(stats.t.sf(t_lower, dfp))
            p_upper = float(stats.t.cdf(t_upper, dfp))
            p = max(p_lower, p_upper)
            eq_level = 1 - 2 * alpha
            lo, hi = tcrit_ci(est, se, dfp, eq_level)
            base.update(
                ci_low=lo, ci_high=hi, ci_level=eq_level, ci_method="TOST_paired_equivalence_CI",
                statistic=float(min(t_lower, -t_upper)), p_value=float(p),
                equivalence_margin_lower=lo_m, equivalence_margin_upper=hi_m, equivalence_alpha=alpha,
                tost_p_lower=p_lower, tost_p_upper=p_upper,
                equivalence_conclusion=bool(p_lower < alpha and p_upper < alpha),
                estimand_note="Equivalence is tested on paired mean differences against prespecified raw-scale margins; p_value is max(p_lower, p_upper).",
            )
        r.update(base)
        r.update(pair_diag)
        _stamp_missingness(r, candidate, len(d), unit, missing_strategy)

    elif typ == "mann_whitney":
        y, g = a["outcome"], a["group"]
        ga, gb = a["group_a"], a["group_b"]
        _require_columns(df, [y, g], aid)
        mask_a = categorical_level_mask(df[g], ga)
        mask_b = categorical_level_mask(df[g], gb)
        candidate = int((mask_a | mask_b).sum())
        x1 = _nonnull_numeric(df.loc[mask_a, y])
        x2 = _nonnull_numeric(df.loc[mask_b, y])
        if len(x1) < 1 or len(x2) < 1:
            raise ValueError(f"{aid}: need >=1 numeric observation per group")
        test = stats.mannwhitneyu(x2, x1, alternative="two-sided", method="auto")
        p = _finite_or_error(test.pvalue, "p_value", aid)
        rbc = 2 * float(test.statistic) / (len(x1) * len(x2)) - 1
        meddiff = float(np.median(x2) - np.median(x1))
        lo, hi = bootstrap_ci(lambda b, aa: np.median(b) - np.median(aa), [x2, x1], confidence_level=level, seed=seed, n_resamples=n_resamples)
        d1, d2 = _describe_array(x1), _describe_array(x2)
        r.update(
            n_a=len(x1), n_b=len(x2), group_a=ga, group_b=gb,
            group_a_json=json.dumps(jsonable_level(ga)), group_b_json=json.dumps(jsonable_level(gb)),
            estimate=meddiff, estimate_name="median_difference_b_minus_a_descriptive", null_value=0.0,
            ci_low=lo, ci_high=hi, ci_level=level, ci_method="percentile_bootstrap_descriptive",
            effect_size=rbc, effect_size_name="rank_biserial_b_minus_a",
            statistic=float(test.statistic), p_value=p,
            median_a=d1["median"], median_b=d2["median"], q1_a=d1["q1"], q3_a=d1["q3"], q1_b=d2["q1"], q3_b=d2["q3"],
            estimand_note="Mann-Whitney tests rank/stochastic separation; the median difference is reported only as a descriptive companion and is not generally the test estimand.",
        )
        _stamp_missingness(r, candidate, len(x1) + len(x2), "rows", missing_strategy)

    elif typ == "wilcoxon":
        xa, xb, candidate, unit, pair_diag = _paired_arrays_with_counts(df, a)
        d = xb - xa
        if len(d) < 2:
            raise ValueError(f"{aid}: need >=2 complete pairs")
        nonzero = d[d != 0]
        if len(nonzero) == 0:
            raise ValueError(f"{aid}: Wilcoxon signed-rank is not estimable because all paired differences are zero")
        test = stats.wilcoxon(d, zero_method="wilcox", alternative="two-sided", method="auto")
        p = _finite_or_error(test.pvalue, "p_value", aid)
        med = float(np.median(d))
        lo, hi = bootstrap_ci(lambda x: np.median(x), [d], confidence_level=level, seed=seed, n_resamples=n_resamples)
        r.update(
            n_pairs=len(d), n_nonzero_differences=len(nonzero),
            estimate=med, estimate_name="median_paired_difference_b_minus_a_descriptive", null_value=0.0,
            ci_low=lo, ci_high=hi, ci_level=level, ci_method="percentile_bootstrap_descriptive",
            effect_size=matched_rank_biserial(d), effect_size_name="matched_rank_biserial_b_minus_a",
            statistic=float(test.statistic), p_value=p,
            median_a=float(np.median(xa)), median_b=float(np.median(xb)),
            estimand_note="Wilcoxon signed-rank targets the distribution/ranks of paired differences under symmetry assumptions; the median paired difference is a descriptive companion.",
        )
        if not (a.get("outcome_a") and a.get("outcome_b")):
            cond_labels = level_display_labels([a["condition_a"], a["condition_b"]])
            r.update(
                condition_a_json=json.dumps(jsonable_level(a["condition_a"])),
                condition_b_json=json.dumps(jsonable_level(a["condition_b"])),
                condition_orientation=f"{cond_labels[1]} minus {cond_labels[0]}",
            )
        r.update(pair_diag)
        _stamp_missingness(r, candidate, len(d), unit, missing_strategy)

    elif typ in {"pearson", "spearman"}:
        _require_columns(df, [a["x"], a["y"]], aid)
        candidate = len(df)
        pair = df[[a["x"], a["y"]]].apply(pd.to_numeric, errors="coerce").dropna()
        x = pair.iloc[:, 0].to_numpy(float); y = pair.iloc[:, 1].to_numpy(float)
        if len(x) < 3:
            raise ValueError(f"{aid}: correlation requires >=3 complete numeric pairs")
        if np.ptp(x) == 0 or np.ptp(y) == 0:
            raise ValueError(f"{aid}: correlation is undefined when x or y is constant")
        if typ == "pearson":
            test = stats.pearsonr(x, y); est = _finite_or_error(test.statistic, "correlation", aid); p = _finite_or_error(test.pvalue, "p_value", aid)
            try:
                ci = test.confidence_interval(confidence_level=level); lo, hi = float(ci.low), float(ci.high); method = "Fisher/Scipy"
            except Exception:
                lo, hi = bootstrap_ci(lambda xx, yy: stats.pearsonr(xx, yy).statistic, [x, y], confidence_level=level, seed=seed, n_resamples=n_resamples, paired=True); method = "percentile_bootstrap"
        else:
            test = stats.spearmanr(x, y); est = _finite_or_error(test.statistic, "correlation", aid); p = _finite_or_error(test.pvalue, "p_value", aid)
            lo, hi = bootstrap_ci(lambda xx, yy: stats.spearmanr(xx, yy).statistic, [x, y], confidence_level=level, seed=seed, n_resamples=n_resamples, paired=True); method = "percentile_bootstrap"
        r.update(n=len(x), estimate=est, estimate_name=f"{typ}_r", null_value=0.0, ci_low=lo, ci_high=hi, ci_level=level, ci_method=method, effect_size=est, effect_size_name=f"{typ}_r", statistic=est, p_value=p)
        _stamp_missingness(r, candidate, len(x), "rows", missing_strategy)

    elif typ == "linear_regression":
        cols = [a["outcome"]] + list(a["predictors"]); _require_columns(df, cols, aid)
        candidate = len(df)
        sub = df[cols].copy(); y = pd.to_numeric(sub[a["outcome"]], errors="coerce")
        X = sub[a["predictors"]].copy()
        for c in X.columns: X[c] = pd.to_numeric(X[c], errors="coerce")
        z = pd.concat([y.rename("__y"), X], axis=1).dropna()
        if len(z) <= len(a["predictors"]) + 1:
            raise ValueError(f"{aid}: insufficient complete rows for OLS relative to the number of predictors")
        y2 = z.pop("__y"); X2 = sm.add_constant(z, has_constant="add")
        if np.linalg.matrix_rank(X2.to_numpy(float)) < X2.shape[1]:
            raise ValueError(f"{aid}: regression design matrix is rank-deficient (constant/collinear predictors)")
        robust = a.get("robust_se", "HC3"); fit = sm.OLS(y2, X2).fit(cov_type="HC3" if robust == "HC3" else "nonrobust")
        target = a.get("report_predictor") or a["predictors"][0]
        if target not in fit.params.index: raise ValueError(f"{aid}: report_predictor {target} not in fitted model")
        cis = fit.conf_int(alpha=1 - level); ci = cis.loc[target]; p = _finite_or_error(fit.pvalues[target], "p_value", aid); diag = _ols_diagnostics(fit, X2)
        r.update(
            n=int(fit.nobs), estimate=float(fit.params[target]), estimate_name=f"coefficient:{target}", null_value=0.0,
            ci_low=float(ci.iloc[0]), ci_high=float(ci.iloc[1]), ci_level=level, ci_method="OLS_HC3" if robust == "HC3" else "OLS",
            effect_size=float(fit.params[target]), effect_size_name=f"coefficient:{target}", statistic=float(fit.tvalues[target]), p_value=p, df=float(fit.df_resid),
            r_squared=float(fit.rsquared), adjusted_r_squared=float(fit.rsquared_adj), model_predictors=";".join(a["predictors"]), robust_se=robust,
            model_coefficients_json=_coeff_json(fit, level), **diag,
        )
        _stamp_missingness(r, candidate, int(fit.nobs), "rows", missing_strategy)

    elif typ == "ancova_two_group":
        cols = [a["outcome"], a["group"]] + list(a["covariates"]); _require_columns(df, cols, aid)
        ga, gb = a["group_a"], a["group_b"]
        mask_a = categorical_level_mask(df[a["group"]], ga)
        mask_b = categorical_level_mask(df[a["group"]], gb)
        target_rows = mask_a | mask_b; candidate = int(target_rows.sum())
        sub = df.loc[target_rows, cols].copy(); y = pd.to_numeric(sub[a["outcome"]], errors="coerce")
        X = pd.DataFrame(index=sub.index); X["group_b_vs_a"] = categorical_level_mask(sub[a["group"]], gb).astype(float)
        for c in a["covariates"]: X[c] = pd.to_numeric(sub[c], errors="coerce")
        z = pd.concat([y.rename("__y"), X], axis=1).dropna()
        if len(z) <= len(a["covariates"]) + 2:
            raise ValueError(f"{aid}: insufficient complete rows for ANCOVA relative to group + covariates")
        if z["group_b_vs_a"].nunique() != 2:
            raise ValueError(f"{aid}: both declared groups must have complete observations after covariate filtering")
        y2 = z.pop("__y"); X2 = sm.add_constant(z, has_constant="add")
        if np.linalg.matrix_rank(X2.to_numpy(float)) < X2.shape[1]:
            raise ValueError(f"{aid}: ANCOVA design matrix is rank-deficient (constant/collinear covariates)")
        robust = a.get("robust_se", "HC3"); fit = sm.OLS(y2, X2).fit(cov_type="HC3" if robust == "HC3" else "nonrobust")
        target = "group_b_vs_a"; ci = fit.conf_int(alpha=1 - level).loc[target]; p = _finite_or_error(fit.pvalues[target], "p_value", aid); diag = _ols_diagnostics(fit, X2)
        r.update(
            n=int(fit.nobs), group_a=ga, group_b=gb,
            group_a_json=json.dumps(jsonable_level(ga)), group_b_json=json.dumps(jsonable_level(gb)),
            estimate=float(fit.params[target]), estimate_name="covariate_adjusted_mean_difference_b_minus_a", null_value=0.0,
            ci_low=float(ci.iloc[0]), ci_high=float(ci.iloc[1]), ci_level=level, ci_method="ANCOVA_OLS_HC3" if robust == "HC3" else "ANCOVA_OLS",
            effect_size=float(fit.params[target]), effect_size_name="adjusted_mean_difference_b_minus_a", statistic=float(fit.tvalues[target]), p_value=p, df=float(fit.df_resid),
            r_squared=float(fit.rsquared), adjusted_r_squared=float(fit.rsquared_adj), covariates=";".join(a["covariates"]), robust_se=robust,
            model_coefficients_json=_coeff_json(fit, level),
            estimand_note="Two-group covariate-adjusted conditional mean difference under an additive linear model with common covariate slopes; interactions/nonlinearity require a broader model.",
            **diag,
        )
        _stamp_missingness(r, candidate, int(fit.nobs), "rows", missing_strategy)

    elif typ == "logistic_regression":
        cols = [a["outcome"]] + list(a["predictors"]); _require_columns(df, cols, aid)
        candidate = len(df); sub = df[cols].copy(); outcome = sub[a["outcome"]]
        event_level = a["event_level"]
        nonevent_level = a["nonevent_level"]
        observed = outcome.dropna().unique().tolist()
        extra = [v for v in observed if not (_level_equal(v, event_level) or _level_equal(v, nonevent_level))]
        if extra:
            raise ValueError(f"{aid}: outcome contains levels outside declared event/nonevent levels: {extra}")
        def _encode_binary(v):
            if pd.isna(v):
                return np.nan
            if _level_equal(v, event_level):
                return 1.0
            if _level_equal(v, nonevent_level):
                return 0.0
            return np.nan
        y = outcome.map(_encode_binary)
        X = sub[a["predictors"]].copy()
        for c in X.columns: X[c] = pd.to_numeric(X[c], errors="coerce")
        z = pd.concat([y.rename("__y"), X], axis=1).dropna()
        if z["__y"].nunique() != 2:
            raise ValueError(f"{aid}: logistic regression requires both event and non-event outcomes after complete-case filtering")
        if len(z) <= len(a["predictors"]) + 2:
            raise ValueError(f"{aid}: insufficient complete rows for logistic regression relative to predictor count")
        y2 = z.pop("__y"); X2 = sm.add_constant(z, has_constant="add")
        if np.linalg.matrix_rank(X2.to_numpy(float)) < X2.shape[1]:
            raise ValueError(f"{aid}: logistic design matrix is rank-deficient (constant/collinear predictors)")
        robust = a.get("robust_se", "HC0")
        try:
            with warnings.catch_warnings(record=True) as caught:
                warnings.simplefilter("always")
                fit = sm.GLM(y2, X2, family=sm.families.Binomial()).fit(cov_type="HC0" if robust == "HC0" else "nonrobust")
            if any(issubclass(w.category, PerfectSeparationWarning) or "perfect separation" in str(w.message).lower() for w in caught):
                raise ValueError(f"{aid}: logistic regression shows perfect separation/prediction; use a separation-aware specialist workflow rather than ordinary MLE logistic regression")
        except ValueError:
            raise
        except Exception as e:
            raise ValueError(f"{aid}: logistic regression failed to fit (possible separation/non-identifiability): {e}") from e
        if not bool(getattr(fit, "converged", True)):
            raise ValueError(f"{aid}: logistic regression did not converge")
        target = a.get("report_predictor") or a["predictors"][0]
        if target not in fit.params.index: raise ValueError(f"{aid}: report_predictor {target} not in fitted model")
        beta = _finite_or_error(fit.params[target], "log_odds_coefficient", aid); ci_beta = fit.conf_int(alpha=1-level).loc[target]
        or_est = float(math.exp(beta)); lo = float(math.exp(float(ci_beta.iloc[0]))); hi = float(math.exp(float(ci_beta.iloc[1]))); p = _finite_or_error(fit.pvalues[target], "p_value", aid)
        cond = float(np.linalg.cond(X2.to_numpy(float)))
        r.update(
            n=int(fit.nobs), estimate=or_est, estimate_name=f"odds_ratio_per_unit:{target}", null_value=1.0,
            ci_low=lo, ci_high=hi, ci_level=level, ci_method="logit_HC0_Wald" if robust == "HC0" else "logit_Wald",
            effect_size=or_est, effect_size_name=f"odds_ratio:{target}", statistic=float(fit.tvalues[target]), p_value=p,
            log_odds_coefficient=beta, model_predictors=";".join(a["predictors"]), report_predictor=target, robust_se=robust,
            event_level=jsonable_level(a["event_level"]), nonevent_level=jsonable_level(a["nonevent_level"]),
            event_level_json=json.dumps(jsonable_level(a["event_level"])), nonevent_level_json=json.dumps(jsonable_level(a["nonevent_level"])),
            event_orientation=(lambda labels: f"odds({labels[0]}) / odds({labels[1]})")(level_display_labels([a["event_level"], a["nonevent_level"]])),
            model_converged=bool(getattr(fit, "converged", True)), condition_number=cond, model_coefficients_json=_coeff_json(fit, level, exp_label="odds_ratio"),
            estimand_note="Odds ratio for a one-unit increase in the reported numeric predictor, conditional on the other declared numeric predictors.",
        )
        _stamp_missingness(r, candidate, int(fit.nobs), "rows", missing_strategy)

    elif typ == "welch_anova":
        y, g = a["outcome"], a["group"]
        levels = list(a["group_levels"])
        _require_columns(df, [y, g], aid)
        target = categorical_levels_mask(df[g], levels)
        candidate = int(target.sum())
        outside_declared = int((df[g].notna() & ~target).sum())
        arrays = []
        means = []
        variances = []
        ns = []
        for lv in levels:
            arr = _nonnull_numeric(df.loc[categorical_level_mask(df[g], lv), y])
            if len(arr) < 2:
                raise ValueError(f"{aid}: Welch ANOVA requires at least two complete numeric observations in every declared group; {lv!r} has {len(arr)}")
            var = float(np.var(arr, ddof=1))
            if not np.isfinite(var) or var <= 0:
                raise ValueError(f"{aid}: Welch ANOVA is not estimable because declared group {lv!r} has zero/non-finite variance")
            arrays.append(arr); means.append(float(np.mean(arr))); variances.append(var); ns.append(len(arr))
        test = anova_oneway(arrays, use_var="unequal", welch_correction=True)
        p = _finite_or_error(test.pvalue, "p_value", aid)
        f2 = float(effectsize_oneway(np.asarray(means), np.asarray(variances), np.asarray(ns), use_var="unequal"))
        f_effect = math.sqrt(max(0.0, f2))
        def _welch_f_effect(*samples):
            mm = np.asarray([np.mean(x) for x in samples], float)
            vv = np.asarray([np.var(x, ddof=1) for x in samples], float)
            nn = np.asarray([len(x) for x in samples], float)
            if np.any(~np.isfinite(vv)) or np.any(vv <= 0):
                return np.nan
            val = effectsize_oneway(mm, vv, nn, use_var="unequal")
            return math.sqrt(max(0.0, float(val))) if np.isfinite(val) else np.nan
        lo, hi = bootstrap_ci(_welch_f_effect, arrays, confidence_level=level, seed=seed, n_resamples=n_resamples)
        vr = float(max(variances) / min(variances))
        r.update(
            n=int(sum(ns)), n_groups=len(levels),
            estimate=f_effect, estimate_name="Cohen_f_Welch", null_value=0.0,
            ci_low=lo, ci_high=hi, ci_level=level, ci_method="stratified_percentile_bootstrap_Cohen_f",
            effect_size=f_effect, effect_size_name="Cohen_f_Welch",
            statistic=float(test.statistic), p_value=p, df_num=float(test.df_num), df_denom=float(test.df_denom),
            group_levels_json=json.dumps([jsonable_level(x) for x in levels]), group_ns_json=json.dumps(ns),
            group_means_json=json.dumps(means), group_sds_json=json.dumps([math.sqrt(v) for v in variances]),
            variance_ratio_max_to_min=vr, welch_correction=True, n_rows_outside_declared_groups=outside_declared,
            estimand_note="Welch omnibus test of equality of declared group means under heteroscedasticity. Cohen's f is the statsmodels Welch-compatible omnibus effect size; its bootstrap interval resamples within each declared group. The omnibus test is non-directional; prespecified pairwise follow-ups should be separate analysis items with declared multiplicity handling.",
        )
        _stamp_missingness(r, candidate, int(sum(ns)), "rows", missing_strategy)

    elif typ == "welch_contrast":
        y, g = a["outcome"], a["group"]
        terms = list(a["contrast_terms"])
        levels = [t["level"] for t in terms]
        weights = np.asarray([float(t["weight"]) for t in terms], float)
        _require_columns(df, [y, g], aid)
        target = categorical_levels_mask(df[g], levels)
        candidate = int(target.sum())
        outside_declared = int((df[g].notna() & ~target).sum())
        arrays, means, variances, ns = [], [], [], []
        for lv in levels:
            arr = _nonnull_numeric(df.loc[categorical_level_mask(df[g], lv), y])
            if len(arr) < 2:
                raise ValueError(f"{aid}: Welch contrast requires at least two complete numeric observations in every declared contrast group; {lv!r} has {len(arr)}")
            var = float(np.var(arr, ddof=1))
            if not np.isfinite(var) or var < 0:
                raise ValueError(f"{aid}: Welch contrast group {lv!r} has non-finite variance")
            arrays.append(arr); means.append(float(np.mean(arr))); variances.append(var); ns.append(len(arr))
        means_a = np.asarray(means, float)
        vars_a = np.asarray(variances, float)
        ns_a = np.asarray(ns, float)
        est = float(np.sum(weights * means_a))
        components = (weights ** 2) * vars_a / ns_a
        se2 = float(np.sum(components))
        denom = float(np.sum((components ** 2) / (ns_a - 1)))
        if not np.isfinite(se2) or se2 <= 0 or not np.isfinite(denom) or denom <= 0:
            raise ValueError(f"{aid}: Welch contrast is not estimable because the weighted sampling variance is zero/degenerate")
        se = math.sqrt(se2)
        dfw = (se2 ** 2) / denom
        stat = est / se
        p = _finite_or_error(2 * stats.t.sf(abs(stat), dfw), "p_value", aid)
        lo, hi = tcrit_ci(est, se, dfw, level)
        display_levels = level_display_labels(levels)
        positive = [(display_levels[i], float(weights[i])) for i in range(len(levels)) if weights[i] > 0]
        negative = [(display_levels[i], float(weights[i])) for i in range(len(levels)) if weights[i] < 0]
        orientation = " + ".join(f"{w:g}*mean({lv})" for lv, w in positive) + " versus " + " + ".join(f"{abs(w):g}*mean({lv})" for lv, w in negative)
        r.update(
            n=int(sum(ns)), n_groups=len(levels),
            estimate=est, estimate_name="planned_weighted_mean_contrast", null_value=0.0,
            ci_low=lo, ci_high=hi, ci_level=level, ci_method="Welch_Satterthwaite_contrast_t",
            effect_size=est, effect_size_name="raw_scale_planned_contrast",
            statistic=float(stat), p_value=p, df=float(dfw), standard_error=float(se),
            group_levels_json=json.dumps([jsonable_level(x) for x in levels]), group_ns_json=json.dumps(ns),
            group_means_json=json.dumps(means), group_sds_json=json.dumps([math.sqrt(v) for v in variances]),
            contrast_terms_json=json.dumps([{"level": jsonable_level(t["level"]), "weight": float(t["weight"])} for t in terms]),
            contrast_weight_sum=float(np.sum(weights)), contrast_l1_norm=float(np.sum(np.abs(weights))),
            contrast_orientation=orientation, n_rows_outside_declared_groups=outside_declared,
            estimand_note="Prespecified linear contrast of independent group means using a Welch-Satterthwaite standard error and degrees of freedom under heteroscedasticity. Weights are used exactly as declared and are not normalized; rescaling all weights rescales the raw effect and CI but leaves the t statistic and p-value unchanged. This is a directional scientific contrast, not an automatically selected post-hoc comparison.",
        )
        _stamp_missingness(r, candidate, int(sum(ns)), "rows", missing_strategy)

    elif typ == "poisson_regression":
        cols = [a["outcome"]] + list(a["predictors"])
        if a.get("exposure"):
            cols.append(a["exposure"])
        if a.get("offset"):
            cols.append(a["offset"])
        _require_columns(df, cols, aid)
        candidate = len(df)
        sub = df[cols].copy()
        y = pd.to_numeric(sub[a["outcome"]], errors="coerce")
        X = sub[a["predictors"]].copy()
        for c in X.columns:
            X[c] = pd.to_numeric(X[c], errors="coerce")
        pieces = [y.rename("__y"), X]
        offset_mode = "none"
        if a.get("exposure"):
            expv = pd.to_numeric(sub[a["exposure"]], errors="coerce")
            pieces.append(expv.rename("__exposure")); offset_mode = f"log_exposure:{a['exposure']}"
        elif a.get("offset"):
            offv = pd.to_numeric(sub[a["offset"]], errors="coerce")
            pieces.append(offv.rename("__offset")); offset_mode = f"offset:{a['offset']}"
        z = pd.concat(pieces, axis=1).dropna()
        if len(z) <= len(a["predictors"]) + 2:
            raise ValueError(f"{aid}: insufficient complete rows for Poisson regression relative to predictor count")
        y2 = z.pop("__y")
        if (y2 < 0).any() or not np.allclose(y2.to_numpy(float), np.round(y2.to_numpy(float)), atol=1e-8):
            raise ValueError(f"{aid}: Poisson outcome must contain nonnegative integer counts after complete-case filtering")
        if float(y2.sum()) <= 0 or y2.nunique() < 2:
            raise ValueError(f"{aid}: Poisson regression requires a non-degenerate count outcome with at least one positive count")
        offset_arr = None
        if "__exposure" in z.columns:
            expv = z.pop("__exposure")
            if (expv <= 0).any():
                raise ValueError(f"{aid}: exposure values must be strictly positive before log transformation")
            offset_arr = np.log(expv.to_numpy(float))
        elif "__offset" in z.columns:
            offset_arr = z.pop("__offset").to_numpy(float)
        X2 = sm.add_constant(z, has_constant="add")
        if np.linalg.matrix_rank(X2.to_numpy(float)) < X2.shape[1]:
            raise ValueError(f"{aid}: Poisson design matrix is rank-deficient (constant/collinear predictors)")
        robust = a.get("robust_se", "HC0")
        try:
            fit = sm.GLM(y2, X2, family=sm.families.Poisson(), offset=offset_arr).fit(cov_type="HC0" if robust == "HC0" else "nonrobust")
        except Exception as e:
            raise ValueError(f"{aid}: Poisson regression failed to fit: {e}") from e
        if not bool(getattr(fit, "converged", True)):
            raise ValueError(f"{aid}: Poisson regression did not converge")
        target = a.get("report_predictor") or a["predictors"][0]
        if target not in fit.params.index:
            raise ValueError(f"{aid}: report_predictor {target} not in fitted model")
        beta = _finite_or_error(fit.params[target], "log_rate_coefficient", aid)
        ci_beta = fit.conf_int(alpha=1-level).loc[target]
        irr = float(math.exp(beta)); lo = float(math.exp(float(ci_beta.iloc[0]))); hi = float(math.exp(float(ci_beta.iloc[1])))
        p = _finite_or_error(fit.pvalues[target], "p_value", aid)
        cond = float(np.linalg.cond(X2.to_numpy(float)))
        pearson_disp = float(fit.pearson_chi2 / fit.df_resid) if fit.df_resid > 0 else None
        deviance_disp = float(fit.deviance / fit.df_resid) if fit.df_resid > 0 else None
        zero_fraction = float((y2 == 0).mean())
        r.update(
            n=int(fit.nobs), estimate=irr, estimate_name=f"incidence_rate_ratio_per_unit:{target}", null_value=1.0,
            ci_low=lo, ci_high=hi, ci_level=level, ci_method="Poisson_log_HC0_Wald" if robust == "HC0" else "Poisson_log_Wald",
            effect_size=irr, effect_size_name=f"incidence_rate_ratio:{target}", statistic=float(fit.tvalues[target]), p_value=p,
            log_rate_coefficient=beta, model_predictors=";".join(a["predictors"]), report_predictor=target, robust_se=robust,
            model_converged=bool(getattr(fit, "converged", True)), condition_number=cond,
            pearson_dispersion_ratio=pearson_disp, deviance_dispersion_ratio=deviance_disp, zero_fraction=zero_fraction,
            offset_mode=offset_mode, total_count=int(round(float(y2.sum()))), model_coefficients_json=_coeff_json(fit, level, exp_label="incidence_rate_ratio"),
            estimand_note="Incidence-rate ratio for a one-unit increase in the reported numeric predictor, conditional on the other declared numeric predictors. If exposure is declared, its log is used as an offset. Overdispersion/zero inflation diagnostics must be reviewed; negative-binomial or other count models remain specialist handoffs when Poisson assumptions are strained.",
        )
        _stamp_missingness(r, candidate, int(fit.nobs), "rows", missing_strategy)

    elif typ in {"chi_square", "fisher_exact"}:
        _require_columns(df, [a["row"], a["column"]], aid)
        candidate = len(df); pair_df = df[[a["row"], a["column"]]].dropna().copy()
        if len(pair_df) == 0: raise ValueError(f"{aid}: no complete categorical rows")
        # pandas crosstab/grouping follows Python equality and can silently merge
        # scientifically distinct typed encodings such as True and 1 before later
        # metadata checks run. Reject such inputs at the contingency-table boundary.
        assert_no_equality_colliding_levels(pair_df[a["row"]], label=f"{aid}: row variable")
        assert_no_equality_colliding_levels(pair_df[a["column"]], label=f"{aid}: column variable")
        tab = pd.crosstab(pair_df[a["row"]], pair_df[a["column"]])
        if typ == "fisher_exact":
            if a.get("row_levels") is not None:
                missing = [x for x in a["row_levels"] if x not in tab.index]
                if missing: raise ValueError(f"{aid}: declared row_levels absent from data: {missing}")
                tab = tab.reindex(index=a["row_levels"], fill_value=0)
            if a.get("column_levels") is not None:
                missing = [x for x in a["column_levels"] if x not in tab.columns]
                if missing: raise ValueError(f"{aid}: declared column_levels absent from data: {missing}")
                tab = tab.reindex(columns=a["column_levels"], fill_value=0)
            if tab.shape != (2, 2): raise ValueError(f"{aid}: fisher_exact requires a 2x2 table after any declared level ordering; got {tab.shape}")
            row_levels_native = [jsonable_level(x) for x in tab.index.tolist()]; col_levels_native = [jsonable_level(x) for x in tab.columns.tolist()]
            row_levels = row_levels_native; col_levels = col_levels_native
            raw_or, fisher_p = _fisher_exact_two_sided_2x2(tab.to_numpy(dtype=int)); p = _finite_or_error(fisher_p, "p_value", aid)
            cells = tab.to_numpy(dtype=float); zero_cell = bool(np.any(cells == 0)); cc = 0.5 if zero_cell else 0.0; a1, b1, c1, d1 = (cells + cc).ravel()
            orr = float((a1 * d1) / (b1 * c1))
            logor = math.log(orr); se = math.sqrt(1 / a1 + 1 / b1 + 1 / c1 + 1 / d1); zq = stats.norm.ppf((1 + level) / 2)
            lo, hi = math.exp(logor - zq * se), math.exp(logor + zq * se)
            row_display = level_display_labels(row_levels)
            col_display = level_display_labels(col_levels)
            orientation = f"odds({col_display[0]}/{col_display[1]} | {row_display[0]}) / odds({col_display[0]}/{col_display[1]} | {row_display[1]})"
            estimate_name = "odds_ratio_haldane_anscombe" if zero_cell else "odds_ratio"
            ci_method = "Woolf_log_OR_Haldane_Anscombe_0.5" if zero_cell else "Woolf_log_OR"
            raw_or_finite = raw_or if raw_or is not None and np.isfinite(raw_or) else None
            r.update(
                n=int(cells.sum()), estimate=orr, estimate_name=estimate_name, null_value=1.0,
                ci_low=lo, ci_high=hi, ci_level=level, ci_method=ci_method, effect_size=orr, effect_size_name=estimate_name,
                statistic=raw_or_finite, p_value=p, table_shape="2x2", row_levels_json=json.dumps(row_levels), column_levels_json=json.dumps(col_levels),
                odds_ratio_orientation=orientation, table_counts_json=json.dumps(cells.astype(int).tolist()),
                zero_cell_correction_applied=zero_cell, zero_cell_correction=cc,
                fisher_raw_sample_odds_ratio=raw_or_finite, fisher_raw_sample_odds_ratio_nonfinite=bool(raw_or is not None and not np.isfinite(raw_or)),
                odds_ratio_estimation_method="Haldane-Anscombe 0.5 correction" if zero_cell else "sample cross-product odds ratio",
                estimand_note=(
                    "Fisher exact p-value is computed from the uncorrected 2x2 table. Because at least one cell is zero, the reported finite odds-ratio estimate and Woolf interval use a declared Haldane-Anscombe 0.5 correction."
                    if zero_cell else
                    "Fisher exact p-value is computed from the 2x2 table; the reported sample odds ratio and Woolf interval use the same uncorrected cell counts."
                ),
            )
        else:
            if tab.shape[0] < 2 or tab.shape[1] < 2: raise ValueError(f"{aid}: chi_square requires at least a 2x2 contingency table")
            # Use the uncorrected Pearson chi-square definition consistently for
            # both inference and Cramer's V. SciPy otherwise applies Yates'
            # continuity correction by default for 2x2 tables, which would make
            # the point statistic/effect size inconsistent with the bootstrap
            # interval below (computed from uncorrected Pearson chi-square).
            chi2, p, dof, expected = stats.chi2_contingency(tab.to_numpy(), correction=False); p = _finite_or_error(p, "p_value", aid); n = tab.to_numpy().sum(); k = min(tab.shape) - 1; v = math.sqrt(chi2 / (n * k)) if k > 0 and n > 0 else None
            row_levels = [jsonable_level(x) for x in tab.index.tolist()]; col_levels = [jsonable_level(x) for x in tab.columns.tolist()]
            rc, row_map = _categorical_codes(pair_df[a["row"]], tab.index.tolist(), aid, "row variable")
            ccodes, col_map = _categorical_codes(pair_df[a["column"]], tab.columns.tolist(), aid, "column variable")
            nr, nc = len(row_map), len(col_map)
            def _cv_idx(idx):
                flat = np.bincount(rc[idx] * nc + ccodes[idx], minlength=nr * nc); t = flat.reshape(nr, nc)
                if np.any(t.sum(axis=0) == 0) or np.any(t.sum(axis=1) == 0): return np.nan
                try:
                    c = stats.chi2_contingency(t, correction=False)[0]; nn = t.sum(); kk = min(t.shape) - 1
                    return math.sqrt(c / (nn * kk)) if nn > 0 and kk > 0 else np.nan
                except Exception: return np.nan
            rng = np.random.default_rng(seed); boots = []
            for _ in range(n_resamples):
                idx = rng.integers(0, len(rc), size=len(rc)); vv = _cv_idx(idx)
                if np.isfinite(vv): boots.append(vv)
            if len(boots) >= max(100, n_resamples // 20):
                alpha = 1 - level; lo = float(np.quantile(boots, alpha / 2)); hi = float(np.quantile(boots, 1 - alpha / 2)); cim = "row_bootstrap_percentile"
            else: lo = hi = None; cim = "not_estimable"
            exp = np.asarray(expected, float); lt5 = int((exp < 5).sum()); lt1 = int((exp < 1).sum())
            r.update(n=int(n), estimate=v, estimate_name="Cramers_V", null_value=0.0, ci_low=lo, ci_high=hi, ci_level=level, ci_method=cim, effect_size=v, effect_size_name="Cramers_V", statistic=float(chi2), p_value=p, df=int(dof), min_expected=float(np.min(expected)), expected_lt5_count=lt5, expected_lt5_fraction=float(lt5/exp.size), expected_lt1_count=lt1, table_shape=f"{tab.shape[0]}x{tab.shape[1]}", row_levels_json=json.dumps(row_levels), column_levels_json=json.dumps(col_levels), table_counts_json=json.dumps(tab.to_numpy(dtype=int).tolist()), chi_square_correction="none", estimand_note="Pearson chi-square and Cramer's V use the same uncorrected contingency-table definition; sparse tables require diagnostic review or Fisher/exact/specialist alternatives as appropriate.")
        _stamp_missingness(r, candidate, len(pair_df), "rows", missing_strategy)

    else:
        raise ValueError(f"Unsupported analysis type: {typ}")

    if "p_value" in r and (r["p_value"] is None or not np.isfinite(float(r["p_value"]))):
        raise ValueError(f"{aid}: p_value is not finite")
    return r


def apply_multiplicity(results, plan):
    byfam = {}
    for i, r in enumerate(results):
        fam = r.get("multiplicity_family")
        if fam: byfam.setdefault(fam, []).append(i)
    for fam, idxs in byfam.items():
        spec = plan.get("multiplicity", {}).get(fam, {"method": "none"}); method = spec.get("method", "none"); ps = np.array([results[i]["p_value"] for i in idxs], float)
        if not np.all(np.isfinite(ps)): raise ValueError(f"Multiplicity family {fam} contains non-finite p-values")
        if method == "none": adj = ps
        else: adj = multipletests(ps, method={"holm": "holm", "bonferroni": "bonferroni", "fdr_bh": "fdr_bh"}[method])[1]
        for i, padj in zip(idxs, adj): results[i]["p_adjust_method"] = method; results[i]["p_adjusted"] = float(padj)
    for r in results:
        if "p_adjusted" not in r: r["p_adjust_method"] = "none"; r["p_adjusted"] = r.get("p_value")


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--data", required=True); ap.add_argument("--plan", required=True); ap.add_argument("--out-csv", required=True); ap.add_argument("--out-json", required=True); args = ap.parse_args()
    df = read_table(args.data); plan = read_json(args.plan); errors, warnings = validate(plan)
    if errors: raise ValueError("Invalid analysis plan: " + "; ".join(errors))
    for w in warnings: print(f"WARNING: {w}")
    level = float(plan.get("confidence_level", 0.95)); base_seed = int(plan.get("random_seed", 0)); n_resamples = int(plan.get("resampling", {}).get("n_resamples", 2000)); missing_strategy = plan.get("missing_data", {}).get("strategy", "complete_case")
    data_hash = sha256_file(args.data); plan_hash = sha256_file(args.plan)
    results = [run_item(df, a, level, stable_seed(base_seed, a["analysis_item_id"]), n_resamples=n_resamples, missing_strategy=missing_strategy) for a in plan["analyses"]]
    apply_multiplicity(results, plan)
    for r in results:
        r["data_sha256"] = data_hash; r["plan_sha256"] = plan_hash; r["skill_version"] = SKILL_VERSION
    rdf = pd.DataFrame(results); Path(args.out_csv).parent.mkdir(parents=True, exist_ok=True); rdf.to_csv(args.out_csv, index=False)
    write_json({"skill_version": SKILL_VERSION, "analysis_plan_schema_version": plan.get("analysis_plan_schema_version"), "analysis_id": plan.get("analysis_id"), "confidence_level": level, "missing_data": plan.get("missing_data"), "resampling": plan.get("resampling"), "data_sha256": data_hash, "plan_sha256": plan_hash, "results": results}, args.out_json)
    print(f"Wrote {len(results)} results")


if __name__ == "__main__": main()
