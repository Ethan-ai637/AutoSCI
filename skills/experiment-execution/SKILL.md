---
name: experiment-execution
description: Plan and run reproducible multi-run research campaigns. Use when a user needs disciplined seed staging, complete benchmark execution, immutable configs, run/checkpoint/result tracking, remote job coordination, or campaign-level provenance audits. Optional companion skills can support study design, implementation, remote packaging, and scientific interpretation.
---

# Experiment Execution

Release: 1.11.0 (see [CHANGELOG.md](CHANGELOG.md)).

When selecting or changing a numeric gate, read [Threshold rationale](references/threshold-rationale.md). It distinguishes statistically supported design requirements from repository policy and structural schema checks; do not present a structural or local-policy value as a universal field standard.

Make every planned run traceable from the protocol through its exact benchmark scope, config, seed/replicate, source commit and complete source state, environment, command, checkpoint, metrics, and logs. Keep compute efficient by limiting early-stage conditions and seeds, never by shrinking the benchmark or changing its evaluation protocol.

## Non-negotiable rules

1. **Use the complete official benchmark scope.** Pin the benchmark name/version, official task suite, splits, and evaluation protocol. Every scientific run must cover all official tasks/examples required by that benchmark protocol. Do not sample, truncate, cherry-pick tasks/classes/examples, drop hard cases, or quietly change splits to save time.
2. **Do not invent research data or benchmark infrastructure.** Do not generate a substitute dataset, synthetic benchmark tasks, labels, examples, or evaluation targets for scientific runs. Reuse the benchmark's official loader, task definitions, reference implementation, and evaluator/metrics when available. Do not rebuild an existing wheel for convenience. If an official component is unavailable or incompatible, record the blocker and ask before proposing a replacement.
3. **Separate engineering tests from research runs.** Unit tests may use tiny fixtures only to test code plumbing; keep them outside benchmark result directories and never use them as evidence. For smoke checks, prefer syntax/config/CLI dry-runs that consume no benchmark examples. If a scientific smoke run is requested, use the complete official benchmark scope; never use a benchmark subset as a smoke shortcut.
4. **Spend seeds only at the right stage.** A pilot/screening campaign uses exactly one seed per stochastic condition under this skill's declared screening policy; this is a compute/anti-seed-shopping rule, not a field-wide statistical standard. Pilot results are exploratory and cannot support a final variance, significance, or robustness claim. Add multiple seeds only in the predeclared confirmatory campaign. Two runs are only the mathematical floor for estimating between-run variance, not an adequate sample-size guarantee. Set the actual confirmatory count before seeing outcomes and justify it from the benchmark's protocol or a power/precision analysis. Do not multiply seeds across an early grid. See [threshold rationale](references/threshold-rationale.md).
5. **Use a small, justified condition matrix.** Predeclare the hypothesis-relevant method/baseline/ablation conditions. Avoid Cartesian sweeps and decorative ablations. Reduce the number of conditions, models, or checkpoints when justified; do not reduce the benchmark scope for any condition.
6. **Freeze identity before launch.** Record the protocol commit, source commit and dirty/patch state, benchmark/data version, official and executed scope-manifest hashes, config hash, seed or replicate ID, environment, command argv, resource plan, checkpoint selection rule, and expected output schema before remote execution.
7. **Never overwrite evidence.** Each attempt has a unique `attempt_id`. Keep failed, interrupted, OOM, and cancelled attempts in an append-only ledger. Save checkpoints and results under immutable run/attempt-specific paths with hashes; do not silently replace a checkpoint or select a favorable retry.
8. **A partial benchmark run is incomplete.** If budget, storage, time, or hardware cannot support the full scope, stop before launch or mark the attempt incomplete. Do not report a partial score as benchmark performance. Ask for a revised scope only if the user explicitly wants to change the scientific question; otherwise wait for adequate resources.
9. **Do not execute expensive jobs locally.** Follow repository policy for remote GPU work. A planning or packaging request does not authorize renting hardware, spending credits, or launching a costly job.
10. **Keep provenance and claims aligned.** A completed status requires successful execution, full benchmark coverage, valid official-scope hashes, config/commit identity, and complete output artifacts. Only scientifically reviewed evidence can support claims; campaign execution audit alone does not approve claims.

## Workflow

### 1. Establish the campaign contract

Read any repository research state, findings, approved experiment protocol, and applicable local execution rules. If no approved protocol exists, stop before preflight or execution and get the protocol approved; use `$experiment-planner` if installed and needed. This skill can independently turn an approved protocol into an auditable run campaign.

For each campaign, record:

- the experiment/hypothesis and whether it is a `pilot` or `confirmatory` stage;
- the official benchmark identity, version/revision, complete task/split scope, official loader/evaluator entrypoints, and how completeness will be verified;
- the exact conditions and immutable config files;
- each condition's randomness mode (`seeded_stochastic`, `uncontrolled_stochastic`, or `deterministic`), the seed/replicate plan, and its rationale;
- the expected full task/example count and result schema for every run;
- expected hardware, wall time, memory, storage, and checkpoint policy;
- a predeclared comparison/stop/continue rule.

