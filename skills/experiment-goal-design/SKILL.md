---
name: experiment-goal-design
description: Use after a research idea or hypothesis exists to turn its claims into literature-aligned, benchmark-comparable experiment goals and evidence-backed decision criteria before implementation or execution.
---

# Experiment Goal Design

Turn a proposed research claim into a reviewable experiment goal whose datasets, scope, baselines, metrics, and evaluation protocol can be defended against the closest relevant field work. Make every numerical pass/fail or continue/stop threshold traceable to an applicable source or an explicit, defensible derivation. Never invent a cutoff to make a plan look decisive.

This Skill is for **designing what an experiment must answer**, not generating research ideas, reconstructing a specific published experiment, implementing runs, or analyzing completed data. Route those tasks to `research-idea-scout`, `paper-reproduction`, `experiment-execution`, and `scientific-data-analysis` as appropriate. It can hand an approved goal contract to `experiment-execution`.

## Non-negotiable decisions

- A research claim does not need an arbitrary numeric success bar. A directional hypothesis, a defined estimand, and an analysis that reports the estimate with appropriate uncertainty can be a complete goal.
- Do not invent numeric targets such as “improve by 3%”, a minimum number of datasets, a universal sample/seed count, a p-value cutoff, or a compute limit. Every number that changes a scientific or operational decision needs an evidence record. Structural values and user-provided constraints are labeled as such, not misrepresented as scientific thresholds.
- Whenever a named official benchmark is used for scientific evidence, use its complete official evaluation scope and protocol. Do not carve out a hand-picked subset, even if the claim is labeled narrow. A deliberately narrower question must use a separately justified evaluation population or an officially defined full track, and must not be reported as a result on the broader benchmark.
- One run/seed per condition is the default. More runs are optional; add them only when the benchmark protocol or the stated claim requires between-run uncertainty, a predeclared inferential design, or a defined selection/optimization question. Trying other seeds late to select a higher-scoring run is an optional score-optimization strategy, never a requirement; declare the selection rule, preserve every tried outcome, and do not describe the selected score as an unbiased or robust estimate. A single run cannot support a claim about run-to-run variability.
- Keep the goal, threshold rationale, and comparator evidence frozen before examining outcomes that could influence them. Any change after outcome access must be dated, justified, and labeled exploratory or post hoc.
- A cited paper is not automatically comparable because it is recent, highly cited, or from a top venue. Match the study to the claim, population/task, benchmark version, split, metric, protocol, baseline, and analysis. Record consequential mismatches.

## Workflow

### 1. Define the claim before choosing a score

Read the supplied idea, hypothesis, relevant findings, and literature. State:

- the scientific question and intended contribution;
- the claim type (comparative performance, mechanism, generalization, robustness, efficiency, causal effect, or another explicit category);
- the target population, task, setting, and scope of inference;
- what observation would weaken or falsify the claim;
- what this experiment can and cannot establish.

Split compound claims into independently testable claims. Do not turn aspirations into achieved goals. A falsifier can be a design or pattern of evidence and need not be a fabricated numeric cutoff.

### 2. Find the field's applicable evidence and rules

Use `literature-research` when a search, screening, or source-conflict workflow is needed. Prefer primary sources and inspect the version that actually defines the protocol. Resolve the field's state of practice by checking, where available, the official benchmark/protocol paper and documentation, the official leaderboard or task suite, and directly comparable peer-reviewed work in the field's leading venues. Verify venue/version status from official records. Rank sources by match to the claim and protocol, not venue prestige alone. Record why each selected anchor is representative and what important evidence is missing; do not imply coverage from a single convenient study. There is no universal required paper count. Record stable identifiers, publication/version status, date accessed for mutable guidance, and precise section/table/appendix/code locators.

Use a source hierarchy that fits the decision:

