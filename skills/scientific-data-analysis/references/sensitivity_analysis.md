# Sensitivity analysis guide

Sensitivity analysis asks whether a scientific conclusion depends strongly on a defensible analysis choice or a pre-identified data-quality uncertainty. It is not a license to try many analyses and report the preferred result.

## Plan the sensitivity before looking for a preferred answer

Good sensitivity questions are tied to a specific vulnerability:

- one observation was pre-flagged for measurement review;
- a transformation is scientifically plausible but not uniquely required;
- heteroskedasticity may affect conventional OLS standard errors;
- a rank-based analysis is useful as a qualitatively different view of a skewed/ordinal outcome;
- a missing-data assumption has a plausible alternative;
- subject-level aggregation is being compared with a specialist multilevel-model handoff.

Write the vulnerability and rationale explicitly.

## Same estimand vs changed estimand

This distinction is essential.

Examples that can preserve the same estimand:

- OLS coefficient with conventional vs HC3 standard errors;
- the same mean-difference analysis with vs without a measurement that was independently pre-flagged;
- the same model under a defensible subset restriction that does not redefine the target population beyond the stated sensitivity question.

Examples that often change the estimand:

- mean difference (Welch t) vs Mann–Whitney rank separation;
- Pearson linear correlation vs Spearman monotonic rank association;
- raw-scale coefficient vs transformed-outcome coefficient.

When the estimand changes, do not summarize the sensitivity as a percent change in “the effect.” Report the two quantities separately and explain what each answers. v1.2 requires `estimand_relation = same | different | uncertain` in the plan; the runner no longer infers this from a result label.

From v1.4.4, the validator also rejects **mechanically contradictory** `same` declarations. It does not decide the hard scientific cases for you. Examples that cannot be labeled `same` include changing Welch t to Mann–Whitney, Pearson to Spearman, changing the reported regression predictor or adjustment set, or changing a planned contrast's levels/weight scale. By contrast, changing only robust standard errors can preserve the same coefficient estimand, and switching a raw mean-difference test to its TOST counterpart can preserve the same raw mean-difference estimand while changing the inferential decision rule. Whether a subset restriction changes the target population remains a scientific judgment and is not auto-classified.

## Supported v1.4 filter grammar

`data_filter.exclude_if` uses explicit column rules. Supported operators:

- `eq`, `ne`
- `in`, `not_in`
- `isna`, `notna`
- `lt`, `le`, `gt`, `ge`

Rules are combined as an OR for exclusion: a row is excluded if it matches any declared exclusion rule.

Categorical membership is **typed** in v1.4.3: numeric `1`/`1.0` are one numeric level, while boolean `true` and string `"1"` are distinct levels when the source format preserves those scalar types. `eq`, `ne`, `in`, and `not_in` follow the same identity rules as cleaning and base inference. `in`/`not_in` lists must be non-empty and contain typed-distinct scalar values. Use `isna`/`notna` for missingness rather than `eq: null`. Numeric comparison operators require finite numeric thresholds.

Avoid outcome-driven filters such as “exclude observations above the 95th percentile because the result becomes non-significant.” If an outlier rule is scientifically justified, define it from measurement/QC logic before looking at the inferential result.

## Reporting

For every sensitivity analysis report:

- rationale;
- exact data filter and method override;
- rows before/after;
- estimate and interval;
- whether the estimand matches the base analysis;
- direction/precision changes without cherry-picking;
- any limitation introduced by the sensitivity itself.

Do not turn a collection of sensitivity results into a binary “robust/not robust” label unless that criterion was itself prespecified and scientifically meaningful.
