# Manuscript Coverage Closure

A release manuscript is not fully auditable if traceability works only in one direction.

Two directions must close:

1. **ledger -> manuscript**: every active claim intended for the current manuscript resolves to a real manuscript location;
2. **manuscript -> ledger/source identity**: scientific paragraphs, structured citations, and figure/table references in covered sections resolve back to active claims and declared sources.

This prevents two common failure classes:

- a valid claim exists in the ledger but was accidentally omitted from the manuscript;
- scientifically meaningful prose, a citation, or a figure/table reference was added directly to the manuscript without entering the evidence/claim system.

## Default coverage policy

For multi-section/full-manuscript work, the default covered sections are:

- Abstract
- Methods
- Results
- Discussion
- Conclusion

Introduction is not required by default because literature-heavy introductions often use a separate literature-grounding workflow. Add `Introduction` to `project.json.coverage_policy.required_sections` when claim-level introduction coverage is desired.

Example:

```json
{
  "coverage_policy": {
    "required_sections": ["Abstract", "Methods", "Results", "Discussion", "Conclusion"],
    "allow_exemptions": true
  }
}
```

## Claim presence

`claims.jsonl` may use:

- `manuscript_presence: "required"` — the active claim must have a `manuscript_anchor` and resolve into the current manuscript;
- `manuscript_presence: "optional"` — the claim may remain in the ledger without appearing in the current manuscript;
- `manuscript_presence: "not_in_manuscript"` — the claim is intentionally excluded from the current manuscript and should include `manuscript_presence_reason`.

If the field is omitted, active claims in the default covered sections are treated as `required` for multi-section/full-manuscript work and as `optional` otherwise.

Do not use `not_in_manuscript` to hide a contradictory or inconvenient result. Scientific omission decisions still need to satisfy the reporting contracts, section plan, and ordinary scientific QA.

## Paragraph coverage

In covered sections, every prose paragraph should contain at least one registered active claim anchor, for example:

```markdown
<!-- CLAIM:C017 -->
The primary outcome was higher in condition A than condition B ...
```

A paragraph may contain more than one claim anchor when it genuinely expresses multiple ledger claims.

A purely structural/non-scientific paragraph may be exempted only when the project policy allows exemptions:

```markdown
<!-- COVERAGE:EXEMPT reason="transition sentence only" -->
We next examine the secondary analysis.
```

Use exemptions sparingly. They are visible in the coverage report and are not a substitute for grounding scientific prose.

## Reverse figure/table identity

The coverage audit scans covered paragraphs for structured object references such as:

- `Fig. 2`
- `Figure 3b`
- `Table 1`
- `Fig. S4`

Every detected object reference must:

1. resolve to a declared source `object_label` or locator; and
2. be declared in `object_refs` of at least one active claim in that paragraph.

This is the reverse complement to the forward figure/table check. It catches a manuscript writer inserting `Fig. 4` directly into prose without updating the claim/source identity contract.

## Reverse citation coverage

Structured Pandoc-style citation keys such as `[@Smith2024]` are reverse-audited.

Every detected key must:

1. match a source `citation_key`; and
2. appear in `citation_keys` of at least one active claim in the same paragraph.

Other citation styles (for example plain `(Smith et al., 2024)` text or numeric `[12]`) are not inferred as identities by this deterministic audit unless transformed into a structured citation-key representation upstream.

## Recommended command

```bash
python scripts/audit_manuscript_coverage.py . \
  --profile release \
  --report manuscript_coverage.json
```

`preflight.py` runs this audit automatically.

Coverage closure proves that manuscript content participates in the declared provenance system. It does not prove that a claim is scientifically valid; evidence verification and scientific review remain separate gates.

## v1.8 exact-span layer

Paragraph coverage remains the coarse bidirectional safety net. In v1.8 workspaces, `audit_claim_spans.py` adds a finer layer for configured scientific sections: exact start/end claim spans must own their text, numbers, citations, and figure/table references, and material prose may not sit outside governed spans. See `19-claim-span-traceability.md`.
