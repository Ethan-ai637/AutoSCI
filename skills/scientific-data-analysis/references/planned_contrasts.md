# Planned contrasts

A planned contrast is a scientific estimand, not a post-hoc search strategy.

## Core v1.4 contract

`welch_contrast` supports independent groups only. Declare the outcome, grouping column, and an ordered `contrast_terms` list. Each term contains a group `level` and a numeric `weight`.

Example for the average of two treatments minus control:

```json
"contrast_terms": [
  {"level": "treatment_A", "weight": 0.5},
  {"level": "treatment_B", "weight": 0.5},
  {"level": "control", "weight": -1.0}
]
```

Hard rules:

- at least two groups;
- every declared weight is finite and nonzero;
- at least one positive and one negative weight;
- weights sum to zero within numerical tolerance;
- every participating group has at least two complete numeric observations;
- weights are used exactly as declared and are never silently normalized or optimized from the data.

## Scale matters

A contrast and a constant multiple of that contrast encode the same null direction but not the same raw-scale effect. For example, `[0.5, 0.5, -1]` and `[1, 1, -2]` yield the same t statistic and p-value but the second estimate and CI are twice as large. Therefore the planned weight scale is part of the scientific estimand and should be chosen for interpretability before inference.

The core reports the raw-scale contrast as both the primary estimate and the effect magnitude. It does not invent a standardized contrast effect size whose interpretation would depend on an additional convention.

## Inference

For independent groups with sample means `m_i`, sample variances `s_i^2`, sample sizes `n_i`, and weights `c_i`, the estimate is:

`L = sum(c_i * m_i)`

with heteroscedastic sampling variance:

`SE^2 = sum(c_i^2 * s_i^2 / n_i)`

and Welch–Satterthwaite degrees of freedom:

`df = SE^4 / sum((c_i^2 * s_i^2 / n_i)^2 / (n_i - 1))`.

The core uses a two-sided t test of `L = 0` and a matching t confidence interval. Zero or degenerate weighted sampling variance is a hard failure rather than a p-value of 1.

## Omnibus tests and multiplicity

A Welch omnibus ANOVA and a planned contrast answer different questions. A significant omnibus test is not a license to search many contrasts and report the smallest p-value. Conversely, a scientifically primary planned contrast does not require a significant omnibus test as a gatekeeper unless the protocol explicitly defines such a hierarchy.

When several contrasts address one family of claims, declare them as separate analysis items and place them in the same multiplicity family. The existing Holm, Bonferroni, or BH-FDR correction is then applied to the declared p-values.

## Plotting

The `group_comparison` plot shows raw observations and group mean confidence intervals, with declared contrast weights shown on the x-axis. These group summaries are descriptive support for the contrast. The inferential contrast estimate and CI remain in the results/report; the plot does not fabricate a fitted contrast line or automatic significance brackets.

## Escalate instead of forcing this core path

Use a broader model for repeated measures, nested/clustered groups, factorial interactions, covariate-adjusted general linear hypotheses, unequal dependence structures, estimated marginal means from fitted models, or data-driven post-hoc contrast discovery.
