# Results to prose

## Principle

A Results paragraph is a compressed, accurate view of the analysis—not a place to maximize rhetorical strength.

## Recommended sentence order

1. State the question/comparison.
2. Name the relevant population, condition, endpoint, or model if ambiguity exists.
3. Report direction and magnitude.
4. Report uncertainty/statistical evidence when available.
5. Point to the supporting figure/table.
6. Add only restrained interpretation that is needed to understand the result.

## Numeric discipline

Preserve:

- numerator/denominator and analysis population;
- sign/direction;
- unit;
- estimate type;
- CI/credible interval/SE/SD distinction;
- raw vs adjusted values;
- multiplicity-adjusted vs unadjusted p-values;
- timepoint and baseline definition;
- reference category.

Do not replace a confidence interval with only a p-value when the interval is available.

## Null results

Prefer wording such as:

- “We did not detect a difference…”
- “The estimate was compatible with both small benefit and small harm…”
- “The analysis did not provide evidence of association…”

Do not write “there was no effect” unless the design/analysis actually supports equivalence or a sufficiently bounded null conclusion.

## Multiple analyses

Label primary, secondary, exploratory, subgroup, sensitivity, and post hoc analyses explicitly when relevant. Do not present an exploratory analysis as if it were the preregistered primary result.

## Benchmark / ML / engineering results

Keep dataset/split, metric, comparator, evaluation protocol, and uncertainty together. A higher metric on one benchmark does not automatically establish general superiority, robustness, or real-world utility.
## Numeric-token contract

`evidence.value_tokens` records exact source tokens that may need preservation. Claim-level `required_value_tokens` controls which of those tokens must appear verbatim in a specific claim.

- `required_value_tokens: null` -> for a `Results` / `result` claim, inherit all linked evidence tokens; elsewhere inherit none.
- `required_value_tokens: []` -> no exact-token requirement for that claim.
- `required_value_tokens: ["12.4", "0.03"]` -> those tokens must appear exactly in the claim.

This prevents Abstract, Discussion, and Conclusion from being forced to repeat every statistic while keeping precise Results claims mechanically auditable. Use the list explicitly when rounding or selective reporting is scientifically intended.\n