1. **Official protocol or rule** for a named benchmark, task, clinical/field standard, or requested venue. This controls compliance only within its stated scope.
2. **Field-specific consensus or reporting/statistical guidance** for design, measurement, uncertainty, and reporting. A reporting checklist is not a universal scientific effect threshold.
3. **Directly comparable peer-reviewed studies** for observed prior results and design practice. Prefer studies matching the target task and protocol; record version and comparability limitations.
4. **Prospective derivation** from a declared estimand, analysis model, empirical variance source, or explicit resource budget. Show the inputs and calculation; label assumptions and sensitivity.

Do not use citation counts, one convenient paper, or a generic “common practice” statement as sufficient evidence for a numeric gate. If sources conflict, record the conflict and explain which source controls this exact question; do not silently select the more favorable value. Read [references/evidence-and-thresholds.md](references/evidence-and-thresholds.md) for source appraisal and threshold handling.

### 3. Build the comparability map

For each anchor study or standard that materially informs the goal, record at least:

- exact source identity and version, venue/year, and evidence locator;
- dataset/benchmark version, official task/track, population, and split;
- loader/preprocessing and evaluation harness where available;
- primary metric, unit, aggregation, and direction;
- baselines and their versions/checkpoints;
- the experimental factor being changed and variables held constant (for example, data/split, training budget, tuning budget, optimizer, compute, evaluation code, and selection rule, where applicable);
- training/tuning/evaluation protocol and any selection rule;
- uncertainty/statistical analysis and the source of variation;
- compute/resource context when it affects fairness or feasibility;
- match status and every mismatch that limits transfer to the proposed claim.

Choose comparisons that answer the claim, not a fixed number of papers or datasets. Distinguish benchmark compliance from scientific comparability: a correct score on one official benchmark does not establish broader generalization. Do not average incompatible datasets or metrics without a justified estimand and analysis.

### 4. Write a claim-to-goal contract

Create `experiment_goal_contract.yaml` from [templates/experiment_goal_contract.template.yaml](templates/experiment_goal_contract.template.yaml). The contract supports multiple evaluation protocols and links each goal and experimental condition to its applicable protocol IDs. For every claim, specify:

- one research question and testable hypothesis/estimand;
- the complete evaluation population/protocol and exact sources defining it; for a named official benchmark, record its complete official scope;
- the primary metric and aggregation from the benchmark or field protocol;
- a strong, relevant comparator set and why each is fair;
- the factor being tested, the controlled variables, and justified deviations from anchor protocols;
- the intended analysis unit and uncertainty method, including their assumptions;
- a falsification interpretation and claim limit;
- optional secondary, robustness, or ablation goals only when they resolve a stated uncertainty;
- the explicit condition matrix: proposed method, baseline/control/ablation role, factor levels, linked goals/protocols, and per-condition randomness mode;
- a seed/run plan. Default to one run per condition; justify any extra repeats against the claim or protocol before seeing results.

Use a threshold only when the decision genuinely needs one. Put every numeric outcome, inference, resource, or readiness cutoff that can change a decision into the `decision_thresholds` register. See [references/evidence-and-thresholds.md](references/evidence-and-thresholds.md) for required fields and disposition when evidence is absent. A numeric value appearing only in prose is still a threshold and must be registered.

### 5. Review for evidence alignment and avoid gate creep

Before handoff, check that:

- each goal directly tests a named claim and has an interpretable falsifier;
- the closest relevant protocols, benchmarks, and strong baselines have been compared, with mismatches disclosed;
- every experiment using a named official benchmark uses its complete official scope, split/task manifest, metric, loader, and evaluator; an official named track is allowed only when that entire track is run;
- no dataset/condition/run-count/score threshold was introduced merely because it is conventional or easy to state;
- every numeric threshold has a complete, applicable rationale frozen before outcome access;
- all goal/protocol/condition/comparator/source IDs resolve, and each official scope and metric has a source ID plus exact locator;
- seed count is not treated as a proxy for benchmark coverage, claim quality, or scientific validity;
- exploratory goals, confirmatory claims, and post hoc decisions are clearly distinguished;
- resource constraints are real and sourced, and do not quietly alter scientific scope.

