# Effect size and uncertainty

## Raw-scale first
Prefer effects in scientific units when possible:
- mean difference;
- paired mean change;
- regression coefficient;
- odds ratio;
- correlation.

Standardized effects help comparison across scales but are less directly interpretable.

## Hedges g
For two independent groups, Hedges g is a small-sample corrected standardized mean difference. Report it alongside the raw mean difference rather than instead of it.

## Paired standardized effect
For paired data, standardizing the mean change by the SD of within-pair differences answers a different question than independent-group Cohen d. Label the definition used.

## Rank-biserial effect
For Mann-Whitney/Wilcoxon workflows, a rank-biserial effect communicates direction/magnitude on a rank/probability scale. Ties and zero differences affect definitions; report the implemented convention.

## Confidence intervals
Intervals communicate precision and a range of effects compatible with the model/assumptions. They are not a probability that the fixed true parameter lies in the realized interval.

## Bootstrap
Use a fixed seed and enough resamples. Bootstrap methods can fail with tiny samples, degenerate statistics, extreme discreteness, or strong dependence. Resample at the correct independent-unit level.

## Practical interpretation
Avoid universal labels such as “small/medium/large” as the primary scientific interpretation. Domain context and minimally important effects matter more than generic thresholds.

## Bootstrap intervals in v1.2

Selected rank/correlation/association summaries use a deterministic percentile bootstrap seeded from the analysis plan. The resample count is declared in `resampling.n_resamples` and recorded in result artifacts. Each analysis receives an order-independent seed derived from the plan seed and `analysis_item_id`.

This is a practical default, not a claim that 2,000 percentile resamples are universally sufficient or superior. For high-stakes tail precision, difficult statistics, very small samples, or publication-specific requirements, consider a specialist interval method (e.g. BCa, permutation/exact inference, model-based interval) and document it explicitly.

If too few finite bootstrap replicates are available, the interval is reported as not estimable rather than fabricated.


## Equivalence intervals

For TOST, the interval relevant to the equivalence decision is the `(1 - 2*alpha)` confidence interval. At alpha=0.05 this is a 90% CI. Equivalence is supported only when that interval lies within the prespecified raw-scale equivalence margins (equivalently, both one-sided tests pass). Do not substitute the ordinary 95% CI or choose the margins after seeing the estimate.


## Welch ANOVA

The core reports a Welch-compatible Cohen's f derived from group means, variances, and sample sizes using the same unequal-variance family as the omnibus test. Its percentile-bootstrap interval resamples observations independently within each declared group. Cohen's f is non-directional; it does not identify which groups differ.

## Poisson regression

The target effect is the incidence-rate ratio `exp(beta)` for the declared report predictor, with a log-scale Wald interval exponentiated back to the rate-ratio scale. With an exposure offset, the interpretation is conditional on equal modeled exposure rate rather than equal raw count. Review overdispersion and zero structure before interpreting the interval as sufficient evidence that the Poisson model is adequate.


## Planned multi-group contrasts

For `welch_contrast`, the raw weighted combination of group means is itself the primary effect magnitude. The core intentionally does not invent a standardized contrast index because standardization requires an additional scientific/statistical convention. Report the declared weight scale, raw contrast, matching Welch–Satterthwaite CI, and group summaries. If all contrast weights are multiplied by a constant, the t statistic and p-value are unchanged but the raw effect and CI rescale; that is why the weight scale must be locked in the plan.
