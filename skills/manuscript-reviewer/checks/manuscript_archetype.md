# Manuscript archetype routing

## Objective

Adapt audit emphasis to the scientific object the manuscript actually contributes without changing the core evidence standard.

The archetype is a **routing aid**, not a quality score and not a license to invent field-specific requirements. All papers still receive the six core audits when in scope; the archetype changes which claims and evidence objects deserve the most attention.

## Archetype assignment

Assign one dominant archetype when clear. Use `mixed` when two or more contribution types are genuinely central.

- `method_model_system` — proposes an algorithm, model, architecture, system, workflow, or optimization method.
- `empirical_study` — primarily reports observational, experimental, clinical, behavioral, social, or scientific measurements about a phenomenon.
- `dataset_benchmark_resource` — contributes a dataset, benchmark, annotation scheme, evaluation suite, corpus, or other research resource.
- `theory_mathematical` — central contribution is a theorem, proof, formal result, bound, impossibility result, or mathematical characterization.
- `survey_review` — synthesizes prior literature, taxonomy, evidence, or research trends; includes narrative/systematic surveys when the main contribution is synthesis rather than a new empirical method.
- `application_translational` — applies an existing or adapted method to an operational, clinical, industrial, policy, or real-world decision setting where utility/deployment claims are central.
- `mixed` — multiple archetypes are central and should be routed claim-by-claim.

Do not infer a manuscript type solely from venue, title keywords, or field convention. Use the manuscript's stated contribution and primary evidence objects.

## Routing rule

For each central atomic claim, ask which contribution type creates its evidentiary burden. In a mixed paper, route claims individually rather than forcing one global standard.

The archetype changes **priority**, not truth conditions:
- a causal claim still needs causal evidence regardless of paper type;
- a universal comparative claim still needs evidence at the stated scope;
- a citation claim still requires source inspection for semantic verification;
- a numerical contradiction still requires protocol comparability.

## High-risk claims by archetype

### `method_model_system`
Prioritize:
- novelty and contribution identity;
- superiority/SOTA language;
- baseline provenance and protocol comparability;
- ablation -> contribution vs ablation -> mechanism;
- robustness/generalization claims;
- efficiency claims (runtime, memory, FLOPs, latency, throughput, cost) and whether the measured quantity matches the wording;
- claims that implementation details are irrelevant or broadly transferable.

Primary evidence objects often include main comparison tables, ablations, robustness tests, complexity/runtime measurements, and core equations/algorithms.

### `empirical_study`
Prioritize:
- population/sample scope vs conclusion scope;
- association vs causal wording;
- subgroup/generalization claims;
- null/equivalence claims;
- outcome/construct alignment;
- statistical/numerical consistency between tables, figures, and narrative;
- whether abstract/conclusion loses design qualifiers present in methods/results.

This skill checks claim-evidence and reporting consistency; it should not pretend to perform a full domain-specific statistical or causal-validity review unless the needed evidence and requested scope support that task.

### `dataset_benchmark_resource`
Prioritize:
- claims of coverage, diversity, representativeness, difficulty, realism, or comprehensiveness;
- dataset/split identity and denominator consistency;
- benchmark protocol and metric definitions;
- claims about leakage, contamination, annotation quality, or reliability only when evidence is actually inspected;
- whether benchmark rankings are generalized into model-quality claims beyond the benchmark's measured construct;
- whether paper narrative matches dataset/table statistics.

Do not assume a benchmark is representative merely because it is large, or unrepresentative merely because it is narrow.

### `theory_mathematical`
Prioritize:
- theorem/lemma statement consistency with assumptions;
- symbol and quantifier scope;
- equation/prose consistency;
- whether corollaries/conclusions preserve the theorem's conditions;
- empirical examples being used as illustration vs proof;
- claims of generality that drop formal assumptions.

Do not demand empirical experiments merely because other archetypes normally include them. Conversely, experiments cannot substitute for a claimed formal proof.

### `survey_review`
Prioritize:
- scope and inclusion criteria vs claims of completeness/comprehensiveness;
- taxonomy/category consistency;
- citation placement and semantic support;
- whether synthesis claims are actually supported by the cited set;
- date/database/search-window qualifiers when the manuscript makes coverage claims;
- unsupported priority language such as "first", "only", or "comprehensive".

Do not demand ablations, model baselines, or new experiments simply because those are common in method papers. For systematic/meta-analytic work, inspect protocol/result consistency to the extent materials permit.

### `application_translational`
Prioritize:
- proxy metric -> practical outcome jumps;
- benchmark performance -> deployment utility;
- safety/reliability/fairness claims;
- operating conditions, population/domain, and decision context;
- whether latency/cost/workflow claims are actually measured under deployment-relevant conditions;
- whether limitations contradict broad real-world language.

Do not infer practical invalidity merely because deployment evidence is absent; instead check whether the manuscript actually makes a deployment-level claim.

## Mixed manuscripts

When `mixed`:
1. tag each central claim with the relevant archetype burden;
2. identify the primary evidence object for that claim;
3. apply only the relevant archetype-specific emphasis;
4. keep one unified finding if one root defect crosses archetypes.

Example: a benchmark paper that also proposes a model may have dataset-representativeness claims routed as `dataset_benchmark_resource` and superiority claims routed as `method_model_system`.

## Anti-overreach rules

- Do not use archetype routing to add a new review dimension the user did not request unless it is necessary to judge one of the six core audits.
- Do not penalize a paper for lacking an artifact that is not necessary for its stated claim.
- Do not assume field norms without evidence when the manuscript itself provides a coherent alternative convention.
- Do not convert "this would strengthen the paper" into "this is required" unless the current claim actually depends on it.
