---
name: scientific-data-analysis
description: Clean, audit, statistically analyze, quantify effect sizes and uncertainty, run declared sensitivity analyses, reproducibly visualize scientific tabular data, and prospectively plan power/sample size with explicit provenance. Use for experimental or observational tabular data analysis, descriptive statistics, prespecified hypothesis tests, effect-size estimation, confidence intervals, multiple-testing correction, robustness checks, publication-oriented plotting, and prospective power/sample-size planning before main-study outcome analysis. Lock the scientific question, estimand, independent unit, variable roles, exclusions, and analysis family before inference. Use deterministic Python tooling for profiling, cleaning-rule execution, statistical calculations, sensitivity analysis, plotting, provenance capture, report assembly, and preflight QA. Never silently impute, silently collapse repeated observations, drop outliers to obtain significance, switch tests after seeing results, treat technical replicates as independent biological samples, or report p-values without effect magnitude and uncertainty when an effect estimate is meaningful.
---

# Scientific Data Analysis — v1.6.1

Work through two auditable branches:

**Post-data inference:** research question -> data contract -> immutable raw identity -> profile -> locked analysis plan -> validated cleaning rules -> analysis-ready data -> descriptive inspection -> prespecified inference -> effect sizes + uncertainty -> multiplicity -> declared sensitivity analyses -> reproducible figures -> deterministic report -> preflight -> provenance bundle -> researcher interpretation

**Pre-data planning:** design question -> independent analysis unit -> effect/variance/rate assumptions + provenance -> alpha/power/sidedness/allocation -> locked power plan -> deterministic sample-size / prospective-power / MDE calculation -> assumption scenarios -> planning figures/report -> power preflight -> provenance bundle

The researcher/model makes scientific decisions. Deterministic scripts execute declared transformations and calculations, preserve hashes, reject unsafe structural shortcuts, and check cross-artifact consistency.

## Mission

Produce analyses that another researcher can inspect, rerun, and challenge.

Priority order:

1. scientific question and estimand;
2. correct unit of analysis / dependence structure;
3. data integrity and transparent cleaning;
4. effect magnitude and uncertainty;
5. statistical validity;
6. robustness / sensitivity;
7. reproducibility and traceability;
8. readable, data-faithful visualization;
9. p-values and threshold decisions.

A small p-value does not rescue pseudoreplication, post-hoc outcome switching, silent exclusions, hidden duplicate pairing, invalid aggregation, or an uninterpretable effect size.

## Current release — v1.6.1

v1.6.1 is a **release-hardening patch**. The post-data analysis-plan schema remains `1.4`; the power-plan schema remains `1.1`; statistical estimands and formulas are unchanged.

Release contract:

- Python `>=3.10`;
- `numpy`, `pandas`, `scipy`, `statsmodels`, `matplotlib`, and `openpyxl` are required runtime dependencies;
- `scripts/release_check.py --full` is the canonical pre-release/CI gate; the no-flag form is the fast local contract check;
- current workflow instructions live in this file, while historical release notes/migrations live in `CHANGELOG.md`.

The v1.6 scientific expansion retained here is prospective `welch_contrast` planning aligned with post-data planned-contrast inference. Planning supports `sample_size`, `prospective_power`, and `minimum_detectable_effect` under declared group SD/allocation assumptions using a generalized Welch–Satterthwaite noncentral-t calculation. Contrast levels/weights are estimand-defining and immutable across scenarios.

Migration from v1.6.0: no schema migration. Re-run version-bound artifacts after upgrading.

## Hard rules

