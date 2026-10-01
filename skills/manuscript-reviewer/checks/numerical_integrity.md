# Numerical integrity audit

## Objective

Verify arithmetic and numerical summaries used to support scientific claims without inventing precision or silently mixing protocols.

Run this pass on primary results and any derived quantity that is emphasized in the abstract, contributions, results, discussion, or conclusion.

## Preconditions

Only compute from values that are explicitly readable and protocol-compatible.

Before arithmetic, verify as applicable:
- same dataset/population;
- same split/protocol;
- same metric and direction;
- same unit/scale;
- same model/checkpoint;
- same aggregation convention;
- same evaluation budget;
- same denominator/sample set;
- compatible provenance/version for imported, rerun, or derived inputs.

If comparability is uncertain, do not force a computation.

## Arithmetic checks

### Absolute difference

For raw metrics:
`delta = new - reference`

For percentages, name this a **percentage-point difference** when values are percentage points.

### Relative percentage change

`relative_change = (new - reference) / reference * 100%`

Do not call a percentage-point difference a relative percentage improvement.

### Error reduction

If the paper converts accuracy to error or vice versa, recompute from the same base and verify the claimed reduction.

Example:
- accuracy: 90% -> 92%
- error: 10% -> 8%
- accuracy gain: +2 percentage points
- relative error reduction: 20%

These are different claims.

### Aggregates

When the manuscript reports an average/rank/total:
- recompute only if all required constituent values are available and use the stated aggregation rule;
- check whether macro/micro/weighted/unweighted averaging is specified;
- verify omitted tasks/datasets are not silently excluded;
- do not infer hidden weights.

### Counts and denominators

For reported percentages/fractions:
- verify denominator when stated;
- check that subgroup counts reconcile with totals where the categories are intended to be exhaustive and non-overlapping;
- account for missing/excluded samples when documented.

### Uncertainty summaries

Check that `mean ± x` has a defined `x` where important.
Do not convert SD, SE, CI, IQR, or range into one another unless inputs and formulas are explicitly available.

### Rounding tolerance

Use the displayed precision and reasonable rounding.
Do not flag a discrepancy that is fully explained by rounding.

For values reconstructed from rounded components, report the tolerance limitation.

## Internal derivation record

For each consequential derived-number finding, keep an internal derivation:
- source values, locations, and provenance/version when material;
- formula used;
- computed value;
- manuscript-stated value;
- rounding/protocol assumptions.

The final report should show enough arithmetic to make the finding auditable, but not unnecessary calculation detail.

## High-value targets

Prioritize:
- headline improvement percentages;
- SOTA margins;
- average scores/ranks;
- efficiency ratios/speedups;
- parameter/FLOP reductions;
- subgroup prevalence/rates;
- sample attrition counts;
- claimed percentage changes;
- totals that feed a central conclusion.

## Do not over-flag

- Do not recompute metrics from plots by visual estimation.
- Do not mix values from different protocols to manufacture a discrepancy.
- Do not treat a non-reconstructable aggregate as false. Use `unavailable_to_verify`/coverage gap when required material is inaccessible, or an `author_query` when the manuscript's aggregation/denominator is materially ambiguous. Use a finding only when the reporting omission itself is demonstrably a scientific/reproducibility defect.