If a proposed numeric threshold has no strong, applicable basis, do **not** guess and do not block all experimentation just to manufacture one. Remove the pass/fail gate; state the goal as estimation/comparison with suitable uncertainty, or mark the specific decision as unresolved and ask the research owner to settle the scientific tradeoff. Do not call an unsupported goal “confirmatory.” If a required official protocol is missing or the full declared scope cannot be run, record that blocker rather than silently relaxing the scope.

### 6. Handoff

Deliver the completed contract, comparator evidence, a `protocol.md` draft based on [templates/protocol.template.md](templates/protocol.template.md), and unresolved decisions. The research owner must approve the protocol before it is handed to `experiment-execution`; keep its path and hash with the campaign. Do not treat generation of a draft or campaign file as approval to run. When the benchmark campaign schema applies, create a separate campaign for each official benchmark protocol and each incompatible goal group; its schema has one `benchmark`, stage, question, and decision rule. Goals may share a campaign only when their protocol/scope, stage, condition matrix, and prespecified decision interpretation can all be represented truthfully by that campaign. Split them when any of those differ. Never collapse multiple protocols into a mismatched synthetic scope. Map the goal contract as follows:

- `exploratory` maps to campaign `stage: pilot`; `confirmatory` maps to `stage: confirmatory`. The campaign stage does not change benchmark scope.
- One campaign's `research_question` is the linked claim/goal question. Its `decision_rule` describes the prespecified estimation/comparison interpretation; if there is no numeric gate, state that and keep `decision_thresholds: []`.
- Map each supported threshold to the exact campaign fields (`threshold_id`, `decision`, `operator`, numeric `value`, `unit`, `basis_type`, `basis_reference`, `source_locator`, `applicability`, `derivation`). Keep evidence status and ownership in the goal contract/note. Never pass an `unsupported` or unresolved threshold as an executable gate.
- Map benchmark identity/version, selected official complete track, code revision, full required scopes/manifests, loader/evaluator/metric entrypoints, and `scope_policy: full_official_benchmark` from the linked evaluation protocol. Preserve the campaign's official full-scope `data_policy`.
- Map each condition-matrix row to a campaign `condition`, preserving its condition ID/role, factor level, and linked comparison. Map its `randomness_mode` and run plan. Default to one planned run per condition: one declared seed for `seeded_stochastic`, one replicate ID for `uncontrolled_stochastic`, and one seedless run for `deterministic`. Record extra runs only when justified in advance; a score-selection search is optional and must retain every attempt and disclose selection.
- Campaign preparation owns execution details not decided by goal design: campaign/experiment IDs, the approved protocol path and hash, local source commit/state, immutable config hashes, run IDs, checkpoint policy, and full-scope runtime/memory/storage estimate with its evidence basis. Complete these from evidence before preflight; never guess resource values or reduce official scope to fit them.

The `experiment-execution` campaign schema is benchmark-specific. For a non-benchmark population or field study, preserve its own complete approved protocol and use a suitable domain execution workflow instead of filling an unrelated benchmark record. Use `scientific-data-analysis` for a prospective power/precision plan or later statistical analysis. The handoff does not itself authorize running experiments. `research-idea-scout` is an optional upstream route when that Skill is installed; it is not bundled in AutoSCI.

## Output

- `experiment_goal_contract.yaml` — claims, scope, metrics, comparators, analysis, run plan, and threshold register;
- `comparability_matrix.csv` — source-linked comparison of the relevant protocols and their transfer limits;
- `protocol.md` — owner-reviewable experiment protocol draft with goals, scope, conditions/controls, analysis, and evidence-backed decision rules;
- a short `goal_design_note.md` — decision rationale, controlled-variable choices, unresolved evidence gaps, and handoff status.

Keep the output proportional to the study. Do not create a large literature review when a well-supported benchmark protocol and a small number of directly relevant studies settle the design question.