1. **Never modify the raw source in place.** Create an analysis-ready derivative and preserve a SHA-256 identity for the raw input.
2. **Declare the unit of analysis before inference.** Technical replicates, repeated measures, fields of view, cells nested in animals, and multiple observations from one participant are not automatically independent samples.
3. **Lock variable roles before testing:** outcome(s), predictor/group, covariates, pairing/subject ID, blocking factors, strata, and analysis family.
4. **No silent row deletion.** Every mechanically excluded row must be explainable by a declared rule and written to the cleaning log.
5. **No silent imputation or silent complete-case loss.** Missing-data handling must be explicit, and each analysis must record how many candidate units were actually analyzed. Simple imputation is not a neutral default.
6. **No silent pair collapse.** If long-format paired data contain more than one observation for the same `pair_id × condition`, core paired tests must stop. Aggregate declared technical replicates first or use an appropriate repeated/multilevel model.
7. **No silent metadata collapse during technical-replicate aggregation.** Group/condition/covariate metadata must be invariant inside a declared replicate group; conflicts are hard failures.
8. **Do not delete outliers merely because they weaken significance.** Use predeclared measurement/error rules, domain-justified flags, robust methods, and/or sensitivity analysis.
9. **Do not choose tests by p-hacking.** Test choice follows design, estimand, scale, dependence, and assumptions—not whichever yields p < 0.05.
10. **Prefer Welch over equal-variance independent t-tests unless equal variance is substantively justified.**
11. **For paired/repeated data, preserve pairing.** Do not analyze paired observations as independent.
12. **Report effect size + uncertainty whenever scientifically meaningful.** A p-value alone is not a result.
13. **Separate confirmatory from exploratory analyses.** Label post-hoc analyses and hypothesis-generating findings.
14. **Define the multiple-testing family.** If several inferential tests address one family of claims, apply or justify multiplicity handling.
15. **Do not interpret non-significance as equivalence or evidence of no effect.** Equivalence requires prespecified raw-scale margins and an appropriate analysis such as TOST; do not choose margins after seeing the estimate.
16. **Do not infer causality from association without a design/identification strategy that supports it.**
17. **Do not describe rank tests as automatically testing median differences.** Descriptive median differences may accompany a rank test but must be labeled as descriptive unless the estimand assumptions justify stronger wording.
18. **Plots must show the data-generating structure when practical.** Avoid bars-with-error-bars as the default for continuous outcomes; prefer raw observations plus appropriate summaries/intervals.
19. **Statistical summaries and plotted summaries must come from the same analysis-ready data and declared plan.**
20. **Record software versions, random seeds, input hashes, plan hash, and output hashes.**
21. **Never fabricate sample sizes, exclusions, test statistics, confidence intervals, p-values, effect sizes, or sensitivity outcomes.**
22. **Do not call an analysis reproducible if the plan, data identity, code/environment record, or artifact hashes needed to rerun it are missing.**
23. **When the design requires a method outside the core scope, stop automatic inference and produce a specialist handoff rather than forcing a simpler test.**

## Prospective planning workflow — separate from post-data inference

Use this branch **before collecting/analyzing the main study data** when the task is sample-size, prospective-power, or minimum-detectable-effect planning.

Start from `templates/power_plan.template.json` and set:

- `power_plan_schema_version = "1.1"`;
- explicit `unit_of_analysis`;
- planning question and independent analysis unit in the narrative/provenance;
- global or per-item `alpha`, `target_power`, and `alternative`;
- design-specific effect/variance/rate assumptions;
- analyzable allocation or fixed n when relevant;
- `attrition_rate` for enrollment inflation;
- `assumption_source` with kind + non-empty reference/note;
- optional named `scenarios` for plausible assumption variation.

Validate:

```bash
python scripts/validate_power_plan.py power_plan.json
```

Run deterministic planning:

```bash
python scripts/run_power.py --plan power_plan.json --out planning/power_results.csv
```

Preflight by full deterministic recomputation:

```bash
python scripts/preflight_power.py \
  --plan power_plan.json \
  --results planning/power_results.csv \
  --report planning/power_preflight.json
```

Render scenario summaries and a factual report:

```bash
python scripts/plot_power.py \
  --plan power_plan.json \
  --results planning/power_results.csv \
  --outdir planning/figures

python scripts/build_power_report.py \
  --plan power_plan.json \
  --results planning/power_results.csv \
  --preflight planning/power_preflight.json \
  --out planning/power_report.md
```

Freeze provenance with `make_manifest.py` exactly as for analysis artifacts.

Planning hard rules:

1. Do not calculate "observed power" from the completed study's observed effect and use it to interpret a result.
2. A power number is conditional on assumptions; it is not the probability that H1 is true.
3. Use the independent scientific analysis unit. Technical replicates do not automatically increase power.
4. For paired planning, use the SD of within-pair differences, not a marginal SD unless scientifically justified.
5. One-sided planning requires a prespecified scientific direction; `larger` means the declared signed effect/contrast is > 0 and `smaller` means it is < 0.
6. If an effect/variance assumption comes from a pilot, preserve its uncertainty with scenarios rather than treating the point estimate as truth.
7. Do not reduce clustered, survival, adaptive/sequential, equivalence/noninferiority, complex regression, or repeated multi-timepoint designs to these simple core formulas.

Read `references/power_sample_size.md`.

## 1. Choose a profile

Use `templates/analysis_plan.template.json` and set `profile`:

- `exploratory`: rapid profiling and hypothesis generation. Inferential claims must remain exploratory.
- `standard`: **default**. Frozen plan, auditable cleaning, effect size + CI, declared tests, multiplicity, planned sensitivities when material, reproducible plots, preflight, and provenance.
- `confirmatory`: for preregistered/protocol-driven analyses. Requires a locked input SHA-256 and explicit `analysis_role` for each inferential item. Deviations require a new plan version and explicit deviation record outside the immutable prior plan.

Keep three concepts distinct:

- **skill version** — implementation version, e.g. `1.6.1`;
- **analysis-plan schema version** — structural contract, currently `1.4`;
- **plan version** — researcher-controlled version of this study's plan, e.g. `1.0`, `1.1`.

Do not silently reinterpret an old plan under a new contract.

## 2. Establish the data contract

Before cleaning, identify:

- input file(s) and immutable SHA-256;
- observational unit and independent experimental unit;
- subject/cluster/pair identifiers;
- outcome variable(s) and units;
- exposure/group/predictor variable(s);
- covariates and whether they were prespecified;
- repeated-measures or hierarchical structure;
- valid ranges / impossible values;
- missing-value encodings;
- technical replicate policy;
- planned exclusions and reason codes;
- primary vs secondary/exploratory outcomes.

Create a data dictionary from `templates/data_dictionary.template.csv` when columns are not self-documenting.

Run the profiler first:

```bash
python scripts/profile_data.py data.csv --out analysis/profile.json
```

The profiler describes the dataset. It does **not** decide which rows are valid, whether duplicates are scientific replicates, or which statistical test to use.

## 3. Write and validate the analysis plan

Copy `templates/analysis_plan.template.json` into the workspace and fill it before inferential testing.

Minimum plan content:

- `analysis_plan_schema_version`;
- `analysis_id`, `plan_version`, `profile`;
- `research_question`;
- `unit_of_analysis`;
- `input.path` and expected hash when available;
- variable roles;
- cleaning rules and ID-duplicate policy;
- explicit `missing_data.strategy` (v1.4 core supports `complete_case` only, with per-analysis accounting);
- explicit `resampling.method` and `resampling.n_resamples`;
- explicit analyses with stable `analysis_item_id` and, where helpful, an `estimand` description;
- `analysis_role` for confirmatory items;
- multiplicity families;
- confidence level;
- random seed;
- planned plots;
- planned sensitivity analyses, including `estimand_relation = same | different | uncertain`.

Validate it:

```bash
python scripts/validate_plan.py analysis_plan.json
```

`standard` mode warns when the input hash has not yet been locked. `confirmatory` mode treats a missing input hash as an error.

## 4. Clean data with explicit rules

