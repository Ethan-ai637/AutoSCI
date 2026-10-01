# Prospective power and sample-size planning

## Scope

The v1.6 planning workflow is deliberately **pre-data**. It answers design questions under declared assumptions; it does not reinterpret a completed study using observed/post-hoc power.

Supported core designs:

1. `welch_two_group_mean` — two independent groups, raw mean difference oriented as group B minus group A, with separate assumed SDs and Welch–Satterthwaite noncentral-t planning.
2. `welch_contrast` — a prespecified linear contrast of two or more independent group means under heteroscedasticity, aligned with the post-data `welch_contrast` inference family.
3. `paired_mean` — paired/repeated two-condition mean difference, planned using the SD of within-pair differences.
4. `independent_proportions` — two independent binary proportions, planned with a two-proportion normal approximation using pooled-null and non-pooled-alternative variance.

Supported solve targets:

- `sample_size`: solve analyzable integer sample size for a target power;
- `prospective_power`: calculate design power for a fixed **prospectively chosen analyzable n** under a prespecified effect assumption;
- `minimum_detectable_effect`: solve the raw continuous effect detectable at a fixed n and target power. This is available for the continuous mean and planned-contrast designs, not the binary-proportion design.

## Hard rules

- Declare `unit_of_analysis` explicitly in the power plan. Sample size refers to this independent scientific unit.
- Never substitute the observed effect estimate from a completed study and label the result "power" evidence for or against the study conclusion.
- Every planning item requires `assumption_source`. Use `scientific_threshold` for a smallest effect worth detecting, `external_evidence` for prior independent evidence, `pilot` for genuine pre-main-study pilot information, or `scenario` for an intentionally hypothetical design scenario.
- If an effect assumption comes from a pilot, preserve the pilot's uncertainty and run sensitivity scenarios rather than treating a noisy pilot point estimate as truth.
- Power is conditional on assumptions. It is not `P(H1 is true | data)` and it is not a substitute for confidence intervals after data collection.
- Sample-size inflation for attrition only changes enrollment targets. It does not model informative dropout, noncompliance, clustering, or missing-not-at-random mechanisms.
- The planned unit count must refer to the independent analysis unit. Technical replicates do not increase biological/sample-level power unless the scientific estimand and analysis model truly operate at that level.
- One-sided alternatives require a direction justified before seeing outcome data. For mean/proportion designs, `larger` means the declared signed effect is positive and `smaller` means it is negative.

## Welch two-group mean planning

Required assumptions:

- raw `mean_difference` (B − A) for `sample_size` / `prospective_power`;
- `sd_a`, `sd_b` > 0;
- allocation ratio `n_b / n_a` for sample-size solving;
- alpha, alternative, target power as applicable.

The tool uses

`SE = sqrt(sd_a^2 / n_a + sd_b^2 / n_b)`

and Welch–Satterthwaite degrees of freedom, then computes noncentral-t power. For `sample_size`, integer group sizes are searched and power is recomputed after rounding.

For `minimum_detectable_effect`, the tool numerically solves the raw B − A difference needed to reach target power at fixed `n_a`, `n_b`, and assumed SDs.

## Welch planned-contrast planning

`welch_contrast` is for an **exact, prespecified linear contrast**

`theta = sum_i c_i * mu_i`

across independent groups. Each `contrast_terms` entry declares:

- `level` — the scientific group label;
- `weight` — the fixed contrast coefficient;
- `sd` — the prospective within-group SD assumption;
- for `sample_size`, an `allocation_ratio` (default `1.0`);
- for fixed-n `prospective_power` / `minimum_detectable_effect`, an integer analyzable `n`.

The weights must be non-zero, include at least one positive and one negative coefficient, and sum to zero. They define the estimand. The skill never normalizes or data-optimizes the weights.

For fixed group sizes:

`Var(theta_hat) = sum_i c_i^2 * sd_i^2 / n_i`

