# scientific-data-analysis v1.6.1

An audit-first AutoSCI skill for reproducible scientific tabular-data analysis **and prospective power/sample-size planning**.

## Design

The skill separates **scientific judgment** from **deterministic execution**:

- the researcher/agent defines the question, estimand, independent unit, variable roles, exclusions, missing-data strategy, model/test family, multiplicity family, equivalence margins when relevant, sensitivity questions, **prospective design assumptions for power planning**, and interpretation;
- Python tooling profiles data, executes declared cleaning rules, rejects unsafe structural shortcuts, runs prespecified statistics, computes effect sizes/uncertainty, applies multiplicity correction, executes declared sensitivity analyses, **solves declared prospective power/sample-size problems**, generates reproducible plots, reconciles hashes, assembles factual reports, and audits provenance.

It intentionally refuses to auto-select a statistical test from observed p-values or from a normality-test threshold.

## Core workflows

Post-data inference remains the analysis-schema `1.4` workflow:

```text
raw data
  -> profile
  -> schema-validated analysis plan
  -> audited cleaning
  -> analysis-ready data
  -> descriptive inspection
  -> prespecified inference
  -> effect size + CI
  -> multiplicity
  -> declared sensitivity analyses
  -> reproducible plots
  -> deterministic report
  -> preflight reconciliation
  -> provenance manifest
```

v1.5 introduced a **separate pre-data planning workflow**; v1.6 advances that contract to power-plan schema `1.1`:

```text
research/design question
  -> independent analysis unit
  -> effect/variance/rate assumptions + provenance
  -> alpha / target power / sidedness / allocation
  -> schema-validated power plan
  -> deterministic sample-size / power / MDE calculation
  -> assumption scenarios
  -> planning plots + report
  -> deterministic power preflight
  -> provenance manifest
```

The power planner never reads a completed-study dataset and never treats observed/post-hoc power as evidence for or against a scientific conclusion.

## v1.6.1 release hardening

v1.6.1 keeps `analysis_plan_schema_version = "1.4"` and `power_plan_schema_version = "1.1"`; there are **no statistical or plan-schema changes**. This patch makes the skill easier to publish and verify as a GitHub repository component:

- removes stale version-history prose from the current README/SKILL contract and keeps release history in `CHANGELOG.md`;
- makes `doctor.py` enforce the actual runtime contract (`Python >=3.10` and `openpyxl` as a required dependency because XLSX/XLSM scalar-preserving input is a supported core path);
- adds `scripts/release_check.py`, a one-command release gate covering version/schema consistency, source compilation, dependency diagnostics, bundled-plan validation, and both self-test suites;
- keeps the v1.6 planned-contrast prospective-design workflow unchanged.

For historical release notes and migrations, see [`CHANGELOG.md`](CHANGELOG.md).

## Current v1.6 capabilities

Post-data inference uses analysis-plan schema `1.4`. Prospective planning uses power-plan schema `1.1`. The v1.6 planning addition is `welch_contrast`, aligned with the post-data planned-contrast inference already supported by the skill.

- Plan an exact prespecified linear contrast across 2+ independent groups with separate SD assumptions.
- `sample_size` solves a common reference-group n under declared per-group allocation ratios, rounds each group upward, and recomputes power at the actual integer allocation.
- `prospective_power` and `minimum_detectable_effect` accept explicit analyzable n for every group.
- Power uses `Var(contrast) = sum(c_i^2 sigma_i^2 / n_i)` with generalized Welch–Satterthwaite degrees of freedom and a noncentral-t calculation.
- Contrast levels and weights define the estimand and are immutable across scenario overrides.
- The v1.5 binary-proportion adequacy guard, solve-aware scenario rules, deterministic power reconciliation, and strict separation from observed/post-hoc power remain active.

Migration from v1.6.0: no schema migration. Re-run version-bound artifacts when upgrading.

## Install