Use `scripts/clean_data.py` only with declared rules from the plan.

Supported mechanical cleaning rules in v1.2 include:

- normalize configured missing-value tokens;
- require non-missing values in specified columns;
- require numeric values in specified columns;
- numeric min/max validity ranges;
- allowed categorical levels;
- exact duplicate-row removal;
- independent-ID duplicate auditing or hard failure;
- optional aggregation of explicitly declared technical replicates.

Run:

```bash
python scripts/clean_data.py \
  --input data.csv \
  --plan analysis_plan.json \
  --output analysis/data.clean.csv \
  --log analysis/cleaning_log.csv \
  --report analysis/cleaning_report.json
```

Important v1.2 behavior:

- values that must be numeric but cannot be parsed are logged and excluded rather than silently becoming analysis-time NaNs;
- `id_duplicate_policy=error` prevents duplicate independent-unit IDs from passing cleaning;
- technical-replicate aggregation verifies all carried metadata are invariant within each replicate group;
- conflicting group/condition/covariate metadata cause failure rather than being resolved by taking an arbitrary first value.

If a rule needs scientific judgment—e.g. waveform artifact, failed assay, impossible morphology—encode the reviewed decision in a flag column or a reviewed exclusion file. Do not ask the cleaning script to infer scientific invalidity from the outcome value.

Read `references/data_cleaning.md`.

## 5. Describe before testing

For each analysis item, inspect:

- n at the correct independent-unit level;
- missingness by relevant group/timepoint;
- center and spread;
- raw distributions;
- paired trajectories when paired;
- extreme/influential observations;
- measurement floor/ceiling;
- transformations if scientifically justified.

Mean/SD is useful for mean-based estimands and approximately symmetric data. Median/IQR may be more interpretable for skewed or ordinal distributions. Do not use a normality-test p-value as an automatic test selector.

## 6. Run only prespecified analyses

Execute the declared items:

```bash
python scripts/run_stats.py \
  --data analysis/data.clean.csv \
  --plan analysis_plan.json \
  --out-csv analysis/results.csv \
  --out-json analysis/results.json
```

Core v1.4 analysis types:

- `independent_t`: Welch independent-samples t-test; mean difference + Hedges g;
- `paired_t`: paired t-test; paired mean difference + paired standardized effect;
- `mann_whitney`: independent rank test; rank-biserial effect plus clearly labeled descriptive median difference;
- `wilcoxon`: paired signed-rank test; matched rank-biserial effect plus clearly labeled descriptive paired median difference;
- `pearson`: Pearson correlation + CI;
- `spearman`: Spearman rank correlation + deterministic bootstrap CI;
- `linear_regression`: numeric-predictor OLS with optional HC3 robust SE; target coefficient + full coefficient JSON + influence/conditioning diagnostics;
- `ancova_two_group`: restricted two-group OLS adjustment with numeric covariates, common slopes, optional HC3 SE, and adjusted group difference;
- `logistic_regression`: declared binary event/non-event outcome with numeric predictors; reports the target predictor odds ratio and event orientation;
- `welch_anova`: prespecified three-or-more-group heteroscedastic omnibus mean comparison; reports Welch F/df, Welch-compatible Cohen's f + stratified bootstrap CI, and declared group summaries;
- `welch_contrast`: prespecified weighted linear contrast of two or more independent group means with weights summing to zero; reports the raw-scale contrast, Welch–Satterthwaite CI/test, declared weights, group summaries, and exact contrast orientation;
- `poisson_regression`: nonnegative integer count outcome with numeric predictors, optional positive exposure/log offset, target-predictor incidence-rate ratio, and dispersion/zero diagnostics;
- `chi_square`: contingency-table association; Cramér's V + bootstrap interval when estimable + expected-cell diagnostics;
- `fisher_exact`: ordered 2×2 Fisher exact test; odds ratio + explicit orientation and level order; zero-cell tables report a finite Haldane–Anscombe-corrected OR/CI while retaining the exact uncorrected-table p-value;
- `equivalence_tost_independent`: two one-sided Welch tests against prespecified raw-scale equivalence margins;
- `equivalence_tost_paired`: paired TOST against prespecified raw-scale equivalence margins.

