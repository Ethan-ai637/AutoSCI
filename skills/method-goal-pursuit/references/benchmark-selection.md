# Benchmark Selection for Conclusion-Value Experiments

Choose a benchmark that can answer the method paper's central question with evidence relevant to the intended use. Benchmark choice is part of the scientific design. Freeze it before seeing outcomes that could favor one method.

## Selection dimensions

Assess every plausible benchmark using primary sources and record exact locators.

| Dimension | Evidence to inspect | Decision question |
| --- | --- | --- |
| Task relevance | Approved claim/goal, official benchmark task definitions, input/output schema, task instructions | Does the benchmark directly instantiate the task and mechanism named by the claim? |
| Real-world grounding | Official data provenance, collection setting, population/domain, time range, workflow or practitioner validation | Does the benchmark reflect the users, conditions, and data the claim concerns? |
| Difficulty and information value | Benchmark design paper/docs, expert-validated challenge design, documented failure modes, official results or peer-reviewed evaluations on the same version/protocol | Does the benchmark exercise a meaningful challenge for the proposed method and distinguish it from relevant alternatives? |
| Evaluation validity | Official split, loader, evaluator, labels/targets, metric, contamination/leakage analysis, known limitations | Can results support the intended conclusion under a trustworthy protocol? |
| Comparability and access | Versioned benchmark sources, official code/data route, compatible baseline protocols, permissions and resource requirements | Can the full official scope be run and compared fairly? |

Use a reasoned qualitative comparison. Do not invent a weighted score, minimum difficulty rating, real-world percentage, or benchmark-count threshold. Task relevance is essential. Among relevant candidates, favor stronger real-world grounding and documented challenge while accounting for validity, comparability, and access.

## Evidence for challenge and real-world relevance

- Verify the official benchmark version and its task/data provenance. Record source URL or repository revision plus section, table, dataset card, or code locator.
- Ground claims of real-world relevance in collection context, target population/domain, operational workflow, or documented practitioner validation. A benchmark title or marketing description alone is insufficient.
- Ground claims of difficulty in benchmark construction, expert-validated challenges, known failure analyses, or results from relevant methods evaluated on the same benchmark version and protocol. A low score by one model alone does not establish that a benchmark is difficult.
- Treat benchmark difficulty as task- and method-relative. Explain which capability the benchmark challenges and why that capability matters to the claim.
- Identify synthetic, toy, stale, narrow-population, or contamination-prone content. Follow repository rules against synthetic/generated research data; do not describe limited or simulated coverage as real-world evidence.

## Selection and freezing procedure

1. Start from the approved method claim and intended use. Map the claim to benchmark task definitions, data population, inputs/outputs, and official metrics.
2. Shortlist official benchmarks with direct task fit. Compare real-world provenance, documented challenge, evaluation validity, access, and compatibility using the dimensions above.
3. Select one main benchmark if its full official scope can answer the claim. Add complementary benchmarks only when the claim requires a distinct population, deployment condition, or capability; each selected benchmark is run at full official scope.
4. Record selected and rejected candidates, source locators, scope, limitations, and selection rationale in the method iteration record. Freeze the decision before accessing outcomes that could affect benchmark choice.
5. Keep the selected benchmark and protocol fixed across candidate iterations. Preserve results from every condition. Do not swap to a more favorable benchmark, remove a difficult official task, or report partial coverage as a benchmark result.

If no candidate adequately matches the task and real-world context, state the gap, propose the closest defensible full-scope benchmark and its limitations, and identify the user decision or data-access dependency. Do not create a substitute benchmark or use a hand-picked subset. A benchmark added after outcomes are known is exploratory unless it is prospectively frozen for a separate confirmatory campaign.
