# Version lineage and change provenance

A manuscript revision is scientifically auditable only when the final semantic state can be tied to a known pre-edit state and to explicit revision records.

## Why hashes alone are not enough

A release manifest proves which bytes were delivered. It does not explain why a claim changed, whether an evidence row was silently rewritten, or whether a previously verified revision was later modified without re-verification.

For `revise` and `refresh`, use two semantic state IDs:

- `base_state_id`: the exact pre-edit semantic state;
- `verified_state_id`: the exact post-edit semantic state on which the revision was actually checked.

The semantic state covers the manuscript-facing scientific contract: project metadata, section plan, source ledger plus declared local source-file hashes, evidence ledger, claim ledger, reporting contracts, paragraph composition contracts, and manuscript text. Revision logs and QA outputs are excluded so that recording verification does not change the semantic state being verified.

## Recommended revision transaction

Before material editing:

```bash
python scripts/checkpoint_workspace.py . --output workspace_state.previous.json
```

Make the scientific changes. Update source/evidence/claim ledgers before polishing prose. Generate a real manuscript diff when manuscript text changed:

```bash
python scripts/revision_diff.py \
  --old manuscript.before.md \
  --new manuscript.md \
  --claims claims.jsonl \
  --report revision_diff.json
```

Capture the candidate final state:

```bash
python scripts/checkpoint_workspace.py . --output workspace_state.current.json
```

For each verified material `revision_log.jsonl` row, record:

- `base_state_id` = `workspace_state.previous.json.state_id`;
- `verified_state_id` = `workspace_state.current.json.state_id`;
- `source_ids` for scientific source-ledger or source-file changes;
- `writing_source_ids` for dynamic writing-guideline source changes;
- `affected_evidence_ids` for evidence-ledger changes;
- `affected_claim_ids` for claim additions, removals, lifecycle transitions, or edits;
- `affected_sections` for manuscript changes;
- `changed_artifacts` for governed semantic artifacts such as `project.json`, `section_plan.json`, `writing_profile.json`, `manuscript_contract.json`, `reporting_contracts.jsonl`, or `paragraph_contracts.jsonl`;
- a concrete `action`, `rationale`, and `verification=verified` only after inspection.

Then run release preflight. If anything semantic changes after verification, `verified_state_id` becomes stale and release must be re-verified.

## What the provenance audit checks

`audit_change_provenance.py` compares `workspace_state.previous.json` with the current workspace and checks that:

1. revise/refresh release work has a baseline checkpoint;
2. actual local source-file changes are detected even when a filename is reused;
3. added/removed/changed sources, evidence units, and claims are covered by a verified revision record;
4. project policy/conflict-disposition and section/reporting/paragraph-contract changes are explicitly declared;
5. a changed manuscript has a `revision_diff.json` whose old/new SHA-256 values match the baseline/current manuscript hashes;
6. verified revision rows bind to both the baseline state and the exact current state;
7. post-verification silent edits invalidate the previous verification.

This is a provenance gate, not a scientific-validity proof. A perfectly traced wrong analysis is still wrong.

## Checkpoint policy

For a short revision, one baseline -> one final verified state is sufficient.

For long revisions with independently reviewed milestones, checkpoint after a stable milestone and make that checkpoint the next `workspace_state.previous.json`. Do not keep using a very old baseline after accepting a new scientific state, because that obscures which change introduced a later regression.

## Release lineage

`freeze_snapshot.py` writes `workspace_state.current.json` and a manifest containing:

- `workspace_state_id` for the frozen release;
- `parent_workspace_state_id` when a previous state exists;
- file-level SHA-256 entries.

For the next revision cycle, the frozen current state can serve as the conceptual parent. Capture a fresh `workspace_state.previous.json` before editing the working copy.
