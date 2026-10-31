# Benchmark Selection for Method Experiments

Choose a benchmark that can answer the method paper's central claim with evidence relevant to its intended use. Prefer benchmarks with direct task fit, documented challenge, real-world grounding, valid evaluation, and accessible complete official scope. Freeze the choice before inspecting project outcomes that could favor one candidate or benchmark.

## Outcome-access rule

When selection is open, inspect the project goal, protocol, benchmark inventory, and other non-outcome metadata first. Do not open project-specific score tables, result summaries, logs, plots, predictions, or reviewer judgments that reveal candidate performance until selection is recorded and frozen.

Follow local project instructions about required files. If they require reading result-bearing files before selection is frozen, record which outcomes were exposed, when they were exposed, and which decisions could have been influenced. Do not describe that selection as outcome-independent. Keep prior observations in the research record. For confirmatory claims, prospectively freeze a campaign with an outcome source that has not influenced selection or candidate development, such as an untouched official split or a distinct official benchmark when the claim requires it.

Official benchmark documentation, data cards, design papers, and published evaluations may be used to assess task construction, challenge, protocol, or known limitations. Record the sources and disclose when published scores materially informed benchmark choice. Do not use current project candidate outcomes to choose the favorable benchmark, split, task list, or metric.

## Selection dimensions

Assess plausible official benchmarks using primary sources and record precise source locators.

| Dimension | Evidence to inspect | Decision question |
| --- | --- | --- |
| Task relevance | Approved claim, official task definitions, input/output schema, instructions | Does the benchmark directly instantiate the task and mechanism named by the claim? |
| Real-world grounding | Data provenance, collection context, target population/domain, workflow, practitioner validation | Does the benchmark represent the people, conditions, and data the claim concerns? |
| Data coverage and currency | Data collection period/version, geography, language, population, operational setting, documented distribution changes | Are known coverage boundaries and data age acceptable for the intended claim? |
| Difficulty and information value | Benchmark design, expert-validated challenge, documented failure modes, peer-reviewed evaluations on the same version/protocol | Does it exercise a meaningful capability and distinguish relevant methods? |
| Evaluation validity | Official splits, labels, loader, evaluator, metric, aggregation, contamination/leakage analysis | Can the official protocol support the intended conclusion? |
| Comparability and access | Versioned source, license/access route, complete task inventory, compatible method protocols, resource requirements | Can the complete official scope be run and compared fairly? |

Use a reasoned qualitative comparison. Do not invent a weighted score, minimum difficulty rating, recency cutoff, real-world percentage, or benchmark-count threshold. Task relevance is essential. Among relevant candidates, favor stronger real-world grounding and documented challenge while accounting for evaluation validity, data coverage, comparability, access, and the approved claim.

## Evidence for challenge and real-world relevance

- Verify the benchmark version and record an official source URL or repository revision plus a section, table, dataset-card field, or code locator.
- Ground real-world claims in collection setting, population/domain, date range, operational workflow, or practitioner validation. A benchmark name or marketing summary alone is insufficient.
- Record the collection period or release date and compare it with the claim's intended deployment setting. Note known population, language, geographic, or distribution limits. Data age alone is not an automatic rejection reason.
- Ground difficulty in benchmark construction, expert-validated challenges, known failure analyses, or relevant results measured on the same version and protocol. A low score from one model alone does not establish difficulty.
- State which capability the benchmark challenges and why that capability matters to the method claim.
- Identify synthetic, toy, narrow-population, stale, contaminated, or otherwise limited content. Do not describe simulated or limited coverage as real-world evidence. Synthetic/generated data and toy tasks cannot be scientific benchmark evidence.

## Freeze the official evaluation scope

Before confirmatory outcome access, record enough detail to reproduce the exact official evaluation:

- benchmark release/version, source URL, repository revision, and data license/access terms;
- official task, example, and split inventory, using identifiers and expected counts or immutable hashes where available;
- official loader, evaluator, metric, aggregation, and their versions or revisions;
- inclusion rules mandated by the official protocol, plus the expected complete-coverage condition;
- the loader-emitted per-attempt scope manifest and the audit that will compare it with the frozen official inventory;
- dataset download route, access prerequisites, and data provenance/time range;
- contamination, leakage, annotation, and known validity limitations relevant to the claim.

Do not create a custom task list, remove difficult official cases, or replace an official loader/evaluator to obtain a scientific score. Use every task and example in each split required by the official evaluation protocol. A convenience sample, quickstart slice, or optional subset does not count as complete benchmark evidence, even when documentation explains how to create it. If resources cannot support the complete official scope, block the scientific run and record the resource dependency.

## Selection procedure

1. Start from the approved method claim and intended use. Map the claim to official task definitions, inputs/outputs, target population, and metrics.
2. Shortlist benchmarks with direct task fit. Compare real-world provenance, data coverage, documented challenge, evaluation validity, access, and compatibility using the evidence above.
3. Select one main benchmark when its complete official scope can answer the claim. Add a complementary benchmark only for a distinct population, deployment condition, or capability; run each selected benchmark at full official scope.
4. Record selected and rejected candidates, exact source locators, outcome exposure, official scope, limitations, and rationale in the method iteration record. Freeze the decision before accessing project outcomes that could affect it.
5. Keep the frozen benchmark and protocol fixed across candidate iterations. Preserve every condition. Treat adaptive candidate selection after outcome review as exploratory; a confirmatory claim requires a prospectively frozen candidate and an outcome source that has not informed selection or development.

If no candidate adequately matches the task or complete official scope is inaccessible, state the gap, propose the closest defensible full-scope option, and identify the access or user-decision dependency. Do not create a substitute benchmark or run a hand-picked subset. A benchmark selected after relevant project outcomes are known must carry that exposure in the record.