Requires **Python 3.10+**. Install the declared runtime dependencies, then run the environment diagnostic.

```bash
cp -R scientific-data-analysis "${CODEX_HOME:-$HOME/.codex}/skills/"
python -m pip install -r scientific-data-analysis/requirements.txt
python scientific-data-analysis/scripts/doctor.py
```

## Self-test

```bash
python scientific-data-analysis/scripts/self_test.py
python scientific-data-analysis/scripts/power_self_test.py
```

## Release check

Use the quick gate during local iteration:

```bash
python scientific-data-analysis/scripts/release_check.py
```

Before a GitHub release or merge, run the full gate:

```bash
python scientific-data-analysis/scripts/release_check.py --full
```

The quick gate verifies version/schema consistency across `VERSION`, code, templates, examples and documentation; compiles all scripts; runs `doctor.py`; and validates bundled analysis/power plans. `--full` additionally runs both complete self-test suites. A nonzero exit means the skill should not be released.

The post-data self-test exercises the 16 core inference paths plus numeric-binary missingness, multiplicity reconciliation, deterministic rejection of tampered core result values, v1.4 multi-group/contrast/count input guards, GLM covariance-label validation, duplicate-pairing, technical-replicate metadata/provenance, sparse-Fisher, perfect-separation, deterministic-resampling, typed contingency-boundary rejection, model-plot complete-case cohort reconciliation, stale-artifact, and JSON-portability guardrails.

## Supported core inference in v1.4

- Welch independent t-test
- paired t-test
- Mann–Whitney U
- Wilcoxon signed-rank
- Pearson correlation
- Spearman correlation
- numeric-predictor OLS regression with optional HC3 robust SE
- restricted two-group ANCOVA with numeric covariates
- binary logistic regression with numeric predictors, explicit event orientation, and HC0/nonrobust GLM covariance
- Welch one-way ANOVA across three or more declared independent groups
- Welch–Satterthwaite planned linear contrasts across two or more declared independent groups
- Poisson regression for count outcomes with numeric predictors, optional exposure/offset, and HC0/nonrobust GLM covariance
- chi-square association
- ordered 2×2 Fisher exact test, with explicit zero-cell OR/CI handling
- independent-samples TOST equivalence testing
- paired TOST equivalence testing
- Holm / Bonferroni / Benjamini–Hochberg corrections

The runner never auto-picks among these methods. The analysis plan must specify the method.

## Prospective power/sample-size workflow in v1.6

Validate and run a power plan independently of the post-data analysis plan:

```bash
python scientific-data-analysis/scripts/validate_power_plan.py power_plan.json

python scientific-data-analysis/scripts/run_power.py \
  --plan power_plan.json \
  --out planning/power_results.csv

python scientific-data-analysis/scripts/preflight_power.py \
  --plan power_plan.json \
  --results planning/power_results.csv \
  --report planning/power_preflight.json

python scientific-data-analysis/scripts/plot_power.py \
  --plan power_plan.json \
  --results planning/power_results.csv \
  --outdir planning/figures

python scientific-data-analysis/scripts/build_power_report.py \
  --plan power_plan.json \
  --results planning/power_results.csv \
  --preflight planning/power_preflight.json \
  --out planning/power_report.md
```

Then freeze provenance with the existing manifest tool:

```bash
python scientific-data-analysis/scripts/make_manifest.py \
  --plan power_plan.json \
  --inputs planning/power_results.csv planning/power_preflight.json planning/power_report.md \
  --out planning/provenance.json
```

Use `templates/power_plan.template.json` and `examples/power_plan.json`. Read `references/power_sample_size.md` before planning when effect assumptions, sidedness, attrition, or pilot/external evidence are non-trivial.

**Do not** put a completed-study input dataset or inference results into the power plan. `prospective_power` is only prospective design power at a fixed planned analyzable n under an effect assumption; it is not observed/post-hoc power.

## Missing-data contract

