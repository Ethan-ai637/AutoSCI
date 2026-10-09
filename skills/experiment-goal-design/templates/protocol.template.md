# Experiment Protocol — Draft for Approval

**Status:** Draft (not approved for execution)<br>
**Protocol ID / version:**<br>
**Created / last changed:**<br>
**Approval owner / approval date:** Pending

## Research question and claim

State the research question, claim ID(s), target population/task, hypothesis or estimand, and what this protocol can and cannot establish.

## Evidence and comparability basis

Link the relevant source IDs and the comparability matrix. Identify the strongest relevant benchmark/protocol and prior studies, explain why the selected comparators transfer, and list unresolved protocol differences.

## Evaluation scope and data protocol

For each evaluation protocol ID, record dataset/benchmark identity and version, population/track, complete required scope/splits, official loader, evaluator, metric/aggregation, and exact source IDs/locators. If a named official benchmark is used, run its complete official scope. Do not use hand-picked subsets.

## Conditions, experimental factors, and controls

List every condition ID, method/system, baseline/control/ablation role, factor level, linked goal/protocol, and randomness mode. State controlled variables and deviations from the anchor protocols. Keep comparisons fair and explain any unavoidable difference.

## Outcomes and analysis

Name the primary metric, unit, aggregation, analysis unit, estimand, uncertainty method, assumptions, and multiplicity handling where applicable. State how each outcome would weaken or fail to support the claim. A directional or estimation goal is valid without an arbitrary score cutoff.

## Decision thresholds

List only supported/derived numerical criteria and their threshold IDs, source locators, applicability, and derivation from the goal contract. If none are justified, write: **No numeric go/no-go threshold; report the prespecified estimate/comparison and uncertainty.** Do not invent a threshold.

## Run and randomness plan

Default to one run per condition: one predeclared seed for seeded stochastic methods, one replicate ID for uncontrolled stochastic methods, or one seedless run for deterministic methods. State why additional runs are needed if planned. Late seed selection for a higher score is optional, must preserve all tried results, and must be disclosed; it is not a required experiment.

## Deviations, outcome access, and change log

Record changes with date, reason, affected goal/threshold, whether outcomes had been accessed, and whether the affected analysis is now exploratory/post hoc.

## Execution handoff checklist

Before campaign preflight, the execution workflow must add the approved protocol path/hash, source revision/state, immutable configs and hashes, run IDs, checkpoint policy, full official scope manifests, and full-scope runtime/memory/storage estimate with evidence basis. These execution details do not authorize a scope reduction.

## Approval

- Research owner:
- Reviewer (if applicable):
- Approval decision and date:
- Conditions or unresolved items:
