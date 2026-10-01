#!/usr/bin/env python3
"""Smoke + guardrail tests for scientific-data-analysis."""
from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

import pandas as pd
from scipy import stats
from run_stats import run_item, _paired_arrays_with_counts
from clean_data import _technical_replicate_aggregate
from run_sensitivity import apply_filter
from validate_plan import validate
from plot_results import model_plot_cohort, _assert_plot_cohort_matches_result
from _common import categorical_levels_mask, typed_row_duplicate_mask, typed_duplicate_mask, read_table, write_table, table_roundtrip_identity_mismatches, typed_scalar_key

ROOT = Path(__file__).resolve().parents[1]
PYTHON = sys.executable


def run(*args, expect_fail=False):
    env = os.environ.copy()
    for key in ["OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS"]:
        env[key] = "1"
    proc = subprocess.run([PYTHON, *map(str, args)], cwd=ROOT, text=True, capture_output=True, env=env)
    if expect_fail:
        if proc.returncode == 0:
            raise AssertionError(f"Expected failure but command passed: {args}\n{proc.stdout}\n{proc.stderr}")
        return proc
    if proc.returncode != 0:
        raise RuntimeError(f"Command failed: {args}\nSTDOUT:\n{proc.stdout}\nSTDERR:\n{proc.stderr}")
    return proc


def base_plan(data_path):
    return {
        "analysis_plan_schema_version": "1.4",
        "analysis_id": "self-test",
        "plan_version": "1.0",
        "profile": "exploratory",
        "research_question": "Self-test",
        "unit_of_analysis": "row",
        "confidence_level": 0.95,
        "random_seed": 7,
        "input": {"path": str(data_path), "sha256": ""},
        "variables": {"id": "id", "group": "group", "outcomes": [], "pair_id": None, "covariates": []},
        "cleaning": {
            "missing_tokens": ["", "NA"], "require_nonmissing": [], "require_numeric": [],
            "numeric_ranges": {}, "allowed_levels": {}, "drop_exact_duplicates": False,
            "id_duplicate_policy": "allow", "technical_replicates": None,
        },
        "missing_data": {"strategy": "complete_case", "report_per_analysis": True, "imputation": "none"},
        "resampling": {"method": "percentile", "n_resamples": 200},
        "analyses": [], "multiplicity": {}, "plots": [], "sensitivity_analyses": [],
    }


