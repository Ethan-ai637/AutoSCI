# State model — authoritative vocabulary

## Purpose

This file is the single authoritative registry for judgment-bearing states in manuscript-reviewer 1.x. Other files may explain how to choose a state, but they should not invent alternate names or incompatible meanings.

If prose guidance and this registry conflict, preserve the scientific meaning and update the package before release; do not silently introduce a new runtime state.

## Evidence states

Use exactly one when applicable:

- `verified_support` — inspected evidence directly supports the atomic claim at the stated scope.
- `partial_support` — evidence supports only part of the wording or a narrower scope.
- `contradicted` — inspected evidence directly conflicts with the claim.
- `missing_required_evidence` — the manuscript makes a material support-bearing claim, plausible evidence locations were checked, and the required support is not reported.
- `ambiguous_mapping` — potentially relevant evidence exists, but the mapping between claim and evidence is materially unclear.
- `unavailable_to_verify` — verification is blocked by unavailable or unreadable evidence.
- `not_applicable` — the object does not require this evidence relation in context.

`missing_required_evidence` is a statement about the current manuscript's reported support, not proof that the underlying scientific proposition is false.

## Outward dispositions

Every surviving concern is exactly one of:

- `finding` — a sufficiently verified manuscript defect or material manuscript-internal support/reporting gap;
- `author_query` — a material ambiguity for which multiple plausible interpretations remain and author clarification is needed to adjudicate the concern;
- `coverage_gap` — verification is blocked by unavailable or unreadable material.

Internal-only terminal candidate state:

- `resolved_no_issue` — a candidate concern was checked and should not be reported.

`resolved_no_issue` is never a revision transition and never an outward review item.

## Severity

Only `finding` records receive scientific severity:

- `Critical`
- `Major`
- `Moderate`
- `Minor`

Severity reflects the consequence of leaving the current defect unrepaired. It does not encode repair cost, frequency of occurrence, author effort, or historical severity.

## Confidence

- `High`
- `Medium`
- `Low`

Confidence refers to support for the review assessment, not confidence that the paper's scientific hypothesis is true or false.

## Salience

Presentation tiers:

- `main_comment`
- `secondary_finding`
- `cleanup`
- `query`
- `coverage_gap`

Canonical salience determines outward placement. Rendering must not independently re-rank an item.

## Primary categories / ID prefixes

- `CE` — claim–evidence
- `FT` — figure/table/text consistency
- `NI` — numerical integrity
- `NT` — notation
- `CI` — citation
- `OC` — overclaim
- `XR` — cross-category/root issue
- `AQ` — public ID prefix for author queries
- `CG` — public ID prefix for coverage gaps

A record has one primary category even when the root spans multiple audit families.

## Revision transitions

For each prior material root in scope, use exactly one:

- `resolved` — the prior root no longer holds because current evidence/reporting actually repairs or verifies it;
- `partially_resolved` — the same scientific root remains, but its scope, strength, consequence, or unsupported burden is materially reduced;
- `persistent` — the same material root remains without meaningful defect reduction, even if it is described more clearly;
- `reclassified` — new evidence changes the disposition/category of the same lineage, such as an author query becoming a verified finding;
- `not_reassessable` — current resolution cannot be determined because required evidence remains unavailable;
- `no_longer_material` — the old verification need remains unresolved, but the current manuscript no longer relies on it for any material claim.

Current open records in a revision context may use `revision_status`:

- `new`
- `persistent`
- `partially_resolved`
- `reclassified`

Fully resolved, not-reassessable, and no-longer-material historical roots live in the revision-delta layer rather than as active current records unless there is an independent current concern.

## Decision boundary: finding vs author query

Use a `finding` when the current manuscript defect itself is verified even if the underlying scientific truth could later be established. Example: a paper explicitly states `p < 0.05` for all gains, but a completed manuscript/supplement check shows no reported test, paired unit, statistics, or output. The verified defect is unsupported reporting; do not infer that the result is non-significant.

Use an `author_query` when the defect itself cannot yet be established because two or more plausible interpretations remain and author clarification would decide between them.

## Compatibility rule

Changing the meaning of an existing state, removing one, or adding a new judgment-bearing state is a compatibility-sensitive 1.x change. Update schemas, examples, templates, regression fixtures, and release notes together.