The runner **does not auto-pick a test**.

Structural guardrails include:

- no duplicate long-format pair×condition cells;
- no constant-input correlation;
- no degenerate zero-variance mean test;
- no rank-deficient OLS/ANCOVA/logistic/Poisson design matrix;
- no logistic result without both declared outcome levels and convergence;
- no Welch omnibus result with undeclared/missing groups or degenerate within-group variance;
- no Welch planned contrast with data-selected/invalid weights, nonzero weight sum, missing declared groups, or degenerate weighted sampling variance;
- no Poisson result with noninteger/negative counts, nonpositive exposure, rank deficiency, or non-convergence;
- no TOST without prespecified lower/upper equivalence margins;
- no Fisher result without an explicit recorded orientation;
- no non-finite p-values entering multiplicity correction.

Every result row is stamped with the cleaned-data hash and plan hash used to produce it, plus the declared missing-data strategy, resampling count, and per-analysis candidate/analyzed/excluded-unit accounting.

See `references/statistical_decisions.md`.

## 7. Quantify effect size and uncertainty

Default confidence level is 95% unless the plan states otherwise.

Whenever applicable, report:

- raw-scale effect (difference, coefficient, odds ratio, correlation);
- confidence interval;
- standardized effect as a secondary aid when meaningful;
- analyzed sample counts;
- interval method.

Use standardized effects for comparability, not as a substitute for original scientific units.

v1.4 uses deterministic percentile bootstrap intervals for selected statistics when a simple analytic interval is not used. `resampling.n_resamples` is locked in the plan and recorded in every result. Each analysis item gets a stable derived RNG seed, so reordering the analysis list does not change that item's bootstrap stream. Percentile bootstrap is not a universal high-precision or BCa interval.

Read `references/effect_size_uncertainty.md`.

## 8. Handle multiplicity explicitly

Group related inferential items using `multiplicity_family`.

Supported corrections:

- `holm` — strong family-wise error control;
- `bonferroni` — deliberately conservative family-wise correction;
- `fdr_bh` — Benjamini–Hochberg false-discovery-rate control.

The runner preserves raw p-values and adds adjusted p-values. Never overwrite raw p-values.

If a family contains multiple tests and `method=none`, give a justification. In confirmatory mode, an unjustified multi-test `none` family is invalid.

## 9. Declare and execute sensitivity analyses

Sensitivity analysis is part of the plan, not a post-hoc search for a preferred answer.

v1.2 supports controlled sensitivity specifications with:

- a `base_analysis_item_id`;
- an explicit rationale;
- explicit `estimand_relation = same | different | uncertain`;
- optional safe row filters in `data_filter.exclude_if`;
- limited `analysis_overrides`, currently method type / robust-SE / reported predictor when structurally valid.

Example:

```json
{
  "sensitivity_id": "exclude_preflagged_measurement",
  "base_analysis_item_id": "primary_outcome",
  "rationale": "Check sensitivity to measurements pre-flagged for review.",
  "estimand_relation": "same",
  "data_filter": {
    "exclude_if": [
      {"column": "qc_flag", "operator": "eq", "value": "review"}
    ]
  },
  "analysis_overrides": {}
}
```

Run:

```bash
python scripts/run_sensitivity.py \
  --data analysis/data.clean.csv \
  --plan analysis_plan.json \
  --base-results analysis/results.csv \
  --out-csv analysis/sensitivity_results.csv \
  --out-json analysis/sensitivity_results.json
```

The sensitivity runner records:

