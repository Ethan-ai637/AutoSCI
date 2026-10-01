# Evidence coverage and bidirectional claim mapping

## Objective

Prevent omission-based reviewing by ensuring:
1. every central atomic claim is mapped to evidence or explicitly unresolved; and
2. every primary result object is reconciled with the narrative claims made from it across the manuscript.

Coverage is **bidirectional**: claim → evidence and evidence → narrative.

## Centrality test

Treat a claim as central if one or more apply:
- it appears in the title, abstract, contributions, or conclusion;
- it expresses the main novelty or method advantage;
- a primary experiment was designed to demonstrate it;
- if false, the paper's main scientific message would materially change;
- it is likely to influence a reviewer's assessment of the work.

If a central sentence contains separable propositions, use the atomic claims defined by `claim_decomposition.md`.

## Claim → evidence matrix

For each central atomic claim, record internally:

| Field | Meaning |
|---|---|
| Claim | Exact or minimally paraphrased atomic proposition |
| Parent | Original compound sentence/claim when relevant |
| Location | Page/section/sentence |
| Type | comparative/causal/generalization/etc. |
| Scope | datasets, populations, metrics, conditions, time, domain |
| Evidence | table/figure/experiment/equation/citation |
| State | fixed evidence-state vocabulary |
| Gap | missing test, unclear mapping, unavailable source, contradiction |

## Claim → evidence rules

1. Every central empirical claim needs at least one linked empirical evidence object unless clearly framed as hypothesis/future work.
2. A citation is not a substitute for the paper's own experiment when the manuscript claims a new empirical result.
3. An ablation is evidence for component contribution, not automatically for the claimed mechanism.
4. A main-table aggregate may support average performance but not universal per-dataset/per-subgroup superiority.
5. A single in-domain benchmark does not cover OOD/generalization scope.
6. A point estimate alone may not cover claims about stability, significance, equivalence, or reliability.
7. If the evidence object exists but the manuscript never clearly links it to the claim, use `ambiguous_mapping` rather than `missing_required_evidence`.
8. If required material might be in unavailable supplement/source, use `unavailable_to_verify`.
9. Evidence for one atomic clause does not automatically support sibling clauses from the same sentence.
10. Before assigning `missing_required_evidence`, perform a claim-directed absence check across the plausible available locations for that evidence. A failed phrase search or partial section scan is not enough.

## Evidence → narrative map

For each **primary result object**, record where and how it is interpreted:
- caption/footnote;
- results prose;
- abstract;
- introduction/contribution summary;
- discussion;
- conclusion;
- limitations.

Check whether these interpretations preserve:
- metric identity/direction;
- dataset/population/split;
- aggregation level;
- uncertainty/statistical status;
- comparison set;
- tested scope;
- causal vs associative language;
- robustness/generalization axis;
- deployment/practical scope.

## Reverse-map failure patterns

### Scope drift
A table supports performance on three benchmarks; the conclusion turns this into general real-world effectiveness.

### Qualifier loss
Results say "on average"; abstract says "consistently across datasets".

### Exception disappearance
The main table contains an exception that disappears from the narrative summary.

### Caption/body conflict
Caption constrains the analysis to validation data; body presents it as test performance.

### Statistical inflation
Table reports point estimates/uncertainty; narrative upgrades this to "significantly better" without inferential support.

## Coverage summary

For standard/exhaustive reviews, include compact totals such as:
- central atomic claims identified: 9;
- verified/adequately supported: 5;
- partial/qualified support: 2;
- contradicted: 1;
- unavailable to verify: 1;
- primary result objects identified: 4;
- primary result objects cross-surface checked: 4.

Do not turn these counts into an acceptance score or percentage grade.

## Long-document integration

For long or structurally complex manuscripts, claim coverage is not complete until the material section/dependency checkpoints in `long_document_coverage.md` are complete. A claim with no currently mapped evidence must remain unresolved while a relevant method/result/appendix dependency is still `partial` or `blocked`.
