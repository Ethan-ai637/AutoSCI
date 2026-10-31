# Iteration Policy

## Persistent goal, revisable method

Keep the user's approved method contribution and venue target active across candidate failures. Revise the method in response to evidence; preserve the goal and evaluation contract. An explicit user decision can change either.

Lack of positive evidence for the current candidate is not sufficient reason to end the research loop. It triggers a new candidate proposal tied to a failure mechanism, prior result, relevant source, or clearly labeled hypothesis. Do not impose an arbitrary iteration count as a scientific stopping rule. Follow user-approved resource limits, project policies, and execution approvals. When a limit blocks the next run, deliver the candidate and the precise resource or approval dependency.

The Skill organizes work toward a method contribution. It cannot ensure that any candidate will improve a score, establish novelty, or meet a venue's standards. Preserve that uncertainty in every report.

## Candidate quality

A candidate must specify:

- a concrete change to a method component;
- a plausible mechanism connected to the active claim;
- a falsifiable prediction on the frozen evaluation metric;
- a relevant source, prior result, theoretical argument, or explicitly provisional engineering hypothesis;
- one experiment that can distinguish the proposed mechanism from the previous candidate and baseline.

Do not recycle a failed configuration without a reasoned change. Keep exploratory candidate generation separate from confirmatory claims. A candidate may be tested with one run per condition; multiple seeds are optional unless the protocol or claim requires them.

## Positive increment and fair comparison

Define the intended positive increment using the approved goal and metric. Do not make an unregistered effect-size cutoff. When no justified threshold exists, state a directional hypothesis and report the estimate with appropriate uncertainty and limitations.

Compare method and baseline under the same benchmark version, official scope, splits, loader, evaluator, metric, and declared resource budget. Budget accounting should identify the relevant units, such as accelerator time/FLOPs, training tokens, inference tokens/API calls, data access, or tuning trials. Freeze the accounting rule before outcomes. Report any unavoidable mismatch and qualify the conclusion.

The minimum condition matrix may contain the proposed method and one strong comparator, with only mechanism-relevant ablations. “Minimum” refers to the number of conditions; it never authorizes benchmark subsampling, synthetic research data, or evaluator substitution.

## Frozen contract

Keep the following unchanged during method iteration unless the user approves a protocol revision before the affected run:

- benchmark identity/version and complete official tasks, examples, and splits;
- loader, evaluator, metric, aggregation, and data access conditions;
- baseline identity and resource-matching rule;
- decision thresholds, stopping rules, and statistical analysis plan;
- target claim and venue aspiration;
- API provider/model version, endpoint, prompts, decoding parameters, cache/retry behavior, and request-selection policy when APIs are involved.

If an official protocol changes or a contract revision is approved, version the protocol and state which conclusions remain comparable. Do not revise a frozen element after seeing outcomes to improve the measured result.

## Outcome and continuation states

Use states that preserve both scientific accuracy and forward motion:

- `candidate_planned` — hypothesis, condition matrix, and budget are ready for review;
- `awaiting_approval` — protocol or resource authorization is required;
- `running` — an approved execution is active;
- `observed_no_gain` — the candidate did not improve under the frozen comparison; retain evidence and prepare the next candidate;
- `observed_support` — results support the directional hypothesis under the frozen comparison; record limitations and next validation;
- `incomplete` — execution or artifacts do not support a complete comparison;
- `blocked` — a specific resource, protocol, data-access, or tooling dependency prevents the next valid test;
- `user_paused` or `goal_changed` — recorded only after the corresponding user decision.

A diagnostic or blocker report includes the active goal, the next proposed candidate, the experiment needed, and the exact dependency. A NO-GO label alone does not satisfy the iteration contract. Keep unsuccessful and incomplete outcomes in append-only research records; do not omit them from summaries of tried candidates.

## Reporting language

Separate hypothesis from evidence. Use `planned` for unrun work, `observed` for executed outcomes, and `incomplete` or `blocked` when the comparison cannot support a conclusion. A selected run or seed is a selection-conditioned result and must be labeled accordingly. Preserve negative results as method-development evidence; never rewrite them as positive findings.
