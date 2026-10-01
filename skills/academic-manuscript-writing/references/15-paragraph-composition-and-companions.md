# Paragraph Composition and Claim Companions

A paragraph can be scientifically unsafe even when every individual claim is valid. The risk appears when claims are combined: a qualifier may disappear, an interpretation may be fused with a result, or two supported statements may be written as a stronger unsupported conclusion.

## Core rule

For release work, any manuscript paragraph containing two or more active claim anchors must have exactly one stable paragraph marker and a matching `paragraph_contracts.jsonl` record.

Example manuscript block:

```markdown
<!-- PARAGRAPH:P001 -->
<!-- CLAIM:C003 -->
<!-- CLAIM:CQ1 -->
The result supports a difference within the analyzed samples, but the estimate remains limited to the prespecified analysis population.
```

Example contract:

```json
{"paragraph_id":"P001","section":"Discussion","claim_ids":["C003","CQ1"],"composition":"qualified","primary_claim_id":"C003","qualifier_claim_ids":["CQ1"],"required_text_tokens":["analyzed samples"],"forbidden_terms":["proves"],"notes":""}
```

The contract does not replace scientific judgment. It makes the intended composition inspectable and gives deterministic QA enough structure to detect dropped qualifiers, wrong claim membership, stale paragraph identity, and prohibited wording.

## Composition types

Use one of:

- `additive` — claims are listed together without implying a new relation.
- `comparison` — claims are intentionally compared.
- `contrast` — claims are intentionally contrasted.
- `qualified` — a primary claim is explicitly bounded by one or more qualifier/limitation claims.
- `result_interpretation` — a measured result and its interpretation share a paragraph; both claim types must be represented.
- `synthesis` — multiple evidence-backed claims are combined into a higher-level synthesis already represented in the ledger.
- `method_context` — a scientific claim is paired with method context needed to interpret it.

Do not use a paragraph contract to legalize an unsupported inference. If the combined prose asserts a new proposition, create a separate claim for that proposition and link it to evidence.

## Required companions

A claim may declare claims that must remain nearby:

```json
"required_companions": [
  {"claim_id":"CQ1","scope":"same_paragraph"}
]
```

Allowed scopes:

- `same_paragraph` — strongest protection; useful for material qualifiers that must travel with the claim.
- `same_section` — companion must be represented somewhere in the same manuscript section.
- `manuscript` — companion must appear somewhere in the current manuscript.

Typical use cases:

- a positive result that must retain a prespecified population qualifier;
- a secondary/subgroup finding that must remain paired with its exploratory status;
- an interpretation that must retain a key limitation;
- a benchmark result that must remain paired with the evaluation setting.

## Prose guardrails

`required_text_tokens` and `forbidden_terms` are deliberately literal, not semantic. Use them sparingly for high-value release invariants such as an essential qualifier or a wording prohibition. They are not a substitute for reading the manuscript.

## Release behavior

At release, deterministic QA fails when:

- a multi-claim paragraph lacks exactly one `PARAGRAPH:<id>` marker;
- the paragraph marker has no matching contract;
- contract claim IDs differ from the manuscript claim anchors;
- the declared section is wrong;
- `qualified` composition loses a qualifier claim;
- `result_interpretation` lacks either a result or an interpretation claim;
- a required companion is missing from its declared scope;
- required literal text disappears or a forbidden term appears;
- a paragraph contract is orphaned from the manuscript.

This layer complements claim-level evidence grounding. It protects the meaning created by **composition**, not just the correctness of isolated statements.

## v1.8 interaction with exact claim spans

Paragraph contracts remain the composition layer **above** atomic claims. In v1.8 governed prose, each claim should occupy its own non-overlapping exact span (`CLAIM` ... `END-CLAIM`), while `PARAGRAPH:<id>` declares how those spans combine. Exact spans govern claim ownership; paragraph contracts govern the relationship among claims.
