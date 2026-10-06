# Campaign Schema Migration

## Campaign schema 1.0 to 1.1

Campaign schema 1.1 requires a prelaunch `resource_plan` containing:

- `accelerator`: the intended hardware class;
- `memory_gb` and `storage_gb`: finite positive estimates;
- `expected_runtime_hours`: a finite positive estimate;
- `estimate_basis`: a concise evidence-based explanation, such as a comparable full-scope run, benchmark throughput, or documented model/data size calculation.

Set `schema_version` to `1.1` only after adding those fields and the dirty-source snapshot fields required by the current campaign template. Do not invent estimates to pass preflight. If the full benchmark resource estimate is unknown, gather a valid full-scope estimate or leave the campaign blocked before launch.

## Campaign schema 1.1 to 1.2

Campaign schema 1.2 requires `decision_thresholds`. Inspect the approved protocol, research goals, and decision rules; add every numeric pass/fail, continue/stop, success, or prioritization threshold with its value, operator, unit, evidence class, source reference, exact locator, applicability, and derivation. Use an empty array only when no numeric decision threshold is planned. Do not infer missing thresholds from outcomes or silently adopt values from unrelated domains. If no source supports a proposed threshold, remove it or keep the decision blocked until it is justified. A one-seed confirmatory run is valid by default; repeat runs are optional unless the official benchmark or planned statistical claim requires them. If adding repeats to estimate variation, state the basis in `seed_policy.additional_runs_basis`; if searching seeds for a high score, classify and report it as optimization/selection rather than confirmatory evidence. Rename a prior `confirmatory_basis` value to `additional_runs_basis` only when it justified actual repeat runs; no repeat basis is required for a single seed.

Set `schema_version` to `1.2` only after auditing the protocol and populating `decision_thresholds`. Existing campaign schema 1.1 files must be explicitly migrated; adding an empty list without checking protocol thresholds is not a complete migration.

## Attempt records

Run-record rows continue to use schema version `1.0`. Every ledger row must include `schema_version: "1.0"`; the audit rejects missing or unknown versions. The audit requires `runtime_seconds` to match the `started_at`/`finished_at` interval within a bound derived from the two serialized timestamps' displayed precision and floating-point representation error. The former fixed `max(5 seconds, 2% of elapsed time)` allowance is retired because it was not grounded in a measurement standard. For older records whose timestamps cannot support this precision check, recover precise values only from preserved logs or scheduler records; never alter times merely to pass the audit. Metrics records, environment snapshots, and source snapshot manifests retain their own independent schema versions.

## Metrics record 1.0 to 1.1

Metrics record 1.1 requires `raw_evaluator_output_path` and `raw_evaluator_output_sha256` to point to a separate raw evaluator/scorer output file under `results/<run_id>/<attempt_id>/`. Capture exact evaluator stdout when no file is emitted. Backfill only from preserved original outputs; do not invent or reconstruct a raw-output artifact from normalized metric values. If the original output is unavailable, leave the attempt incomplete and rerun it under a new attempt identity when appropriate. The campaign and ledger schema versions are unchanged; update each metrics record's `schema_version` to `1.1` only after the provenance fields are complete.

## Environment snapshot 1.0 to 1.1

Environment snapshot 1.1 requires observed hardware inventory: CPU model, logical CPU count, system memory in bytes, and an accelerator list (empty for CPU-only runs). Each accelerator records kind, model, device count, and per-device memory in bytes when reported; use `null` only when the platform does not report per-device memory. `hardware_evidence` must cite one or more exact probe commands and attempt-local raw output files with SHA-256 hashes. The completed attempt's ledger `hardware` object must match this hash-bound snapshot exactly. Capture values from the actual execution host, not the campaign resource estimate. These files are not hardware attestation; compare them with scheduler allocation before hardware-dependent claims. Existing 1.0 snapshots do not satisfy this gate; recover from preserved host evidence or leave the attempt incomplete rather than guessing.
