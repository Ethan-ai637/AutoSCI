---
name: method-goal-pursuit
description: Sustain a method-paper goal through evidence-led method iterations, full-scope benchmark experiments, and runnable open-source baseline and SOTA comparisons.
---

# Method Goal Pursuit

Use this Skill when pursuing a method-paper contribution through repeated experiment and method-design cycles, including AutoSOTA-style workflows. Keep the declared contribution and venue goal active while improving the method against a frozen evaluation contract. Each round must produce a concrete method candidate, a falsifiable hypothesis, and a main experiment that can test it.

The research direction remains active when a candidate has no positive result. Use evidence to change the method and test a defensible next candidate. Keep unfavorable and inconclusive outcomes visible. The Skill supports forward progress; it cannot guarantee a score gain, novelty, or acceptance.

## Invariants

- Preserve the user's method-paper contribution and venue goal. Do not reframe the work as a findings-only paper, a benchmark report, or a lower-tier submission solely because a candidate fails. Change the goal only when the user does.
- Make the main experiment the center of each iteration. Compare the proposed method with a small, justified set of relevant baselines and SOTA methods. Explain each method's claim relevance, strength, protocol compatibility, and reproducibility. Do not invent a universal comparator count.
- Select benchmarks for claim fit, real-world relevance, documented challenge, evaluation validity, and full-scope feasibility. Use the benchmark-selection procedure. Do not select a benchmark because observed results make it look favorable.
- Keep project-specific outcome artifacts out of an open benchmark-selection decision. Follow local instructions about required files; if they require reading result-bearing material before selection is frozen, record the exposure and do not claim outcome-independent selection. Benchmark papers and official documentation may establish task design and difficulty; disclose when published evaluations materially informed the choice.
- Prefer official benchmarks with evidence tied to the intended population, domain, workflow, and deployment setting. Record the data collection period or version date, currentness relative to the claim, and known population or distribution limits. Do not impose an arbitrary age cutoff.
- Use every task, example, and split required by the official protocol for every scientific condition. Reduce the number of conditions when resources are limited; never reduce benchmark coverage. Do not use hand-picked subsets, toy benchmark tasks, synthetic or generated research data, or replacement loaders/evaluators as scientific evidence. Isolated engineering fixtures are not research evidence.
- Freeze the benchmark version, official scope inventory, loader, evaluator, metric and aggregation, comparator set, analysis, decision rules, and applicable API contract before confirmatory outcomes are accessed. For every run, retain the loader-emitted scope manifest and audit complete coverage. A benchmark change or a post-outcome selection must be labeled and justified in the record.
- A controlled SOTA comparator must have publicly accessible source under a clearly identified open-source license compatible with the planned use. Verify the separate terms and availability of every required checkpoint, dataset, and asset; pin the source revision and record verified download locations and hashes. If source or required assets are inaccessible, unavailable, or incompatible, use the next strongest comparable open-source candidate and document why.
- Freeze a ranked fallback list for access or implementation failures before outcome review. Do not replace a comparator because its valid result is unfavorable. Preserve every failed attempt and its original config, source, environment, and artifacts. If execution is incomplete because of a technical fault, a recovery attempt may correct that fault with the same predeclared seed or replicate; it must use a new attempt identity and full official scope. Do not inspect partial metrics or predictions to tune the method. An incomplete attempt is not a statistical replicate. If the correction changes method semantics, benchmark scope, metric, comparator, or analysis, treat it as a new candidate or protocol revision and obtain the required approval before execution. Keep recovery within the approved resource estimate; retain the frozen API retry policy.
- Tie every numeric success, continuation, stopping, and resource gate to an applicable source or explicit derivation with a precise locator. Never invent a score margin, threshold, seed count, or stopping rule. When no numeric gate is justified, prespecify an estimate or comparison objective and leave unresolved decisions explicit.
- Early and exploratory screening uses exactly one complete valid run per condition: one seed when controllable, one replicate for an uncontrolled stochastic API, and one run for a deterministic method. Technical recovery of an incomplete attempt does not add a seed or replicate and cannot contribute partial results. Multi-seed or multi-replicate evaluation is optional, never an automatic requirement for initial experiments, method progress, or paper readiness. Add repeats only in a predeclared confirmatory campaign when an official protocol, the target claim, or a supported statistical plan justifies them; cite the applicable source and locator or provide the statistical derivation, then freeze the rationale and count before seeing those outcomes. A generic appeal to common practice or venue reputation is insufficient. One seed remains valid when no supported requirement applies. Do not add seeds solely because an early result is weak or the target venue is selective. Keep API conditions under their independent freeze rules.
- Match the resource budget dimensions that govern each method, such as training compute, inference tokens or API calls, data access, tuning trials, and wall-clock allocation. Record units, amounts, evidence, and unavoidable mismatches. Before campaign preflight, include finite positive estimates for full-scope runtime, peak memory, and storage, the intended accelerator class, and the evidence basis. Qualify conclusions when budgets cannot be matched.
- Preserve all attempts, failures, null results, deviations, and raw artifacts. A favorable claim requires observed evidence under the frozen contract. Do not launch costly remote compute or incur API expense without the required authorization.

## Workflow

### 1. Restore the active goal and check outcome access

