# Changelog

## 1.6.1 — 2026-10-01

Release-engineering and documentation hardening; no statistical or schema changes.

- Make `doctor.py` enforce Python >=3.10 and treat `openpyxl` as required, matching the supported XLSX/XLSM type-preserving input path and `requirements.txt`.
- Add `scripts/release_check.py` with a fast local gate and `--full` GitHub/release mode covering version/schema consistency, script compilation, environment diagnostics, bundled-plan validation, and both self-test suites.
- Remove accumulated historical release prose from the active README/SKILL contract; keep current behavior prominent and use `CHANGELOG.md` as the canonical release history.
- Keep `analysis_plan_schema_version = "1.4"` and `power_plan_schema_version = "1.1"`; no plan migration from v1.6.0.

## 1.6.0 — 2026-10-01

Planned-contrast prospective power/sample-size expansion. Post-data analysis-plan schema remains `1.4`; power-plan schema advances to `1.1`.

### Added

- `welch_contrast` prospective planning for prespecified linear contrasts of two or more independent group means under heteroscedasticity.
- `sample_size`, `prospective_power`, and `minimum_detectable_effect` solve modes using generalized Welch–Satterthwaite standard error/df and noncentral-t power.
- Group-specific SD assumptions, sample-size-mode allocation ratios, fixed-n group sizes, group-wise enrollment inflation, typed contrast metadata, and contrast orientation in power artifacts/reports.
- Scenario support that may vary variance/allocation/n assumptions while preserving the exact typed contrast levels and weight scale.

### Guardrails

- Contrast weights must be finite, nonzero, include positive and negative terms, and sum to zero.
- Scenario overrides cannot redefine the contrast estimand by changing levels, order, or weights.
- `sample_size` contrast terms use allocation ratios and cannot contain fixed n; fixed-n solve modes require explicit n and reject allocation-ratio fields.
- MDE target-status tolerance now matches numerical root-solving precision.

### Migration

- Change `power_plan_schema_version` from `1.0` to `1.1`; existing v1.5 item definitions otherwise retain their semantics.
- Regenerate version-bound power results/reports/preflight artifacts under v1.6.0.

### QA

- Added sample-size minimality, fixed-n prospective power, MDE, variance-scenario, invalid-weight, and estimand-preservation regression tests for `welch_contrast`.
- Existing binary approximation-adequacy and post-data inference regression suites remain in force.

## 1.5.2 — 2026-10-01

Binary-proportion planning approximation-adequacy patch. Post-data analysis-plan schema remains `1.4`; power-plan schema remains `1.0`.

### Added

- `independent_proportions` planning rows now record expected events/non-events for each group, `min_expected_cell_count`, and `normal_approximation_adequacy`.
- Power reports surface the approximation-adequacy diagnostic rather than hiding sparse-cell risk in prose.

### Guardrails

- `preflight_power.py` fails release when the minimum expected event/non-event count is below 1 (`poor_extreme_sparsity`).
- Counts from 1 to below 5 produce a prominent sparse-normal-approximation warning; counts at least 5 are labeled adequate by the skill's conservative count rule.
- These thresholds are explicitly documented as QA heuristics, not guarantees of normal-approximation validity.

### QA

- Added regression cases for an extreme binary design (`p_A=0.05`, `p_B=0.95`) that numerically solves to 4+4 but must fail release, and a rare-event caution case (`p_A=0.01`, `p_B=0.05`).
- Existing v1.5.1 power formula/scenario tests and post-data inference regression pipelines remain in force.

## 1.5.1 — 2026-10-01

Prospective-planning scenario-semantics and QA-state patch. Post-data analysis-plan schema remains `1.4`; power-plan schema remains `1.0`.

### Fixed

- Scenario override validation is now conditional on both planning `type` and `solve_for`, preventing declared assumption changes that the selected calculation would silently ignore.
- Fixed-n prospective-power scenarios cannot override allocation ratio without changing the actual `n_a`/`n_b`; sample-size scenarios cannot override solver-owned n fields; MDE scenarios cannot override the effect being solved.
- `meets_target_power` uses the effective item/plan/default target for every solve mode, including item-only prospective targets.
- Prospective-power plots show scenario-specific target-power markers when scenario targets differ.
- Power preflight deterministic reconciliation now incorporates duplicate result keys and row-count integrity, not just unique-key sets and recomputed numeric fields.

### QA