and the planner uses

`df = Var(theta_hat)^2 / sum_i [ (c_i^2 * sd_i^2 / n_i)^2 / (n_i - 1) ]`

with a noncentral-t power calculation.

For `sample_size`, each declared `allocation_ratio` is normalized by the smallest ratio. The planner searches the smallest integer reference-group n under those normalized ratios, rounds every group upward with `ceil`, and recomputes power at the actual integer group sizes. Multiplying all allocation ratios by the same constant therefore does not change the design.

`contrast_effect` is the raw value of the declared linear contrast, not a standardized effect. For example, with weights `[-1, 0.5, 0.5]`, a `contrast_effect` of `5` means `(mean_B + mean_C)/2 - mean_A = 5` in the outcome's original units.

Scenario overrides may alter SDs, sample-size/allocation assumptions appropriate to the solve mode, or the raw contrast effect, but if `contrast_terms` is replaced the **typed levels, order, and weights must remain identical**. A scenario is not allowed to silently redefine the contrast estimand.

## Paired mean planning

Use `sd_difference`: the SD of within-pair differences. Do not substitute the marginal SD from condition A or B unless that is actually justified by the dependence structure.

For fixed `n_pairs`, the planning SE is `sd_difference / sqrt(n_pairs)` with `df = n_pairs - 1` and noncentral-t power.

## Independent proportions

The planning effect is the declared event-rate difference B − A. The core calculation uses the two-proportion normal approximation implemented with pooled null variance and non-pooled alternative variance; Cohen's h is reported descriptively and is not the quantity used to solve the sample size.

Every result records expected events and non-events under the declared alternative rates:

- `expected_events_a`, `expected_nonevents_a`;
- `expected_events_b`, `expected_nonevents_b`;
- `min_expected_cell_count`;
- `normal_approximation_adequacy`.

The release QA uses a deliberately conservative count heuristic:

- `< 1`: `poor_extreme_sparsity` and power preflight **fails** release;
- `1` to `< 5`: `caution_sparse` and power preflight emits a warning;
- `>= 5`: `adequate_by_conservative_count_rule`.

This is not a theorem that guarantees normal-approximation accuracy. Rare events, highly imbalanced rates, small samples, exact-test designs, regulatory contexts, or high-consequence planning may require exact or simulation-based design calculations even when the heuristic passes. Conversely, a count below 5 is a conservative review trigger rather than proof that every normal approximation is unusable.

## Scenario analysis

Each planning item can contain named `scenarios` whose `overrides` change explicit assumptions. Overrides are validated against both the design type and `solve_for`: a scenario is rejected if the requested field would be ignored by that calculation.

Examples:

- two-group `sample_size`: vary the assumed effect/rates, variability, allocation ratio, alpha, target power, sidedness, or attrition; do not override solver-owned n fields;
- `welch_contrast` `sample_size`: vary `contrast_effect`, alpha/target/sidedness/attrition, or replace `contrast_terms` only to change SD/allocation assumptions while preserving the exact levels and weights;
- fixed-n `prospective_power`: vary effect/rates, variability, fixed n, alpha, target benchmark, sidedness, or attrition;
- `minimum_detectable_effect`: vary variability, fixed n, alpha, target power, sidedness, or attrition; do not override the effect because the effect is the quantity being solved.

For prospective-power plots, a single target line is used only when all scenarios share the same target. If scenario target powers differ, each scenario receives its own target marker. Scenario tables are not probability distributions. Do not label the most convenient scenario "likely" unless supported independently.

## What the v1.6 core does not cover

The core planner intentionally does not automate clustered/cluster-randomized designs, multi-timepoint repeated measures, survival/time-to-event designs, complex regression power, adaptive/sequential monitoring, Bayesian assurance, equivalence/noninferiority sample size, or negative-binomial/zero-inflated count planning. Those require additional design-specific parameters and should not be reduced to a generic independent-sample calculation.
