# Evidence and Numerical Decision Thresholds

Use this reference whenever a number could change whether a goal passes, a campaign continues, a claim is supported, or a resource plan is accepted.

## Distinguish a measurement from a gate

A planned metric, estimate, or confidence interval is not automatically a pass/fail threshold. A goal may ask for an estimate and its uncertainty without declaring a minimum acceptable score. Create a decision threshold only when the research question or an official protocol needs an explicit decision rule.

Keep these roles separate:

| Number type | Examples | Required basis |
| --- | --- | --- |
| Protocol-defined value | Official split, task count, metric, benchmark aggregation | Exact official benchmark/version and locator; use the whole protocol-defined scope for a benchmark claim |
| Scientific importance threshold | Smallest effect worth acting on; equivalence/non-inferiority margin | Field/clinical consequence or theory and direct supporting evidence; explain transfer to the target population and metric. A stakeholder's preference may identify the decision context but does not by itself validate a scientific effect threshold. |
| Statistical design value | Significance level, confidence level, target power, precision, sample/run count | Applicable field/statistical standard or a prospective design with the estimand, model, assumptions, variance/effect source, calculation, and sensitivity; never imply that a conventional default is universal |
| Prior-performance reference | Expected score or comparator value | Directly relevant published/official result, same metric and compatible benchmark version/split, with the original protocol and uncertainty inspected |
| Resource/readiness limit | Runtime, memory, storage, budget | User/project constraint or measured/derived full-scope estimate; do not relabel feasibility as scientific success. A resource constraint cannot justify a scientific performance cutoff or reduced official benchmark scope. |
| Structural/tool invariant | Non-empty ID, valid hash syntax, schema-required field | Explicit schema/tool requirement; state that it is a validation invariant, not an empirical scientific threshold |

## Required threshold record

For every numeric value that changes a decision, record:

1. stable threshold ID and decision it governs;
2. metric/quantity, unit, comparator, target population/task, and direction/operator;
3. exact value or formula, including aggregation and rounding where relevant;
4. `basis_type`, using the downstream `experiment-execution` vocabulary: `official_benchmark_protocol`, `domain_standard`, `peer_reviewed_source`, `statistical_design`, `local_empirical_evidence`, `resource_constraint`, `repository_policy`, or `mathematical_derivation`;
5. primary source identity (DOI/official URL/version), venue and year when applicable, exact section/table/appendix/code locator, and date checked for mutable rules;
6. the source's stated value or rule, distinguished from the proposed value;
7. why the source applies to this claim, benchmark, metric, population, and decision;
8. any transformation/derivation with formula, input values, provenance, assumptions, and sensitivity;
9. whether it was fixed before outcome access; if not, label it post hoc/exploratory and never use it as a confirmatory gate;
10. evidence disposition (`supported`, `derived`, `contested`, or `unsupported`), decision owner, and resulting action. `resource_constraint` and `repository_policy` may justify only an operational/resource gate within that scope; they cannot establish a scientific success threshold.

A citation alone does not justify the number: the locator and transfer argument must support the decision actually being made. If the source reports a score but never recommends it as a minimum, do not convert that score into a success cutoff without a separate justification. If relevant studies use different versions or protocols, report the incompatibility instead of pooling their numbers.

When a threshold uses several sources, cite each stable source ID in `basis_reference` and its exact locator in `source_locator`; explain which source supports which input or premise in `derivation`. A locally observed pilot can inform variance or feasibility only within its design and scope. It does not establish a broadly meaningful improvement threshold by itself.

## When no defensible threshold exists

- Do not substitute common-looking values (for example a fixed percentage gain, p-value, number of datasets, number of seeds, or “top-k” cutoff).
- Remove the pass/fail gate and define an estimation or comparison goal with the official metric and appropriate uncertainty. Explain what magnitude can and cannot be ruled out if the design has a justified precision or sensitivity analysis.
- If a consequential choice truly requires a threshold, present the choice and evidence to the research owner; leave the gate unresolved until decided. Do not pause unrelated exploratory work if it can answer a useful question without that gate.
- If an official benchmark or safety/clinical protocol specifies the rule, follow it exactly in its scope. A deviation is a protocol change and changes what claim can be made.
- A numerical preference supplied by a project owner can be recorded as an operational constraint only when that is what it is. Do not present an unsupported owner-selected number as a field norm or evidence-backed scientific success criterion; ask the owner to resolve the scientific decision or report the outcome descriptively.
- Never reduce a named official benchmark to a hand-picked subset. Use a separately defined population or an official complete track for a genuinely narrower question, and name/report it as that scope.
- Preserve a single-run result as a single-run observation. Do not infer between-seed stability from it. Additional runs may be chosen when the claim requires a variability estimate or when a prospective design supports the added cost, but no generic seed count is mandatory.

