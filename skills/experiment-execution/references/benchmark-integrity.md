# Benchmark Integrity

## What “full benchmark” means

Use the benchmark's complete, official evaluation scope for the named benchmark/version: all required official tasks/examples and the split protocol that the benchmark specifies for the research question. Official train/validation/test splits are part of the protocol; selecting a hand-picked fraction of a required split is not. A benchmark may publish named tracks or variants. Use one only when it is an official, independently specified track and the campaign runs that entire track; do not create a local “easy/low/small” variant by selecting cases.

The campaign protocol must identify required scopes before execution. Normalize each official scope to a JSON manifest with `scope_id` and either a unique `unit_ids` list or an `artifacts` list containing immutable artifact IDs, SHA-256 hashes, and unit counts. Use sample/task IDs when practical; for large datasets, shard/file identities avoid materializing millions of example IDs. Record a reviewable official source URL, revision, and code/document locator for every scope. Retain an execution manifest emitted by the actual loader/evaluation path; it must enumerate the same population. Preflight checks structure, duplicates, counts, hashes, and identity. A self-authored list can still falsely claim to be official: independently inspect the cited benchmark source and code path before accepting preflight as valid.

## Forbidden shortcuts in scientific runs

- `limit`, `max_examples`, `take`, random sampling, task allowlists, class filters, hand-selected seeds of tasks, omitted failures, reduced image resolution, shortened context, or fewer episodes unless the benchmark's official protocol itself requires that exact setting.
- Synthetic/generated rows, labels, tasks, or benchmark replacements used as scientific evaluation data.
- A home-built replacement for an available official dataset loader, baseline implementation, metric, or evaluation harness.
- Reporting an engineering fixture, dry-run, smoke test, incomplete run, or benchmark subset as benchmark performance.

If the benchmark officially requires preprocessing, augmentation, or generated intermediate artifacts, follow and cite that exact protocol. Such artifacts do not authorize changing the official input population or evaluation scope.

## Data integrity gate

Before coding or launching a campaign, record:

1. benchmark name, version/release, canonical source, official code revision, and named track/suite;
2. official split/task manifests and their hashes, counts, and license/access constraints;
3. the official loader, evaluator, and metric entrypoints used by the run;
4. the matching execution-scope manifests and how the run will expose observed counts;
5. any required preprocessing and its benchmark-specified parameters.

Pin `official_code_revision` to a full 40- or 64-character commit SHA. If the official implementation is distributed only as a versioned archive/package, preserve that exact source archive inside the campaign and record its SHA-256; mutable refs such as `main`, `master`, or `latest` alone are not reproducible pins.

The preflight script checks the declared scope and hashes. The experiment owner must verify benchmark authenticity and code-path behavior; do not treat a self-authored manifest or a passing static check as proof of official compliance.

## If the full run is infeasible

Do not downsample to make the job fit. Stop before scientific execution, record a resource blocker with a full-scope cost estimate, and use a no-data dry-run to validate command/config plumbing. Then wait for resources or ask the user to authorize a different scientific question/scope. A scope change requires a new protocol and campaign identity before the run.
