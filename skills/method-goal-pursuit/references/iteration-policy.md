# Method Iteration Policy

## Persistent goal, revisable method

Keep the user's approved method contribution and venue target active across candidate failures. Revise the method in response to evidence; preserve the goal and frozen evaluation contract. An explicit user decision can change either.

Lack of positive evidence for the current candidate is not sufficient reason to end the research loop. It triggers a new candidate proposal tied to a failure mechanism, prior result, relevant source, or clearly labeled hypothesis. Do not impose an arbitrary iteration count as a scientific stopping rule. Follow user-approved resource limits, project policy, and execution approvals. When a limit blocks the next run, deliver a candidate and the precise resource or approval dependency.

The Skill supports research toward a method contribution. It cannot ensure that a candidate will improve a score, establish novelty, or meet a venue's standards. Preserve that uncertainty in every report.

## Candidate quality

A candidate must specify:

- a concrete change to a method component;
- a plausible mechanism connected to the active claim;
- a falsifiable prediction on the frozen evaluation metric;
- a relevant source, prior result, theoretical argument, or explicitly provisional engineering hypothesis;
- an experiment that can distinguish the proposed mechanism from the previous candidate and baseline.

Do not recycle a valid unfavorable configuration without a reasoned method change. Keep exploratory candidate generation separate from confirmatory claims. Early and exploratory screening uses one complete valid run per condition. Multi-seed or multi-replicate evaluation is optional; it is not a default requirement for preliminary experiments, continued method work, or paper readiness. Add valid repeats only in a prospectively declared confirmatory campaign when the official protocol, claim, or supported statistical plan justifies them. Record the applicable source and locator or statistical derivation, then freeze the rationale and count before viewing those outcomes. Common practice or venue reputation alone does not justify a repeat count. One seed remains valid when no supported requirement calls for more. Do not add seeds automatically to improve a weak score. Technical recovery of an incomplete attempt is handled separately below and does not add a seed or replicate.

## Outcome access and benchmark choice

When benchmark selection is open, first review the approved goal, protocol, candidate benchmark inventory, and other non-outcome metadata. Keep project-specific scores, result summaries, run logs, plots, predictions, and review judgments out of the selection decision until it is recorded and frozen. Follow local repository instructions; if they require earlier result access, record the exposure and classify the affected selection accordingly.

Official benchmark documentation, data cards, design papers, and published evaluations can support judgments about construction, difficulty, protocol, and limitations. Record the source and state when published results influenced selection. Do not inspect current project candidate results to find a favorable benchmark, split, metric, or task list.

If relevant outcomes have already been seen, preserve them and state the exposure. Adaptive method selection after reviewing results is exploratory. For a confirmatory claim, freeze the candidate, analysis, and campaign before accessing an outcome source that has not influenced benchmark choice or candidate development. This may require an untouched official split or a distinct official benchmark when required by the claim. Keep full official scope for each selected benchmark.

## Main experiment and comparator set

Center the paper's main experiment on the central method claim. Compare the candidate with a small, justified set of relevant baselines and SOTA methods under the same benchmark version, official scope, split, loader, evaluator, metric, and declared resource budget. Select comparators by claim relevance, strength, protocol compatibility, and reproducibility. Include strong directly comparable SOTA methods and canonical baselines needed to interpret the result. State the rationale for selections and important omissions. No universal comparator count applies.

For each controlled SOTA comparator, verify the public source repository, pinned revision, code license, setup instructions, entry point, required checkpoints/assets, separate asset terms, download route, and available hashes. Record benchmark/evaluator compatibility and required data access. Do not treat a published paper score, public repository, or successful download alone as proof of a reproducible controlled comparison.

Record access-failure fallbacks in rank order before outcome review. Replace a method only for a documented access, licensing, compatibility, or implementation failure under the declared environment. Preserve every failed attempt and its artifacts. A valid but unfavorable score is evidence; it is not a reason to swap the comparator. A partial failed run is incomplete and cannot be reported as a benchmark score.

Check implementation readiness with static checks, dependency resolution, imports, config validation, or command help. A benchmark-subset smoke evaluation is prohibited. Isolated engineering fixtures can validate plumbing but never count as scientific evidence. A method's complete official-scope run and audit establish controlled comparability.