## Statistical interpretation safeguards

Never use a single p-value cutoff as the complete basis for a scientific conclusion. State the estimand, design, analysis unit, assumptions, multiplicity strategy, effect estimate, and uncertainty. Do not treat a non-significant result as evidence of equivalence unless an appropriate equivalence/non-inferiority question and margin were prespecified and justified. Do not present an error bar without defining the quantity and its variability source.

The sources below support these principles but do **not** define universal performance targets, seed counts, or dataset counts:

- NeurIPS, [Paper Checklist](https://neurips.cc/public/guides/PaperChecklist), especially claims/limitations and experimental setting, statistical significance, and compute-resource items. This is current venue reporting guidance; it asks authors to explain variability and error bars, not to meet one universal repeat count or improvement threshold.
- Pineau et al., [Improving Reproducibility in Machine Learning Research](https://jmlr.org/papers/v22/20-303.html), *JMLR* 22(164), 2021. The NeurIPS reproducibility program and checklist support transparent, reproducible reporting; this paper is not a universal experiment-goal threshold table.
- Wasserstein & Lazar, [The ASA Statement on p-Values: Context, Process, and Purpose](https://doi.org/10.1080/00031305.2016.1154108), *The American Statistician* 70(2), 2016. Scientific conclusions should not rest only on whether a p-value crosses a specific threshold.
- Lakens, [Sample Size Justification](https://doi.org/10.1525/collabra.33267), *Collabra: Psychology* 8(1), 2022. Discusses distinct sample-size rationales such as a smallest effect of interest, detectable effect, expected effect, and interval precision; it requires justified assumptions, not a portable fixed n.
- Demšar, [Statistical Comparisons of Classifiers over Multiple Data Sets](https://jmlr.org/papers/v7/demsar06a.html), *JMLR* 7, 2006. Discusses tests for classifier comparisons across multiple datasets and their assumptions. It does not imply that every research question needs a fixed number of datasets; choose the analysis for the actual experimental unit and design.

## Reference and venue currency

Venue checklists, benchmark versions, and domain standards can change. Before applying them, resolve the exact requested venue/year and benchmark release from official sources. Record the accessed date for mutable pages and do not assume last year's guidance remains current. Use a field-specific standard when the field has one; do not transplant medical, psychological, or ML norms into another discipline without a reasoned applicability argument.

## Campaign handoff field mapping

The goal contract is a design artifact; it is not the execution campaign schema. When a goal is approved, copy each supported numeric decision rule into the `experiment-execution` campaign register using its exact schema fields:

| Goal evidence | Campaign field |
| --- | --- |
| Stable threshold ID | `threshold_id` |
| Decision being made | `decision` |
| Comparison operator | `operator` |
| Evaluated numeric result/cutoff | `value` |
| Metric/quantity unit | `unit` |
| Evidence category | `basis_type` (the eight-value enum above) |
| Source IDs plus complete citations/URLs | `basis_reference` |
| Exact page/section/table/appendix/code locations | `source_locator` |
| Applicability and transfer limits | `applicability` |
| Formula, inputs, assumptions, source-to-input mapping, and sensitivity | `derivation` |

The goal-to-campaign handoff also maps `exploratory` to campaign `stage: pilot` and `confirmatory` to `stage: confirmatory`; a linked claim/goal group to `research_question`; the prespecified estimation/comparison interpretation to `decision_rule`; the condition matrix to campaign `conditions`; and the run plan to `seed_policy` and `runs`. Group goals together only if one campaign can truthfully represent their protocol/scope, stage, conditions, and decision rule; otherwise split them. Keep one run per condition unless additional runs are justified before outcomes. Seeded stochastic conditions use one chosen seed, uncontrolled APIs one replicate ID, and deterministic methods no seed. A campaign still needs an owner-approved, source-hashed protocol, source commit/state, immutable configs, run IDs, checkpoint policy, complete benchmark manifests, and a full-scope resource plan; `experiment-execution` owns these execution-ready details. Its schema represents one benchmark per campaign, so split multi-benchmark work into separate campaigns. Do not route a non-benchmark study into that benchmark-only schema.

The execution schema rejects extra fields inside threshold objects. Preserve supplemental source links, review status, ownership, and comparability rationale in the goal contract/design note; include the required evidence in the campaign's allowed fields. A benchmark campaign must also satisfy the execution schema's `scope_policy: full_official_benchmark` and its full-scope manifests. Never transform an unsupported draft threshold into an executable gate merely to satisfy campaign schema requirements.
