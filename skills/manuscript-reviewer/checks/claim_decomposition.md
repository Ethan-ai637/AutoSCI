# Atomic claim decomposition and scope normalization

## Objective

Prevent compound scientific sentences from receiving one vague evidence judgment when their clauses require different evidence.

## Atomicity rule

Before claim–evidence mapping, split a material sentence into the smallest independently testable propositions that could differ in truth or support state.

Example:

> "Our method is more accurate, robust to domain shift, and suitable for real-world deployment."

Treat as at least three claims:
1. comparative accuracy;
2. robustness under domain shift;
3. real-world/deployment suitability.

Do not let evidence for one clause support the others by proximity.

## Preserve qualifiers

For every atomic claim, retain qualifiers that change scope or evidentiary burden:
- all / some / most;
- consistently / on average;
- significantly;
- under the tested settings;
- in-domain / out-of-domain;
- across datasets / on Dataset X;
- causal verbs such as causes, drives, explains;
- temporal qualifiers;
- population/subgroup qualifiers;
- resource constraints;
- safety/reliability qualifiers.

A qualifier removed during paraphrase can change the review outcome. Prefer exact wording for contentious claims.

## Claim identity

Two claims are the same root claim only when their scientific proposition and scope are materially equivalent.

Examples:
- "best average accuracy across datasets" is not identical to "best on every dataset";
- "lower parameter count" is not identical to "lower inference cost";
- "robust to Gaussian noise" is not identical to "robust to distribution shift".

## Compound citation rule

When one sentence contains multiple externally sourced propositions followed by one citation cluster, map citations to atomic propositions before deciding whether support is clear.

## Output discipline

Do not flood the final report with every atomic claim. Atomic decomposition is an internal reasoning tool. Report only material mismatches, and merge related atomic failures when they share one root cause.