- Added regression coverage for no-op scenario overrides, item-level prospective targets, scenario-specific target thresholds, and duplicate-row reconciliation status.
- Existing prospective-planning formula self-tests and post-data inference regression pipelines remain in force.

## 1.5.0 — 2026-09-30

Prospective power/sample-size planning expansion. Post-data analysis-plan schema remains `1.4`; new power-plan schema is `1.0`.

### Added

- Separate `power_plan_schema_version = "1.0"` contract that never reads a completed-study analysis dataset/results.
- `welch_two_group_mean` prospective planning with separate SD assumptions, unequal allocation, noncentral-t power, Welch–Satterthwaite df, sample-size search, fixed-n prospective power, and raw-scale MDE.
- `paired_mean` planning using the SD of within-pair differences, with sample-size, prospective-power, and raw-scale MDE modes.
- `independent_proportions` sample-size and fixed-n prospective-power planning using a two-proportion z-test power approximation (pooled null variance, non-pooled alternative variance).
- Required assumption provenance (`scientific_threshold`, `external_evidence`, `pilot`, or `scenario`) and named assumption-sensitivity scenarios.
- Attrition inflation reported separately from analyzable sample size.
- Deterministic `validate_power_plan.py`, `run_power.py`, `preflight_power.py`, `build_power_report.py`, `plot_power.py`, and `power_self_test.py` tooling.
- `templates/power_plan.template.json`, `examples/power_plan.json`, and `references/power_sample_size.md`.
- Provenance manifest support for both analysis plans and power plans.

### Guardrails

- Current-study `input`, post-data `analyses`, or results fields are rejected in a power plan.
- Observed/post-hoc power is not a supported evidentiary workflow.
- One-sided directions must agree with the declared signed effect/rate difference.
- Binary-proportion MDE, clustered/repeated multi-timepoint, survival, adaptive/sequential, equivalence/noninferiority, complex-regression, and count-model power planning remain explicit escalation cases in v1.5.0.

### QA

- Added independent power-planning self-tests covering Welch sample-size minimality, paired MDE, proportion prospective power, one-sided direction guards, prospective/post-hoc workflow separation, scenario override validation, and unsupported-design rejection.
- Added deterministic power-artifact reconciliation and tamper detection.

## 1.4.7 — 2026-09-30

Type-preserving table-I/O fidelity patch. Analysis-plan schema remains `1.4`.

### Fixed

- XLSX/XLSM input now preserves native workbook cell scalar types before pandas dtype inference can collapse boolean/numeric/string category identity.
- Cleaning audits the requested analysis-ready serialization by reloading it and comparing plan-relevant columns with typed scalar identity; lossy CSV/TSV output is refused.
- Added type-preserving JSONL/NDJSON analysis-ready I/O for mixed scalar categorical/identifier data.
- Generated artifact readers keep `*_json` columns as text so JSON scalar metadata is not re-inferred as boolean/numeric by pandas during preflight, reporting, plotting, or sensitivity execution.
- Missing-token replacement no longer uses pandas `replace`, avoiding silent object-column downcasting in type-sensitive data.
- Categorical plan-level validation is consistent across cleaning and inference: boolean, finite numeric, and non-empty string levels are accepted; invalid/non-scalar levels are rejected early.

### QA

- Added native XLSX scalar-preservation and JSONL round-trip regression coverage for boolean `true`, numeric `1`, and string `"1"`.
- Added an end-to-end XLSX -> JSONL -> inference -> deterministic preflight case; the same input requested as analysis-ready CSV must fail rather than silently collapse categories.
- Existing 16 inference paths and deterministic base/sensitivity reconciliation remain in force.

## 1.4.6 — 2026-09-30

Identifier and paired-unit identity fidelity patch. Analysis-plan schema remains `1.4`.

### Fixed

- Exact-duplicate removal uses typed row identity instead of pandas equality, preventing boolean/numeric aliases from being silently collapsed.
- Independent-unit duplicate auditing uses typed ID identity and records the typed non-missing unique-ID count.
- Long-format paired analyses use typed `pair_id` keys for duplicate-cell checks and pivoting, so equality-colliding subject identifiers remain distinct.
- Missing `pair_id` rows are excluded before pairing rather than being grouped into one synthetic missing-ID pair; paired results record `n_rows_missing_pair_id`.
- Dataset profiling uses typed unique counts, typed top-value counts, and typed exact-duplicate detection.

### QA

- Added regression coverage for equality-colliding identifiers (`True` versus numeric `1`), missing pair IDs, typed exact-row duplicate detection, and paired-unit candidate/analyzed-count consistency.
- Existing 16 inference paths and deterministic base/sensitivity reconciliation remain in force.

