---
name: method-goal-pursuit
description: Keep a method-paper goal active by selecting task-relevant, challenging real-world benchmarks and centering main experiments on a small, justified baseline and SOTA comparison set.
---

# Method Goal Pursuit

Use this Skill to keep a declared method-paper contribution moving through evidence-led iterations centered on the main experiment. Choose benchmarks that directly represent the research task, document meaningful difficulty, and reflect real-world use. Keep the approved benchmark scope, metrics, decision rules, and protocol obligations stable while improving the method candidate. Apply it to autonomous method-research loops, including AutoSOTA-style work.

The working commitment is persistent pursuit with honest evidence. A candidate that underperforms creates a reason to revise the method and test another defensible candidate. The cycle must keep producing a concrete next experiment. A diagnostic report or NO-GO label alone does not complete an iteration.

This Skill cannot promise score gains, novelty, or acceptance. It never hides an unfavorable result, changes an evaluation rule to create a favorable result, or claims an unobserved improvement.

## Invariants

- Keep the user's declared method contribution and venue goal active. Do not reframe the project as a benchmark report, finding-only paper, or lower-tier target solely because an early candidate fails. Change the goal or target only when the user explicitly changes it.
- The absence of positive evidence for the current candidate is not a stopping reason. Use the result to propose the next evidence-grounded method and experiment while the approved goal remains active.
- Make the main experiment the center of each iteration. Compare the proposed method with a small, rationale-selected set of relevant baselines and SOTA methods. Select comparators by claim relevance, strength, protocol comparability, and reproducibility; explain the selection without inventing a universal count.
- Select benchmarks for conclusion value: direct fit to the research claim, evidence of real-world relevance, and documented challenge. Read [Benchmark selection](references/benchmark-selection.md), record sources and tradeoffs, and freeze the choice before outcome access. Do not choose a benchmark because it appears easier for the proposed method.
- Prefer official benchmarks grounded in real-world data or validated operational tasks. Do not use toy or synthetic/generated research data as benchmark evidence. If a benchmark has limited real-world coverage, state the boundary and add a complementary real-world benchmark only when it is needed for the claim.
- A SOTA method used in the controlled main experiment must have publicly accessible source code under a clearly identified open-source license compatible with the planned research use, plus downloadable required checkpoints/assets. Verify the repository, pinned revision, license, and artifact access before selection. If code or required files are unavailable, record the blocker and replace it with the next strongest comparable open-source method. Keep published-paper scores labeled as literature results, never as rerun baseline measurements.
- Freeze the approved benchmark/version, complete official task and split scope, loader, evaluator, metric, baseline, analysis, acceptance rule, and relevant API contract. Preserve independent API freeze rules for each API condition, including model/version, endpoint, prompts, decoding parameters, retries, caching, and request-selection rules when applicable.
- Use the complete official benchmark scope for every scientific candidate and baseline run. A minimal experiment may reduce the number of conditions; it must preserve complete benchmark coverage for each condition.
- Keep every numeric success, continue, stop, or resource gate tied to its applicable source or derivation under `experiment-goal-design` and `experiment-execution`. Never invent a score margin, seed count, threshold, or stopping rule. If no threshold is justified, use a prespecified estimation/comparison goal or leave the decision unresolved.
- Default to one run/seed per condition. Add repeats when the official protocol or the scientific claim requires them, with the count justified and frozen before outcomes. Preserve every attempt and disclose any optional late seed selection.
- Compare the proposed method with a small, justified set of relevant baselines and SOTA methods under the same declared resource budget and evaluation contract. Include the strongest directly comparable methods when their protocols can be matched. Match the budget dimensions that govern the method, such as training compute, inference tokens/API calls, data access, tuning trials, and wall-clock allocation. Record the selection rationale and exact accounting. If comparable budgets cannot be established, report the resource difference and keep the performance comparison qualified.
- Keep failures, null results, and deviations in the research record. A favorable claim must be supported by observed results under the frozen contract.
- Do not launch costly remote compute or incur API expense without the authorization required by the project and user.

## Iteration workflow

### 1. Restore the active goal

Read the current research state, findings, approved goal contract, and protocol. Write the active contribution and target venue in the iteration record. List the evaluation and resource invariants that remain frozen. If benchmark selection is still open, defer method-specific outcome review until the benchmark is selected and frozen. If the protocol is missing or unapproved, draft the next experiment and identify the approval needed before execution.

