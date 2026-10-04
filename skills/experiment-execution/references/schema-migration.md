# Campaign Schema Migration

## Campaign schema 1.0 to 1.1

Campaign schema 1.1 requires a prelaunch `resource_plan` containing:

- `accelerator`: the intended hardware class;
- `memory_gb` and `storage_gb`: finite positive estimates;
- `expected_runtime_hours`: a finite positive estimate;
- `estimate_basis`: a concise evidence-based explanation, such as a comparable full-scope run, benchmark throughput, or documented model/data size calculation.

Set `schema_version` to `1.1` only after adding those fields and the dirty-source snapshot fields required by the current campaign template. Do not invent estimates to pass preflight. If the full benchmark resource estimate is unknown, gather a valid full-scope estimate or leave the campaign blocked before launch.

## Attempt records

Run-record rows continue to use schema version `1.0`. Every ledger row must include `schema_version: "1.0"`; the audit rejects missing or unknown versions. The audit also requires `runtime_seconds` to match the interval between process `started_at` and `finished_at`, within max(5 seconds, 2% of elapsed time). For older records with insufficient timestamp precision, recover timestamps/runtime only from preserved logs or scheduler records; never alter times merely to pass the audit. Metrics records, environment snapshots, and source snapshot manifests retain their own independent schema versions.

## Metrics record 1.0 to 1.1

Metrics record 1.1 requires `raw_evaluator_output_path` and `raw_evaluator_output_sha256` to point to a separate raw evaluator/scorer output file under `results/<run_id>/<attempt_id>/`. Capture exact evaluator stdout when no file is emitted. Backfill only from preserved original outputs; do not invent or reconstruct a raw-output artifact from normalized metric values. If the original output is unavailable, leave the attempt incomplete and rerun it under a new attempt identity when appropriate. The campaign and ledger schema versions are unchanged; update each metrics record's `schema_version` to `1.1` only after the provenance fields are complete.

## Environment snapshot 1.0 to 1.1

Environment snapshot 1.1 requires observed hardware inventory: CPU model, logical CPU count, system memory in bytes, and an accelerator list (empty for CPU-only runs). Each accelerator records kind, model, device count, and per-device memory in bytes when reported; use `null` only when the platform does not report per-device memory. `hardware_evidence` must cite one or more exact probe commands and attempt-local raw output files with SHA-256 hashes. The completed attempt's ledger `hardware` object must match this hash-bound snapshot exactly. Capture values from the actual execution host, not the campaign resource estimate. These files are not hardware attestation; compare them with scheduler allocation before hardware-dependent claims. Existing 1.0 snapshots do not satisfy this gate; recover from preserved host evidence or leave the attempt incomplete rather than guessing.