- rows before/after filtering;
- filter and override specification;
- sensitivity estimate/CI/p-value;
- base estimate/CI/p-value;
- the plan-declared estimand relation (`same`, `different`, or `uncertain`);
- estimate change only when direct numeric comparison is defensible;
- null-relative direction and interval relation as descriptive metadata.

Changing from a mean comparison to a rank-based test generally changes the estimand. The skill no longer guesses this from `estimate_name`; the researcher/agent must declare the relation and justify it scientifically.

Read `references/sensitivity_analysis.md`.

## 10. Plot reproducibly

Generate figures from the cleaned data + plan + matching result table:

```bash
python scripts/plot_results.py \
  --data analysis/data.clean.csv \
  --plan analysis_plan.json \
  --results analysis/results.csv \
  --outdir analysis/figures
```

The plotter checks that the result table hashes match the supplied cleaned data and plan.

Plot rules:

- show raw observations when feasible;
- for paired data, show within-subject trajectories where useful;
- align visual summaries with the estimand family;
- use deterministic jitter from the plan seed;
- label units;
- avoid truncated axes when they distort interpretation;
- do not make significance stars the primary message;
- keep plotted n consistent with reported n.

For complex publication figures, hand off authoritative cleaned data + results to `$scientific-figure` rather than redrawing invented values.

Read `references/reproducible_plotting.md`.

## 11. Preflight the complete analysis bundle

Run:

```bash
python scripts/preflight.py \
  --plan analysis_plan.json \
  --data analysis/data.clean.csv \
  --results analysis/results.csv \
  --cleaning-log analysis/cleaning_log.csv \
  --cleaning-report analysis/cleaning_report.json \
  --sensitivity-results analysis/sensitivity_results.csv \
  --report analysis/preflight.json
```

If no sensitivity analyses are planned, omit `--sensitivity-results`.

Preflight checks include:

- plan validity;
- result IDs exactly match planned IDs;
- current plan/data hashes match result hashes;
- cleaning-report output/plan/log hashes reconcile with current files;
- p-values/adjusted p-values lie in [0,1];
- confidence intervals are ordered;
- effect-size fields are present or explicitly warned as non-estimable;
- sample counts are positive and plausible;
- per-analysis candidate/analyzed/missing counts are present and internally consistent;
- result missing-data strategy and resampling count match the plan;
- multiplicity families reconcile;
- every recomputable result field independently reconciles against a fresh deterministic rerun from the current analysis-ready data + plan;
- cleaning log has explicit reasons;
- no accidental index columns;
- Fisher and logistic event/odds orientations are recorded;
- TOST conclusions match both one-sided p-values and the corresponding equivalence CI/margins;
- regression/ANCOVA/logistic conditioning and influence diagnostics trigger review warnings rather than automatic row deletion;
- planned sensitivity IDs are unique, all executed, hash/version-matched, and every recomputable sensitivity field independently reconciles against a fresh deterministic rerun using freshly recomputed base analyses;
- low chi-square expected counts generate warnings.

A passing preflight establishes structural/internal consistency plus deterministic numerical reconciliation of both base inference and declared sensitivity analyses with the current data + plan + skill implementation. It still does not establish scientific truth, causal validity, or appropriateness of the chosen model.


## 12. Build an artifact-grounded report

Create a deterministic report skeleton from completed artifacts:

```bash
python scripts/build_report.py \
  --plan analysis_plan.json \
  --cleaning-report analysis/cleaning_report.json \
  --cleaning-log analysis/cleaning_log.csv \
  --results analysis/results.csv \
  --sensitivity-results analysis/sensitivity_results.csv \
  --preflight analysis/preflight.json \
  --out analysis/analysis_report.md
```

The report builder may state only facts directly represented in artifacts:

- research question/profile/unit;
- cleaning counts and hashes;
- estimate, CI, effect size, p-values, n, and per-analysis missingness accounting;
- multiplicity method;
- sensitivity outputs and the explicitly declared estimand relation;
- preflight status plus deterministic base-result and sensitivity-result reconciliation status.