Budget accounting should identify relevant units such as accelerator time/FLOPs, training tokens, inference tokens/API calls, data access, tuning trials, and wall-clock allocation. Freeze the accounting rule before outcome review. Report unavoidable mismatch and qualify the comparison. Before preflight, estimate full-scope runtime, peak memory, and storage, identify the accelerator class, and cite the evidence used for each estimate.

The condition matrix can stay small by limiting it to the proposed method, selected comparators, and mechanism-relevant ablations. Small applies to the number of conditions; it never authorizes benchmark subsampling, synthetic research data, or evaluator substitution. Do not let an ablation or parameter catalog displace the primary comparison.

## Incomplete execution and technical recovery

Treat an attempt as incomplete when it fails before producing a valid result over the complete frozen scope, including failures that leave missing outputs or an unverifiable scope manifest. Do not treat partial metrics or predictions as a benchmark result or use them to choose or tune the next method candidate. Follow mandatory local artifact-access rules and record any exposure; exclude exposed partial outcomes from the next-candidate rationale. Error messages, environment diagnostics, and provenance may be inspected to identify the technical fault. If partial outcomes have been accessed, classify subsequent candidate evaluation as exploratory and use an untouched outcome source for a confirmatory claim.

When a specific technical fault has a supported correction, preserve the original attempt unchanged and record its cause, artifacts, and config/source/environment hashes. Make a new attempt with a new identity and rerun the complete official scope using the same predeclared seed or replicate. The correction must preserve method semantics, comparator identity, benchmark, metric, analysis, and decision rules. A stateful resume is allowed only when the official protocol supports it and the final audit proves full-scope coverage.

A technical recovery is not an additional statistical replicate. Count only one complete valid run per condition during exploratory screening. If the correction changes method behavior or any frozen contract element, register a new candidate or approve a protocol revision before execution. If a complete valid result is unfavorable, do not classify it as a technical failure or rerun it for a more favorable score; use the evidence to design the next method candidate. Every recovery must fit within the approved resource envelope. API request retries remain governed by their independently frozen retry contract.

## Frozen contract

Keep the following unchanged during method iteration unless a protocol revision is approved before the affected run:

- benchmark identity/version, official task/example/split inventory, and complete required scope;
- loader, evaluator, metric, aggregation, and data-access conditions;
- comparator identities and resource-matching rule;
- decision thresholds, stopping rules, and statistical analysis plan;
- target claim and venue aspiration;
- API provider/model version, endpoint, prompts, decoding parameters, cache/retry behavior, and request-selection policy when APIs are involved.

If an official protocol changes or a contract revision is approved, version the protocol and state which conclusions remain comparable. Do not revise a frozen element after seeing outcomes to improve the measured result. Numeric gates require an applicable source or explicit derivation with a precise locator. When no supported numeric gate exists, preregister an estimation or comparison objective and leave the decision unresolved where needed.

## Outcome and continuation states

Use states that preserve scientific accuracy and forward motion:

- candidate_planned — hypothesis, condition matrix, and budget are ready for review;
- awaiting_approval — protocol or resource authorization is required;
- running — an approved execution is active;
- observed_no_gain — the candidate did not support the directional hypothesis under the frozen comparison; retain evidence and prepare the next candidate;
- observed_support — results support the hypothesis under the frozen comparison; record limitations and next validation;
- incomplete — execution or artifacts do not support a complete comparison;
- blocked — a specific resource, protocol, data-access, or tooling dependency prevents the next valid test;
- user_paused or goal_changed — recorded only after the corresponding user decision.

A diagnostic or blocker report includes the active goal, next proposed candidate, needed experiment, and exact dependency. A NO-GO label alone does not satisfy the iteration contract. Keep unsuccessful and incomplete outcomes in append-only research records and disclose them when summarizing tried candidates.

## Reporting

Separate hypothesis from evidence. Use planned for unrun work, observed for executed outcomes, and incomplete or blocked when the comparison cannot support a conclusion. Preserve negative results as method-development evidence; never rewrite them as positive findings. A selected run or seed is selection-conditioned and must be labeled accordingly. Exploratory adaptation and confirmatory evidence must be distinguished in the paper and experiment records.
