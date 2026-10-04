# Changelog

## 1.10.0

- Make companion skills optional so the campaign workflow remains usable when installed by itself.
- Add standalone fallbacks that rely on the approved protocol, this skill's campaign tooling, and repository result-review policy without assuming a project-specific result collector or findings layout.

## 1.9.0

- Upgrade environment snapshots to schema 1.1 with observed CPU, memory, and accelerator inventory.
- Require the ledger hardware record to match the hash-bound environment snapshot exactly.
- Require attempt-local, hash-bound raw hardware-probe outputs and document that they are not cryptographic attestation.
- Document migration for earlier snapshots without hardware provenance.

## 1.8.0

- Reject attempt records whose declared runtime differs from the process start/end timestamp interval by more than max(5 seconds, 2% of elapsed time).
- Clarify that attempt timestamps measure process execution rather than scheduler queue time.

## 1.7.0

- Upgrade normalized metrics records to schema 1.1 and require a distinct hash-bound raw evaluator/scorer output for every completed attempt.
- Require the source output to live inside its attempt directory; capture exact evaluator stdout when the evaluator does not emit a file.
- Add a migration path that keeps completed attempts incomplete when their original metric source is unavailable.

## 1.6.0

- Compare JSON identity fields recursively with exact types, so a boolean cannot impersonate an integer seed in attempt, metrics, or checkpoint records, or pass as an integer nested in source-state or scope-hash records. Scope counts already had an explicit Boolean rejection.

## 1.5.0

- Upgrade the campaign contract to schema 1.1 and require an explicit resource plan.
- Fail preflight when accelerator/estimate basis is missing or runtime, memory, or storage is non-positive, non-finite, or not numeric.
- Add a migration note for earlier campaign contracts.

## 1.4.0

- Make campaign preflight reject unsupported or missing campaign schema versions.
- Require every run-ledger row to carry a supported schema version and reject unknown/missing versions during audit.

## 1.3.0

- Require dirty-source campaigns to preserve a hash-bound ZIP snapshot and reviewable patch.
- Verify the source snapshot manifest, base commit, archive membership, and per-file hashes during preflight.
- Document a manual working-tree comparison so untracked execution files are not omitted from the snapshot.

## 1.2.0

- Require hash-bound per-attempt environment snapshots for completed runs, including platform and exact software versions.
- Validate snapshot identity and structure; verify an optional dependency-lock artifact when supplied.
- Include the environment snapshot artifact in attempt-level path uniqueness checks.

## 1.1.0

- Bind every completed attempt to its own loader-emitted full-scope manifests and reject reused artifact paths.
- Enforce sequential retries and make a completed attempt terminal within a run history.
- Include raw evaluator outputs in attempt-level artifact path uniqueness checks.
- Tighten attempt provenance and anti-overwrite audit gates.

## 1.0.0

- Initial versioned release baseline for the complete-benchmark campaign workflow, staged seed policy, immutable run ledger, and provenance audit.