## 1.4.5 — 2026-09-30

Analysis-cohort plotting and contingency-boundary fidelity patch. Analysis-plan schema remains `1.4`.

### Fixed

- ANCOVA, multivariable OLS, and Poisson plots now use the same complete-case cohort as model fitting instead of reintroducing rows that were excluded because another declared covariate/predictor/exposure field was missing.
- Model plotting reconciles reconstructed cohort size against the current result-row `n` and refuses to render a mismatched cohort.
- ANCOVA and multivariable OLS plots explicitly distinguish raw descriptive displays from adjusted inferential estimands.
- Chi-square and Fisher exact now reject Python/pandas equality-colliding category encodings before crosstab construction, preventing silent boolean/numeric category collapse.

### QA

- Added regression tests for model-plot complete-case cohorts, plot/result n reconciliation, and pre-crosstab collision rejection in both chi-square and Fisher exact.
- Existing 16 inference paths and deterministic base/sensitivity reconciliation remain in force.

## 1.4.4 — 2026-09-30

Estimand-consistency guard. Analysis-plan schema remains `1.4`.

### Fixed

- Sensitivity plans can no longer claim `estimand_relation = "same"` when the declared override mechanically changes the statistical estimand family.
- Regression/GLM same-estimand sensitivities must preserve the reported predictor and predictor/adjustment set; ANCOVA must preserve its covariate set.
- Planned-contrast same-estimand sensitivities must preserve exact typed levels and weight scale.
- Mean-difference tests and matching TOST procedures are recognized as sharing a raw mean-difference estimand family, so changing the decision rule does not automatically force a changed-estimand label.

### Guardrails

- Obvious cross-family overrides such as Welch t -> Mann–Whitney and Pearson -> Spearman must use `different` or `uncertain`.
- The guard deliberately does not infer whether a data subset changes the target population; that remains scientific judgment.

### QA

- Added regression tests for cross-family mislabeling, regression adjustment changes, planned-contrast rescaling, robust-SE-only sensitivities, and t-test -> TOST compatibility.
- Existing 16 inference paths and deterministic base/sensitivity reconciliation remain in force.

## 1.4.3 — 2026-09-30

Sensitivity-selector consistency patch. Analysis-plan schema remains `1.4`.

### Fixed

- Sensitivity `eq` / `ne` / `in` / `not_in` filters now use the same typed categorical identity as cleaning and base inference instead of pandas equality/`isin`.
- Equality-colliding encodings such as boolean `True` and numeric `1` no longer change the declared sensitivity subset.
- Numeric filter operators remain explicitly numeric; categorical missingness continues to use `isna` / `notna`.

### Guardrails

- `in` / `not_in` now require a non-empty list of finite numeric, boolean, or non-empty string scalars.
- Typed-duplicate filter levels such as `[1, 1.0]` fail plan validation.
- `eq` / `ne` reject non-scalar or missing filter values; missingness must be declared explicitly.

### QA

- Added regression coverage for `True` versus numeric `1` and string `"1"` in sensitivity `eq`, `in`, and `not_in` subsets.
- Existing 16 inference paths, base-result reconciliation, and sensitivity-result reconciliation remain in force.

## 1.4.2 — 2026-09-30

Typed categorical selector and cleaning-fidelity patch. Analysis-plan schema remains `1.4`.

### Fixed

- Cleaning `allowed_levels` now uses typed scalar identity instead of pandas equality/`isin`.
- Independent two-group tests, ANCOVA, long-format paired conditions, Welch analyses, logistic event coding, and group-comparison plotting use the same typed category matcher.
- Technical-replicate carry-column conflict checks distinguish equality-colliding values such as boolean `True` and numeric `1`; equality-colliding technical-replicate grouping keys fail explicitly instead of being silently merged.
- Two-group result rows now include `group_a_json` / `group_b_json`; long-format paired rows include `condition_a_json` / `condition_b_json`; logistic rows include `event_level_json` / `nonevent_level_json` so scalar category type survives CSV artifact round trips.
- Logistic and paired human-readable orientations no longer depend on lossy string coercion.

### QA

- Added typed-selector regression coverage for two-group inference, paired-long conditions, logistic outcomes, cleaning-level gates, and technical-replicate metadata/grouping collisions.
- Existing 16 inference paths and deterministic base/sensitivity reconciliation remain in force.

