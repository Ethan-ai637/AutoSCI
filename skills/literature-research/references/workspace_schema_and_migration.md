# Workspace Schema and Migration

## Three versions, three meanings

Keep these independent:

- `protocol_version` — version of the scientific review protocol;
- `workspace_schema` — structural contract for review artifacts;
- skill `VERSION` — implementation version of `literature-research`.

Changing one does not automatically justify changing another.

## Supported workspace schemas

### v1

`autosci-literature-research-workspace-v1` / `schemas/workspace-v1.json`

Introduced in skill v1.5. It provides structural headers and metadata but does not explicitly distinguish successful vs failed search execution or attempted vs completed full-text screening.

### v2

`autosci-literature-research-workspace-v2` / `schemas/workspace-v2.json`

Introduced in skill v1.6. It adds:

- search execution status and marginal-yield/stopping-evidence fields;
- screening `access_level`;
- separate `evidence_stage` in final screening;
- explicit `full_text_attempted` vs `full_text_screened` semantics;
- protocol `deterministic_exclusion_rules`.

New workspaces use v2.

## Validation

`validate_workspace.py` auto-selects the declared schema from `review/workspace_meta.json`. This means an unchanged v1 workspace can still be validated under its original v1 contract.

Use `--schema` only when intentionally testing against an explicit contract.

Structural validation does not imply scientific correctness. Run domain audits and `preflight.py` separately.

## Migration policy

Preview first:

```bash
python scripts/migrate_workspace.py --root .
```

Apply only after inspection:

```bash
python scripts/migrate_workspace.py --root . --apply
```

Migration may:

- create/update `workspace_meta.json`;
- add missing required CSV columns as blanks;
- add an empty `deterministic_exclusion_rules` list when absent;
- back up files before rewriting;
- record migration history.

Migration must not invent claim IDs, screening judgments, study identity, citation relationships, evidence, source-access claims, or synthesis conclusions.

### Critical v1 -> v2 rule

Legacy `stage=full_text` is semantically ambiguous. Migration **does not** rewrite it to `full_text_screened` or `full_text_attempted`. It leaves the value intact, adds the new structural fields, and emits a manual-follow-up warning. The reviewer must inspect what source was actually accessed and relabel the event honestly.

A migrated workspace can therefore be schema-valid while scientific preflight still fails. That is intentional: structural repair is not scientific repair.
