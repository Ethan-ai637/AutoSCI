# Claim-span traceability

v1.8 adds an exact manuscript-span layer between the claim ledger and paragraph composition.

The goal is to prevent a release paragraph from passing merely because the ledger claim appears somewhere in the paragraph while nearby scientific prose, citations, figures, or numbers escape claim-level governance.

## Marker syntax

A span-governed claim uses the existing start marker plus a matching end marker:

```markdown
<!-- CLAIM:C001 -->
The primary outcome was 12.4 units in condition A versus 10.1 units in condition B (p = 0.03).
<!-- END-CLAIM:C001 -->
```

The claim record declares:

```json
{
  "claim_id": "C001",
  "manuscript_anchor": "CLAIM:C001",
  "anchor_precision": "span",
  "span_exemption_reason": ""
}
```

`anchor_precision=paragraph` remains available for legacy workspaces and rare cases that cannot be represented as exact prose spans. In a v1.8 release workspace, a paragraph fallback in a required section/type needs an explicit `span_exemption_reason` when exemptions are allowed by policy.

## Project policy

New v1.8 workspaces initialize:

```json
"claim_span_policy": {
  "required_sections": ["Abstract", "Methods", "Results", "Discussion", "Conclusion"],
  "required_claim_types": ["result", "method", "interpretation", "limitation", "literature_context"],
  "allow_exemptions": true,
  "max_uncovered_words_per_paragraph": 2,
  "require_exact_claim_text": true,
  "enforce_reverse_references": true
}
```

The policy applies only to v1.8+ workspaces or workspaces that explicitly define `claim_span_policy`. Historical v1.7-and-earlier projects keep their previous paragraph-anchor behavior.

## Exact text closure

For a span claim, the visible text between the start and end markers must match the claim ledger text after deterministic normalization of Markdown emphasis and structured citation syntax.

This is intentionally stronger than the older paragraph-level rule, which only required the claim text to occur somewhere in the anchored paragraph.

If a claim changes, its exact span must change with it. If surrounding prose changes while the span does not, that surrounding prose is not silently inherited by the claim.

## Numeric closure

`required_value_tokens` must occur inside the exact claim span. A number elsewhere in the paragraph does not satisfy the claim.

This prevents one neighboring claim from accidentally satisfying another claim's numeric-fidelity requirement.

## Citation closure

When `enforce_reverse_references=true`:

- every Pandoc-style citation inside a claim span must resolve to a source `citation_key`;
- every citation inside the span must be declared in that claim's `citation_keys`;
- every declared `citation_key` for a span claim must actually appear inside the span at release.

A citation used by one sentence therefore cannot be justified merely because another claim in the same paragraph declares it.

## Figure/table closure

For exact spans:

- every `Fig./Figure/Table` reference inside the span must resolve to source object identity;
- the exact claim must declare the reference in `object_refs`;
- a declared object reference must appear inside the span at release.

Paragraph-level object identity checks remain in place as a second layer.

## Span coverage closure

In governed sections, material visible prose may not sit outside exact claim spans.

The default tolerance is two uncovered words per paragraph so conjunctions such as "However" or "In contrast" do not force artificial claims. More substantial uncovered prose fails release.

For a legitimate structural exception, use:

```markdown
<!-- SPAN-COVERAGE:EXEMPT reason="transition sentence only" -->
```

Use this sparingly. Existing `COVERAGE:EXEMPT` paragraphs are also excluded from span-coverage enforcement, which is useful for structured tables or intentionally non-scientific blocks already governed by the paragraph coverage policy.

## No overlapping claim spans

Exact claim spans may be adjacent but may not overlap or nest.

If two propositions interact in one paragraph, represent them as adjacent atomic spans and use a `PARAGRAPH:<id>` composition contract over the paragraph. This keeps the layers distinct:

```text
evidence -> atomic claim -> exact claim span -> paragraph composition -> section/reporting contract
```

## Span-aware revision diffs

`revision_diff.py` schema v4 compares exact claim spans when both the old and new draft contain valid span markers for an `anchor_precision=span` claim. This prevents a change to one claim in a multi-claim paragraph from falsely marking neighboring claims as changed merely because the paragraph block changed.

When the old manuscript predates v1.8 and has only the start anchor, the diff falls back to the legacy paragraph block for that claim and records the fallback scope. This allows a v1.7 baseline to be upgraded without losing revision-verification continuity.

## Backward compatibility

v1.8 does not reinterpret old workspaces:

- projects with `skill_version < 1.8` and no `claim_span_policy` skip the new audit;
- their existing paragraph anchors continue to work;
- new v1.8 workspaces default to exact span governance.

## Release intent

The span layer is not a semantic reasoner. It does not decide whether a sentence is scientifically true. It makes the manuscript location governed by a claim precise enough that deterministic QA can answer:

1. exactly which words express this claim;
2. exactly which numbers belong to it;
3. exactly which citations and figures/tables support or contextualize it;
4. whether material prose has been added outside the claim ledger.