The v1.4 deterministic core supports only explicit complete-case analysis:

```json
"missing_data": {
  "strategy": "complete_case",
  "report_per_analysis": true,
  "imputation": "none"
}
```

This is intentionally conservative. The skill records how many candidate units were excluded from each analysis because required analysis variables were missing or nonnumeric. Multiple imputation, inverse-probability missingness models, and other specialized strategies are explicit handoff cases rather than silent approximations.

## Reproducible resampling contract

```json
"resampling": {
  "method": "percentile",
  "n_resamples": 2000
}
```

Selected intervals use deterministic percentile bootstrap. Each analysis item's RNG stream is derived from the global seed and the stable `analysis_item_id`, so reordering the analysis list does not change that item's bootstrap stream.

## Formal equivalence testing

A difference test with `p >= 0.05` does not establish equivalence. v1.2+ includes TOST analyses that require margins before execution:

```json
{
  "analysis_item_id": "primary_equivalence",
  "type": "equivalence_tost_independent",
  "outcome": "response",
  "group": "group",
  "group_a": "control",
  "group_b": "treatment",
  "equivalence_margin_lower": -2.0,
  "equivalence_margin_upper": 2.0,
  "equivalence_alpha": 0.05
}
```

The result records both one-sided p-values, the equivalence CI, the margins, and a deterministic equivalence conclusion. Margins are scientific inputs and must not be chosen after seeing the result.

## Controlled ANCOVA core

`ancova_two_group` is intentionally narrow: two declared groups, numeric covariates, additive linear adjustment, common slopes, optional HC3 robust SE. It reports the adjusted group B minus group A mean difference and model diagnostics.

Interactions, nonlinear terms, categorical covariates requiring encoding decisions, repeated/nested data, or more complex factorial designs should be handed off to a broader model rather than forced into the core.

## Binary logistic regression core

`logistic_regression` requires explicit `event_level` and `nonevent_level`, numeric predictors, and a `report_predictor` when more than one predictor is present. It reports an oriented odds ratio + CI and records convergence/conditioning diagnostics.

Rare-event corrections, penalized/Firth methods, multinomial/ordinal outcomes, separation-sensitive analysis, and categorical-predictor encoding strategies remain explicit handoff cases.

## Multi-group Welch ANOVA core

`welch_anova` requires an explicit ordered `group_levels` list with at least three groups. The runner does not discover a favorable subset of groups from the data. It tests the global null of equal declared group means under unequal variances and reports a non-directional omnibus effect size.

Example:

```json
{
  "analysis_item_id": "dose_omnibus",
  "type": "welch_anova",
  "outcome": "response",
  "group": "dose_group",
  "group_levels": ["control", "low", "high"],
  "multiplicity_family": "dose_family"
}
```

A significant omnibus result does not identify which groups differ. Prespecified pairwise comparisons should be separate `independent_t` items and share a declared multiplicity family. Arbitrary linear contrasts, factorial interactions, repeated measures, and clustered designs remain broader-model handoffs.

## Poisson count-regression core

`welch_contrast` encodes a scientific linear contrast directly instead of approximating it with a collection of pairwise tests. Use `contrast_terms` such as:

```json
{
  "analysis_item_id": "treatment_average_vs_control",
  "type": "welch_contrast",
  "outcome": "response",
  "group": "arm",
  "contrast_terms": [
    {"level": "treatment_A", "weight": 0.5},
    {"level": "treatment_B", "weight": 0.5},
    {"level": "control", "weight": -1.0}
  ],
  "multiplicity_family": "planned_contrasts"
}
```

The weights define the raw-scale estimand. They must sum to zero and are never normalized automatically. This core path is only for independent groups; repeated measures, factorial interaction contrasts, and covariate-adjusted general linear hypotheses require a broader model.

`poisson_regression` requires a nonnegative integer outcome and numeric predictors. An optional `exposure` column must be strictly positive and is transformed to `log(exposure)` internally; alternatively, an already-defined numeric `offset` column may be supplied. Both cannot be declared at once.