### 2. Select or confirm the benchmark

Read [Benchmark selection](references/benchmark-selection.md). Preserve an already approved benchmark contract across method iterations. If benchmark choice is still open, compare official candidates against the claim, real-world grounding, documented difficulty, evaluation quality, and protocol comparability before reviewing method-specific outcomes. Record the evidence and decision before accessing outcomes that could influence selection. Select one main benchmark when it fully answers the claim; add a small complementary set only when the claim requires broader coverage. Use every selected benchmark's complete official scope. If no suitable full-scope benchmark is accessible, keep the campaign blocked at that dependency and propose a valid access path or a user-approved protocol change.

### 3. Learn from the latest attempt

Inspect the recorded result, logs, configuration, and protocol-compliance evidence. State what the outcome supports, what it rules out, and what remains uncertain. Treat diagnosis as an input to method design. Keep the next method candidate and experiment as required outputs of the round.

### 4. Propose the next method candidate

Choose a candidate that addresses a specific failure mechanism or tests a credible new mechanism. Ground the proposal in relevant literature, theory, prior experiments, or a clearly labeled engineering hypothesis. Record:

- the exact method change and the component it affects;
- the mechanism connecting that change to the active research claim;
- a falsifiable directional hypothesis on the frozen metric;
- the source, prior result, or reasoning that motivates the change;
- the main failure mode and the evidence that would distinguish it.

Prefer a meaningful method change over arbitrary hyperparameter movement. Do not call a proposed improvement an observed result. If several candidates are plausible, select one lead candidate and list alternatives only when they add a distinct testable mechanism.

### 5. Design the main experiment

Make the experiment that directly tests the paper's main claim the primary deliverable. Include the lead method and a small, justified comparator set covering relevant baselines and SOTA methods. Prefer the strongest directly comparable SOTA methods and canonical baselines needed to interpret the result. Every controlled SOTA comparator must have accessible code under a compatible open-source license and downloadable required artifacts; replace unavailable methods with the next strongest comparable option and record the reason. Explain why each selected method is relevant and why any obvious alternative is omitted. Add an ablation only when it isolates a mechanism needed for the main claim. Keep every condition on the complete official benchmark scope under the frozen loader and evaluator. Define the condition matrix, configs, one-seed default, matched resource budget, metric, expected artifacts, and analysis before running.

Use the already-approved success or decision rule. Do not move the goalposts after inspecting results. When the goal has no defensible numerical gate, compare the prespecified estimate and uncertainty and state the limits of a single run.

Use `experiment-execution` for campaign preflight, run identity, attempt records, scope manifests, and provenance audit when it is installed. Hand off only an approved protocol and a validated campaign. Keep method iteration planning separate from authorization to execute.

### 6. Record and continue

Append the candidate, hypothesis, frozen contract, budget match, planned experiment, outcomes, and next action to the method iteration record. Mark each statement as `planned`, `observed`, `incomplete`, or `blocked` as appropriate. Preserve raw evidence and failures.

If a candidate improves the frozen metric under the declared comparison, record the evidence and plan the next validation step required by the approved protocol. If it does not, name the next evidence-based method candidate and its experiment. If resources or protocol approval prevent a run, retain the active goal, specify a viable candidate, and state the exact dependency needed to test it. A user pause or an explicit goal change is recorded as such.

## Required output for every round

Every iteration ends with a concise forward plan containing:

1. active method-paper claim and target venue;
2. selected benchmark and evidence for task fit, real-world relevance, and challenge;
3. evidence-based interpretation of the last attempt;
4. next method candidate and falsifiable mechanism hypothesis;
5. main experiment with complete benchmark scope and a small, justified baseline/SOTA comparator set whose code and required artifacts are accessible;
6. equal-budget comparison and resource accounting for every selected comparator;
7. frozen metric, protocol, threshold evidence, and one-seed plan;
8. required approval/resource dependency and next executable action.

Use [`references/benchmark-selection.md`](references/benchmark-selection.md) for benchmark choice, [`references/iteration-policy.md`](references/iteration-policy.md) for continuation and reporting boundaries, and [`templates/method-iteration.template.md`](templates/method-iteration.template.md) for each round's record.
