# Revision and refresh mode

## Two different tasks

`revise` changes prose against a stable evidence base.

`refresh` updates prose because the evidence base itself changed.

Treating a refresh as ordinary proofreading is dangerous because a single changed analysis can invalidate multiple sections.

## Revision protocol

1. Identify requested change.
2. Convert actionable reviewer/editor/user requests into revision obligations when traceability matters.
3. Identify authoritative source.
4. Find linked claim IDs and lifecycle state.
5. Find manuscript anchors/locations.
6. Edit the minimum necessary scientific span.
7. Propagate terminology, number, caption, and cross-reference changes.
8. Run a before/after revision diff when a pre-edit manuscript exists.
9. Re-run preflight.
10. Record and verify the material change.

## Refresh protocol

After a changed analysis/figure/table:

- fingerprint sources;
- compare snapshots;
- identify affected active claims;
- re-check primary and derived claims;
- decide whether each affected proposition remains active, is replaced (`superseded`), or should disappear (`retired`);
- re-check Abstract, Results, Discussion, Conclusion, captions, and supplement;
- re-check statements of novelty or superiority that depended on the changed result;
- remove inactive claim prose from the current manuscript while preserving historical ledger records.

A claim may remain textually identical after review; it still counts as reviewed if its source changed. A materially different scientific proposition should normally receive a new claim ID rather than silently overwriting the historical claim.

## Protected text

When revising an existing manuscript, preserve sections or facts the user marks as protected unless they conflict with authoritative evidence. If they conflict, surface that conflict rather than silently overriding either instruction.

## v1.7 locality rule

For `revise`/`refresh`, configure `project.json.revision_policy` **before editing** and read `18-revision-locality-and-manuscript-preservation.md`.

A targeted revision should preserve the original title and unaffected scientific prose by default. If a journal transfer, restructuring request, or other explicit obligation genuinely requires a global rewrite, authorize it before editing with a reason and verified change IDs. Keep audit/provenance narration outside `manuscript.md`.
