# Statistical decision guide

Start from design and estimand, not from a menu of tests.

## Two independent groups, continuous outcome
Question: difference in means on the original scale.
Default core test: Welch independent t-test.
Report: group means/SD, mean difference + CI, Hedges g, p-value.
Use a rank-based test when the estimand is stochastic/rank separation rather than a mean difference, or when the scale/distribution makes a mean comparison scientifically poor.

## Paired continuous outcome
Question: mean within-pair change.
Use paired t-test when mean change is the estimand and differences are reasonably behaved.
Report raw paired difference + CI and paired standardized effect.
For strongly asymmetric/ordinal paired data, consider Wilcoxon signed-rank, but note it is not simply a test of medians without assumptions.

## Correlation
Pearson: linear association, sensitive to influential points.
Spearman: monotonic rank association.
Correlation is not agreement and not causality.

## Linear regression
Use when a coefficient conditional on prespecified covariates is the estimand.
HC3 robust standard errors can reduce sensitivity to heteroskedasticity in many ordinary OLS settings but do not fix dependence, omitted-variable bias, nonlinearity, or bad causal identification.
Inspect residual structure and influential observations.

## Categorical association
Chi-square for sufficiently populated contingency tables.
Fisher exact for 2x2 tables, especially small counts.
Report an association magnitude such as Cramér's V or odds ratio.

## Pearson chi-square definition

The core `chi_square` path uses **uncorrected Pearson chi-square** (`correction=False`) for the test statistic and p-value, and derives Cramér's V from that same statistic. The row-bootstrap interval for Cramér's V uses the same uncorrected Pearson definition. This keeps the inferential statistic, effect-size point estimate, and interval on one statistical definition. For sparse 2×2 tables, do not switch to or from Yates correction opportunistically after seeing the result; inspect expected counts and use Fisher/exact or a specialist categorical model when appropriate.

## Do not auto-select from normality tests
A Shapiro-Wilk p-value is sample-size dependent and does not encode the research estimand. Inspect distribution, residuals, sample size, scale, and robustness.

## Hierarchy / pseudoreplication
If cells are nested within animals, trials within participants, fields within specimens, etc., the independent unit is not the raw row. Consider subject-level aggregation only if it matches the estimand; otherwise use an appropriate multilevel/repeated model.

## Multiple groups / repeated timepoints
v1.4 supports two deliberately bounded independent-group cases: `welch_anova` for an omnibus mean comparison across three or more prespecified groups, and `welch_contrast` for an exact prespecified linear contrast of two or more independent group means. It still does not automate full factorial ANOVA/mixed-model decision trees. Repeated timepoints, crossed factors, covariate-adjusted multi-group designs, or interactions central to the question require a broader model rather than a collection of pairwise tests.

## Equivalence / noninferiority
Non-significance is not equivalence. Define a scientifically meaningful margin and use an appropriate equivalence/noninferiority procedure.

## Causal claims
Regression adjustment alone is not a causal design. Causal language requires assumptions and identification appropriate to the data-generating process.

## Rank tests and estimands

Mann–Whitney and Wilcoxon are often described too loosely as “nonparametric tests of medians.” That wording is generally unsafe. Their null hypotheses and interpretation depend on distributional/rank structure; a median difference can be a useful descriptive companion but is not automatically the tested estimand.

In v1.2+, median differences accompanying rank tests are labeled `descriptive` for this reason. If the scientific question is specifically a median difference, choose an estimator/inference procedure designed for that estimand rather than relying on a generic rank test label.

## Degenerate data are analysis failures, not zero effects

Constant inputs, zero within-group variance, identical paired differences, and rank-deficient regression designs can make a declared procedure undefined or misleading. Do not coerce these cases into effect size `0` or p-value `1`; stop and reconsider the estimand/model/data quality.

## Fisher exact orientation and zero cells

An odds ratio from a 2×2 table has an orientation. Declare `row_levels` and `column_levels` when the scientific direction matters. The skill records the exact level order and a textual odds-ratio orientation in the result table.

