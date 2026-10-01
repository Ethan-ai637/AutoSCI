#!/usr/bin/env python3
from __future__ import annotations

import argparse
import math
import numpy as np
import pandas as pd
from statsmodels.stats.multitest import multipletests

from _common import read_json, read_table, read_artifact_csv, sha256_file, write_json, SKILL_VERSION, stable_seed, jsonable_level
from run_stats import run_item, apply_multiplicity
from run_sensitivity import compute_sensitivity_rows
from validate_plan import validate

EFFECT_REQUIRED = {
    "independent_t", "paired_t", "mann_whitney", "wilcoxon", "pearson", "spearman",
    "linear_regression", "ancova_two_group", "logistic_regression", "poisson_regression", "welch_anova", "welch_contrast", "chi_square", "fisher_exact",
    "equivalence_tost_independent", "equivalence_tost_paired",
}


def _unique_nonnull(series):
    return {str(x) for x in series.dropna().unique()}


def _truthy(v):
    if isinstance(v, bool):
        return v
    return str(v).strip().lower() in {"true", "1", "yes"}




def _values_match(actual, expected, *, rtol=1e-10, atol=1e-12):
    """Compare a CSV-roundtripped value with a freshly recomputed value."""
    if expected is None:
        return pd.isna(actual)
    try:
        if pd.isna(expected):
            return pd.isna(actual)
    except Exception:
        pass
    if isinstance(expected, str) and expected == "" and pd.isna(actual):
        # Empty CSV fields round-trip through pandas as NaN by default.
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


def recompute_result_rows(data, plan, data_hash, plan_hash):
    """Return the current deterministic base-analysis rows for data + plan."""
    base_seed = int(plan.get("random_seed", 0))
    level = float(plan.get("confidence_level", 0.95))
    n_resamples = int(plan.get("resampling", {}).get("n_resamples", 2000))
    missing_strategy = plan.get("missing_data", {}).get("strategy", "complete_case")
    expected_rows = [
        run_item(
            data, a, level, stable_seed(base_seed, a["analysis_item_id"]),
            n_resamples=n_resamples, missing_strategy=missing_strategy,
        )
        for a in plan.get("analyses", [])
    ]
    apply_multiplicity(expected_rows, plan)
    for rr in expected_rows:
        rr["data_sha256"] = data_hash
        rr["plan_sha256"] = plan_hash
        rr["skill_version"] = SKILL_VERSION
    return expected_rows


def reconcile_results_against_current_run(data, plan, actual_results, data_hash, plan_hash, expected_rows=None):
    """Recompute deterministic inference from current data+plan and compare every generated field."""
    if expected_rows is None:
        expected_rows = recompute_result_rows(data, plan, data_hash, plan_hash)

    if "analysis_item_id" not in actual_results.columns:
        return ["results.csv is missing analysis_item_id; deterministic result reconciliation cannot run"]
    if actual_results["analysis_item_id"].astype(str).duplicated().any():
        return ["results.csv contains duplicate analysis_item_id rows; deterministic result reconciliation cannot run"]

    actual_by_id = {str(r["analysis_item_id"]): r for _, r in actual_results.iterrows()}
    mismatches = []
    for exp in expected_rows:
        aid = str(exp["analysis_item_id"])
        act = actual_by_id.get(aid)
        if act is None:
            mismatches.append(f"{aid}: missing result row during deterministic reconciliation")
            continue
        for field, ev in exp.items():
            if field not in actual_results.columns:
                mismatches.append(f"{aid}: results.csv missing recomputable field {field}")
                continue
            av = act.get(field)
            if not _values_match(av, ev):
                mismatches.append(f"{aid}: deterministic reconciliation mismatch for {field} (artifact={av!r}, recomputed={ev!r})")
            if len(mismatches) >= 25:
                mismatches.append("deterministic reconciliation stopped after 25 mismatches")
                return mismatches
    return mismatches