with tempfile.TemporaryDirectory(prefix="scientific-data-analysis-") as td_raw:
    td = Path(td_raw)

    print("self-test: 1 end-to-end", flush=True)
    # 1) Bundled core pipeline example: cleaning -> statistics -> sensitivity -> preflight -> report.
    # profile/plot/manifest are lightweight wrappers covered by the release QA rather than repeated here.
    plan = ROOT / "examples/analysis_plan.json"
    data = ROOT / "examples/toy_data.csv"
    run(ROOT / "scripts/clean_data.py", "--input", data, "--plan", plan, "--output", td / "clean.csv", "--log", td / "cleaning_log.csv", "--report", td / "cleaning_report.json")
    run(ROOT / "scripts/run_stats.py", "--data", td / "clean.csv", "--plan", plan, "--out-csv", td / "results.csv", "--out-json", td / "results.json")
    run(ROOT / "scripts/run_sensitivity.py", "--data", td / "clean.csv", "--plan", plan, "--base-results", td / "results.csv", "--out-csv", td / "sensitivity.csv", "--out-json", td / "sensitivity.json")
    run(ROOT / "scripts/preflight.py", "--plan", plan, "--data", td / "clean.csv", "--results", td / "results.csv", "--cleaning-log", td / "cleaning_log.csv", "--cleaning-report", td / "cleaning_report.json", "--sensitivity-results", td / "sensitivity.csv", "--report", td / "preflight.json")
    run(ROOT / "scripts/build_report.py", "--plan", plan, "--cleaning-report", td / "cleaning_report.json", "--cleaning-log", td / "cleaning_log.csv", "--results", td / "results.csv", "--sensitivity-results", td / "sensitivity.csv", "--preflight", td / "preflight.json", "--out", td / "analysis_report.md")
    assert (td / "analysis_report.md").exists()
    assert json.loads((td / "preflight.json").read_text())["status"] == "PASS"

    print("self-test: separation guardrail", flush=True)
    sep_df = pd.DataFrame({"id": list(range(10)), "x": list(range(10)), "binary": ["no"] * 5 + ["yes"] * 5})
    sep_path = td / "separation.csv"; sep_df.to_csv(sep_path, index=False)
    sp = base_plan(sep_path)
    sp["analyses"] = [{"analysis_item_id": "sep", "type": "logistic_regression", "outcome": "binary", "event_level": "yes", "nonevent_level": "no", "predictors": ["x"]}]
    sp_path = td / "separation_plan.json"; sp_path.write_text(json.dumps(sp, indent=2))
    proc = run(ROOT / "scripts/run_stats.py", "--data", sep_path, "--plan", sp_path, "--out-csv", td / "sep.csv", "--out-json", td / "sep.json", expect_fail=True)
    assert "perfect separation" in (proc.stdout + proc.stderr).lower()

    print("self-test: numeric binary levels with missing outcome", flush=True)
    # Numeric 0/1 outcomes are often promoted to float 0.0/1.0 when a CSV has missing values.
    # Declared numeric event levels must still match by scalar value rather than string rendering.
    numeric_logit = pd.DataFrame({
        "id": list(range(1, 13)),
        "x": [0.2, 0.5, 0.8, 1.1, 1.4, 1.7, 2.0, 2.3, 2.6, 2.9, 3.2, 3.5],
        "binary": [0, 0, 0, 1, 0, 1, 0, 1, 1, None, 1, 1],
    })
    numeric_logit_path = td / "numeric_logit_missing.csv"; numeric_logit.to_csv(numeric_logit_path, index=False)
    nlp = base_plan(numeric_logit_path)
    nlp["analyses"] = [{"analysis_item_id": "numeric_logit", "type": "logistic_regression", "outcome": "binary", "event_level": 1, "nonevent_level": 0, "predictors": ["x"]}]
    nlp_path = td / "numeric_logit_plan.json"; nlp_path.write_text(json.dumps(nlp, indent=2))
    run(ROOT / "scripts/run_stats.py", "--data", numeric_logit_path, "--plan", nlp_path, "--out-csv", td / "numeric_logit_results.csv", "--out-json", td / "numeric_logit_results.json")
    nlr = pd.read_csv(td / "numeric_logit_results.csv").iloc[0]
    assert int(nlr["n_candidate_units"]) == 12 and int(nlr["n_analyzed_units"]) == 11 and int(nlr["n_missing_or_invalid_excluded"]) == 1

    print("self-test: categorical level fidelity", flush=True)
    # Distinct scalar categories must not be collapsed by string rendering.
    mixed_cat = pd.DataFrame({
        "row": [1, 1, "1", "1", 2, 2, "2", "2"],
        "col": ["A", "B", "A", "B", "A", "B", "A", "B"],
    })
    mixed_chi = run_item(
        mixed_cat, {"analysis_item_id": "mixed_chi", "type": "chi_square", "row": "row", "column": "col"},
        0.95, 17, n_resamples=200,
    )
    assert mixed_chi["table_shape"] == "4x2"
    assert json.loads(mixed_chi["row_levels_json"]) == [1, 2, "1", "2"]

    ambiguous_cat = pd.DataFrame({
        "row": [True, True, 1, 1, False, False, 0, 0],
        "col": ["A", "B", "A", "B", "A", "B", "A", "B"],
    })
    for ambiguous_type in ["chi_square", "fisher_exact"]:
        try:
            run_item(
                ambiguous_cat,
                {"analysis_item_id": f"ambiguous_{ambiguous_type}", "type": ambiguous_type, "row": "row", "column": "col"},
                0.95, 18, n_resamples=200,
            )
        except ValueError as e:
            assert "Python/pandas equality would merge" in str(e)
        else:
            raise AssertionError(f"Expected equality-colliding boolean/numeric categories to fail explicitly for {ambiguous_type}")

    mixed_two = pd.DataFrame({
        "g": [1, 1, 1, "1", "1", "1"],
        "y": [1.0, 1.2, 0.9, 2.0, 2.2, 1.8],
    })
    mixed_contrast = run_item(
        mixed_two, {
            "analysis_item_id": "mixed_contrast", "type": "welch_contrast",
            "outcome": "y", "group": "g",
            "contrast_terms": [{"level": 1, "weight": -1}, {"level": "1", "weight": 1}],
        },
        0.95, 19, n_resamples=200,
    )
    assert json.loads(mixed_contrast["group_levels_json"]) == [1, "1"]
    assert "number" in mixed_contrast["contrast_orientation"] and "string" in mixed_contrast["contrast_orientation"]

    # v1.4.2: declared categorical selectors use typed identity everywhere,
    # so equality-colliding Python scalars (True vs 1) are not silently merged.
    typed_groups = pd.DataFrame({
        "g": pd.Series([True, True, True, 1, 1, 1], dtype=object),
        "y": [1.0, 1.2, 0.8, 2.0, 2.4, 1.8],
    })
    typed_t = run_item(
        typed_groups,
        {"analysis_item_id": "typed_t", "type": "independent_t", "outcome": "y", "group": "g", "group_a": True, "group_b": 1},
        0.95, 20, n_resamples=200,
    )
    assert typed_t["n_a"] == 3 and typed_t["n_b"] == 3
    assert json.loads(typed_t["group_a_json"]) is True and json.loads(typed_t["group_b_json"]) == 1

    typed_pairs = pd.DataFrame({
        "pair": ["p1", "p1", "p2", "p2", "p3", "p3"],
        "condition": pd.Series([True, 1, True, 1, True, 1], dtype=object),
        "y": [1.0, 2.0, 2.0, 2.5, 3.0, 4.0],
    })
    typed_pair = run_item(
        typed_pairs,
        {"analysis_item_id": "typed_pair", "type": "paired_t", "outcome": "y", "pair_id": "pair", "condition": "condition", "condition_a": True, "condition_b": 1},
        0.95, 21, n_resamples=200,
    )
    assert typed_pair["n_pairs"] == 3
    assert json.loads(typed_pair["condition_a_json"]) is True and json.loads(typed_pair["condition_b_json"]) == 1

    typed_logit_df = pd.DataFrame({
        "outcome": pd.Series([True, 1, True, 1, True, 1, 1, True, 1, True, 1, True], dtype=object),
        "x": [0.1, 0.3, 0.5, 0.7, 0.9, 1.1, 1.3, 1.5, 1.7, 1.9, 2.1, 2.3],
    })
    typed_logit = run_item(
        typed_logit_df,
        {"analysis_item_id": "typed_logit", "type": "logistic_regression", "outcome": "outcome", "event_level": True, "nonevent_level": 1, "predictors": ["x"], "robust_se": "HC0"},
        0.95, 22, n_resamples=200,
    )
    assert json.loads(typed_logit["event_level_json"]) is True
    assert json.loads(typed_logit["nonevent_level_json"]) == 1

    allowed_series = pd.Series([True, 1, False, 0], dtype=object)
    assert categorical_levels_mask(allowed_series, [1, 0]).tolist() == [False, True, False, True]

    # v1.4.3: sensitivity categorical filters must use the same typed identity
    # as the base cleaning/inference path rather than pandas eq/isin semantics.
    sensitivity_df = pd.DataFrame({
        "flag": pd.Series([True, 1, False, 0, "1"], dtype=object),
        "y": [10, 20, 30, 40, 50],
    })
    kept, excluded = apply_filter(sensitivity_df, {"exclude_if": [{"column": "flag", "operator": "eq", "value": True}]})
    assert excluded.tolist() == [True, False, False, False, False]
    assert kept["y"].tolist() == [20, 30, 40, 50]
    kept, excluded = apply_filter(sensitivity_df, {"exclude_if": [{"column": "flag", "operator": "in", "values": [1, "1"]}]})
    assert excluded.tolist() == [False, True, False, False, True]
    assert kept["y"].tolist() == [10, 30, 40]
    kept, excluded = apply_filter(sensitivity_df, {"exclude_if": [{"column": "flag", "operator": "not_in", "values": [True, False]}]})
    assert excluded.tolist() == [False, True, False, True, True]
    assert kept["y"].tolist() == [10, 30]

    # Sensitivity filter validation should reject empty/ambiguous categorical
    # value sets before execution rather than producing accidental all/none subsets.
    filter_plan = base_plan(td / "unused.csv")
    filter_plan["analyses"] = [{"analysis_item_id": "base", "type": "independent_t", "outcome": "y", "group": "g", "group_a": "A", "group_b": "B"}]
    filter_plan["sensitivity_analyses"] = [{
        "sensitivity_id": "bad_filter", "base_analysis_item_id": "base", "rationale": "guard", "estimand_relation": "same",
        "data_filter": {"exclude_if": [{"column": "flag", "operator": "not_in", "values": []}]},
    }]
    errors, _ = validate(filter_plan)
    assert any("requires a non-empty values list" in e for e in errors)

    filter_plan["sensitivity_analyses"][0]["data_filter"]["exclude_if"][0] = {"column": "flag", "operator": "in", "values": [1, 1.0]}
    errors, _ = validate(filter_plan)
    assert any("duplicate typed levels" in e for e in errors)

    # v1.4.4: a plan may not label a mechanically different statistical
    # target as the same estimand merely because the user wrote "same".
    estimand_plan = base_plan(td / "unused_estimand.csv")
    estimand_plan["analyses"] = [{"analysis_item_id": "base", "type": "independent_t", "outcome": "y", "group": "g", "group_a": "A", "group_b": "B"}]
    estimand_plan["sensitivity_analyses"] = [{
        "sensitivity_id": "rank", "base_analysis_item_id": "base", "rationale": "guard",
        "analysis_overrides": {"type": "mann_whitney"}, "estimand_relation": "same",
    }]
    errors, _ = validate(estimand_plan)
    assert any("structurally incompatible" in e and "estimand family changes" in e for e in errors)
    estimand_plan["sensitivity_analyses"][0]["estimand_relation"] = "different"
    errors, _ = validate(estimand_plan)
    assert not any("structurally incompatible" in e for e in errors)

    regression_plan = base_plan(td / "unused_regression.csv")
    regression_plan["analyses"] = [{"analysis_item_id": "reg", "type": "linear_regression", "outcome": "y", "predictors": ["x"], "report_predictor": "x", "robust_se": "HC3"}]
    regression_plan["sensitivity_analyses"] = [{
        "sensitivity_id": "adjusted", "base_analysis_item_id": "reg", "rationale": "guard",
        "analysis_overrides": {"predictors": ["x", "z"]}, "estimand_relation": "same",
    }]
    errors, _ = validate(regression_plan)
    assert any("predictor/adjustment set changes" in e for e in errors)
    regression_plan["sensitivity_analyses"][0]["analysis_overrides"] = {"robust_se": "nonrobust"}
    errors, _ = validate(regression_plan)
    assert not any("structurally incompatible" in e for e in errors)

    contrast_plan = base_plan(td / "unused_contrast.csv")
    contrast_plan["analyses"] = [{
        "analysis_item_id": "c", "type": "welch_contrast", "outcome": "y", "group": "g",
        "contrast_terms": [{"level": "A", "weight": -0.5}, {"level": "B", "weight": -0.5}, {"level": "C", "weight": 1.0}],
    }]
    contrast_plan["sensitivity_analyses"] = [{
        "sensitivity_id": "c2", "base_analysis_item_id": "c", "rationale": "guard",
        "analysis_overrides": {"contrast_terms": [{"level": "A", "weight": -1.0}, {"level": "B", "weight": -1.0}, {"level": "C", "weight": 2.0}]},
        "estimand_relation": "same",
    }]
    errors, _ = validate(contrast_plan)
    assert any("planned contrast levels or weight scale changes" in e for e in errors)

    # Switching a mean-difference test to TOST changes the decision rule/margins
    # but preserves the raw mean-difference estimand, so this declaration remains allowed.
    tost_plan = base_plan(td / "unused_tost.csv")
    tost_plan["analyses"] = [{"analysis_item_id": "t", "type": "independent_t", "outcome": "y", "group": "g", "group_a": "A", "group_b": "B"}]
    tost_plan["sensitivity_analyses"] = [{
        "sensitivity_id": "eq", "base_analysis_item_id": "t", "rationale": "guard",
        "analysis_overrides": {"type": "equivalence_tost_independent", "equivalence_margin_lower": -1.0, "equivalence_margin_upper": 1.0, "equivalence_alpha": 0.05},
        "estimand_relation": "same",
    }]
    errors, _ = validate(tost_plan)
    assert not any("structurally incompatible" in e for e in errors)

    # v1.4.5: model plots must use the exact model complete-case cohort,
    # not reintroduce rows that were excluded because another covariate/predictor was missing.
    plot_df = pd.DataFrame({
        "g": ["A", "A", "B", "B"],
        "y": [1.0, 1.2, 2.0, 2.2],
        "x": [0.1, 0.2, 0.3, 0.4],
        "z": [1.0, None, 1.5, 1.7],
        "count": [1, 2, 3, 4],
        "exposure": [1.0, 1.0, 2.0, 2.0],
    })
    ols_cohort = model_plot_cohort(plot_df, {"type": "linear_regression", "outcome": "y", "predictors": ["x", "z"]})
    assert len(ols_cohort) == 3
    ancova_cohort = model_plot_cohort(plot_df, {"type": "ancova_two_group", "outcome": "y", "group": "g", "group_a": "A", "group_b": "B", "covariates": ["z"]})
    assert len(ancova_cohort) == 3
    poisson_cohort = model_plot_cohort(plot_df, {"type": "poisson_regression", "outcome": "count", "predictors": ["x", "z"], "exposure": "exposure"})
    assert len(poisson_cohort) == 3
    _assert_plot_cohort_matches_result(ols_cohort, {"n": 3}, "plot_cohort")
    try:
        _assert_plot_cohort_matches_result(ols_cohort, {"n": 4}, "plot_cohort")
    except ValueError as e:
        assert "refusing to render a plot from a different analysis cohort" in str(e)
    else:
        raise AssertionError("Expected model plot cohort/result n mismatch to fail")

    typed_meta_conflict = pd.DataFrame({
        "_row_id": [1, 2], "id": ["S1", "S1"],
        "meta": pd.Series([True, 1], dtype=object), "value": [1.0, 1.2],
    })
    try:
        _technical_replicate_aggregate(typed_meta_conflict, {"group_by": ["id"], "value_columns": ["value"], "carry_columns": ["meta"], "method": "mean"})
    except ValueError as e:
        assert "Conflicting metadata" in str(e)
    else:
        raise AssertionError("Expected typed technical-replicate metadata conflict to fail")

    # v1.4.6: identifier identity must not fall back to pandas equality.
    # Rows/IDs that differ only by boolean True vs numeric 1 are distinct under
    # the skill contract even though pandas considers them equal.
    id_identity = pd.DataFrame({"id": pd.Series([True, 1], dtype=object), "y": [5.0, 5.0]})
    assert typed_row_duplicate_mask(id_identity, keep="first").tolist() == [False, False]
    assert typed_duplicate_mask(id_identity["id"], keep=False).tolist() == [False, False]

    # Missing pair IDs must never be grouped into one synthetic subject.
    pair_missing = pd.DataFrame({
        "pid": [None, None, "S1", "S1", "S2", "S2"],
        "cond": ["A", "B", "A", "B", "A", "B"],
        "y": [100.0, 200.0, 1.0, 2.0, 3.0, 5.0],
    })
    pair_analysis = {
        "analysis_item_id": "pair_missing", "type": "paired_t", "pair_id": "pid",
        "condition": "cond", "outcome": "y", "condition_a": "A", "condition_b": "B",
    }
    pair_result = run_item(pair_missing, pair_analysis, 0.95, 17, n_resamples=50)
    assert int(pair_result["n_pairs"]) == 2
    assert int(pair_result["n_candidate_units"]) == 2
    assert int(pair_result["n_analyzed_units"]) == 2
    assert int(pair_result["n_rows_missing_pair_id"]) == 2
    assert abs(float(pair_result["estimate"]) - 1.5) < 1e-12

    # Equality-colliding but typed-distinct pair IDs remain separate analysis units.
    pair_typed = pd.DataFrame({
        "pid": pd.Series([True, True, 1, 1], dtype=object),
        "cond": ["A", "B", "A", "B"],
        "y": [1.0, 2.0, 10.0, 20.0],
    })
    pa, pb, pcandidate, _, pdiag = _paired_arrays_with_counts(pair_typed, pair_analysis)
    assert pcandidate == 2 and pdiag["n_rows_missing_pair_id"] == 0
    assert pa.tolist() == [1.0, 10.0] and pb.tolist() == [2.0, 20.0]

    typed_group_key_collision = pd.DataFrame({
        "_row_id": [1, 2], "id": pd.Series([True, 1], dtype=object), "value": [1.0, 1.2],
    })
    try:
        _technical_replicate_aggregate(typed_group_key_collision, {"group_by": ["id"], "value_columns": ["value"], "carry_columns": [], "method": "mean"})
    except ValueError as e:
        assert "equality-colliding" in str(e)
    else:
        raise AssertionError("Expected equality-colliding technical replicate group key to fail")

    # v1.4.7: file I/O must not silently erase typed categorical/ID identity.
    # JSONL preserves JSON scalar type; CSV must be rejected by the cleaner when
    # a plan-relevant column would change typed identity on round-trip.
    mixed_io = pd.DataFrame({
        "id": ["S1", "S2", "S3"],
        "g": pd.Series([True, 1, "1"], dtype=object),
        "y": [1.0, 2.0, 3.0],
    })
    mixed_jsonl = td / "typed_roundtrip.jsonl"
    write_table(mixed_io, mixed_jsonl)
    mixed_reloaded = read_table(mixed_jsonl)
    assert [typed_scalar_key(v) for v in mixed_reloaded["g"].tolist()] == [typed_scalar_key(v) for v in mixed_io["g"].tolist()]
    mixed_csv = td / "typed_roundtrip.csv"
    write_table(mixed_io, mixed_csv)
    csv_reloaded = read_table(mixed_csv)
    assert table_roundtrip_identity_mismatches(mixed_io, csv_reloaded, ["g"]), "CSV should be detected as lossy for mixed scalar identity"

    # Native XLSX cell types must be preserved on input before pandas can coerce
    # boolean TRUE and numeric 1 into a single homogeneous dtype.
    from openpyxl import Workbook
    xlsx = td / "typed_input.xlsx"
    wb = Workbook(); ws = wb.active
    ws.append(["id", "g", "y"]); ws.append(["S1", True, 1.0]); ws.append(["S2", 1, 2.0]); ws.append(["S3", "1", 3.0]); wb.save(xlsx)
    xdf = read_table(xlsx)
    assert [typed_scalar_key(v) for v in xdf["g"].tolist()] == [("bool", True), ("num", 1.0), ("str", "1")]

    print("self-test: 2 inference families", flush=True)
    # 2) Exercise every core inference family on nondegenerate toy data.
    all_df = pd.DataFrame({
        "id": [f"S{i:02d}" for i in range(1, 13)],
        "group": ["A"] * 6 + ["B"] * 6,
        "y": [1.1, 1.5, 1.3, 1.8, 1.6, 1.2, 2.2, 2.5, 2.1, 2.8, 2.6, 2.4],
        "a": [2.0, 2.2, 1.9, 2.5, 2.3, 2.1, 1.8, 2.0, 2.2, 2.1, 2.4, 2.3],
        "b": [2.4, 2.1, 2.2, 2.8, 2.6, 2.5, 2.0, 2.3, 2.5, 2.0, 2.8, 2.7],
        "x": list(range(1, 13)),
        "z": [1, 2, 3, 1, 2, 3, 1, 2, 3, 1, 2, 3],
        "reg_y": [None, 2.5, 3.2, 3.6, 4.2, 5.1, 5.4, 6.1, 6.9, 7.0, 8.2, 8.4],
        "binary": ["no", "yes", "no", "yes", "no", "yes", "no", "yes", "yes", "no", "yes", "yes"],
        "group3": ["A", "A", "A", "A", "B", "B", "B", "B", "C", "C", "C", "C"],
        "multi_y": [1.0, 1.3, 0.9, 1.2, 2.0, 2.4, 1.8, 2.2, 3.2, 3.7, 3.0, 3.5],
        "count_y": [0, 1, 1, 2, 1, 2, 3, 4, 2, 4, 5, 7],
        "exposure": [1.0, 1.0, 1.5, 1.0, 1.0, 2.0, 1.5, 1.0, 2.0, 1.0, 1.5, 2.0],
        "rowcat": ["r1", "r1", "r1", "r2", "r2", "r2", "r1", "r1", "r2", "r2", "r2", "r1"],
        "colcat": ["c1", "c1", "c2", "c1", "c2", "c2", "c1", "c2", "c1", "c2", "c2", "c1"],
        "row2": ["case", "case", "case", "case", "case", "case", "ctrl", "ctrl", "ctrl", "ctrl", "ctrl", "ctrl"],
        "col2": ["yes", "yes", "yes", "yes", "yes", "yes", "yes", "no", "no", "no", "yes", "no"],
    })
    all_path = td / "alltypes.csv"; all_df.to_csv(all_path, index=False)
    p = base_plan(all_path)
    p["analyses"] = [
        {"analysis_item_id": "t", "type": "independent_t", "outcome": "y", "group": "group", "group_a": "A", "group_b": "B"},
        {"analysis_item_id": "pt", "type": "paired_t", "outcome_a": "a", "outcome_b": "b"},
        {"analysis_item_id": "mw", "type": "mann_whitney", "outcome": "y", "group": "group", "group_a": "A", "group_b": "B"},
        {"analysis_item_id": "wx", "type": "wilcoxon", "outcome_a": "a", "outcome_b": "b"},
        {"analysis_item_id": "pr", "type": "pearson", "x": "x", "y": "reg_y"},
        {"analysis_item_id": "sr", "type": "spearman", "x": "x", "y": "reg_y"},
        {"analysis_item_id": "ols", "type": "linear_regression", "outcome": "reg_y", "predictors": ["x"], "robust_se": "HC3"},
        {"analysis_item_id": "chi", "type": "chi_square", "row": "rowcat", "column": "colcat"},
        {"analysis_item_id": "fish", "type": "fisher_exact", "row": "row2", "column": "col2", "row_levels": ["case", "ctrl"], "column_levels": ["yes", "no"]},
        {"analysis_item_id": "eqi", "type": "equivalence_tost_independent", "outcome": "y", "group": "group", "group_a": "A", "group_b": "B", "equivalence_margin_lower": -2.0, "equivalence_margin_upper": 2.0, "equivalence_alpha": 0.05},
        {"analysis_item_id": "eqp", "type": "equivalence_tost_paired", "outcome_a": "a", "outcome_b": "b", "equivalence_margin_lower": -1.0, "equivalence_margin_upper": 1.0, "equivalence_alpha": 0.05},
        {"analysis_item_id": "ancova", "type": "ancova_two_group", "outcome": "y", "group": "group", "group_a": "A", "group_b": "B", "covariates": ["z"], "robust_se": "HC3"},
        {"analysis_item_id": "logit", "type": "logistic_regression", "outcome": "binary", "event_level": "yes", "nonevent_level": "no", "predictors": ["x", "z"], "report_predictor": "x", "robust_se": "HC0"},
        {"analysis_item_id": "wanova", "type": "welch_anova", "outcome": "multi_y", "group": "group3", "group_levels": ["A", "B", "C"]},
        {"analysis_item_id": "wcontrast", "type": "welch_contrast", "outcome": "multi_y", "group": "group3", "contrast_terms": [{"level": "A", "weight": -0.5}, {"level": "B", "weight": -0.5}, {"level": "C", "weight": 1.0}]},
        {"analysis_item_id": "pois", "type": "poisson_regression", "outcome": "count_y", "predictors": ["x", "z"], "report_predictor": "x", "exposure": "exposure", "robust_se": "HC0"},
    ]
    all_plan = td / "alltypes_plan.json"; all_plan.write_text(json.dumps(p, indent=2))
    run(ROOT / "scripts/clean_data.py", "--input", all_path, "--plan", all_plan, "--output", td / "all_clean.csv", "--log", td / "all_cleaning_log.csv", "--report", td / "all_cleaning_report.json")
    run(ROOT / "scripts/run_stats.py", "--data", td / "all_clean.csv", "--plan", all_plan, "--out-csv", td / "all_results.csv", "--out-json", td / "all_results.json")
    run(ROOT / "scripts/preflight.py", "--plan", all_plan, "--data", td / "all_clean.csv", "--results", td / "all_results.csv", "--cleaning-log", td / "all_cleaning_log.csv", "--cleaning-report", td / "all_cleaning_report.json", "--report", td / "all_preflight.json")
    all_results = pd.read_csv(td / "all_results.csv")
    assert len(all_results) == 16
    assert json.loads((td / "all_preflight.json").read_text())["status"] == "PASS"
    assert {"n_candidate_units", "n_analyzed_units", "n_missing_or_invalid_excluded"}.issubset(all_results.columns)
    assert int(all_results.loc[all_results.analysis_item_id == "pr", "n_missing_or_invalid_excluded"].iloc[0]) == 1
    assert {"eqi", "eqp"}.issubset(set(all_results.loc[all_results["equivalence_conclusion"].notna(), "analysis_item_id"]))
    assert bool(all_results.loc[all_results.analysis_item_id == "logit", "model_converged"].iloc[0])
    wanova = all_results.loc[all_results.analysis_item_id == "wanova"].iloc[0]
    assert int(wanova["n_groups"]) == 3 and float(wanova["estimate"]) >= 0 and 0 <= float(wanova["p_value"]) <= 1
    wcontrast = all_results.loc[all_results.analysis_item_id == "wcontrast"].iloc[0]
    assert int(wcontrast["n_groups"]) == 3 and abs(float(wcontrast["contrast_weight_sum"])) < 1e-12
    assert float(wcontrast["estimate"]) > 0 and 0 <= float(wcontrast["p_value"]) <= 1 and float(wcontrast["df"]) > 0
    pois = all_results.loc[all_results.analysis_item_id == "pois"].iloc[0]
    assert bool(pois["model_converged"]) and str(pois["offset_mode"]) == "log_exposure:exposure"
    assert float(pois["estimate"]) > 0 and float(pois["pearson_dispersion_ratio"]) > 0
    fish = all_results.loc[all_results.analysis_item_id == "fish"].iloc[0]
    assert bool(fish["zero_cell_correction_applied"])
    assert pd.notna(fish["estimate"]) and float(fish["estimate"]) > 0 and float(fish["estimate"]) != float("inf")
    assert "Haldane_Anscombe" in str(fish["ci_method"])
    chi = all_results.loc[all_results.analysis_item_id == "chi"].iloc[0]
    chi_tab = pd.crosstab(all_df["rowcat"], all_df["colcat"]).to_numpy()
    chi_expected = stats.chi2_contingency(chi_tab, correction=False)[0]
    assert str(chi["chi_square_correction"]).lower() == "none"
    assert abs(float(chi["statistic"]) - float(chi_expected)) < 1e-12

    print("self-test: 2b RNG", flush=True)
    # 2b) RNG guardrail: reordering analyses must not change an analysis item's bootstrap stream.
    bootstrap_ids = ["sr", "chi", "mw", "wanova"]
    p_reordered = dict(p)
    subset = [a for a in p["analyses"] if a["analysis_item_id"] in bootstrap_ids]
    p_reordered["analyses"] = list(reversed(subset))
    reordered_plan = td / "bootstrap_plan_reordered.json"; reordered_plan.write_text(json.dumps(p_reordered, indent=2))
    run(ROOT / "scripts/run_stats.py", "--data", all_path, "--plan", reordered_plan, "--out-csv", td / "bootstrap_results_reordered.csv", "--out-json", td / "bootstrap_results_reordered.json")
    reordered = pd.read_csv(td / "bootstrap_results_reordered.csv")
    for aid in bootstrap_ids:
        left = all_results.loc[all_results.analysis_item_id == aid, ["ci_low", "ci_high"]].iloc[0]
        right = reordered.loc[reordered.analysis_item_id == aid, ["ci_low", "ci_high"]].iloc[0]
        assert left.equals(right), f"Order changed deterministic interval for {aid}"

    print("self-test: v1.4 multigroup/contrast/count guardrails", flush=True)
    # v1.4) Reject underspecified multi-group tests/contrasts, mislabeled GLM HC3,
    # noninteger counts, and nonpositive exposure.
    bad_welch = base_plan(all_path)
    bad_welch["analyses"] = [{"analysis_item_id": "bad_w", "type": "welch_anova", "outcome": "multi_y", "group": "group3", "group_levels": ["A", "B"]}]
    bad_welch_path = td / "bad_welch_plan.json"; bad_welch_path.write_text(json.dumps(bad_welch, indent=2))
    proc = run(ROOT / "scripts/validate_plan.py", bad_welch_path, expect_fail=True)
    assert "at least three" in (proc.stdout + proc.stderr)

    bad_contrast = base_plan(all_path)
    bad_contrast["analyses"] = [{"analysis_item_id": "bad_wc", "type": "welch_contrast", "outcome": "multi_y", "group": "group3", "contrast_terms": [{"level": "A", "weight": 1.0}, {"level": "B", "weight": 1.0}, {"level": "C", "weight": -1.0}]}]
    bad_contrast_path = td / "bad_contrast_plan.json"; bad_contrast_path.write_text(json.dumps(bad_contrast, indent=2))
    proc = run(ROOT / "scripts/validate_plan.py", bad_contrast_path, expect_fail=True)
    assert "weights must sum to zero" in (proc.stdout + proc.stderr)

    bad_contrast_alias = base_plan(all_path)
    bad_contrast_alias["analyses"] = [{"analysis_item_id": "bad_wc_alias", "type": "welch_contrast", "outcome": "multi_y", "group": "group3", "contrast_terms": [{"level": 1, "weight": 1.0}, {"level": 1.0, "weight": -1.0}]}]
    bad_contrast_alias_path = td / "bad_contrast_alias_plan.json"; bad_contrast_alias_path.write_text(json.dumps(bad_contrast_alias, indent=2))
    proc = run(ROOT / "scripts/validate_plan.py", bad_contrast_alias_path, expect_fail=True)
    assert "distinct under scalar data equality" in (proc.stdout + proc.stderr)

    bad_glm = base_plan(all_path)
    bad_glm["analyses"] = [{"analysis_item_id": "bad_g", "type": "poisson_regression", "outcome": "count_y", "predictors": ["x"], "robust_se": "HC3"}]
    bad_glm_path = td / "bad_glm_plan.json"; bad_glm_path.write_text(json.dumps(bad_glm, indent=2))
    proc = run(ROOT / "scripts/validate_plan.py", bad_glm_path, expect_fail=True)
    assert "HC0" in (proc.stdout + proc.stderr)

    bad_count_df = all_df.copy(); bad_count_df["count_y"] = bad_count_df["count_y"].astype(float); bad_count_df.loc[0, "count_y"] = 0.5
    bad_count_path = td / "bad_count.csv"; bad_count_df.to_csv(bad_count_path, index=False)
    bad_count = base_plan(bad_count_path)
    bad_count["analyses"] = [{"analysis_item_id": "bad_c", "type": "poisson_regression", "outcome": "count_y", "predictors": ["x"], "robust_se": "HC0"}]
    bad_count_plan = td / "bad_count_plan.json"; bad_count_plan.write_text(json.dumps(bad_count, indent=2))
    proc = run(ROOT / "scripts/run_stats.py", "--data", bad_count_path, "--plan", bad_count_plan, "--out-csv", td / "bad_count_results.csv", "--out-json", td / "bad_count_results.json", expect_fail=True)
    assert "nonnegative integer counts" in (proc.stdout + proc.stderr)

    bad_exp_df = all_df.copy(); bad_exp_df.loc[0, "exposure"] = 0
    bad_exp_path = td / "bad_exposure.csv"; bad_exp_df.to_csv(bad_exp_path, index=False)
    bad_exp = base_plan(bad_exp_path)
    bad_exp["analyses"] = [{"analysis_item_id": "bad_e", "type": "poisson_regression", "outcome": "count_y", "predictors": ["x"], "exposure": "exposure", "robust_se": "HC0"}]
    bad_exp_plan = td / "bad_exposure_plan.json"; bad_exp_plan.write_text(json.dumps(bad_exp, indent=2))
    proc = run(ROOT / "scripts/run_stats.py", "--data", bad_exp_path, "--plan", bad_exp_plan, "--out-csv", td / "bad_exp_results.csv", "--out-json", td / "bad_exp_results.json", expect_fail=True)
    assert "strictly positive" in (proc.stdout + proc.stderr)

    print("self-test: 3 duplicate pairs", flush=True)
    # 3) Guardrail: duplicate pair×condition rows must fail, never silently use 'first'.
    pair_df = pd.DataFrame({
        "id": ["p1", "p1", "p1", "p2", "p2"],
        "pair": ["p1", "p1", "p1", "p2", "p2"],
        "condition": ["A", "A", "B", "A", "B"],
        "outcome": [1.0, 1.1, 1.4, 2.0, 2.3],
        "group": ["g"] * 5,
    })
    pair_path = td / "duplicate_pairs.csv"; pair_df.to_csv(pair_path, index=False)
    pp = base_plan(pair_path)
    pp["analyses"] = [{"analysis_item_id": "paired", "type": "paired_t", "outcome": "outcome", "pair_id": "pair", "condition": "condition", "condition_a": "A", "condition_b": "B"}]
    pp_path = td / "duplicate_pairs_plan.json"; pp_path.write_text(json.dumps(pp, indent=2))
    proc = run(ROOT / "scripts/run_stats.py", "--data", pair_path, "--plan", pp_path, "--out-csv", td / "bad.csv", "--out-json", td / "bad.json", expect_fail=True)
    assert "multiple observations" in (proc.stdout + proc.stderr)

    print("self-test: 4 tech conflict", flush=True)
    # 4) Guardrail: conflicting metadata inside technical replicates must fail.
    tech_df = pd.DataFrame({"id": ["S1", "S1", "S2", "S2"], "group": ["A", "B", "A", "A"], "value": [1.0, 1.1, 2.0, 2.2]})
    tech_path = td / "tech.csv"; tech_df.to_csv(tech_path, index=False)
    tp = base_plan(tech_path)
    tp["variables"]["id"] = "id"
    tp["cleaning"]["technical_replicates"] = {"group_by": ["id"], "value_columns": ["value"], "carry_columns": ["group"], "method": "mean"}
    tp["analyses"] = [{"analysis_item_id": "dummy", "type": "pearson", "x": "value", "y": "value"}]
    tp_path = td / "tech_plan.json"; tp_path.write_text(json.dumps(tp, indent=2))
    proc = run(ROOT / "scripts/clean_data.py", "--input", tech_path, "--plan", tp_path, "--output", td / "tech_clean.csv", "--log", td / "tech_log.csv", "--report", td / "tech_report.json", expect_fail=True)
    assert "Conflicting metadata" in (proc.stdout + proc.stderr)

    print("self-test: 5 tech provenance", flush=True)
    # 5) Provenance guardrail: valid technical-replicate aggregation preserves raw-row membership.
    tech_ok = pd.DataFrame({
        "id": ["S1", "S1", "S2", "S2", "S3", "S3"],
        "group": ["A", "A", "A", "A", "B", "B"],
        "value": [1.0, 1.2, 2.0, 2.2, 3.0, 3.4],
    })
    tech_ok_path = td / "tech_ok.csv"; tech_ok.to_csv(tech_ok_path, index=False)
    top = base_plan(tech_ok_path)
    top["variables"]["id"] = "id"
    top["analyses"] = [{"analysis_item_id": "trace_only", "type": "pearson", "x": "value", "y": "value"}]
    top["cleaning"]["technical_replicates"] = {"group_by": ["id"], "value_columns": ["value"], "carry_columns": ["group"], "method": "mean"}
    top_path = td / "tech_ok_plan.json"; top_path.write_text(json.dumps(top, indent=2))
    run(ROOT / "scripts/clean_data.py", "--input", tech_ok_path, "--plan", top_path, "--output", td / "tech_ok_clean.csv", "--log", td / "tech_ok_log.csv", "--report", td / "tech_ok_report.json")
    tech_clean = pd.read_csv(td / "tech_ok_clean.csv")
    assert {"_source_row_ids", "_technical_replicate_n"}.issubset(tech_clean.columns)
    assert tech_clean["_technical_replicate_n"].tolist() == [2, 2, 2]
    assert tech_clean["_source_row_ids"].astype(str).tolist() == ["1;2", "3;4", "5;6"]

    print("self-test: 6 stale artifact provenance", flush=True)
    # 6) A sensitivity run must not accept stale/tampered base results, and
    # preflight must reject result artifacts from a different skill version.
    stale_base = pd.read_csv(td / "results.csv")
    stale_base["data_sha256"] = "0" * 64
    stale_base_path = td / "stale_base_results.csv"; stale_base.to_csv(stale_base_path, index=False)
    proc = run(ROOT / "scripts/run_sensitivity.py", "--data", td / "clean.csv", "--plan", plan, "--base-results", stale_base_path, "--out-csv", td / "stale_sens.csv", "--out-json", td / "stale_sens.json", expect_fail=True)
    assert "data_sha256" in (proc.stdout + proc.stderr)

    tampered_core = pd.read_csv(td / "results.csv")
    core_idx = tampered_core.index[0]
    tampered_core.loc[core_idx, "estimate"] = float(tampered_core.loc[core_idx, "estimate"]) + 0.314159
    tampered_core_path = td / "tampered_core_results.csv"; tampered_core.to_csv(tampered_core_path, index=False)
    proc = run(ROOT / "scripts/preflight.py", "--plan", plan, "--data", td / "clean.csv", "--results", tampered_core_path, "--cleaning-log", td / "cleaning_log.csv", "--cleaning-report", td / "cleaning_report.json", "--sensitivity-results", td / "sensitivity.csv", "--report", td / "tampered_core_preflight.json", expect_fail=True)
    core_text = proc.stdout + proc.stderr + (td / "tampered_core_preflight.json").read_text()
    assert "deterministic reconciliation mismatch for estimate" in core_text

    tampered_sens = pd.read_csv(td / "sensitivity.csv")
    sens_idx = tampered_sens.index[0]
    tampered_sens.loc[sens_idx, "estimate"] = float(tampered_sens.loc[sens_idx, "estimate"]) + 0.271828
    tampered_sens_path = td / "tampered_sensitivity.csv"; tampered_sens.to_csv(tampered_sens_path, index=False)
    proc = run(ROOT / "scripts/preflight.py", "--plan", plan, "--data", td / "clean.csv", "--results", td / "results.csv", "--cleaning-log", td / "cleaning_log.csv", "--cleaning-report", td / "cleaning_report.json", "--sensitivity-results", tampered_sens_path, "--report", td / "tampered_sensitivity_preflight.json", expect_fail=True)
    sens_text = proc.stdout + proc.stderr + (td / "tampered_sensitivity_preflight.json").read_text()
    assert "deterministic sensitivity reconciliation mismatch for estimate" in sens_text

    duplicate_sens = pd.concat([pd.read_csv(td / "sensitivity.csv"), pd.read_csv(td / "sensitivity.csv").iloc[[0]]], ignore_index=True)
    duplicate_sens_path = td / "duplicate_sensitivity.csv"; duplicate_sens.to_csv(duplicate_sens_path, index=False)
    proc = run(ROOT / "scripts/preflight.py", "--plan", plan, "--data", td / "clean.csv", "--results", td / "results.csv", "--cleaning-log", td / "cleaning_log.csv", "--cleaning-report", td / "cleaning_report.json", "--sensitivity-results", duplicate_sens_path, "--report", td / "duplicate_sensitivity_preflight.json", expect_fail=True)
    dup_sens_text = proc.stdout + proc.stderr + (td / "duplicate_sensitivity_preflight.json").read_text()
    assert "duplicate sensitivity_id" in dup_sens_text

    tampered_mult = pd.read_csv(td / "results.csv")
    family_mask = tampered_mult["multiplicity_family"].fillna("").astype(str).str.len() > 0
    if family_mask.any():
        idx = tampered_mult.index[family_mask][0]
        tampered_mult.loc[idx, "p_adjusted"] = min(1.0, float(tampered_mult.loc[idx, "p_adjusted"]) + 0.12345)
        tampered_mult_path = td / "tampered_multiplicity_results.csv"; tampered_mult.to_csv(tampered_mult_path, index=False)
        proc = run(ROOT / "scripts/preflight.py", "--plan", plan, "--data", td / "clean.csv", "--results", tampered_mult_path, "--cleaning-log", td / "cleaning_log.csv", "--cleaning-report", td / "cleaning_report.json", "--sensitivity-results", td / "sensitivity.csv", "--report", td / "tampered_mult_preflight.json", expect_fail=True)
        assert "Multiplicity adjusted p-values" in (proc.stdout + proc.stderr + (td / "tampered_mult_preflight.json").read_text())

    old_version = pd.read_csv(td / "results.csv")
    old_version["skill_version"] = "1.2.1"
    old_version_path = td / "old_version_results.csv"; old_version.to_csv(old_version_path, index=False)
    proc = run(ROOT / "scripts/preflight.py", "--plan", plan, "--data", td / "clean.csv", "--results", old_version_path, "--cleaning-log", td / "cleaning_log.csv", "--cleaning-report", td / "cleaning_report.json", "--sensitivity-results", td / "sensitivity.csv", "--report", td / "old_version_preflight.json", expect_fail=True)
    assert "skill_version" in (proc.stdout + proc.stderr + (td / "old_version_preflight.json").read_text())

    print("self-test: JSON portability", flush=True)
    # 7) JSON artifacts must be standards-compliant: no NaN/Infinity tokens.
    for jp in [td / "results.json", td / "all_results.json", td / "tech_ok_report.json"]:
        text = jp.read_text()
        assert "NaN" not in text and "Infinity" not in text and "-Infinity" not in text

print("scientific-data-analysis self-test: PASS")
