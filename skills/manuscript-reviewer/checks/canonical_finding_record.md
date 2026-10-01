# Canonical finding record and evidence packet

## Objective

Make every outward review item derive from one canonical, auditable record rather than being independently rewritten in the main comments, executive summary, and correction checklist.

The canonical record is the **single source of truth** for a final finding, author query, or coverage gap. Natural-language report sections are renderings of this record, not independent judgments.

This prevents:
- severity drift between the finding body and summary;
- an author query becoming an asserted defect in the executive summary;
- a coverage gap becoming “unsupported” or “false”;
- remediation becoming more burdensome when compressed into a checklist;
- duplicate manifestations being reintroduced after root clustering;
- reruns changing issue identity merely because wording changes.

## When to create the record

Do not create a final canonical record at first discovery.

Create it only after:
1. evidence checking;
2. type-specific sufficiency checking;
3. adversarial checking;
4. disposition assignment;
5. root-cause/dependency clustering;
6. salience assignment;
7. stable ID assignment.

Temporary candidate notes are not canonical records.

## Rendering invariant

Once a canonical record is finalized, the report writer must not silently reinterpret judgment-bearing fields. Main/secondary/query/gap placement, severity labels, confidence, and remediation must be rendered from the record.

If prose organization reveals that `salience`, severity, or disposition should change, modify the canonical record first, rerun validation/self-check, and only then regenerate prose. A report in which a record says `salience=main_comment` but appears under “Secondary findings” is internally inconsistent and fails this invariant.

## Core fields

Every final record should preserve, internally, the following when applicable:

- `record_id` — stable public ID assigned after clustering;
- `disposition` — `finding`, `author_query`, or `coverage_gap`;
- `primary_category` — `CE`, `FT`, `NI`, `NT`, `CI`, `OC`, or `XR`;
- `severity` — only for `finding`;
- `confidence` — evidence confidence for the assessment;
- `salience` — report placement tier;
- `locations` — stable manuscript anchors;
- `claim_or_object` — the atomic claim, result object, symbol, citation relation, or conflict under review;
- `evidence_state` — fixed vocabulary from `SKILL.md`;
- `evidence_packet` — anchors and verification facts that make the record reconstructable;
- `observed_evidence` — concise factual observation, not speculative reasoning;
- `assessment` — the exact defect, unresolved question, or verification block;
- `scientific_impact` — why the issue matters, if a finding;
- `remediation_class` — minimal sufficient repair class, if a finding;
- `recommended_fix` — minimal sufficient correction or clarification;
- `dependencies` — downstream manifestations that should not be double-counted;
- `summary_safe_statement` — the strongest short statement that may safely appear in the executive summary;
- `evidence_boundary` — material unavailable evidence or scope limitation affecting interpretation.

For revision/rebuttal contexts, the record may also carry:
- `review_context` — `revision_check`, `rebuttal_check`, or `version_delta`;
- `revision_status` — `new`, `persistent`, `partially_resolved`, or `reclassified` for current open items;
- `prior_record_ids` — historical record IDs in the same scientific lineage;
- `lineage_confidence` — confidence that the prior/current records represent the same root;
- `resolution_basis` — concise evidence-grounded statement of what changed and what remains.

Fully `resolved` prior issues are represented in the revision-delta layer rather than as active current finding records. See `checks/revision_tracking_and_resolution.md` and `schemas/revision_delta.schema.json`.

The machine-readable schema is in `schemas/finding_record.schema.json`.

## Evidence packet

The evidence packet must be sufficient for another reviewer to reconstruct the assessment without searching the whole manuscript.

Include the fields relevant to the defect type:

- `anchors` — claim/evidence/result/source anchors;
- `protocol_comparability` — `established`, `uncertain`, `incompatible`, or `not_applicable`;
- `provenance_status` — `established`, `partial`, `unknown`, or `not_applicable`;
- `inference_bridge` — bridge type when the conclusion is inference-heavy;
- `source_values` — explicit inputs for a numerical derivation, when relevant;
- `derivation` — reconstructable arithmetic/logic for numerical findings, when relevant;
- `external_source_inspected` — required for citation-semantic findings;
- `absence_check_complete` — required before `missing_required_evidence` can support a finding;
- `rendered_page_checked` — required when typography/layout materially determines the assessment;
- `surface_relation` — required for material cross-surface or claim-drift findings.

Do not fill irrelevant fields mechanically.

## Conditional integrity rules

### Finding

A `finding` must have:
- non-null severity;
- confidence;
- evidence state supported by the evidence packet;
- scientific impact;
- remediation class;
- recommended fix;
- summary-safe statement.

### Author query

An `author_query`:
- must not receive scientific severity;
- should state the unresolved ambiguity precisely;
- should record the plausible interpretations that remain when material;
- should ask for the smallest clarification needed to adjudicate the issue;
- must use a summary-safe statement that preserves uncertainty.

### Coverage gap

A `coverage_gap`:
- must not receive scientific severity;
- must identify the unavailable/unreadable material blocking verification;
- must state what claim/check cannot be completed because of that block;
- must not be rewritten as evidence that the manuscript is wrong.

## Type-specific hard requirements

Before finalizing a record, enforce these minimum conditions:

### Numerical integrity
- explicit source values or relationships are readable;
- the relevant protocols are comparable or the issue is specifically the protocol mismatch;
- the derivation is reconstructable;
- units, denominator, aggregation, and rounding alternatives were checked.

### Citation semantic support
- the cited source itself was inspected;
- the relevant source passage/context was inspected;
- the manuscript's atomic claim was mapped to that source;
- disagreement is not inferred from title/abstract/search snippets alone.

### Missing required evidence
- the claim requires the missing evidence;
- plausible manuscript locations were inspected under the selected review mode;
- available appendix/supplement dependencies were followed;
- `absence_check_complete = true`.

### Figure/table/text inconsistency
- the surfaces refer to the same scientific object/protocol, or the defect is that the manuscript falsely presents them as such;
- the conflict is readable without guessing plot geometry;
- if truth cannot be adjudicated, the assessment says `internal inconsistency`, not “surface X is wrong”.

### Claim-surface drift / overclaim
- the semantic fingerprint difference is material;
- harmless paraphrase and legitimate narrowing were excluded;
- the exact added scope/quantifier/modality/causal burden is identified.

### Notation
- the symbol/definition/use is visible in enough context to establish the ambiguity or inconsistency;
- rendered-page inspection was used when extraction or typography could change meaning.

## Summary-safe statement

`summary_safe_statement` is a guardrail, not decorative metadata.

It should be the strongest concise statement that preserves:
- disposition;
- severity, if any;
- uncertainty;
- scope;
- causal/inferential status;
- remediation burden.

Examples:

Finding:
> The abstract's universal superiority claim conflicts with one directly comparable condition in Table 2 and should be narrowed.

Author query:
> Baseline provenance is unclear, so same-protocol comparability of the headline result requires clarification.

Coverage gap:
> Semantic support for citation [12] could not be verified because the cited full text was unavailable.

The executive summary may use this statement or a weaker equivalent. It may not strengthen it.

## Rendering rule

All outward representations must be projections of the same canonical record:

`canonical record -> main comment / secondary finding -> executive summary -> correction checklist`

Do not allow any downstream representation to independently recalculate:
- severity;
- confidence;
- disposition;
- evidence state;
- remediation class;
- issue scope.

If a later verification step changes any of these, update the canonical record first and regenerate the dependent prose.

In a revision/rebuttal review, historical wording is not a second source of truth. First establish prior-to-current lineage, then update/create the **current** canonical record. Render current comments from the current record and render resolution history from the revision-delta record.

## Machine-readable output

Do not output raw canonical records by default.

If the user requests JSON/structured review output, emit final records conforming to `schemas/finding_record.schema.json`. Validation failure means the record is not ready to report.
