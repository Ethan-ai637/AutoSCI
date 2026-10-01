# Revision lifecycle example

Synthetic demonstration of a changed primary analysis that invalidates a previous positive result.

The workspace preserves the previous Abstract/Results/Discussion claims as `superseded`, introduces replacement active claims, keeps `manuscript.before.md`, records the material edit in `revision_log.jsonl`, maps the release obligation in `revision_obligations.jsonl`, and verifies the actual manuscript change with `revision_diff.json`.

Run:

```bash
python ../../scripts/preflight.py . --profile release --report qa_report.json
```

Expected result: release preflight passes with zero errors and zero warnings.

## v1.4 state lineage

This example also includes `workspace_state.previous.json`, representing the exact pre-revision semantic state. `revision_log.jsonl` binds the verified change to both that baseline `state_id` and the final `verified_state_id`. `revision_diff.json` includes old/new manuscript SHA-256 values, so the diff cannot be reused after a later silent edit.

## v1.6 compatibility fixture

The archived project/state metadata intentionally remains at skill version `1.5.0`. v1.6 treats the new `paragraph_contracts.jsonl` ledger as optional when absent, so historical state IDs remain valid instead of being invalidated merely by upgrading the skill.