## 1.4.1 — 2026-09-30

Categorical-level fidelity and mixed-type contingency-table patch. Analysis-plan schema remains `1.4`.

### Fixed

- Welch ANOVA and planned-contrast metadata preserve categorical JSON scalar type instead of coercing every level to string.
- Chi-square bootstrap category coding now uses a type-preserving scalar identity rather than `astype(str)`, preventing numeric `1` and string `"1"` from collapsing into one code and avoiding invalid bootstrap table reshapes. Equality-colliding mixed encodings such as boolean `True` and numeric `1` fail explicitly and must be normalized.
- Fisher exact row/column metadata preserve scalar type.
- Fisher odds-ratio orientation, planned-contrast orientation, and group-comparison plot labels disambiguate display collisions such as `1 [number]` and `1 [string]`.
- Preflight compares Welch/contrast declared metadata without lossy string coercion.

### QA

- Added mixed-type categorical regression coverage for chi-square and planned contrasts.
- Existing 16-path inference and deterministic result/sensitivity reconciliation remain unchanged.

## 1.4.0 — 2026-09-30

Planned-contrast expansion. Analysis-plan schema advances to `1.4`.

### Added

- `welch_contrast` for exact prespecified linear contrasts of two or more independent group means under heteroscedasticity.
- Explicit ordered `contrast_terms` with `{level, weight}` entries; finite nonzero weights must include positive and negative terms and sum to zero.
- Welch–Satterthwaite standard error/degrees of freedom, raw-scale contrast estimate + matching CI, declared group summaries, contrast orientation, weight metadata, and rows-outside-declared-level accounting.
- `group_comparison` plotting for planned contrasts with declared weights displayed alongside raw observations and mean/CI summaries.
- Deterministic preflight reconciliation and multiplicity support for planned contrasts through the existing analysis artifact contract.
- `references/planned_contrasts.md` documenting weight scaling, omnibus-vs-contrast semantics, multiplicity, plotting, and escalation rules.

### Guardrails

- Contrast weights are never normalized, generated, or optimized from observed results.
- Invalid/nonzero-sum/duplicate-level/zero-weight contrasts fail plan validation.
- Every declared contrast group requires at least two complete observations; degenerate weighted sampling variance fails inference.
- Repeated/multilevel contrasts, factorial/covariate-adjusted general linear hypotheses, and data-driven post-hoc contrast searches remain outside the core.

### QA

- Core inference-path coverage increases from 15 to 16.
- Added invalid-weight validation coverage and a confirmatory three-group release QA with two planned contrasts in one Holm multiplicity family.

## 1.3.2 — 2026-09-30

Sensitivity-result reconciliation patch. Analysis-plan schema remains `1.3`.

### Added

- Preflight now deterministically recomputes every declared sensitivity analysis from the current analysis-ready data + plan, using freshly recomputed base-analysis results rather than trusting copied values in the submitted sensitivity artifact.
- Every recomputable sensitivity field is reconciled against `sensitivity_results.csv`, including the sensitivity estimate/CI/p-value, analyzed-unit counts, filter/override metadata, null/direction summaries, base-result copies, and same-estimand change metrics.
- `preflight.json` records `deterministic_sensitivity_reconciliation = PASS|FAIL`, and the Markdown report surfaces the status.
- Sensitivity-result files with duplicate `sensitivity_id` rows are rejected explicitly.

### Fixed

- A sensitivity artifact can no longer pass preflight merely because its IDs, data/plan hashes, skill version, estimand relation, and copied base-result fields are correct after someone edits the sensitivity result itself.
- Preflight reuses the freshly recomputed base-analysis rows for sensitivity reconciliation, avoiding an unnecessary second execution of all base analyses.

### QA

- Added regression coverage that alters a sensitivity estimate while preserving hashes/version and verifies deterministic preflight rejection.
- Added duplicate-`sensitivity_id` rejection coverage.
- Existing v1.3.1 deterministic base-result reconciliation and v1.3 model-family guardrails remain in force.

## 1.3.1 — 2026-09-30

Deterministic result-reconciliation patch. Analysis-plan schema remains `1.3`.

### Added

- Preflight now independently recomputes every prespecified inference from the current analysis-ready data and plan using the same stable per-analysis seeds and plan-controlled resampling count.
- Multiplicity is reapplied to the recomputed raw p-values before comparison.
- Every recomputable field produced by `run_stats.py` is reconciled against `results.csv` with CSV-roundtrip-aware numeric tolerance.
- `preflight.json` records `deterministic_result_reconciliation = PASS|FAIL`, and the deterministic Markdown report surfaces that status.