Use `templates/campaign.template.json` as a machine-readable companion to `experiments/<slug>/protocol.md`. Campaign schema 1.1 requires a finite positive full-scope runtime, memory, and storage estimate plus an evidence-based estimate basis. Follow [schema migration](references/schema-migration.md) when updating older campaigns. Keep `schema_version` at the version declared by `schemas/campaign.schema.json`; preflight rejects unknown versions until the campaign is explicitly migrated. The JSON contract does not replace the scientific protocol.
Use full immutable commit SHAs for both the local source and official benchmark code. If official code is released only as an archive, keep that exact archive in the campaign and hash it; do not pin a moving branch name by itself. If the local source tree is dirty, keep the reviewable patch and a ZIP snapshot with a per-file SHA-256 manifest; include untracked execution files, then compare the archive manifest with the actual working-tree status before launch. A patch alone does not capture untracked files.

### 2. Enforce benchmark integrity before coding or launching

Read [Benchmark integrity](references/benchmark-integrity.md). Verify the benchmark version and full official scope from the benchmark's own documentation/code. Normalize each official scope to JSON with `scope_id` and either unique task/example IDs or immutable shard/file IDs, hashes, and counts; cite a reviewable source URL, revision, and code/document locator. Compare it with the manifest emitted by the exact loader/evaluation path. Record hashes and counts.

Run the deterministic campaign preflight:

```bash
python skills/experiment-execution/scripts/preflight_campaign.py experiments/<slug>/campaign.json
```

The preflight checks declarations, dirty-source patch and snapshot integrity, manifest IDs/counts, hashes, configs, IDs, condition/seed/replicate coverage, and stage policy. It cannot prove that a self-authored source snapshot includes every relevant working-tree file, that a benchmark manifest actually matches the official benchmark, or that arbitrary code consumed it. Verify working-tree status against the source snapshot and verify the cited benchmark source, loader, filtering, task-selection, evaluator call path, and actual completed counts.

If the plan says `synthetic`, `toy`, `debug_subset`, `sample_limit`, `few_shot_fixture`, or a custom task list in a scientific run, stop and revise the campaign. Engineering fixtures must be clearly isolated and cannot appear in benchmark result tables.

### 3. Allocate seeds and conditions

Read [Seed and stage policy](references/seed-policy.md).

- **Pilot:** one run per condition. For `seeded_stochastic`, that means exactly one declared seed; for `uncontrolled_stochastic` APIs, exactly one replicate ID; deterministic conditions run once with no seed. This is a declared screening policy; use results only to detect gross failures or decide whether a condition is worth confirming.
- **Confirmatory:** freeze the condition/config set and a justified seed plan before looking at confirmatory outcomes. Use at least two distinct seeds for seeded stochastic conditions and at least two replicate IDs for uncontrolled stochastic conditions; this floor permits a sample-variance estimate but does not establish adequate power or precision. Justify the actual count from the benchmark protocol or a predeclared analysis. Deterministic conditions run once. Run every planned seed/replicate against the complete official scope.
- Do not rerun a failed attempt in place. Create a new attempt ID, preserve the failure, and record the reason for retry. Retries for one planned run must be sequential, and no attempt may follow a completed attempt; if a successful run must be repeated because its protocol or implementation was invalid, create a corrected campaign/run identity.

### 4. Freeze configs and create the run matrix

Use a stable `condition_id` for each method/configuration and a unique `run_id` for every planned seed/replicate. Hash configs after writing them. Do not edit a config after the first run; a change creates a new config ID/hash and must be added to the protocol before its run.

Set `randomness_mode` on every condition. Never put a fake seed on a deterministic method or an API that does not expose seed control. Use `replicate_id` to distinguish uncontrolled API repetitions. The campaign must enumerate every intended run. Avoid implicit shell loops over undocumented hyperparameter combinations. Validate before packaging:

```bash
python skills/experiment-execution/scripts/preflight_campaign.py experiments/<slug>/campaign.json
```

### 5. Execute remotely and record each attempt

If `$remote-runner-packager` is installed, use it for remote packaging; otherwise follow the repository's remote-run contract directly. Each attempt should record:

- `run_id`, `attempt_id`, `condition_id`, seed or replicate ID, config path/hash;
- separate official and campaign-preflight loader scope hashes, plus observed completed task/example counts;
- the loader-emitted scope manifest for that exact attempt, saved as `results/<run_id>/<attempt_id>/scope-manifests/<scope_id>.json` with its path and SHA-256; a completed attempt must include exactly every required scope, and the audit compares each manifest population with the complete official population;
- source commit, dirty/patch state, environment and hardware; every completed attempt must include a hash-bound environment snapshot at `results/<run_id>/<attempt_id>/environment.json` describing platform, CPU model/count, system memory, accelerator model/count/memory, and exact software versions, using [environment_snapshot.template.json](templates/environment_snapshot.template.json); include exact argv, paths, and hashes for raw hardware probe output under the same attempt directory, and make the ledger hardware object exactly match this snapshot; include the dependency-lock path/hash when available;
- exact command, process start/end time, exit code/status, runtime, stdout/stderr/log paths; `runtime_seconds` must match the start/end interval within the uncertainty implied by each timestamp's recorded precision. Round timestamps to their displayed precision and retain the unrounded runtime value. Timestamps cover actual process execution, not scheduler queue time;
- metrics path/hash and checkpoint path/hash (when a checkpoint is produced);
- checkpoint source/config/seed-or-replicate/step/selection metadata and a retry reason for every attempt after the first;
- failure reason for every non-success status.

Append one JSON object per attempt to `run_ledger.jsonl`. Never delete raw logs or replace rows. Use attempt-specific paths, for example `results/<run_id>/<attempt_id>/` and `checkpoints/<run_id>/<attempt_id>/`.
For each completed run, normalize metrics to `templates/metrics_record.template.json` and keep the raw official evaluator/scorer output as a separate, hash-bound artifact under `results/<run_id>/<attempt_id>/`. If the official evaluator only emits stdout, capture that exact output in the attempt directory. The raw-output artifact must be the source from which the normalized metrics can be checked; do not substitute the normalized metrics file itself. A completed run without this source artifact is incomplete.

### 6. Audit the campaign after runs return

Run:

```bash
python skills/experiment-execution/scripts/audit_campaign.py experiments/<slug>/campaign.json --ledger experiments/<slug>/run_ledger.jsonl
```

The audit checks planned-versus-observed runs, duplicate IDs, seed/replicate/config/commit identity, source patch state, official and per-attempt scope manifests, full task counts, status/timestamp/runtime/retry integrity, environment snapshots, hardware identity, normalized metric-record identity, raw evaluator-output provenance, and result/checkpoint hashes. Runtime must agree with the process start/end interval within the bound derived from the displayed precision of both timestamps plus floating-point representation error; there is no fixed seconds-or-percent allowance. Identity comparisons preserve JSON types (`true` cannot stand in for integer seed `1`), including nested source-state and scope-hash records. A completed attempt must include a hash-bound environment snapshot in `results/<run_id>/<attempt_id>/`; the snapshot must match the run/attempt, list platform and exact software versions, and state CPU, memory, and accelerator inventory. Ledger hardware details must match the snapshot exactly, and the snapshot must point to attempt-local, hash-bound hardware-probe output. These artifacts improve traceability but are not remote hardware attestation; independently inspect the probe output and scheduler allocation before making hardware-dependent claims. A completed attempt cannot satisfy scope integrity by copying only the campaign's preflight hashes or counts: it must provide the actual manifest emitted by that run's loader/evaluation path under `results/<run_id>/<attempt_id>/`, hash-bound and population-matched to the official manifests. Its normalized metrics must reference a separate raw evaluator/scorer output file under the same attempt directory, with a valid hash. The script verifies artifact identity and integrity, not that the reported numbers were correctly derived; inspect or recompute the metric derivation from the preserved output before accepting scientific conclusions. Artifact paths cannot be reused across attempts. Retries must follow the preceding attempt's finish, and a completed attempt ends that run's ledger history. A failure, missing task, changed config, or incomplete artifact keeps the campaign incomplete; it does not get silently dropped from aggregation. It refuses report paths outside the campaign or overwriting an existing report.

If `$result-auditor` is installed, use it to judge scientific validity; otherwise follow the repository's documented review policy and keep claims unapproved until evidence and limitations have been checked. Run a repository result collector only when one exists. Update the experiment analysis, findings, and claim matrix when the repository maintains them; otherwise preserve the campaign audit report and ledger as the execution handoff. This skill tracks execution integrity; it does not infer scientific significance or certify claims.

## Handoff

- Optional from `$experiment-planner`: approved hypothesis, protocol, benchmark choice, baselines, metrics, and decision rule. Without it, take these from the approved protocol and research state.
- Optional to `$codex-experiment-coder`: exact conditions, official benchmark interfaces, config contract, run/result schema, and smoke-test boundary.
- Optional to `$remote-runner-packager`: validated campaign JSON, pinned commit, run matrix, resource estimate, and output paths.
- Optional to `$result-auditor`: complete append-only ledger, full-scope evidence, metrics, logs, configs, checkpoint hashes, and failures. Without it, scientific claims remain unapproved until reviewed under repository policy.

## Definition of done

A campaign is execution-complete only when every planned run/seed has an audited attempt, every successful attempt completed the full official benchmark scope, the official and executed scope identities match, all configs/commits/environments/commands/results/checkpoints are traceable, and every failure or deviation remains visible. Scientific conclusions still require a separate result audit.
