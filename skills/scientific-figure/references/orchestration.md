# Deterministic orchestration and resume

Use this layer to make execution repeatable. It does **not** change scientific semantics or visual taste; it only chooses the workflow path from the existing profile, spec complexity, and current milestone.

## One state file per figure

Initialize after `figure_spec.json` has real content:

```bash
python scripts/orchestrate.py init figure_spec.json --state workflow_state.json
```

The state records:
- resolved profile
- complexity level/score
- whether a layout tournament is required, recommended, or unnecessary
- current milestone
- semantic lock at checkpoint time
- SHA-256 hashes of checkpointed artifacts

It never stores manuscript contents beyond what is already in `figure_spec.json`.

## Milestones

The ordered milestones are:

1. `semantic_contract` — source-grounded spec exists and has been scientifically checked.
2. `semantic_frozen` — required for standard/release; semantic lock is valid.
3. `layout_selected` — one macro-layout has been deliberately selected. A tournament may precede this.
4. `svg_candidate` — editable traceable SVG exists.
5. `qa_passed` — profile-aware deterministic preflight passed for the exact SVG/spec pair.
6. `critic_passed` — semantic + visual critique has no unresolved hard gate. Refinement may move the workflow back to `svg_candidate`.
7. `released` — release profile only; final package/manifest was created and verified.

Draft can skip `semantic_frozen`; non-release work stops after `critic_passed`.

## Ask the orchestrator what to do next

```bash
python scripts/orchestrate.py next figure_spec.json --state workflow_state.json
```

This emits exactly one next action and any deterministic command that should be run. Use `status` for the full plan:

```bash
python scripts/orchestrate.py status figure_spec.json --state workflow_state.json
```

Do not improvise a more expensive path unless the user changes the goal or a real failure justifies it.

## Checkpoint only verified milestones

Examples:

```bash
python scripts/orchestrate.py checkpoint figure_spec.json semantic_contract \
  --state workflow_state.json

python scripts/orchestrate.py checkpoint figure_spec.json layout_selected \
  --state workflow_state.json --file layout_plan.md

python scripts/orchestrate.py checkpoint figure_spec.json qa_passed \
  --state workflow_state.json --file figure_spec.json --file figure.svg
```

`checkpoint` reruns deterministic gates appropriate to the milestone, then hashes the named artifacts. Semantic milestones compare the semantic payload rather than the whole JSON file, so freezing/profile metadata does not create false staleness. If one changes later, `verify` marks that milestone stale:

```bash
python scripts/orchestrate.py verify figure_spec.json --state workflow_state.json
```

That is intentional. If SVG changes after QA, rerun QA rather than trusting the old pass.

## Refinement rollback

After a meaningful SVG edit, checkpoint `svg_candidate` again. This automatically invalidates `qa_passed`, `critic_passed`, and `released`. After a semantic edit, unlock/verify/re-freeze and reinitialize or checkpoint the earlier semantic milestones.

## Layout tournament policy

The orchestrator resolves the existing policy deterministically:

- explicit `workflow.layout_tournament=on` -> required
- explicit `off` -> off
- draft + auto -> off unless the agent explicitly records a real ambiguity
- standard + high complexity -> recommended
- standard + low/medium -> optional/off
- release + medium/high -> required
- release + low -> off

`recommended` does not block progress. `required` means do not checkpoint `layout_selected` until the comparison is actually complete.

## Resume discipline

At the start of a resumed Codex session:

```bash
python scripts/orchestrate.py verify figure_spec.json --state workflow_state.json
python scripts/orchestrate.py next figure_spec.json --state workflow_state.json
```

If state is absent, initialize it. If state is stale, rerun from the earliest stale milestone instead of rereading every reference and rebuilding the figure from scratch.