### Fixed

- A result artifact can no longer pass preflight merely because its data/plan SHA-256 stamps and structural metadata are correct after someone edits an estimate, CI, effect size, p-value, sample count, model diagnostic, Welch/Poisson metadata, or another generated field.

### QA

- Added a regression test that alters a core estimate while preserving the original data/plan hashes and verifies deterministic preflight rejection.
- Existing 15-path inference, multiplicity, stale-artifact, sparse-table, separation, provenance, and JSON-portability tests remain passing.

## 1.3.0 — 2026-09-30

Bounded model-family expansion. Analysis-plan schema advances to `1.3`.

### Added

- `welch_anova` for three or more explicitly declared independent groups using heteroscedastic Welch ANOVA. Results include Welch F/df, a Welch-compatible Cohen's f effect size, a within-group stratified percentile-bootstrap CI, per-group n/mean/SD metadata, and variance-ratio diagnostics.
- `poisson_regression` for nonnegative integer count outcomes with numeric predictors, optional strictly positive exposure (used as `log(exposure)`) or an explicit numeric offset, optional HC0 sandwich-robust SE, incidence-rate-ratio inference, and convergence/conditioning/dispersion/zero-fraction diagnostics.
- Multi-group plotting support for `welch_anova`; `count_regression` visualizes observed count/exposure rates (or count/exp(offset)) without drawing a misleading unadjusted fit line.
- GLM covariance labeling is corrected: `logistic_regression` and `poisson_regression` support `HC0` or `nonrobust`; `HC3` remains reserved for OLS/ANCOVA. This avoids labeling statsmodels GLM White-sandwich covariance as HC3.
- Preflight checks for declared Welch group reconciliation and Poisson offset/exposure semantics, plus heuristic warnings for extreme variance ratios, overdispersion, and high zero fractions.

### Guardrails

- Welch ANOVA requires at least three prespecified distinct groups, at least two complete observations per group, and non-degenerate within-group variance. It does not auto-generate post-hoc comparisons.
- Poisson regression rejects negative/noninteger counts, nonpositive exposure, rank-deficient designs, and non-convergence. Strong overdispersion or excess zeros remain visible diagnostics and trigger specialist-model consideration.
- Pairwise follow-ups after an omnibus test remain separate analysis items and are subject to the existing multiplicity contract.

### QA

- Core inference-path coverage increases from 13 to 15 and now includes Welch ANOVA and exposure-adjusted Poisson regression. The all-types test is cleaned, analyzed, and passed through preflight as a single audited mini-pipeline.

## 1.2.3 — 2026-09-29

Correctness and reconciliation patch. Analysis-plan schema remains `1.2`.

### Fixed

- Binary logistic regression now compares declared event/non-event levels by scalar value rather than lossy string rendering. This preserves valid numeric `0/1` coding when CSV missingness promotes the observed values to `0.0/1.0`; missing outcomes remain complete-case exclusions instead of being misclassified as undeclared levels.
- Preflight now recomputes multiplicity-adjusted p-values from the current raw p-values and declared method, rather than checking only the adjustment-method label. Analyses outside a multiplicity family must have `p_adjusted == p_value`.
- Preflight now rejects duplicate `analysis_item_id` rows in `results.csv`.
- Cleaning reports are now version-bound during preflight, closing the remaining cross-version provenance gap across cleaning, inference, and sensitivity artifacts.

### QA

- Added regression coverage for numeric binary outcomes with missing values and tampered multiplicity-adjusted p-values.

## 1.2.2 — 2026-09-29

Correctness and artifact-binding patch. Analysis-plan schema remains `1.2`.

### Fixed

- `chi_square` now explicitly uses uncorrected Pearson chi-square for the inferential statistic/p-value and Cramér's V, matching the definition already used inside the row-bootstrap Cramér's V interval. This removes the 2×2 Yates-vs-uncorrected mismatch.
- Chi-square results now record `chi_square_correction=none`; preflight verifies it.
- `run_sensitivity.py` rejects base-results files whose data SHA-256, plan SHA-256, analysis IDs, or skill version do not match the current run.
- Preflight rejects previous-version results/sensitivity artifacts and reconciles sensitivity base estimates, confidence limits, and p-values against the current base results.

### QA

- Added regression coverage for the uncorrected Pearson 2×2 χ² definition, stale sensitivity base artifacts, and cross-version result rejection.

