# Revision locality and manuscript preservation

`revise` and `refresh` should modify the existing scientific manuscript, not silently replace it with an audit report.

## Default principle

When an existing manuscript is the editing target:

> preserve valid text and structure; change only what the evidence, reviewer request, journal requirement, or consistency dependency requires.

Do not rewrite the title, Introduction, Methods, or unaffected prose merely because a fresh reconstruction is easier.

## Revision-diff schema v4

`revision_diff.py` schema v4 retains the v3 locality metrics after removing workflow comments/anchors, and adds exact-span claim comparison for v1.8 claims when both drafts contain matching span markers:

- `prose_token_similarity`;
- old/new word counts;
- old/new prose paragraph counts;
- exact old paragraphs preserved;
- preserved-old-paragraph fraction;
- changed-section fraction;
- per-section similarity;
- old/new title and `title_changed`;
- per-claim `comparison_scope`, using `exact_span` for v1.8 spans or `paragraph_fallback_legacy` when the historical baseline lacks end markers.

These metrics are not writing-quality scores. They are change-scope signals.

## Default v1.7 policy

```json
"revision_policy": {
  "preserve_existing_manuscript": true,
  "allow_global_rewrite": false,
  "min_prose_token_similarity": 0.55,
  "min_preserved_old_paragraph_fraction": 0.35,
  "allow_title_change": false
}
```

Thresholds are conservative defaults for targeted manuscript revision. Adjust them before editing when the requested revision is legitimately broader.

## Global rewrites

A global rewrite may be scientifically justified, but it must be explicit rather than accidental:

```json
{
  "allow_global_rewrite": true,
  "global_rewrite_reason": "Journal transfer requires a complete article-format rewrite.",
  "global_rewrite_change_ids": ["R_GLOBAL_01"]
}
```

The linked change IDs must be verified revision records.

## Keep workflow language out of scientific prose

Release revision mode flags common audit/report language such as:

- `this refresh`;
- `supplied methods notes`;
- `supplied current table/results`;
- `allowed sources`;
- `source-conflict note`;
- `benchmark materials/prompt`;
- `source scope`.

These ideas belong in `sources.jsonl`, `source_conflicts.md`, revision logs, QA reports, or reviewer responses—not in the scientific manuscript unless the phrase is genuinely part of the scientific subject matter.

## Typical failure

Bad revision behavior:

```text
Original paper
  -> reconstruct all sections from evidence ledgers
  -> rename title
  -> write "this refresh rechecks..."
  -> technically traceable but no longer a real manuscript revision
```

Preferred behavior:

```text
Original paper
  -> identify affected claims/families
  -> edit only affected spans and dependent sections
  -> preserve unaffected manuscript prose
  -> keep provenance/audit narration outside manuscript.md
```

Use `audit_revision_locality.py` in release preflight to enforce this separation.