```json
{
  "analysis_item_id": "event_rate",
  "type": "poisson_regression",
  "outcome": "event_count",
  "predictors": ["treatment", "baseline_score"],
  "report_predictor": "treatment",
  "exposure": "person_time",
  "robust_se": "HC0"
}
```

The reported effect is an incidence-rate ratio for a one-unit increase in the declared predictor, conditional on the other numeric predictors. Pearson dispersion and zero fraction are surfaced as diagnostics. Strong overdispersion or excess zeros are reasons to inspect negative-binomial, hurdle, zero-inflated, or other specialist count models rather than treating Poisson as universally adequate. For visualization, use plot kind `count_regression`; with exposure it displays observed count/exposure rates and does not pretend that a raw scatterplot is the covariate-adjusted model fit.

## Executable sensitivity layer

A sensitivity item references a base analysis and may apply a safe declared subset rule and/or a limited analysis override. v1.2+ requires the plan to state the scientific relationship between estimands:

```json
"estimand_relation": "same"
```

Allowed values are `same`, `different`, or `uncertain`. The runner no longer guesses this from the result name. Numeric estimate changes are only interpreted directly when the plan explicitly declares the same estimand. In the current v1.4.x workflow, preflight also reruns each declared sensitivity analysis and reconciles every generated field; sensitivity artifacts are therefore audited by content, not only by IDs/hashes and copied base values. Duplicate `sensitivity_id` rows fail preflight.

```bash
python scientific-data-analysis/scripts/run_sensitivity.py \
  --data analysis/data.clean.csv \
  --plan analysis_plan.json \
  --base-results analysis/results.csv \
  --out-csv analysis/sensitivity_results.csv \
  --out-json analysis/sensitivity_results.json
```

## Deliberate escalation cases

Mixed-effects/repeated-measures models, GEE, survival analysis, Bayesian hierarchical models, high-dimensional omics, complex survey inference, compositional models, multinomial/ordinal outcomes, rare-event or penalized logistic models, negative-binomial/hurdle/zero-inflated or clustered-count models, arbitrary factorial/interacted ANOVA, repeated/multilevel or covariate-adjusted general linear contrasts, **clustered/survival/adaptive/equivalence/complex-regression power planning beyond the explicit v1.6 core**, multiple imputation, and causal-identification workflows are not silently approximated by a simpler test. The skill produces an explicit specialist handoff instead.

## Package layout

```text
scientific-data-analysis/
├── SKILL.md
├── README.md
├── VERSION
├── CHANGELOG.md
├── requirements.txt
├── scripts/
│   ├── _common.py
│   ├── _power.py
│   ├── doctor.py
│   ├── profile_data.py
│   ├── validate_plan.py
│   ├── validate_power_plan.py
│   ├── clean_data.py
│   ├── run_stats.py
│   ├── run_power.py
│   ├── run_sensitivity.py
│   ├── plot_results.py
│   ├── plot_power.py
│   ├── build_report.py
│   ├── build_power_report.py
│   ├── preflight.py
│   ├── preflight_power.py
│   ├── make_manifest.py
│   ├── self_test.py
│   └── power_self_test.py
├── references/
│   ├── data_cleaning.md
│   ├── statistical_decisions.md
│   ├── planned_contrasts.md
│   ├── effect_size_uncertainty.md
│   ├── sensitivity_analysis.md
│   ├── power_sample_size.md
│   ├── reproducible_plotting.md
│   └── reporting_checklist.md
├── templates/
│   ├── analysis_plan.template.json
│   ├── power_plan.template.json
│   └── data_dictionary.template.csv
└── examples/
    ├── analysis_plan.json
    ├── power_plan.json
    ├── toy_data.csv
    ├── planned_contrast_plan.json
    └── toy_multigroup.csv
```
