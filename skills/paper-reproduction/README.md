# paper-reproduction

`paper-reproduction` turns a published paper and its research artifacts into a runnable, traceable, auditable reproduction workspace.

It is designed for the missing link between literature research and quantitative analysis:

```text
$literature-research
        ↓
selected paper / verified source
        ↓
$paper-reproduction
        ↓
code + environment + data/checkpoints + run ledger + discrepancies
        ↓
$scientific-data-analysis
        ↓
$scientific-figure / $academic-manuscript-writing / $manuscript-reviewer
```

## Modes

- `REPO_REPRODUCE`: paper + repository → pin revision → map claim to code → reconstruct environment → smoke test → target runs → compare.
- `PAPER_ONLY`: paper only → extract specified implementation → preserve unknowns → reconstruct only what is mechanically recoverable.
- `REPO_AUDIT`: repository only → resolve paper identity → inspect reproduction readiness without pretending execution evidence exists.

## Core design

The central artifact is a **reproduction contract**: the workflow must define the scientific claim it intends to test before expensive execution. The second core artifact is **paper↔code traceability**, linking paper objects to repository paths/configs/data/checkpoints/runs/results.

v1.1 adds **semantic provenance binding**: each scientific target run records hashes of the contract, run plan, repository manifest, data/checkpoint manifests, and claim↔code map that existed when the run was launched. Preflight rejects later mutation or removal of those execution-defining artifacts as if they had governed the older run.

The package deliberately separates:

- source environment vs resolved environment;
- pinned source revision vs modified/dirty execution state;
- execution blockers vs numeric scientific discrepancies;
- claim-scoped reproduction states vs global paper verdicts;
- mechanical candidate reconciliation vs final scientific assessment;
- reproduction provenance vs downstream statistical analysis.

## Quick start

```bash
python scripts/init_workspace.py reproduction --mode REPO_REPRODUCE --profile standard
python scripts/acquire_repo.py --url https://github.com/owner/repo.git --dest work/repo --ref <commit-or-tag> --output reproduction/artifacts/repository_acquisition.json
python scripts/inspect_repo.py --repo work/repo --output reproduction/repository_manifest.json
python scripts/preflight.py reproduction --output reproduction/preflight.json
```

After reviewing safety, identity, revision, contract, data, and environment:

```bash
python scripts/run_with_ledger.py \
  --ledger reproduction/run_ledger.jsonl \
  --workspace reproduction \
  --run-id run_001 \
  --claim-id claim_table2 \
  --run-kind target \
  --cwd /path/to/repo \
  --config configs/main.yaml \
  --dataset-id data_main \
  --checkpoint-id ckpt_main \
  --logs-dir reproduction/logs \
  -- python evaluate.py --config configs/main.yaml
```

For simple scalar claims, generate a non-destructive deterministic candidate assessment:

```bash
python scripts/reconcile_claims.py reproduction
```

For repository-only readiness auditing:

```bash
python scripts/audit_repo_readiness.py reproduction
```

For archival handoff:

```bash
python scripts/release_check.py reproduction
python scripts/freeze_workspace.py reproduction --output reproduction/manifest.sha256
```

## v1.1 release gates

The deterministic preflight checks, where applicable:

- target run ↔ exact pre-run contract/manifest hashes;
- target run commit ↔ pinned repository revision;
- run dataset/checkpoint IDs ↔ declared manifests;
- metric ↔ known run ↔ claim linked to that run;
- claim↔code artifact revision ↔ pinned repository revision;
- `exact_reproduction` eligibility;
- `within_reported_variation` comparison basis;
- PAPER_ONLY assumption-required items ↔ implementation decisions.

These checks validate provenance and state eligibility; they do not prove scientific truth or implementation correctness.

## Important safety note

Research repositories are untrusted code. Inspect installers, build files, shell scripts, containers, hooks, and download logic before execution. Do not expose credentials or use elevated privileges simply to make a reproduction succeed.

## Version

Current release: **v1.2.0** — fail-closed provenance, claim-metric binding, and filtered child-process environments.

## Tooling tests

Run:

```bash
python -m unittest discover -s tests -v
```

The suite covers empty-workspace initialization, Git revision/run capture, dirty-worktree refusal/patch fingerprinting, post-run contract mutation detection, unknown checkpoint references, reproduction-state eligibility, and non-destructive deterministic claim reconciliation.
