# Inference-chain and traceability audit

## Objective

Expose hidden reasoning jumps between what the manuscript **observes** and what it ultimately **claims**, while keeping every consequential reviewer judgment traceable back to inspected evidence.

This is a cross-cutting audit. It does not replace claim–evidence checking; it makes the inferential bridge explicit when a direct claim→evidence mapping is too coarse.

## When to build an inference chain

Build a chain for every central claim whose truth depends on more than direct transcription of a result, especially claims about:
- causality;
- mechanism or explanation;
- robustness/generalization;
- safety/reliability;
- practical, clinical, or deployment utility;
- fairness or broad latent constructs inferred from proxies;
- equivalence / no-effect / no-harm conclusions;
- superiority claims that combine multiple metrics or conditions.

For simple descriptive claims such as “Table 2 reports 91.2% accuracy,” a full chain is usually unnecessary.

## Canonical chain

Represent the reasoning internally as:

`evidence object → observed result → inference bridge → conclusion claim`

Example:

`Ablation Table 4 → removing module X lowers AUROC by 1.8 points → X contributes to predictive performance → X is the mechanism that improves robustness`

The first inference may be supported while the second may not be.

## Bridge types

Classify the bridge when useful:
- `descriptive` — evidence directly states the reported observation;
- `comparative` — two or more protocol-compatible results support an ordering/difference;
- `statistical` — sample evidence is used for inferential language such as significant/equivalent/stable;
- `causal` — intervention/design is used to claim cause/effect;
- `mechanistic` — evidence is used to claim *why* a method or phenomenon works;
- `extrapolative` — tested conditions are generalized to untested populations/domains/times/settings;
- `proxy_to_construct` — a measured proxy is used to claim a broader latent property;
- `deployment_or_utility` — benchmark evidence is used to claim practical/clinical/real-world value;
- `absence_or_equivalence` — failure to detect an effect is used to claim no effect, equivalence, safety, or no harm.

## Bridge status

Use a separate bridge status; do not overload the manuscript evidence-state vocabulary:
- `justified`;
- `partially_justified`;
- `unsupported`;
- `ambiguous`;
- `blocked`.

A claim can have real evidence but still contain an unsupported inferential bridge.

## Warrant and assumption check

For each nontrivial bridge ask:
1. What observation is actually established?
2. What additional proposition must be true for the conclusion to follow?
3. Does the manuscript state or test that proposition?
4. What alternative explanation remains plausible?
5. Does the bridge enlarge population, domain, time, causal strength, mechanism, or construct meaning?
6. Is the conclusion conditional in the text, or stated as general fact?

Do not require authors to formalize every warrant. The purpose is to detect material hidden leaps, not to impose philosophical notation.

## Special handling of null / negative claims

Treat these as inference-heavy, not as direct consequences of a non-significant or failure-free result:
- “no difference”;
- “equivalent”;
- “does not affect”;
- “safe” / “no harm”;
- “robust because no failures were observed”;
- “independent of X”.

Check whether the design, uncertainty, power, equivalence/non-inferiority margin, perturbation coverage, or search space is capable of supporting the negative conclusion. If not, prefer `partial_support`, `missing_required_evidence`, or an author query depending on what is actually known.

## Traceability anchors

Assign stable internal IDs within a review session:
- `Cxx` — atomic claim;
- `Exx` — evidence object (table/figure/experiment/source);
- `Rxx` — result/value/relationship;
- `Bxx` — inference bridge;
- `Fxx` — candidate/root finding.

A consequential finding should be reconstructable as a trace such as:

`C07 ← B03 ← R12 ← E05`

For external citation semantics, add a source anchor identifying what part of the source was inspected.

## Minimum anchor content

### Claim anchor
- exact or minimally quoted wording;
- page/section/sentence or equivalent location;
- scope qualifiers.

### Evidence anchor
- object identity (e.g. Table 3, Fig. 2b, Eq. 7, citation [18]);
- row/column/panel/section when relevant;
- protocol context;
- explicit value, ordering, or relationship actually used.

### Derivation anchor
For arithmetic or statistical reconciliation:
- source values;
- formula/definition;
- reconstructed result.

### Source anchor
For citation Level 3:
- source identity;
- inspected section/page/abstract/results portion;
- proposition actually supported.

## No source-of-truth shortcut

When manuscript surfaces disagree, do **not** automatically assume the table, figure, caption, abstract, or prose is the authoritative truth.

If the available evidence only establishes that two surfaces conflict, report an **internal inconsistency** and ask the authors to reconcile the intended value/interpretation. State which surface is wrong only when provenance or other inspected evidence establishes it.

## Finding dependency

If one root defect causes several downstream narrative errors, preserve the dependency internally rather than counting each symptom as an independent finding.

Example:
- wrong denominator in Table 2;
- abstract percentage inherits that denominator;
- conclusion repeats the inflated percentage.

Prefer one root numerical finding with dependent manifestations unless separate corrections or scientific consequences genuinely require separate findings.

## Reporting discipline

Do not expose raw IDs or full argument graphs by default. For Major/Critical findings, include a concise `Trace path` when it materially improves auditability.

A trace path should show the scientific path, not internal chain-of-thought. Example:

`Trace path: Abstract claim → Table 3 (Dataset B, AUROC) → direct comparison → exception to universal wording.`

Do not include speculative hidden reasoning or unverifiable intermediate steps.