## 1.2.1 — 2026-09-29

Stability, sparse-table, and provenance patch. Analysis-plan schema remains `1.2`.

### Fixed

- Technical-replicate aggregation now preserves source-row membership in `_source_row_ids` and group size in `_technical_replicate_n`; raw inputs using reserved provenance column names are rejected.
- Sparse 2×2 Fisher exact results no longer mix an infinite uncorrected odds-ratio point estimate with a finite continuity-corrected CI. When any cell is zero, the reported finite OR + Woolf CI use a declared Haldane–Anscombe 0.5 correction; the exact Fisher p-value still uses the uncorrected table.
- Fisher two-sided p-values are computed deterministically from the fixed-margin hypergeometric support, avoiding dependence on changing high-level Fisher implementations.
- Perfect-separation warnings in ordinary binary logistic regression now fail explicitly with a separation-aware handoff message.
- JSON output is sanitized to standards-compliant values; non-finite numbers become `null` rather than `NaN`/`Infinity`.
- Preflight rejects non-finite inferential outputs and verifies aggregation provenance columns when technical-replicate aggregation was reported.

### QA

- Added guardrails for source-row aggregation provenance, sparse Fisher tables, perfect separation, and JSON portability on top of the 13 v1.2 inference paths.

## 1.2.0 — 2026-09-29

Scientific-semantics and core-model expansion release.

### Added

- Analysis-plan schema `1.2` with explicit `missing_data` and `resampling` contracts.
- Per-analysis candidate/analyzed/missing-or-invalid unit accounting.
- Plan-controlled bootstrap resample count and order-independent deterministic per-analysis RNG seeds.
- Independent and paired TOST equivalence analyses with prespecified raw-scale margins.
- Restricted two-group ANCOVA with numeric covariates, common slopes, optional HC3 SE, and model diagnostics.
- Binary logistic regression with explicit event/non-event orientation, numeric predictors, odds-ratio inference, and convergence/conditioning metadata.
- OLS/ANCOVA diagnostics: condition number, maximum leverage, and maximum Cook's distance where estimable.
- Chi-square diagnostics for expected-cell counts below 5 and below 1.
- Required sensitivity `estimand_relation = same | different | uncertain`.
- Preflight checks for missingness/resampling contract reconciliation, TOST consistency, logistic orientation/convergence, model diagnostics, and sensitivity estimand declarations.

### Changed

- Sensitivity analysis no longer infers “same estimand” from matching result names; the relationship is an explicit scientific judgment in the plan.
- Bootstrap settings are no longer hidden implementation constants for core results.
- The report builder now includes per-analysis missingness, equivalence margins/results, selected model diagnostics, and explicit estimand relations.
- Self-test coverage increased from 9 to 13 inference paths while preserving the structural guardrail tests.

### Scope boundary

- Full factorial/multi-group ANOVA, interactions, mixed models, GEE, survival analysis, multiple imputation, categorical-predictor encoding strategies, rare-event/penalized logistic regression, and causal-identification workflows remain explicit handoff cases rather than silent simplifications.

## 1.1.0 — 2026-09-29

Guardrail and auditability release.

### Added

- Analysis-plan schema version `1.1` and stricter validation.
- Executable declared sensitivity analyses (`run_sensitivity.py`).
- Deterministic artifact-grounded Markdown report builder (`build_report.py`).
- Data/plan SHA-256 stamps in statistical and sensitivity result rows.
- Preflight reconciliation across cleaned data, cleaning report/log, results, and sensitivities.
- Fisher exact level ordering and explicit odds-ratio orientation.
- Expanded self-test across all nine core inference paths.

### Changed

- Numeric parsing declared by the cleaning plan is now audited during cleaning rather than silently deferred to analysis-time coercion.
- Independent-unit duplicate policy is enforceable (`audit`, `error`, `allow`).
- Technical-replicate aggregation verifies metadata invariance before aggregation.
- Rank-test companion median differences are explicitly labeled descriptive rather than presented as the tested estimand.
- Bootstrap routines skip invalid resamples and return non-estimable intervals rather than failing/fabricating values.

### Hard guardrails

- Duplicate long-format `pair_id × condition` cells now fail paired inference instead of being silently collapsed with `first`.
- Conflicting metadata inside technical-replicate groups now fail cleaning instead of being silently collapsed with `first`.
- Degenerate/constant correlation inputs, zero-variance mean tests, and rank-deficient OLS models now fail explicitly.