def reconcile_sensitivity_against_current_run(data, plan, actual_sensitivity, data_hash, plan_hash, base_rows=None):
    """Recompute every declared sensitivity analysis and compare generated fields."""
    if "sensitivity_id" not in actual_sensitivity.columns:
        return ["sensitivity results are missing sensitivity_id; deterministic sensitivity reconciliation cannot run"]
    if actual_sensitivity["sensitivity_id"].astype(str).duplicated().any():
        return ["sensitivity results contain duplicate sensitivity_id rows; deterministic sensitivity reconciliation cannot run"]

    if base_rows is None:
        base_rows = recompute_result_rows(data, plan, data_hash, plan_hash)
    base_df = pd.DataFrame(base_rows)
    expected_rows = compute_sensitivity_rows(
        data, plan, base_df, data_hash=data_hash, plan_hash=plan_hash,
    )
    actual_by_id = {str(r["sensitivity_id"]): r for _, r in actual_sensitivity.iterrows()}
    mismatches = []
    for exp in expected_rows:
        sid = str(exp["sensitivity_id"])
        act = actual_by_id.get(sid)
        if act is None:
            mismatches.append(f"{sid}: missing sensitivity row during deterministic reconciliation")
            continue
        for field, ev in exp.items():
            if field not in actual_sensitivity.columns:
                mismatches.append(f"{sid}: sensitivity results missing recomputable field {field}")
                continue
            av = act.get(field)
            if not _values_match(av, ev):
                mismatches.append(f"{sid}: deterministic sensitivity reconciliation mismatch for {field} (artifact={av!r}, recomputed={ev!r})")
            if len(mismatches) >= 25:
                mismatches.append("deterministic sensitivity reconciliation stopped after 25 mismatches")
                return mismatches
    return mismatches


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--plan", required=True)
    ap.add_argument("--data", required=True)
    ap.add_argument("--results", required=True)
    ap.add_argument("--cleaning-log", required=True)
    ap.add_argument("--cleaning-report")
    ap.add_argument("--sensitivity-results")
    ap.add_argument("--report", required=True)
    args = ap.parse_args()

    plan = read_json(args.plan)
    data = read_table(args.data)
    res = read_artifact_csv(args.results)
    clog = pd.read_csv(args.cleaning_log)
    errors, warnings = validate(plan)
    plan_hash = sha256_file(args.plan)
    data_hash = sha256_file(args.data)

    planned = {a["analysis_item_id"]: a for a in plan.get("analyses", [])}
    expected = set(planned)
    if "analysis_item_id" not in res.columns:
        errors.append("results.csv is missing analysis_item_id")
        got = set()
        duplicate_result_ids = set()
    else:
        result_ids = res["analysis_item_id"].astype(str)
        got = set(result_ids)
        duplicate_result_ids = set(result_ids[result_ids.duplicated(keep=False)].tolist())
        if duplicate_result_ids:
            errors.append(f"results.csv contains duplicate analysis_item_id rows: {sorted(duplicate_result_ids)}")
    if got != expected:
        errors.append(f"Result IDs mismatch. missing={sorted(expected-got)} extra={sorted(got-expected)}")

    if "_row_id" not in data.columns:
        warnings.append("analysis-ready data has no _row_id; source-row traceability may be reduced")
    accidental = [c for c in data.columns if str(c).startswith("Unnamed:")]
    if accidental:
        errors.append(f"Accidental index-like columns present: {accidental}")

    if "data_sha256" not in res.columns or _unique_nonnull(res["data_sha256"]) != {data_hash}:
        errors.append("results.csv data_sha256 does not uniquely match the current analysis-ready data")
    if "plan_sha256" not in res.columns or _unique_nonnull(res["plan_sha256"]) != {plan_hash}:
        errors.append("results.csv plan_sha256 does not uniquely match the current analysis plan")
    if "skill_version" not in res.columns or _unique_nonnull(res["skill_version"]) != {SKILL_VERSION}:
        errors.append(f"results.csv skill_version does not uniquely match current skill version {SKILL_VERSION}; rerun inference with the current release")
    if "missing_data_strategy" not in res.columns or _unique_nonnull(res["missing_data_strategy"]) != {plan.get("missing_data", {}).get("strategy")}:
        errors.append("results.csv missing_data_strategy does not match the analysis plan")
    expected_resamples = str(plan.get("resampling", {}).get("n_resamples"))
    if "resampling_n_resamples" not in res.columns or _unique_nonnull(res["resampling_n_resamples"].astype(str)) != {expected_resamples}:
        errors.append("results.csv resampling_n_resamples does not match the analysis plan")

    for _, r in res.iterrows():
        aid = r.get("analysis_item_id")
        typ = planned.get(aid, {}).get("type")
        for col in ["p_value", "p_adjusted"]:
            if col in r and pd.notna(r[col]) and not (0 <= float(r[col]) <= 1):
                errors.append(f"{aid}: {col} outside [0,1]")
        if pd.notna(r.get("ci_low")) and pd.notna(r.get("ci_high")) and float(r["ci_low"]) > float(r["ci_high"]):
            errors.append(f"{aid}: ci_low > ci_high")
        if typ in EFFECT_REQUIRED and ("effect_size" not in r or pd.isna(r.get("effect_size"))):
            warnings.append(f"{aid}: effect_size missing/not estimable")
        for c in ["estimate", "effect_size", "statistic"]:
            if c in r.index and pd.notna(r.get(c)):
                try:
                    if not pd.api.types.is_number(r.get(c)) and not isinstance(r.get(c), (int, float)):
                        continue
                    if not __import__("math").isfinite(float(r.get(c))):
                        errors.append(f"{aid}: {c} is non-finite")
                except (TypeError, ValueError):
                    errors.append(f"{aid}: {c} is not a valid numeric value")

        for c in ["n_candidate_units", "n_analyzed_units", "n_missing_or_invalid_excluded"]:
            if c not in r.index or pd.isna(r.get(c)):
                errors.append(f"{aid}: missing required per-analysis missingness field {c}")
        if pd.notna(r.get("n_candidate_units")) and pd.notna(r.get("n_analyzed_units")) and float(r["n_analyzed_units"]) > float(r["n_candidate_units"]):
            errors.append(f"{aid}: analyzed units exceed candidate units")
        if pd.notna(r.get("n_missing_or_invalid_excluded")) and float(r["n_missing_or_invalid_excluded"]) < 0:
            errors.append(f"{aid}: negative missing/invalid exclusion count")

        ncols = [c for c in ["n", "n_a", "n_b", "n_pairs"] if c in r.index and pd.notna(r[c])]
        if ncols and any(float(r[c]) <= 0 for c in ncols):
            errors.append(f"{aid}: non-positive sample count")
        if "n" in r and pd.notna(r.get("n")) and float(r["n"]) > len(data):
            errors.append(f"{aid}: n exceeds analysis-ready row count")
        if typ in {"independent_t", "mann_whitney", "equivalence_tost_independent"} and pd.notna(r.get("n_a")) and pd.notna(r.get("n_b")):
            if float(r["n_a"]) + float(r["n_b"]) > len(data):
                errors.append(f"{aid}: n_a+n_b exceeds analysis-ready row count")

        if typ in {"linear_regression", "ancova_two_group", "logistic_regression", "poisson_regression"}:
            default_robust = "HC3" if typ in {"linear_regression", "ancova_two_group"} else "HC0"
            expected_robust = str(planned.get(aid, {}).get("robust_se", default_robust))
            if str(r.get("robust_se", "")) != expected_robust:
                errors.append(f"{aid}: robust_se metadata does not match the analysis plan")

        if typ == "chi_square":
            if str(r.get("chi_square_correction", "")).strip().lower() != "none":
                errors.append(f"{aid}: chi-square correction metadata missing or inconsistent; the current core requires uncorrected Pearson chi-square so the test statistic, Cramer's V, and bootstrap interval share one definition")
            if pd.notna(r.get("expected_lt1_count")) and int(float(r["expected_lt1_count"])) > 0:
                warnings.append(f"{aid}: at least one expected chi-square cell count is <1; asymptotic approximation is especially questionable")
            elif pd.notna(r.get("expected_lt5_fraction")) and float(r["expected_lt5_fraction"]) > 0.20:
                warnings.append(f"{aid}: >20% of expected chi-square cell counts are <5; approximation may be weak")
        if typ == "fisher_exact":
            if not str(r.get("odds_ratio_orientation", "")).strip():
                errors.append(f"{aid}: Fisher odds-ratio orientation is missing")
            corrected = _truthy(r.get("zero_cell_correction_applied", False))
            if corrected:
                if pd.isna(r.get("zero_cell_correction")) or float(r.get("zero_cell_correction")) <= 0:
                    errors.append(f"{aid}: Fisher zero-cell correction flag is set but correction magnitude is missing/invalid")
                warnings.append(f"{aid}: zero cell detected; finite odds-ratio estimate/CI use the declared Haldane-Anscombe correction while the Fisher p-value remains exact on the uncorrected table")
        if typ == "logistic_regression":
            if not _truthy(r.get("model_converged", False)):
                errors.append(f"{aid}: logistic model did not converge")
            if not str(r.get("event_orientation", "")).strip():
                errors.append(f"{aid}: logistic event orientation missing")

        if typ == "welch_anova":
            declared_levels = [jsonable_level(x) for x in planned.get(aid, {}).get("group_levels", [])]
            if pd.isna(r.get("n_groups")) or int(float(r.get("n_groups"))) < 3:
                errors.append(f"{aid}: Welch ANOVA must report at least three analyzed groups")
            try:
                observed_levels = __import__("json").loads(str(r.get("group_levels_json")))
            except Exception:
                observed_levels = None
            if observed_levels != declared_levels:
                errors.append(f"{aid}: Welch group_levels metadata does not match the analysis plan")
            try:
                group_ns = __import__("json").loads(str(r.get("group_ns_json")))
            except Exception:
                group_ns = None
            if not isinstance(group_ns, list) or len(group_ns) != len(declared_levels) or any(float(x) < 2 for x in group_ns):
                errors.append(f"{aid}: Welch per-group analyzed sample sizes are missing/invalid")
            elif pd.notna(r.get("n")) and abs(sum(float(x) for x in group_ns) - float(r.get("n"))) > 1e-9:
                errors.append(f"{aid}: Welch group sample sizes do not reconcile with total n")
            if not _truthy(r.get("welch_correction", False)):
                errors.append(f"{aid}: Welch ANOVA correction metadata is missing/inconsistent")
            if pd.notna(r.get("variance_ratio_max_to_min")) and float(r.get("variance_ratio_max_to_min")) > 10:
                warnings.append(f"{aid}: group variance ratio exceeds 10; Welch handles heteroscedasticity, but inspect data quality, scale, and influential observations")
            if pd.notna(r.get("n_rows_outside_declared_groups")) and int(float(r.get("n_rows_outside_declared_groups"))) > 0:
                warnings.append(f"{aid}: analysis-ready data contain rows from group levels outside the prespecified Welch group_levels; they were not included in the omnibus candidate set")

        if typ == "welch_contrast":
            terms = planned.get(aid, {}).get("contrast_terms", [])
            declared_levels = [jsonable_level(t.get("level")) for t in terms]
            declared_terms = [{"level": jsonable_level(t.get("level")), "weight": float(t.get("weight"))} for t in terms]
            if pd.isna(r.get("n_groups")) or int(float(r.get("n_groups"))) < 2:
                errors.append(f"{aid}: Welch contrast must report at least two analyzed groups")
            try:
                observed_levels = __import__("json").loads(str(r.get("group_levels_json")))
            except Exception:
                observed_levels = None
            if observed_levels != declared_levels:
                errors.append(f"{aid}: Welch contrast group_levels metadata does not match the analysis plan")
            try:
                observed_terms = __import__("json").loads(str(r.get("contrast_terms_json")))
            except Exception:
                observed_terms = None
            if observed_terms != declared_terms:
                errors.append(f"{aid}: Welch contrast weights metadata does not match the analysis plan")
            try:
                group_ns = __import__("json").loads(str(r.get("group_ns_json")))
            except Exception:
                group_ns = None
            if not isinstance(group_ns, list) or len(group_ns) != len(declared_levels) or any(float(x) < 2 for x in group_ns):
                errors.append(f"{aid}: Welch contrast per-group analyzed sample sizes are missing/invalid")
            elif pd.notna(r.get("n")) and abs(sum(float(x) for x in group_ns) - float(r.get("n"))) > 1e-9:
                errors.append(f"{aid}: Welch contrast group sample sizes do not reconcile with total n")
            if pd.isna(r.get("contrast_weight_sum")) or abs(float(r.get("contrast_weight_sum"))) > 1e-10 * max(1.0, sum(abs(float(t["weight"])) for t in terms)):
                errors.append(f"{aid}: Welch contrast weight sum metadata is missing/inconsistent")
            if pd.notna(r.get("n_rows_outside_declared_groups")) and int(float(r.get("n_rows_outside_declared_groups"))) > 0:
                warnings.append(f"{aid}: analysis-ready data contain rows from group levels outside the prespecified contrast; they were not included in the contrast candidate set")

        if typ == "poisson_regression":
            if not _truthy(r.get("model_converged", False)):
                errors.append(f"{aid}: Poisson model did not converge")
            expected_offset = "none"
            if planned.get(aid, {}).get("exposure"):
                expected_offset = f"log_exposure:{planned[aid]['exposure']}"
            elif planned.get(aid, {}).get("offset"):
                expected_offset = f"offset:{planned[aid]['offset']}"
            if str(r.get("offset_mode", "")) != expected_offset:
                errors.append(f"{aid}: Poisson offset/exposure metadata does not match the analysis plan")
            if pd.notna(r.get("pearson_dispersion_ratio")) and float(r.get("pearson_dispersion_ratio")) > 1.5:
                warnings.append(f"{aid}: Pearson dispersion ratio >1.5; Poisson variance assumptions may be strained—review negative-binomial/quasi-Poisson or other count-model alternatives")
            if pd.notna(r.get("zero_fraction")) and float(r.get("zero_fraction")) > 0.8:
                warnings.append(f"{aid}: >80% of analyzed counts are zero; inspect zero inflation/hurdle structure rather than assuming a standard Poisson model is adequate")

        if typ in {"linear_regression", "ancova_two_group", "logistic_regression", "poisson_regression"}:
            if pd.notna(r.get("condition_number")) and float(r["condition_number"]) > 30:
                warnings.append(f"{aid}: model condition number >30; inspect scaling/collinearity (heuristic diagnostic, not an automatic invalidation)")
        if typ in {"linear_regression", "ancova_two_group"}:
            nobs = float(r.get("n")) if pd.notna(r.get("n")) else None
            if nobs and pd.notna(r.get("max_cooks_distance")) and float(r["max_cooks_distance"]) > 4 / nobs:
                warnings.append(f"{aid}: max Cook's distance exceeds 4/n; inspect influential observations without deleting them solely to improve significance")

        if typ in {"equivalence_tost_independent", "equivalence_tost_paired"}:
            alpha = float(r.get("equivalence_alpha"))
            pl = float(r.get("tost_p_lower")); pu = float(r.get("tost_p_upper"))
            declared = _truthy(r.get("equivalence_conclusion"))
            calculated = pl < alpha and pu < alpha
            if declared != calculated:
                errors.append(f"{aid}: equivalence_conclusion inconsistent with the two one-sided p-values")
            if pd.notna(r.get("ci_low")) and pd.notna(r.get("ci_high")):
                inside = float(r["ci_low"]) > float(r["equivalence_margin_lower"]) and float(r["ci_high"]) < float(r["equivalence_margin_upper"])
                if inside != calculated:
                    errors.append(f"{aid}: TOST conclusion inconsistent with the corresponding equivalence CI and margins")

    if len(clog):
        required_log_cols = {"_row_id", "rule_id", "reason", "column", "value"}
        if not required_log_cols.issubset(clog.columns):
            errors.append(f"Cleaning log missing columns: {sorted(required_log_cols - set(clog.columns))}")
        elif clog["reason"].astype(str).str.strip().eq("").any():
            errors.append("Cleaning log has row(s) without explicit reason")

    family_ids = set()
    method_map = {"holm": "holm", "bonferroni": "bonferroni", "fdr_bh": "fdr_bh"}
    for fam, spec in plan.get("multiplicity", {}).items():
        ids = [a["analysis_item_id"] for a in plan.get("analyses", []) if a.get("multiplicity_family") == fam]
        if not ids:
            continue
        family_ids.update(ids)
        indexed = res.set_index("analysis_item_id", drop=False)
        missing_ids = [aid for aid in ids if aid not in indexed.index]
        duplicate_family_ids = [aid for aid in ids if aid in duplicate_result_ids]
        if missing_ids:
            errors.append(f"Multiplicity family {fam} missing results: {missing_ids}")
            continue
        if duplicate_family_ids:
            errors.append(f"Multiplicity family {fam} cannot be reconciled because result IDs are duplicated: {duplicate_family_ids}")
            continue
        sub = indexed.loc[ids]
        method = spec.get("method", "none")
        if "p_adjust_method" not in sub.columns or any(sub["p_adjust_method"].fillna("none").astype(str) != method):
            errors.append(f"Multiplicity method mismatch in family {fam}")
        try:
            raw = sub["p_value"].astype(float).to_numpy()
            if not np.all(np.isfinite(raw)):
                raise ValueError("non-finite raw p-value")
            expected_adj = raw if method == "none" else multipletests(raw, method=method_map[method])[1]
            actual_adj = sub["p_adjusted"].astype(float).to_numpy()
            if len(actual_adj) != len(expected_adj) or not np.allclose(actual_adj, expected_adj, rtol=1e-12, atol=1e-15):
                errors.append(f"Multiplicity adjusted p-values do not reconcile for family {fam}")
        except Exception as e:
            errors.append(f"Multiplicity family {fam} could not be numerically reconciled: {e}")

    # Analyses outside a declared multiplicity family must retain the raw p-value.
    for _, rr in res.iterrows():
        aid = rr.get("analysis_item_id")
        if aid in family_ids:
            continue
        if str(rr.get("p_adjust_method", "none")) != "none":
            errors.append(f"{aid}: p_adjust_method must be none outside a declared multiplicity family")
        try:
            if not math.isclose(float(rr.get("p_adjusted")), float(rr.get("p_value")), rel_tol=1e-12, abs_tol=1e-15):
                errors.append(f"{aid}: p_adjusted must equal p_value outside a declared multiplicity family")
        except Exception:
            errors.append(f"{aid}: could not reconcile raw and adjusted p-values")

    result_reconciliation_status = "not_run"
    recomputed_base_rows = None
    try:
        recomputed_base_rows = recompute_result_rows(data, plan, data_hash, plan_hash)
        reconciliation_errors = reconcile_results_against_current_run(
            data, plan, res, data_hash, plan_hash, expected_rows=recomputed_base_rows
        )
        if reconciliation_errors:
            result_reconciliation_status = "FAIL"
            errors.extend(reconciliation_errors)
        else:
            result_reconciliation_status = "PASS"
    except Exception as e:
        result_reconciliation_status = "FAIL"
        errors.append(f"Deterministic result reconciliation could not be completed: {e}")

    cleaning_report_status = "not_provided"
    if args.cleaning_report:
        crep = read_json(args.cleaning_report); cleaning_report_status = "checked"
        if crep.get("skill_version") != SKILL_VERSION: errors.append(f"cleaning_report skill_version does not match current skill version {SKILL_VERSION}; rerun cleaning with the current release")
        if crep.get("output_sha256") != data_hash: errors.append("cleaning_report output_sha256 does not match current analysis-ready data")
        if crep.get("plan_sha256") != plan_hash: errors.append("cleaning_report plan_sha256 does not match current analysis plan")
        if crep.get("cleaning_log_sha256") and crep.get("cleaning_log_sha256") != sha256_file(args.cleaning_log): errors.append("cleaning_report cleaning_log_sha256 does not match current cleaning log")
        if crep.get("rows_final") is not None and int(crep.get("rows_final")) != len(data): errors.append("cleaning_report rows_final does not match current analysis-ready row count")
        if crep.get("rows_dropped_events") is not None and int(crep.get("rows_dropped_events")) != len(clog): errors.append("cleaning_report rows_dropped_events does not match cleaning-log row count")
        if crep.get("technical_replicate_aggregation"):
            for c in ["_source_row_ids", "_technical_replicate_n"]:
                if c not in data.columns:
                    errors.append(f"technical-replicate aggregation was reported but provenance column {c} is missing from analysis-ready data")
            if "_source_row_ids" in data.columns and data["_source_row_ids"].astype(str).str.strip().eq("").any():
                errors.append("technical-replicate provenance contains empty _source_row_ids")
    elif plan.get("profile") == "confirmatory":
        errors.append("confirmatory preflight requires --cleaning-report for provenance reconciliation")
    else:
        warnings.append("cleaning_report not supplied; cleaning-output hash reconciliation was skipped")

    planned_sens_specs = {s["sensitivity_id"]: s for s in plan.get("sensitivity_analyses", [])}
    planned_sens = set(planned_sens_specs)
    sensitivity_status = "not_planned" if not planned_sens else "missing"
    sensitivity_reconciliation_status = "not_planned" if not planned_sens else "not_run"
    if planned_sens:
        if not args.sensitivity_results:
            errors.append(f"Planned sensitivity analyses were not supplied to preflight: {sorted(planned_sens)}")
        else:
            sres = read_artifact_csv(args.sensitivity_results)
            sensitivity_status = "checked"
            if "sensitivity_id" not in sres.columns:
                errors.append("sensitivity results are missing sensitivity_id")
                got_sens = set()
                duplicate_sensitivity_ids = set()
            else:
                sid_series = sres["sensitivity_id"].astype(str)
                got_sens = set(sid_series)
                duplicate_sensitivity_ids = set(sid_series[sid_series.duplicated(keep=False)].tolist())
                if duplicate_sensitivity_ids:
                    errors.append(f"sensitivity results contain duplicate sensitivity_id rows: {sorted(duplicate_sensitivity_ids)}")
            if got_sens != planned_sens:
                errors.append(f"Sensitivity IDs mismatch. missing={sorted(planned_sens-got_sens)} extra={sorted(got_sens-planned_sens)}")
            if "data_sha256" not in sres.columns or _unique_nonnull(sres["data_sha256"]) != {data_hash}: errors.append("sensitivity results data_sha256 does not match current analysis-ready data")
            if "plan_sha256" not in sres.columns or _unique_nonnull(sres["plan_sha256"]) != {plan_hash}: errors.append("sensitivity results plan_sha256 does not match current plan")
            if "skill_version" not in sres.columns or _unique_nonnull(sres["skill_version"]) != {SKILL_VERSION}: errors.append(f"sensitivity results skill_version does not match current skill version {SKILL_VERSION}")
            if "estimand_relation" not in sres.columns:
                errors.append("sensitivity results missing estimand_relation")
            else:
                current_by_id = {str(rr["analysis_item_id"]): rr for _, rr in res.iterrows()}
                for _, sr in sres.iterrows():
                    sid = sr.get("sensitivity_id"); planned_rel = planned_sens_specs.get(sid, {}).get("estimand_relation")
                    if str(sr.get("estimand_relation")) != str(planned_rel): errors.append(f"{sid}: sensitivity estimand_relation does not match plan")
                    base_id = str(sr.get("base_analysis_item_id", ""))
                    base_now = current_by_id.get(base_id)
                    if base_now is None:
                        errors.append(f"{sid}: sensitivity references base result '{base_id}' not present in current results.csv")
                        continue
                    for field in ["base_estimate", "base_ci_low", "base_ci_high", "base_p_value", "base_p_adjusted"]:
                        current_field = field.removeprefix("base_")
                        sv = sr.get(field); bv = base_now.get(current_field)
                        if pd.isna(sv) and pd.isna(bv):
                            continue
                        try:
                            if abs(float(sv) - float(bv)) > 1e-12 * max(1.0, abs(float(bv))):
                                errors.append(f"{sid}: {field} does not match current base result {base_id}.{current_field}")
                        except (TypeError, ValueError):
                            if str(sv) != str(bv):
                                errors.append(f"{sid}: {field} does not match current base result {base_id}.{current_field}")

            try:
                sensitivity_reconciliation_errors = reconcile_sensitivity_against_current_run(
                    data, plan, sres, data_hash, plan_hash, base_rows=recomputed_base_rows
                )
                if sensitivity_reconciliation_errors:
                    sensitivity_reconciliation_status = "FAIL"
                    errors.extend(sensitivity_reconciliation_errors)
                else:
                    sensitivity_reconciliation_status = "PASS"
            except Exception as e:
                sensitivity_reconciliation_status = "FAIL"
                errors.append(f"Deterministic sensitivity reconciliation could not be completed: {e}")

    report = {
        "skill_version": SKILL_VERSION,
        "status": "PASS" if not errors else "FAIL",
        "errors": errors,
        "warnings": warnings,
        "plan_sha256": plan_hash,
        "data_sha256": data_hash,
        "rows_analysis_ready": int(len(data)),
        "planned_analyses": len(expected),
        "result_rows": int(len(res)),
        "missing_data_strategy": plan.get("missing_data", {}).get("strategy"),
        "resampling_n_resamples": plan.get("resampling", {}).get("n_resamples"),
        "deterministic_result_reconciliation": result_reconciliation_status,
        "deterministic_sensitivity_reconciliation": sensitivity_reconciliation_status,
        "cleaning_report_status": cleaning_report_status,
        "sensitivity_status": sensitivity_status,
    }
    write_json(report, args.report)
    print(f"Preflight: {report['status']} ({len(errors)} errors, {len(warnings)} warnings)")
    if errors:
        raise SystemExit(1)


if __name__ == "__main__": main()
