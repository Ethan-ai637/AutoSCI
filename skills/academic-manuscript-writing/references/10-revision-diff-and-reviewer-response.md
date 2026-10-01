# Revision diff and reviewer-response linkage

## Revision proof, not revision memory

A revision should be auditable from source change to manuscript change:

`trigger/source -> evidence -> claim/change_id -> manuscript span -> verification`

Do not rely on conversational memory to assert that a requested change was made.

## Before/after diff

For a material revision, preserve the pre-edit manuscript and run:

```bash
python scripts/revision_diff.py \
  --old manuscript.before.md \
  --new manuscript.md \
  --claims claims.jsonl \
  --report revision_diff.json
```

The report identifies changed Markdown sections, anchored claims that changed, intentionally added claim anchors, intentionally removed claim anchors, and anchors absent from both drafts. Schema v4 is span-aware: when a claim uses `anchor_precision=span` and both drafts contain matching `END-CLAIM` markers, only the exact claim span is compared. If the historical baseline predates v1.8 end markers, the diff falls back to the legacy paragraph block for that claim and records `comparison_scope=paragraph_fallback_legacy`. Schema v4 retains the v3 prose-token similarity, paragraph preservation, per-section similarity, changed-section fraction, and title-change metrics for revision-locality auditing. The legacy `missing_or_moved_anchors` union is retained for backwards compatibility. An intentionally removed anchor can be valid when the corresponding claim is `superseded` or `retired`; verify the lifecycle record rather than treating every removal as an error.

The diff is a mechanical audit; inspect the scientific meaning manually.

## Reviewer/editor comments

For new work, prefer `revision_obligations.jsonl` and read `12-revision-obligations-and-claim-lifecycle.md`. It links each actionable request to real revision changes, evidence, affected claims/sections, and verification state.

`reviewer_response_map.jsonl` remains supported for backwards compatibility. A response may state that a manuscript change was completed only when the linked revision exists and the current manuscript/diff supports that statement. If the scientific request cannot be satisfied, record the reason instead of fabricating an experiment, analysis, citation, or manuscript change.

Reviewer-response prose is downstream of the manuscript revision. First make and verify the scientific change; then describe it.