When at least one cell is zero, the ordinary sample cross-product odds ratio may be 0 or infinite and cannot share a finite Woolf interval without changing estimation rules. v1.2.1 therefore keeps the two-sided Fisher exact p-value on the **uncorrected fixed-margin table**, but reports a finite odds-ratio estimate + Woolf interval using an explicit Haldane–Anscombe 0.5 correction. The result records that correction. This is a pragmatic sparse-table summary, not a substitute for a specialist exact/penalized model when the odds ratio itself is the central estimand.


## Restricted two-group ANCOVA in v1.2

`ancova_two_group` answers a narrow question: the conditional mean difference between group B and group A after additive adjustment for prespecified numeric covariates. It assumes common covariate slopes across the two groups. It is not a generic replacement for factorial ANOVA, interactions, nonlinear regression, post-treatment adjustment, repeated measures, or clustered data.

HC3 standard errors can protect standard-error calculations against ordinary heteroskedasticity, but they do not repair model-form or causal-identification problems. Inspect condition number, leverage, Cook's distance, residual patterns, and scientific plausibility.

## Binary logistic regression in v1.2+

In v1.3+, GLM robust covariance is labeled `HC0`, not `HC3`; statsmodels GLM results do not provide a true HC3 covariance matrix through this path. OLS/ANCOVA retain HC3.

Declare the event and non-event levels explicitly. The reported odds ratio is for a one-unit increase in the selected numeric predictor conditional on the other declared numeric predictors. Odds ratios are not risk ratios and can be non-collapsible. Separation, rare outcomes, penalization/Firth methods, categorical encoding decisions, multinomial/ordinal outcomes, and clustered binary data require a broader workflow.

## Formal equivalence in v1.2

`equivalence_tost_independent` and `equivalence_tost_paired` implement two one-sided tests against prespecified raw-scale margins. The margin is a scientific input, not a value to optimize after seeing the data. A failed TOST means equivalence was not established; it does not prove a meaningful difference.


## Three or more independent groups

Use `welch_anova` when the estimand is a global comparison of means across at least three prespecified independent groups and unequal variances are plausible. The omnibus result is non-directional. Do not infer which groups differ from the omnibus p-value.

When the scientific estimand is a prespecified linear contrast—such as the mean of two treatment groups versus control—use `welch_contrast` rather than decomposing the question into unrelated pairwise tests. The contrast weights define the estimand and must be locked before seeing inferential results. Planned pairwise tests may still be separate `independent_t` items. Put multiple claims that belong to the same family into an explicit multiplicity family.

Do not use these core paths for repeated measures, nested samples, factorial interactions, covariate-adjusted multi-group general linear hypotheses, or data-driven post-hoc contrast discovery. Those designs require a broader model.

## Count outcomes

Use `poisson_regression` only for nonnegative integer counts with a scientifically meaningful log-link mean model. Numeric predictors are supported. If observation time/area/person-time differs, declare a strictly positive `exposure` column so the model uses `log(exposure)` as an offset, or declare a precomputed numeric `offset`.

Review Pearson dispersion and the zero fraction. Material overdispersion, excess zeros, clustering, repeated counts, or structural mixture processes can make a standard Poisson model inadequate even when HC0 sandwich-robust standard errors are used. Negative-binomial, quasi-Poisson, hurdle, zero-inflated, GEE, or mixed count models are explicit escalation cases rather than automatic substitutions.

## Prospective power/sample-size planning is a separate decision layer

Do not use the post-data hypothesis-test selector as a substitute for design planning. v1.6 power planning has a separate `power_plan_schema_version = "1.1"` contract and is run before main-study outcome analysis. Effect/variance/rate assumptions require provenance and should be stress-tested with scenarios. Observed/post-hoc power from the completed study is not an inferential remedy for a wide confidence interval or non-significant p-value. Read `power_sample_size.md`.
