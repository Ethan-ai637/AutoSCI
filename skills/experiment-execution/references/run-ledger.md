# Run, Checkpoint, and Result Ledger

## IDs and immutability

Assign a stable `condition_id` to a method/configuration and a unique planned `run_id` to each condition × seed. Every launch/retry gets a unique `attempt_id`. Keep IDs in filenames and ledger rows. A retry never overwrites the prior attempt.

Hash each config before launch and record its relative path and SHA-256. A changed config, code patch, source commit, or benchmark revision is a different run condition and must be represented explicitly in the protocol/campaign.

Prefer a clean committed source tree. If it is dirty, preserve both the reviewable Git patch and `source_snapshot_path`/`source_snapshot_sha256`: a ZIP of the complete runnable source state, including untracked files, with `source-manifest.json` at its root. Use `schemas/source_snapshot_manifest.schema.json` and `templates/source_snapshot_manifest.template.json`; list every other archive file once with its relative path and SHA-256, and set `base_commit` to the campaign's full `source_commit`. Preflight checks archive membership, per-file hashes, and base commit. Before launch, compare the manifest with `git status` and make sure no untracked or ignored execution file was omitted. Do not include datasets/checkpoints when they are separately hash-bound by the benchmark and run artifacts; document exclusions that can affect execution.

## Append-only attempt records

Keep one JSON object per attempt in `run_ledger.jsonl`. Each record must carry the `schema_version` declared by `schemas/run_record.schema.json`; the audit rejects missing or unknown versions rather than guessing how to interpret fields. Record status (`completed`, `failed`, `interrupted`, `oom`, or `cancelled`), exact argv, source commit and dirty/patch/snapshot state, seed or replicate ID, config hash, official scope hashes, observed counts, environment, hardware, ISO-8601 timestamps/runtime, logs, metrics, checkpoint metadata, and artifact hashes. `started_at` and `finished_at` bracket process execution, excluding scheduler queue time; round timestamps to their displayed precision and retain unrounded `runtime_seconds`. The audit derives the allowed timestamp/runtime discrepancy from the actual timestamp precision; see [threshold rationale](threshold-rationale.md). Every retry after the first attempt for a run must include a `retry_reason`. Use `templates/run_record.template.json` as the field contract.

For every completed attempt, save the actual loader/evaluator-emitted scope manifest at `results/<run_id>/<attempt_id>/scope-manifests/<scope_id>.json` and record each required scope's relative path and SHA-256 in `observed_scope_manifests`. Do not reuse only the campaign's preflight manifest as evidence of what a specific run consumed. The campaign audit verifies each attempt manifest's path, hash, structure, scope ID, unit count, and exact population against the full official manifest. Artifact paths cannot be reused across attempts. Failed attempts may record partial manifests when the loader emitted them; they do not count as complete runs.

Every completed attempt also records a hash-bound environment snapshot at `results/<run_id>/<attempt_id>/environment.json`, linked in the `environment` ledger field. Use `schemas/environment_snapshot.schema.json` and `templates/environment_snapshot.template.json`; include the attempt identity, operating system, architecture, CPU model/logical core count, system memory in bytes, accelerator kind/model/count/per-device memory, and exact versions of relevant runtimes/frameworks/packages. Record an empty accelerator list for CPU-only execution. Include exact argv, path, and SHA-256 for raw hardware-probe outputs under the same attempt directory; probes should establish the CPU, memory, and accelerator values stated in the snapshot. The ledger `hardware` object must match the snapshot exactly. These outputs are traceable host reports, not cryptographic attestation; cross-check them against scheduler allocation before hardware-dependent claims. Capture the actual environment at execution time; do not copy planned versions from the protocol as if observed. Include a path and SHA-256 for the dependency lock or immutable environment definition when available. Failed attempts may leave this reference null if execution never reached environment capture.

Do not delete a failed attempt just because a retry succeeded. Retries for the same planned run are sequential: the next attempt must start no earlier than the prior attempt's finish, and every retry needs a reason. A completed attempt is terminal; no later attempt may be appended to that run. If a completed run must be repeated because its protocol or implementation was invalid, correct the protocol and create a new campaign/run identity instead of keeping the earlier success in the same run history. Do not reuse an output directory. Store immutable attempt paths, for example:

```text
results/<run_id>/<attempt_id>/metrics.json
results/<run_id>/<attempt_id>/run.log
checkpoints/<run_id>/<attempt_id>/model.ckpt
```

## Checkpoints

Declare whether a condition needs no checkpoint, an optional checkpoint, or a required checkpoint. Predeclare a selection rule whenever a checkpoint may be recorded. Record the checkpoint path, SHA-256, source commit, config hash, seed/replicate, training step/epoch, and selection rule. Never overwrite a checkpoint or silently choose a later/better checkpoint after seeing evaluation results. Apply the benchmark/paper's declared checkpoint selection rule; if none exists, select it on the official validation procedure and keep the test set for the declared evaluation.

## Results and aggregation

Normalize each completed output with `templates/metrics_record.template.json` and validate against `schemas/metrics_record.schema.json`. Metrics record schema 1.1 requires a separate, hash-bound raw evaluator/scorer output artifact under the same attempt directory. Capture exact evaluator stdout when no file is emitted. This artifact is the source from which normalized metrics can be checked; the normalized metrics file cannot serve as its own source. A completed run without this artifact remains incomplete. Preserve per-run metrics. Aggregate only the predeclared seed/replicate set and protocol. Include incomplete/failed counts in the audit; do not silently omit them from tables. Let `$result-auditor` assess scientific validity before updating findings or manuscript claims.

The campaign audit verifies paths and hashes, planned-run coverage, identity, per-attempt full-scope manifests/counts, and output artifacts. It validates normalized metric-record identity, benchmark/suite, counts, and numeric values, but cannot validate the scientific meaning of a metric or prove that a custom code path is equivalent to the official evaluator.
