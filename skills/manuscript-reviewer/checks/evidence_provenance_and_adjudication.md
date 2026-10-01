# Evidence provenance and adjudication

## Objective

Make consequential review judgments from **where evidence came from and under what protocol/version it was produced**, not from how visually authoritative a manuscript surface looks.

This layer is especially important for:
- imported baseline numbers;
- revised manuscripts with stale text/tables/supplements;
- pooled results assembled from heterogeneous sources;
- citation-derived external facts;
- conflicts among abstract, prose, figures, tables, captions, appendices, and external sources.

## Provenance record

For every central evidence/result object, record enough provenance to answer:
- **producer** — current authors, prior work, dataset maintainers, benchmark organizers, or unknown;
- **version** — current manuscript/revision, supplement version, cited source version, model/checkpoint/version if material;
- **origin** — rerun experiment, imported value, derived value, author-provided analysis, external source;
- **protocol** — dataset/population, split, metric, aggregation, budget/constraints, sample set;
- **transformation** — raw reported value, rounded value, normalized value, recomputed aggregate, relative change, copied baseline;
- **location** — exact manuscript/source anchor.

Do not require all fields for trivial evidence. Require them when provenance can change comparability or adjudication.

## Provenance classes

Useful internal classes:
- `current_author_result` — produced in the current manuscript's study/evaluation;
- `current_author_derived` — computed from current-author results;
- `imported_baseline` — copied from prior work, leaderboard, benchmark paper, or documentation;
- `rerun_baseline` — baseline rerun by current authors under the current protocol;
- `external_primary_source` — original cited empirical/theoretical source;
- `external_secondary_source` — review, survey, commentary, documentation, or secondary report;
- `supplementary_same_work` — appendix/supplement/artifact belonging to the same work;
- `unknown_provenance` — provenance cannot be established from inspected material.

These are not quality scores. They tell the reviewer what can legitimately be compared or used to adjudicate a conflict.

## Adjudication principles

### 1. Provenance outranks presentation format

Do not privilege a table over prose, or a figure over a caption, merely because it appears more structured.

When two manuscript surfaces conflict:
- first identify whether they describe the same scientific object and protocol;
- inspect provenance, derivation, version, and nearby definitions;
- if no inspected evidence establishes which value/statement is intended, report an internal inconsistency rather than choosing a winner.

### 2. Same-protocol evidence is required for direct comparative claims

A rerun baseline under the same protocol can usually support a direct comparison more cleanly than an imported value. An imported baseline may still be valid, but only if protocol compatibility is established.

Do not silently treat:
`current author result vs imported baseline`
as equivalent to:
`same-run/same-protocol head-to-head comparison`.

### 3. Derived values inherit the provenance and assumptions of their inputs

A relative improvement, average, efficiency ratio, or error reduction is only as comparable as the values used to derive it.

Before adjudicating a derived-number conflict, verify:
- the source values;
- the formula/definition;
- the denominator/weights;
- the protocol identity;
- whether rounding can explain the difference.

### 4. Primary-source preference for semantic attribution

For citation Level 3 claims, prefer the original source when the manuscript attributes a specific empirical, theoretical, or methodological result.

A secondary source can support background/synthesis, but do not use it to upgrade an unverified precise primary claim unless the secondary source itself is the intended authority.

### 5. Version consistency matters

A supplement, appendix, model checkpoint, benchmark release, or cited preprint may belong to a different version than the manuscript being reviewed.

If version mismatch is plausible and changes the result/definition:
- do not assert that one version is wrong without evidence;
- classify the issue as an author query or internal inconsistency when appropriate;
- record the version boundary in the evidence packet.

## Conflict-adjudication ladder

When two pieces of evidence conflict, use this order of operations:

1. **Identity check** — are they actually about the same object/claim?
2. **Protocol check** — same metric, population, split, model, aggregation, units, budget, sample set?
3. **Provenance check** — rerun/imported/derived/external; who produced the value?
4. **Version check** — same manuscript/source/artifact version?
5. **Derivation check** — can one value be reconstructed from explicit inputs?
6. **Qualification check** — caption, footnote, local qualifier, exclusion, or uncertainty resolves the apparent conflict?
7. **Adjudicate only if warranted** — state which surface/source is wrong only when inspected evidence establishes it.
8. **Otherwise report the conflict** — do not manufacture a source of truth.

## Baseline provenance gate

For each headline comparison involving a baseline, classify the baseline as:
- rerun under the current protocol;
- imported but protocol-compatible;
- imported with material protocol differences;
- provenance unclear.

Handling:
- `rerun under current protocol` -> direct comparison usually permitted;
- `imported but compatible` -> direct comparison may be permitted; retain provenance note if important;
- `imported with differences` -> do not present raw ranking as clean head-to-head evidence without qualification;
- `provenance unclear` -> author query if the ambiguity is material.

## Provenance failure patterns

### Imported-baseline laundering
A paper presents an imported baseline result beside new results as though all methods were evaluated identically, but protocol equivalence is not established.

### Version drift
The abstract/table/supplement appear to contain results from different revisions or checkpoints.

### Derived-value laundering
A headline relative improvement is computed from values produced under different protocols.

### Secondary-source substitution
A review article is used as if it were direct evidence for a precise primary empirical claim.

### Format authority bias
A table is assumed correct solely because it is a table.

## Reporting discipline

Provenance is usually part of the evidence packet, not a standalone finding.

Create a standalone finding/query only when provenance itself creates a material scientific problem, such as:
- direct comparability cannot be established;
- a baseline source/protocol is materially ambiguous;
- version drift creates unresolved contradictory results;
- the manuscript presents heterogeneous evidence as homogeneous.

Do not burden the final report with provenance metadata that does not affect interpretation.