It must **not** automatically upgrade an association to causality, convert p≥0.05 into “no effect,” or decide practical importance. The final `Researcher interpretation` section remains explicitly human/model judgment grounded in domain context.


## 13. Interpret scientifically, not mechanically

A valid narrative distinguishes:

- **observed data** — what was measured;
- **estimate** — magnitude and direction;
- **uncertainty** — interval / precision;
- **inferential test** — compatibility with a null under assumptions;
- **robustness** — sensitivity to defensible choices;
- **design limitations** — confounding, dependence, missingness, measurement error, sample-size limits;
- **claim strength** — descriptive, associational, predictive, or causal.

Preferred wording emphasizes magnitude and uncertainty before threshold language.

Do not say “there is no difference” solely because p ≥ 0.05. Describe the estimate and uncertainty range.


## 14. Freeze provenance

After analysis/report/preflight, create a manifest:

```bash
python scripts/make_manifest.py \
  --plan analysis_plan.json \
  --inputs \
    data.csv \
    analysis/data.clean.csv \
    analysis/results.csv \
    analysis/sensitivity_results.csv \
    analysis/analysis_report.md \
    analysis/preflight.json \
  --out analysis/provenance.json
```

The manifest records hashes, file sizes, Python/package versions, platform, UTC timestamp, schema/plan version, plan hash, and seed.

Recommended final bundle:

```text
analysis/
├── profile.json
├── data.clean.csv
├── cleaning_log.csv
├── cleaning_report.json
├── results.csv
├── results.json
├── sensitivity_results.csv       # when planned
├── sensitivity_results.json      # when planned
├── figures/
├── preflight.json
├── analysis_report.md
└── provenance.json
analysis_plan.json
```

## 15. Escalation / handoff rules

Do not force core v1.4 methods when the data require:

- mixed-effects / multilevel models for nested or repeated data;
- generalized estimating equations;
- survival/time-to-event models;
- compositional-data analysis;
- multinomial/ordinal outcomes, rare-event/separation-sensitive logistic workflows, categorical-predictor encodings beyond the declared core, or zero-inflated/count models;
- Bayesian hierarchical inference;
- complex survey weights;
- causal inference requiring propensity scores, IV, DiD, RDD, target-trial emulation, etc.;
- high-dimensional omics / thousands of features with domain-specific normalization;
- image/signal preprocessing where measurement extraction is itself part of the scientific method;
- factorial/interacted designs where a collection of pairwise tests would answer the wrong question.

Instead, produce a handoff containing:

- data structure and independent unit;
- estimand;
- dependence/hierarchy;
- candidate model family;
- assumptions and diagnostics needed;
- missing-data strategy;
- multiplicity scope;
- unresolved scientific decisions.

## Reference loading guide

Read only what is needed:

- `references/data_cleaning.md` — missingness, outliers, duplicates, technical replicates, ID policy;
- `references/statistical_decisions.md` — design/estimand → appropriate method, assumption guidance;
- `references/planned_contrasts.md` — planned multi-group contrast semantics, weighting, multiplicity, and escalation rules;
- `references/effect_size_uncertainty.md` — effect-size definitions, CIs, bootstrap, interpretation;
- `references/sensitivity_analysis.md` — robustness design and same-estimand vs changed-estimand comparisons;
- `references/power_sample_size.md` — prospective power/sample-size assumptions, supported designs, scenarios, and anti-post-hoc guardrails;
- `references/reproducible_plotting.md` — scientific plotting grammar and consistency rules;
- `references/reporting_checklist.md` — final reporting / claim-strength / provenance checklist.

## Design principle

**Automate calculations, bookkeeping, provenance, and consistency checks; preserve scientific judgment.**

The skill should make it harder to obtain a polished but invalid analysis, harder to hide data-structure problems behind aggregation, and easier to see exactly how every reported number was produced.
