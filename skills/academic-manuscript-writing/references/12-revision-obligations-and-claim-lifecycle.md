# Revision obligations and claim lifecycle

## Why this layer exists

A manuscript revision can be mechanically complete while remaining scientifically incomplete. Two recurrent failures are:

1. a reviewer/editor request is answered in prose even though the corresponding manuscript change was not actually made or verified;
2. an updated analysis weakens or invalidates an old conclusion, but the old claim remains elsewhere in the manuscript.

Use explicit revision obligations and claim lifecycle states to make those failure modes inspectable.

## Claim lifecycle

`status` and `lifecycle_state` answer different questions:

- `status` asks whether a claim is currently verified, draft, blocked, or needs revision;
- `lifecycle_state` asks whether the claim still belongs to the current manuscript.

Allowed lifecycle states:

- `active` — current claim; eligible to appear in the manuscript;
- `superseded` — historical claim replaced by one or more newer claims;
- `retired` — historical claim that should no longer appear and has no direct replacement.

Use `supersedes_claim_ids` on a newer claim and `superseded_by_claim_ids` on an older claim when a replacement is explicit. A retired claim should record `retirement_reason`.

Do not delete historical claim records merely to make QA pass. Preserve the provenance chain, remove the inactive prose from the current manuscript, and let release QA verify that inactive anchors/text do not remain.

When an analysis changes substantially, prefer a new claim ID for a materially different scientific proposition rather than silently rewriting the historical claim in place. Minor wording fixes that do not change the scientific proposition may keep the same claim ID.

## Revision obligations

Use `revision_obligations.jsonl` for actionable reviewer, editor, user, or internal-audit requests. One obligation should represent one independently verifiable request.

Recommended fields:

- `obligation_id`
- `origin`: `reviewer|editor|user|internal_audit`
- `source_ref`
- `request`
- `disposition`: `pending|completed|not_applicable|declined_with_rationale`
- `required_actions`: one or more of `manuscript_change|analysis|citation|clarification|no_change`
- `affected_claim_ids`
- `affected_sections`
- `evidence_ids`
- `change_ids`
- `verification`: `pending|verified|blocked`
- `rationale`
- `response_text`

A reviewer response is downstream of the scientific work. For a completed `manuscript_change` obligation at release:

1. linked `change_id` records must exist;
2. those changes must be `verification=verified`;
3. `revision_diff.json` must show a corresponding claim change/removal and section change;
4. only then should the response say the manuscript was revised.

For `not_applicable` or `declined_with_rationale`, record the scientific reason. Never fabricate an analysis, citation, experiment, or textual change to satisfy the request.

## Relationship to legacy reviewer_response_map.jsonl

`reviewer_response_map.jsonl` remains accepted for backwards compatibility. New work should prefer `revision_obligations.jsonl` because it covers reviewer, editor, user, and internal-audit obligations with the same verification contract.