Read the project instructions, research state, approved goal contract, and protocol. Check whether the benchmark and evaluation contract are already frozen. If they are frozen, inspect findings, logs, metrics, and other relevant outcomes. If benchmark selection is open, first inspect only material allowed by the outcome-access rule above. Record the active contribution, target venue, current benchmark-selection state, and evaluation/resource invariants.

If the protocol is missing or unapproved, prepare the next protocol draft and identify the approval needed before execution. Planning an experiment does not authorize its execution.

### 2. Select or confirm the benchmark

Read [Benchmark selection](references/benchmark-selection.md). Preserve an approved benchmark contract across method iterations. For an open selection, compare official candidates using primary sources for task fit, real-world grounding, documented challenge, evaluation validity, and access. Record rejected candidates and the evidence for each decision. Freeze the selected benchmark before reviewing project outcomes that could influence the choice.

Record the exact version or revision, official task and split inventory, expected counts or immutable identifiers, data provenance and time range, loader/evaluator/metric versions, access route, scope-completion rule, and planned per-attempt manifest. Select one main benchmark if its full official scope can answer the claim. Add a complementary benchmark only for a distinct claim dimension. If full-scope access is unavailable, identify the dependency and keep the scientific run blocked.

When relevant project outcomes were already seen, retain that history and classify the selection accordingly. Use an untouched outcome source or independent official benchmark for a confirmatory claim when prior exposure could have influenced benchmark or candidate selection.

### 3. Interpret the latest attempt

After the benchmark-selection gate is satisfied, inspect the attempt, configuration, result artifacts, and protocol-compliance evidence. State what the evidence supports, what it rules out, and what remains uncertain. Separate valid unfavorable results from incomplete execution. For incomplete execution, use the technical recovery rules in [Iteration policy](references/iteration-policy.md); keep partial outcomes out of method tuning. Treat diagnosis as input to method design; a diagnostic or NO-GO report alone does not complete the iteration.

### 4. Propose the next method candidate

Choose a method change that addresses a supported failure mechanism or tests a credible new mechanism. Ground it in relevant literature, theory, a prior result, or a clearly labeled engineering hypothesis. Record the exact change, affected component, mechanism, falsifiable prediction on the frozen metric, motivation with source or locator, and a main alternative explanation. Prefer a meaningful method change over arbitrary parameter movement. Select one lead candidate; list alternatives only when they test distinct mechanisms.

### 5. Qualify and freeze the comparator set

Select a small set covering the strongest directly comparable SOTA methods and canonical baselines needed to interpret the claim. Before outcome review, record the rationale for each selection and omission, ranked access-failure fallbacks, source repository and pinned revision, code license, setup and entry point, required asset licenses and download checks, and protocol differences.

Check code and configuration readiness with static checks, dependency resolution, import checks, or command help. Do not run a partial benchmark evaluation as a smoke test. A smoke check on an isolated engineering fixture may validate plumbing only and must never enter the evidence record. Full comparability is established only by the complete official-scope campaign and subsequent audit. Do not infer runnability from a public repository or a published score alone.

### 6. Design the main experiment

Make the main claim test the primary experiment. Define the condition matrix, immutable configs, complete benchmark scope for each condition, one-run exploratory plan, matched resource budget, frozen metric and analysis, numeric gate sources or estimation objective, expected artifacts, and protocol-compliance checks. Add an ablation only when it isolates a claim-critical mechanism.

Estimate the full campaign's runtime, peak memory, and storage using a stated evidence basis; name the intended accelerator class. Use the approved decision rule and do not move it after outcomes. When no defensible numerical gate exists, report the prespecified estimate, uncertainty where available, and limits of the run.

Use the installed experiment-execution workflow for campaign preflight, immutable configs, attempt identity, provenance, scope manifests, and result audit. If that Skill is unavailable, record the equivalent checks in the protocol. Hand off only an approved protocol and a preflighted campaign; keep planning separate from permission to execute.

### 7. Record and continue

Append the candidate, hypothesis, benchmark and comparator decisions, frozen contract, budget, planned experiment, outcomes, attempt history, and next action to the method iteration record. Mark claims as planned, observed, incomplete, or blocked. Preserve raw evidence and failed attempts; never overwrite a failed attempt's config or artifacts.

If a candidate supports the prespecified comparison, record the evidence and next validation needed. If it does not, name the next evidence-based method candidate and experiment while retaining the active goal. If resources or approval prevent execution, state the exact dependency and a viable next action. Record a user pause or goal change only when the user makes that decision.

## Required output for every round

1. Active method-paper claim and target venue.
2. Benchmark selection state and evidence for task fit, real-world grounding, challenge, data coverage, and evaluation validity.
3. Outcome-access status, and evidence-based interpretation of the latest attempt when available.
4. Next method candidate and falsifiable mechanism hypothesis.
5. Main experiment with complete official scope, a small justified comparator set, and predeclared access fallbacks.
6. Comparator source, revision, code and asset terms, download verification, and protocol compatibility.
7. Frozen metric, analysis, threshold sources or estimation objective, and one-run exploratory plan.
8. Matched budget accounting and full-scope runtime, memory, storage, and accelerator estimates with evidence.
9. Required approval/resource dependency and next executable action.

Use [Benchmark selection](references/benchmark-selection.md) for benchmark choice, [Iteration policy](references/iteration-policy.md) for outcome and continuation rules, and [Method iteration template](templates/method-iteration.template.md) for the round record.
