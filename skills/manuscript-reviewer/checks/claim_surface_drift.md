# Claim surface drift and semantic fingerprinting

Use this module to determine whether the **same scientific claim** remains semantically stable across title, abstract, contribution statements, results, discussion, conclusion, and limitations.

The goal is not to punish paraphrase. The goal is to detect scientifically meaningful drift in scope, certainty, causality, comparator, metric, population, or condition.

## Core principle

Two sentences may use different wording while expressing the same claim. Conversely, two sentences may look similar while silently changing the evidentiary burden.

Track central claims using a compact **semantic fingerprint** rather than surface wording alone.

## Claim fingerprint

For each central claim, record only fields that are material:

- **subject/intervention/system** — what entity is being described;
- **predicate/effect** — what is asserted about it;
- **object/outcome** — what quantity/property/result is affected;
- **comparator/reference** — against what baseline or condition;
- **metric/construct** — measured outcome or broader construct;
- **population/domain/dataset** — where the claim applies;
- **condition/protocol** — evaluation setting or assumptions;
- **quantifier** — e.g. some / most / all / consistently / universally;
- **modality/certainty** — suggests / supports / demonstrates / proves;
- **causal or mechanistic status** — descriptive / associative / causal / mechanistic;
- **generalization range** — in-distribution / cross-domain / OOD / real-world / future setting;
- **exception/qualification** — explicit limiting clause, when material.

Do not force every field for every claim.

## Surface map

For each central claim, compare the fingerprint across the manuscript surfaces where it appears:
- title;
- abstract;
- introduction/contributions;
- results;
- discussion;
- conclusion;
- limitations.

Use these internal relations:

- `semantically_equivalent` — wording differs but scientific burden is materially unchanged;
- `narrowed` — later wording is more limited than the mapped claim;
- `strengthened` — later wording requires more evidence or certainty;
- `scope_shifted` — population/domain/condition/generalization range changes;
- `quantifier_shifted` — e.g. “often” becomes “consistently”;
- `modality_shifted` — e.g. “suggests” becomes “demonstrates”;
- `causalized` — associative/descriptive evidence becomes causal/mechanistic wording;
- `metric_or_construct_shifted` — a measured proxy becomes a broader construct or a different outcome;
- `comparator_shifted` — reference class/baseline changes;
- `contradicted` — surfaces make incompatible propositions;
- `ambiguous_coreference` — it is unclear whether two statements refer to the same result/setting.

## What counts as material drift

Report drift only when it changes one of:
- required evidence;
- scientific interpretation;
- population/domain of applicability;
- strength/certainty of conclusion;
- comparator being claimed against;
- causal/mechanistic meaning;
- practical/deployment implication.

Examples of material strengthening:

- “improves accuracy on three tested datasets” → “generalizes across domains”;
- “associated with lower error” → “reduces error” when causality is not established;
- “suggests mechanism X may contribute” → “demonstrates mechanism X”;
- “outperforms baseline A” → “outperforms all baselines”;
- “no significant difference was detected” → “the methods are equivalent”;
- “higher proxy score” → “better clinical utility”.

## What is not automatically drift

Do not report a finding merely because:
- the abstract is shorter than the results section;
- synonyms are used;
- one surface omits non-material implementation detail;
- the conclusion paraphrases a result with the same scope and certainty;
- a limitation is stated elsewhere but remains clearly attached to the claim in context.

If a shortened surface omits a qualification and thereby materially broadens how a reasonable reader would interpret the claim, then it may be drift.

## Canonical-claim rule

Do not choose the abstract, table, or conclusion as the automatic canonical truth source.

The canonical claim for auditing is the **most evidence-faithful proposition reconstructable from inspected manuscript evidence**, not whichever surface is most prominent.

If the manuscript itself does not establish a stable canonical claim, report the internal inconsistency or use an author query.

## Drift and evidence-state interaction

A claim may drift even when every individual sentence is locally plausible.

Example:
- Results: narrow claim is `verified_support`.
- Abstract: strengthened variant is `partial_support`.
- Conclusion: universal variant is `contradicted` by one tested condition.

Treat these as manifestations of one root scope-drift issue when they share the same scientific cause.

## Drift and limitations

Limitations can validly narrow interpretation, but they do not automatically repair a materially overbroad headline claim.

Ask:
- would a reasonable reader see the limitation before relying on the stronger claim?
- does the limitation explicitly qualify that claim or only discuss a neighboring issue?
- does the abstract/title/conclusion remain materially broader?

Use this to decide whether the problem is resolved, Moderate, Major, or an author query.

## Review-mode burden

### Compact

Fingerprint only central headline claims and their abstract/conclusion variants.

### Standard

Fingerprint all central claims across the main narrative surfaces and primary results.

### Exhaustive

Fingerprint all material claims with repeated cross-surface appearances, including appendix/supplement variants when they affect interpretation.

## Reporting

Do not emit the full fingerprint table by default.

For a material drift finding, report:
- the earliest materially narrower/evidence-faithful statement;
- the strengthened/shifted surface(s);
- the exact semantic dimension that changed;
- why the available evidence does not justify the stronger variant;
- the minimal correction: harmonize wording, restore qualification, reconcile comparator/metric, or add genuinely missing evidence if necessary.
