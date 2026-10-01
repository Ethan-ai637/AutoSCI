#!/usr/bin/env python3
from __future__ import annotations

import argparse
import math
from pathlib import Path
import pandas as pd

from _common import read_json, read_artifact_csv, sha256_file, SKILL_VERSION


def fmt(v, digits=4):
    try:
        if pd.isna(v):
            return "NA"
    except Exception:
        pass
    if isinstance(v, bool):
        return str(v)
    try:
        x = float(v)
        if math.isfinite(x):
            if abs(x) >= 1000 or (abs(x) < 0.001 and x != 0):
                return f"{x:.3g}"
            return f"{x:.{digits}f}".rstrip("0").rstrip(".")
    except Exception:
        pass
    return str(v)


def main():
    ap = argparse.ArgumentParser(description="Build a deterministic prospective power/sample-size planning report")
    ap.add_argument("--plan", required=True)
    ap.add_argument("--results", required=True)
    ap.add_argument("--preflight")
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    plan = read_json(args.plan)
    results = read_artifact_csv(args.results)
    plan_hash = sha256_file(args.plan)
    if "plan_sha256" not in results.columns or set(results["plan_sha256"].dropna().astype(str)) != {plan_hash}:
        raise ValueError("Power results do not match the current power plan hash")
    if "skill_version" not in results.columns or set(results["skill_version"].dropna().astype(str)) != {SKILL_VERSION}:
        raise ValueError(f"Power results do not match current skill version {SKILL_VERSION}")
    preflight = read_json(args.preflight) if args.preflight else None

    lines = [
        f"# Prospective Power / Sample-Size Planning — {plan.get('planning_id')}",
        "",
        f"Skill version: `{SKILL_VERSION}`  ",
        f"Power-plan schema: `{plan.get('power_plan_schema_version')}`  ",
        f"Plan version: `{plan.get('plan_version')}`",
        "",
        "## 1. Planning question",
        "",
        plan.get("research_question", ""),
        "",
        "## 2. Non-negotiable scope",
        "",
        "- This is a **prospective design-planning** artifact, not a post-hoc interpretation of an already observed study result.",
        "- Power is conditional on the declared effect/variance/rate assumptions. It is not the probability that a scientific hypothesis is true.",
        "- A planned sample size does not correct bias, confounding, pseudoreplication, measurement error, model misspecification, or selective analysis.",
        "- `prospective_power` means design power under a prespecified effect assumption at a fixed analyzable sample size; it should not be computed by substituting the observed effect from the completed study.",
        "",
        "## 3. Global planning settings",
        "",
        f"- Alpha: {fmt(plan.get('alpha', 0.05))}",
        f"- Target power: {fmt(plan.get('target_power', 0.8))}",
        f"- Alternative: `{plan.get('alternative', 'two-sided')}`",
        f"- Unit of analysis: `{plan.get('unit_of_analysis')}`",
        "",
        "## 4. Planning results",
        "",
    ]

    by_id = {x["planning_item_id"]: x for x in plan.get("planning_items", [])}
    for _, r in results.iterrows():
        item = by_id.get(str(r.get("planning_item_id")), {})
        lines.append(f"### {r.get('planning_item_id')} — scenario `{r.get('scenario_id')}`")
        lines.append("")
        lines.append(f"- Design: `{r.get('type')}`; solve for `{r.get('solve_for')}`; method `{r.get('method')}`.")
        lines.append(f"- Alpha={fmt(r.get('alpha'))}; target power={fmt(r.get('target_power'))}; alternative=`{r.get('alternative')}`.")
        lines.append(f"- Assumption provenance: `{r.get('assumption_source_json')}`")
        if str(r.get("scenario_overrides_json", "{}")) != "{}":
            lines.append(f"- Scenario overrides: `{r.get('scenario_overrides_json')}`")
        typ = str(r.get("type"))
        if typ == "welch_two_group_mean":
            lines.append(f"- Assumed SDs: A={fmt(r.get('sd_a'))}, B={fmt(r.get('sd_b'))}; effect metric: group B − group A raw mean difference.")
        elif typ == "welch_contrast":
            lines.append(f"- Planned contrast: `{r.get('contrast_orientation')}`; effect metric: raw linear-contrast scale.")
            lines.append(f"- Declared contrast/group assumptions: `{r.get('contrast_terms_json')}`")
        elif typ == "paired_mean":
            lines.append(f"- Assumed SD of paired differences: {fmt(r.get('sd_difference'))}.")
        elif typ == "independent_proportions":
            lines.append(f"- Assumed event rates: A={fmt(r.get('p_a'))}, B={fmt(r.get('p_b'))}; risk difference={fmt(r.get('assumed_effect'))}; Cohen h={fmt(r.get('cohen_h'))}.")
            lines.append(
                f"- Normal-approximation adequacy: `{r.get('normal_approximation_adequacy')}`; "
                f"minimum expected event/non-event count under the declared rates={fmt(r.get('min_expected_cell_count'))} "
                f"(A events={fmt(r.get('expected_events_a'))}, A non-events={fmt(r.get('expected_nonevents_a'))}, "
                f"B events={fmt(r.get('expected_events_b'))}, B non-events={fmt(r.get('expected_nonevents_b'))})."
            )

        if pd.notna(r.get("minimum_detectable_effect")):
            lines.append(f"- Minimum detectable effect at the declared target power: **{fmt(r.get('minimum_detectable_effect'))}** ({r.get('effect_metric')}).")
        elif pd.notna(r.get("assumed_effect")):
            lines.append(f"- Effect assumption: {fmt(r.get('assumed_effect'))} ({r.get('effect_metric')}).")

        if pd.notna(r.get("n_a_analyzable")):
            lines.append(f"- Analyzable sample: A={int(float(r.get('n_a_analyzable')))}, B={int(float(r.get('n_b_analyzable')))}, total={int(float(r.get('n_total_analyzable')))}; actual B:A allocation={fmt(r.get('actual_allocation_ratio_b_to_a'))}.")
            lines.append(f"- Enrollment after attrition inflation: A={int(float(r.get('n_a_enroll')))}, B={int(float(r.get('n_b_enroll')))}, total={int(float(r.get('n_total_enroll')))}.")
        elif pd.notna(r.get("n_pairs_analyzable")):
            lines.append(f"- Analyzable pairs: {int(float(r.get('n_pairs_analyzable')))}; enrollment target after attrition inflation: {int(float(r.get('n_pairs_enroll')))} pairs.")
        elif typ == "welch_contrast" and pd.notna(r.get("n_total_analyzable")):
            lines.append(f"- Analyzable group sizes: `{r.get('group_n_analyzable_json')}`; total={int(float(r.get('n_total_analyzable')))}.")
            lines.append(f"- Enrollment group sizes after attrition inflation: `{r.get('group_n_enroll_json')}`; total={int(float(r.get('n_total_enroll')))}.")
            if pd.notna(r.get("n_reference_analyzable")):
                lines.append(f"- Sample-size mode solved the minimum-allocation-ratio reference-group n={int(float(r.get('n_reference_analyzable')))} and then rounded each declared allocation ratio upward.")
        lines.append(f"- Prospective power under these assumptions: **{fmt(r.get('achieved_power'))}**.")
        if r.get("solve_for") == "sample_size":
            lines.append("- Sample-size search rounds integer group sizes upward and then recomputes power at the actual recommended allocation.")
        lines.append("")

    lines += ["## 5. Interpretation and limitations", ""]
    lines += [
        "- `welch_two_group_mean` uses a noncentral-t approximation with Welch–Satterthwaite degrees of freedom under the declared group SDs; it is aligned with unequal-variance two-group inference but remains a planning approximation.",
        "- `welch_contrast` plans a prespecified independent-group linear contrast using sum(c_i^2 sigma_i^2 / n_i) and Welch–Satterthwaite degrees of freedom. The contrast weights define the scientific estimand and are never optimized from data.",
        "- `paired_mean` plans on the distribution of within-pair differences; the assumed SD must therefore be the SD of those differences, not the marginal SD of either condition.",
        "- `independent_proportions` uses a two-proportion normal approximation with pooled variance under the null and non-pooled variance under the alternative; Cohen's h is also reported descriptively. The planner records expected event/non-event counts under the declared rates. A minimum expected count below 5 triggers a caution warning; below 1 is an extreme-sparsity release failure. These thresholds are conservative QA heuristics, not guarantees of approximation quality; exact or simulation-based planning may still be appropriate.",
        "- Attrition inflation assumes the declared attrition rate and does not model informative dropout or differential missingness.",
        "- Scenario rows are assumption-sensitivity analyses, not evidence that one scenario is more likely than another.",
        "- Clustered, repeated multi-timepoint, survival, adaptive, sequential, equivalence/noninferiority, and complex regression designs are outside the v1.6 core planning workflow.",
        "",
        "## 6. QA",
        "",
    ]
    if preflight:
        lines.append(f"- Power preflight: **{preflight.get('status')}**")
        lines.append(f"- Deterministic power reconciliation: **{preflight.get('deterministic_power_reconciliation')}**")
        lines.append(f"- Errors: {len(preflight.get('errors', []))}; warnings: {len(preflight.get('warnings', []))}.")
        for w in preflight.get("warnings", []):
            lines.append(f"  - Warning: {w}")
        for e in preflight.get("errors", []):
            lines.append(f"  - Error: {e}")
    else:
        lines.append("- Power preflight report not supplied.")

    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out).write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {args.out}")


if __name__ == "__main__":
    main()
