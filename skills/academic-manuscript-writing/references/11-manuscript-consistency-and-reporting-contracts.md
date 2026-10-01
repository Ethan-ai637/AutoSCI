# Manuscript consistency and reporting contracts

## Why this layer exists

A valid evidence ledger can still drift away from the rendered manuscript. Typical release-stage failures include a claim anchor placed under the wrong section, ledger text that no longer matches the edited paragraph, a figure source cited under the wrong figure number, or a primary result whose required method/limitation never appears elsewhere in the paper.

Use deterministic manuscript-level checks for these mechanical consistency failures. Scientific judgment still belongs to the researcher/model.

## Anchor contract

For auditable Markdown workspaces, put the claim anchor immediately before the prose block it governs:

```text
<!-- CLAIM:C021 -->
The primary outcome ...
```

At `release`, each declared anchor must occur exactly once, under the section declared by the claim ledger, and the ledger claim text must occur in that anchored block. If a paragraph contains several independently auditable claims, split it or give each claim a separate anchored block rather than pretending one anchor covers unrelated propositions.

The manuscript is allowed to contain ordinary unanchored connective prose. Substantive empirical claims intended for release should be ledger-backed.

## Figure/table identity

`object_refs[].source_id` identifies the scientific object. `object_refs[].label` identifies how that object is named in the manuscript. When the source has `object_label`, the two labels must resolve to the same figure/table number. `Fig. 2` and `Figure 2` are equivalent; `Fig. 2` and `Fig. 3` are not.

Renumbering therefore requires updating source metadata, claim object references, captions, and manuscript text together.

## Reporting contracts

For important multi-section result families, use `reporting_contracts.jsonl` to declare the minimum manuscript dependencies of the result. This is deliberately narrower than a generic paper outline.

Recommended fields:

- `contract_id`
- `claim_family_id`
- `role`: `primary|secondary|sensitivity|exploratory`
- `result_evidence_ids`
- `method_evidence_ids`: method facts that must be represented in Methods
- `qualifier_evidence_ids`: limitations/sensitivity/conflicting evidence that must remain visible in Discussion/Conclusion
- `object_source_ids`: figures/tables expected to carry the result
- `required_sections`
- `abstract_eligible`

A reporting contract does not imply that every statistic belongs in every section. It declares dependencies, not duplicated wording.

For `full_manuscript` or `multi_section` release work, every `section_plan.main_claim_families` entry should have a reporting contract. Standard work may omit one, but preflight should flag the missing coverage.
