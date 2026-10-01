# Reporting checklist

Before finalizing:

- Research question and estimand are explicit.
- Unit of analysis is explicit.
- Raw data identity/hash is recorded.
- Analysis-plan schema version and researcher plan version are distinguishable.
- Cleaning/exclusion counts and reasons are reported.
- Numeric parsing failures, if any, are visible in the cleaning log.
- Independent-ID duplicates are reconciled with the declared policy using typed identifier identity.
- Technical-replicate aggregation did not hide conflicting metadata.
- Paired long-format analysis has exactly one resolved observation per pair × condition, uses non-missing pair IDs, and reports any `n_rows_missing_pair_id`.
- Missingness is reported or discussed at the level relevant to the analysis, including candidate vs analyzed units for every inferential item.
- Descriptive statistics match the analyzed sample.
- Statistical method matches dependence/design and estimand.
- Rank tests are not casually described as generic median tests.
- Effect magnitude is reported in interpretable units where possible.
- Confidence interval / uncertainty is reported and its method is known.
- Raw and adjusted p-values are distinguished when multiplicity applies.
- Fisher exact odds-ratio orientation is explicit when used.
- Logistic event/non-event orientation and reported predictor are explicit when used.
- TOST equivalence margins were prespecified and both one-sided results / equivalence CI are reported when used.
- ANCOVA/regression diagnostics are reviewed without deleting observations solely to improve significance.
- Sensitivity analyses are summarized as a complete declared set, not cherry-picked.
- Same-estimand, changed-estimand, and uncertain-estimand sensitivity analyses are explicitly distinguished.
- Plot sample sizes/data source match the result table; model plots use the exact model complete-case cohort, not a display-variable-only subset.
- Result-table plan/data hashes match the artifacts being reported.
- Causal language is not stronger than the design supports.
- Non-significance is not described as proof of no effect.
- Exploratory/post-hoc analyses are labeled.
- Preflight status and material warnings are visible.
- Software versions, seed, plan, input/output hashes, and manifest are preserved.
- Deterministic report text is separated from researcher/domain interpretation.
## v1.2.1 portability/provenance checks

- If technical replicates were aggregated, verify `_source_row_ids` and `_technical_replicate_n` are present in the analysis-ready data.
- If a Fisher 2×2 table contains a zero cell, report the zero-cell correction used for the finite OR/CI separately from the exact uncorrected-table p-value.
- Machine-readable JSON artifacts must not contain non-standard `NaN`, `Infinity`, or `-Infinity` tokens.

## v1.2.3 reconciliation checks

- Numeric binary event levels must be interpreted by their declared scalar values; missingness-driven `0/1` → `0.0/1.0` type promotion is not a new outcome level.
- Recompute multiplicity-adjusted p-values during preflight and verify the numerical values, not only the method label.
- Reject duplicate analysis result IDs.
- Require the cleaning report, statistical results, and sensitivity results used for a current release QA to be stamped with the current skill version.

## v1.2.2 artifact-binding checks

- For chi-square results, record that the core uses uncorrected Pearson chi-square consistently for the test and Cramér's V (`chi_square_correction=none`).
- Do not reuse an old `results.csv` as the baseline for sensitivity analysis after the data, plan, or skill implementation changes; rerun base inference first.
- Treat a skill-version mismatch in preflight as a stale-artifact failure, not as a cosmetic metadata warning.


## v1.3 model-family checks

For `welch_anova`, report the declared group set, group sample sizes, Welch F and both degrees of freedom, Cohen's f + interval, and any planned follow-up comparisons with their multiplicity correction. Do not describe an omnibus p-value as identifying a specific group difference.

For `poisson_regression`, report count-outcome definition, exposure/offset handling, target-predictor IRR + CI, analyzed n, convergence, Pearson dispersion, zero fraction, and any reason a negative-binomial/hurdle/zero-inflated or clustered-count model was considered instead.
