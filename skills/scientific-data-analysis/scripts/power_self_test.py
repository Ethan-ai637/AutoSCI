#!/usr/bin/env python3
from __future__ import annotations

import math
from copy import deepcopy

from _power import expand_and_calculate, welch_power, paired_power, welch_contrast_power
from validate_power_plan import validate


def base_plan():
    return {
        "power_plan_schema_version": "1.1",
        "planning_id": "selftest",
        "plan_version": "1.0",
        "research_question": "prospective planning self-test",
        "unit_of_analysis": "subject",
        "alpha": 0.05,
        "target_power": 0.8,
        "alternative": "two-sided",
        "planning_items": [],
    }


def main():
    plan = base_plan()
    plan["planning_items"] = [
        {
            "planning_item_id": "welch_n",
            "type": "welch_two_group_mean",
            "solve_for": "sample_size",
            "mean_difference": 5.0,
            "sd_a": 10.0,
            "sd_b": 12.0,
            "allocation_ratio_b_to_a": 1.0,
            "attrition_rate": 0.1,
            "assumption_source": {"kind": "scientific_threshold", "reference": "self-test"},
            "scenarios": [{"scenario_id": "small", "overrides": {"mean_difference": 4.0}}],
        },
        {
            "planning_item_id": "paired_mde",
            "type": "paired_mean",
            "solve_for": "minimum_detectable_effect",
            "sd_difference": 8.0,
            "n_pairs": 40,
            "assumption_source": {"kind": "external_evidence", "reference": "self-test"},
        },
        {
            "planning_item_id": "contrast_n",
            "type": "welch_contrast",
            "solve_for": "sample_size",
            "contrast_effect": 5.0,
            "contrast_terms": [
                {"level": "A", "weight": -1.0, "sd": 10.0, "allocation_ratio": 1.0},
                {"level": "B", "weight": 0.5, "sd": 12.0, "allocation_ratio": 1.0},
                {"level": "C", "weight": 0.5, "sd": 14.0, "allocation_ratio": 1.5}
            ],
            "attrition_rate": 0.1,
            "assumption_source": {"kind": "scientific_threshold", "reference": "self-test contrast"},
            "scenarios": [{"scenario_id": "more_variability", "overrides": {"contrast_terms": [
                {"level": "A", "weight": -1.0, "sd": 12.0, "allocation_ratio": 1.0},
                {"level": "B", "weight": 0.5, "sd": 14.0, "allocation_ratio": 1.0},
                {"level": "C", "weight": 0.5, "sd": 16.0, "allocation_ratio": 1.5}
            ]}}],
        },
        {
            "planning_item_id": "prop_power",
            "type": "independent_proportions",
            "solve_for": "prospective_power",
            "p_a": 0.30,
            "p_b": 0.45,
            "n_a": 160,
            "n_b": 160,
            "assumption_source": {"kind": "external_evidence", "reference": "self-test"},
        },
    ]
    errors, warnings = validate(plan)
    assert not errors, errors
    rows = expand_and_calculate(plan)
    assert len(rows) == 6
    by_key = {(r["planning_item_id"], r["scenario_id"]): r for r in rows}

    w = by_key[("welch_n", "base")]
    assert int(w["n_a_analyzable"]) == 78 and int(w["n_b_analyzable"]) == 78
    assert w["achieved_power"] >= 0.8
    prev_power = welch_power(5.0, 10.0, 12.0, 77, 77, 0.05, "two-sided")[0]
    assert prev_power < 0.8
    assert int(w["n_a_enroll"]) == 87 and int(w["n_b_enroll"]) == 87
    assert by_key[("welch_n", "small")]["n_total_analyzable"] > w["n_total_analyzable"]

    pm = by_key[("paired_mde", "base")]
    assert math.isclose(pm["minimum_detectable_effect"], 3.6340555174671545, rel_tol=1e-9)
    assert math.isclose(pm["achieved_power"], 0.8, rel_tol=1e-9, abs_tol=1e-9)
    assert paired_power(pm["minimum_detectable_effect"], 8.0, 40, 0.05, "two-sided")[0] >= 0.799999999

    cn = by_key[("contrast_n", "base")]
    assert int(cn["n_reference_analyzable"]) == 54
    assert int(cn["n_total_analyzable"]) == 189
    assert cn["achieved_power"] >= 0.8
    prev_terms = [
        {"weight": -1.0, "sd": 10.0, "n": 53},
        {"weight": 0.5, "sd": 12.0, "n": 53},
        {"weight": 0.5, "sd": 14.0, "n": 80},
    ]
    assert welch_contrast_power(5.0, prev_terms, 0.05, "two-sided")[0] < 0.8
    assert cn["contrast_orientation"] == "-1*A + 0.5*B + 0.5*C"
    assert by_key[("contrast_n", "more_variability")]["n_total_analyzable"] > cn["n_total_analyzable"]

    # Allocation-ratio scale is irrelevant; only relative ratios define the design.
    scaled_alloc = base_plan(); scaled_alloc["planning_items"] = [{
        "planning_item_id": "scaled", "type": "welch_contrast", "solve_for": "sample_size",
        "contrast_effect": 5.0,
        "contrast_terms": [
            {"level": "A", "weight": -1.0, "sd": 10.0, "allocation_ratio": 2.0},
            {"level": "B", "weight": 0.5, "sd": 12.0, "allocation_ratio": 2.0},
            {"level": "C", "weight": 0.5, "sd": 14.0, "allocation_ratio": 3.0}
        ],
        "assumption_source": {"kind": "scenario", "reference": "self-test"},
    }]
    errors, _ = validate(scaled_alloc); assert not errors, errors
    scaled = expand_and_calculate(scaled_alloc)[0]
    assert scaled["group_n_analyzable_json"] == cn["group_n_analyzable_json"]

    pr = by_key[("prop_power", "base")]
    assert math.isclose(pr["achieved_power"], 0.794243754499499, rel_tol=1e-10)
    assert math.isclose(pr["assumed_effect"], 0.15, rel_tol=1e-12)
    assert pr["normal_approximation_adequacy"] == "adequate_by_conservative_count_rule"
    assert math.isclose(pr["min_expected_cell_count"], 48.0, rel_tol=1e-12)

    # Additional solve-mode coverage: binary sample size and Welch MDE.
    prop_n = base_plan(); prop_n["planning_items"] = [{
        "planning_item_id": "prop_n", "type": "independent_proportions", "solve_for": "sample_size",
        "p_a": 0.30, "p_b": 0.45, "allocation_ratio_b_to_a": 1.0,
        "assumption_source": {"kind": "scenario", "reference": "self-test"},
    }]
    errors, _ = validate(prop_n); assert not errors, errors
    prop_n_row = expand_and_calculate(prop_n)[0]
    assert int(prop_n_row["n_a_analyzable"]) == 163 and int(prop_n_row["n_b_analyzable"]) == 163
    assert prop_n_row["achieved_power"] >= 0.8

    welch_mde = base_plan(); welch_mde["planning_items"] = [{
        "planning_item_id": "wmde", "type": "welch_two_group_mean", "solve_for": "minimum_detectable_effect",
        "sd_a": 10.0, "sd_b": 12.0, "n_a": 50, "n_b": 60,
        "assumption_source": {"kind": "scenario", "reference": "self-test"},
    }]
    errors, _ = validate(welch_mde); assert not errors, errors
    wmde = expand_and_calculate(welch_mde)[0]
    assert math.isclose(wmde["minimum_detectable_effect"], 5.929551386071438, rel_tol=1e-9)
    assert math.isclose(wmde["actual_allocation_ratio_b_to_a"], 1.2, rel_tol=1e-12)

    contrast_power_plan = base_plan(); contrast_power_plan["planning_items"] = [{
        "planning_item_id": "cp", "type": "welch_contrast", "solve_for": "prospective_power",
        "contrast_effect": 5.0,
        "contrast_terms": [
            {"level": "A", "weight": -1.0, "sd": 10.0, "n": 60},
            {"level": "B", "weight": 0.5, "sd": 12.0, "n": 60},
            {"level": "C", "weight": 0.5, "sd": 14.0, "n": 90}
        ],
        "assumption_source": {"kind": "external_evidence", "reference": "self-test contrast"},
    }]
    errors, _ = validate(contrast_power_plan); assert not errors, errors
    cp = expand_and_calculate(contrast_power_plan)[0]
    assert math.isclose(cp["achieved_power"], 0.8417451116293528, rel_tol=1e-10)
    terms = [
        {"weight": -1.0, "sd": 10.0, "n": 60},
        {"weight": 0.5, "sd": 12.0, "n": 60},
        {"weight": 0.5, "sd": 14.0, "n": 90},
    ]
    assert math.isclose(welch_contrast_power(5.0, terms, 0.05, "two-sided")[0], cp["achieved_power"], rel_tol=1e-12)

    contrast_mde_plan = deepcopy(contrast_power_plan)
    contrast_mde_plan["planning_items"][0]["solve_for"] = "minimum_detectable_effect"
    contrast_mde_plan["planning_items"][0].pop("contrast_effect")
    errors, _ = validate(contrast_mde_plan); assert not errors, errors
    cmde = expand_and_calculate(contrast_mde_plan)[0]
    assert math.isclose(cmde["minimum_detectable_effect"], 4.729803728567496, rel_tol=1e-9)
    assert cmde["meets_target_power"] is True

    # Planned-contrast validation preserves the estimand and solve-mode fields.
    bad_weights = deepcopy(contrast_power_plan)
    bad_weights["planning_items"][0]["contrast_terms"][2]["weight"] = 0.6
    errors, _ = validate(bad_weights); assert any("weights must sum to zero" in e for e in errors)

    bad_scenario_contrast = deepcopy(plan)
    contrast_item = deepcopy(bad_scenario_contrast["planning_items"][2])
    contrast_item["scenarios"] = [{"scenario_id": "bad_weight", "overrides": {"contrast_terms": [
        {"level": "A", "weight": -1.0, "sd": 10.0, "allocation_ratio": 1.0},
        {"level": "B", "weight": 0.4, "sd": 12.0, "allocation_ratio": 1.0},
        {"level": "C", "weight": 0.6, "sd": 14.0, "allocation_ratio": 1.5}
    ]}}]
    bad_scenario_contrast["planning_items"] = [contrast_item]
    errors, _ = validate(bad_scenario_contrast); assert any("preserve the exact typed levels" in e for e in errors)

    # One-sided orientation is explicit and mechanically enforced.
    one = base_plan()
    one["alternative"] = "larger"
    one["planning_items"] = [{
        "planning_item_id": "one", "type": "paired_mean", "solve_for": "sample_size",
        "mean_difference": 2.0, "sd_difference": 5.0,
        "assumption_source": {"kind": "scenario", "reference": "self-test"},
    }]
    errors, _ = validate(one); assert not errors, errors
    one_bad = deepcopy(one); one_bad["planning_items"][0]["mean_difference"] = -2.0
    errors, _ = validate(one_bad); assert any("must be > 0" in e for e in errors)

    # Current-study analysis/data fields are prohibited in the prospective plan.
    contaminated = deepcopy(plan); contaminated["input"] = {"path": "completed-study.csv"}
    errors, _ = validate(contaminated); assert any("separate prospective workflow" in e for e in errors)

    # Unsupported MDE for proportions is rejected rather than approximated silently.
    bad_mde = base_plan(); bad_mde["planning_items"] = [{
        "planning_item_id": "bad", "type": "independent_proportions", "solve_for": "minimum_detectable_effect",
        "p_a": 0.2, "p_b": 0.3,
        "assumption_source": {"kind": "scenario", "reference": "self-test"},
    }]
    errors, _ = validate(bad_mde); assert any("minimum_detectable_effect is not supported" in e for e in errors)

    # Scenario overrides are restricted to numeric/design assumptions, not type/solve target.
    bad_scenario = deepcopy(plan)
    bad_scenario["planning_items"][0]["scenarios"] = [{"scenario_id": "bad", "overrides": {"type": "paired_mean"}}]
    errors, _ = validate(bad_scenario); assert any("unsupported or have no effect" in e for e in errors)


    # Scenario overrides must affect the selected solve mode; no-op overrides are rejected.
    no_op_ratio = base_plan(); no_op_ratio["planning_items"] = [{
        "planning_item_id": "noop_ratio", "type": "welch_two_group_mean", "solve_for": "prospective_power",
        "mean_difference": 2.0, "sd_a": 5.0, "sd_b": 6.0, "n_a": 40, "n_b": 50,
        "assumption_source": {"kind": "scenario", "reference": "self-test"},
        "scenarios": [{"scenario_id": "bad", "overrides": {"allocation_ratio_b_to_a": 2.0}}],
    }]
    errors, _ = validate(no_op_ratio); assert any("no effect" in e for e in errors)

    no_op_n = base_plan(); no_op_n["planning_items"] = [{
        "planning_item_id": "noop_n", "type": "paired_mean", "solve_for": "sample_size",
        "mean_difference": 2.0, "sd_difference": 5.0,
        "assumption_source": {"kind": "scenario", "reference": "self-test"},
        "scenarios": [{"scenario_id": "bad", "overrides": {"n_pairs": 100}}],
    }]
    errors, _ = validate(no_op_n); assert any("no effect" in e for e in errors)

    no_op_effect = base_plan(); no_op_effect["planning_items"] = [{
        "planning_item_id": "noop_effect", "type": "welch_two_group_mean", "solve_for": "minimum_detectable_effect",
        "sd_a": 5.0, "sd_b": 6.0, "n_a": 40, "n_b": 50,
        "assumption_source": {"kind": "scenario", "reference": "self-test"},
        "scenarios": [{"scenario_id": "bad", "overrides": {"mean_difference": 3.0}}],
    }]
    errors, _ = validate(no_op_effect); assert any("no effect" in e for e in errors)

    # Prospective-power target status uses the effective item-level target even when no top-level target is supplied.
    item_target = {
        "power_plan_schema_version": "1.1", "planning_id": "item-target", "plan_version": "1.0",
        "research_question": "self-test", "unit_of_analysis": "subject", "alpha": 0.05,
        "planning_items": [{
            "planning_item_id": "p", "type": "paired_mean", "solve_for": "prospective_power",
            "mean_difference": 1.0, "sd_difference": 2.0, "n_pairs": 30, "target_power": 0.8,
            "assumption_source": {"kind": "scenario", "reference": "self-test"},
        }],
    }
    errors, _ = validate(item_target); assert not errors, errors
    item_target_row = expand_and_calculate(item_target)[0]
    assert isinstance(item_target_row["meets_target_power"], bool)
    assert item_target_row["meets_target_power"] == (item_target_row["achieved_power"] >= 0.8)

    # Binary normal-approximation adequacy is explicit: extreme sparsity is
    # distinguishable from a merely sparse caution case and from an adequate case.
    extreme = base_plan(); extreme["planning_items"] = [{
        "planning_item_id": "extreme", "type": "independent_proportions", "solve_for": "sample_size",
        "p_a": 0.05, "p_b": 0.95,
        "assumption_source": {"kind": "scenario", "reference": "self-test"},
    }]
    errors, _ = validate(extreme); assert not errors, errors
    erow = expand_and_calculate(extreme)[0]
    assert erow["n_a_analyzable"] == 4 and erow["n_b_analyzable"] == 4
    assert erow["normal_approximation_adequacy"] == "poor_extreme_sparsity"
    assert math.isclose(erow["min_expected_cell_count"], 0.2, rel_tol=1e-12)

    caution = base_plan(); caution["planning_items"] = [{
        "planning_item_id": "caution", "type": "independent_proportions", "solve_for": "sample_size",
        "p_a": 0.01, "p_b": 0.05,
        "assumption_source": {"kind": "scenario", "reference": "self-test"},
    }]
    errors, _ = validate(caution); assert not errors, errors
    crow = expand_and_calculate(caution)[0]
    assert crow["normal_approximation_adequacy"] == "caution_sparse"
    assert 1.0 <= crow["min_expected_cell_count"] < 5.0

    print("scientific-data-analysis power self-test: PASS")


if __name__ == "__main__":
    main()
