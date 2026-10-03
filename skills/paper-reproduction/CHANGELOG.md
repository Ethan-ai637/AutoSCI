# Changelog

## 1.2.0

Provenance, reconciliation, and execution-boundary hardening.

- Fail preflight when target-run provenance snapshots are incomplete or an execution-defining manifest has since been removed.
- Require metric rows to match their target claim's declared metric; the scalar reconciler ignores mismatched rows and preflight reports them as errors.
- Filter inherited environment variables before running repository code, allow explicit non-secret variables with `--env NAME`, and reject common credential-like names.
- Record the environment variable names visible to each wrapped command and add regression coverage for provenance deletion, cross-metric reconciliation, and environment filtering.

## 1.1.1

Release-gate correctness fixes.

- Fail preflight when a target run has an incomplete provenance snapshot or an execution-defining manifest has since been removed.
- Require metric rows to match their target claim's declared metric; the scalar reconciler ignores mismatched rows and preflight reports them as errors.
- Add regression coverage for deleted provenance manifests and cross-metric reconciliation.

## 1.1.0

Semantic-provenance and release-gate hardening release.

- Bound every target run to SHA-256 snapshots of the reproduction contract, run plan, repository manifest, data/checkpoint manifests, and claim↔code map.
- Added deterministic detection of post-run mutation of execution-defining artifacts.
- Added cross-artifact reconciliation for pinned repository commit, dataset/checkpoint IDs, metric→run→claim linkage, and claim↔code artifact revisions.
- Added reproduction-state eligibility checks: `exact_reproduction` now requires an exact rule, successful target evidence, clean pinned source state, and no material deviation; `within_reported_variation` requires a declared variation/tolerance basis.
- Added `reconcile_claims.py` for non-destructive candidate assessment of simple scalar claims under predeclared exact/tolerance/variation rules.
- Added dimension-level `audit_repo_readiness.py` and `repository_readiness.schema.json` without an aggregate reproducibility score.
- Added PAPER_ONLY assumption-to-implementation decision checks for assumption-required underspecifications.
- Added semantic regression tests for post-run contract mutation, unknown checkpoint references, ineligible exact-reproduction labeling, and candidate reconciliation behavior.
- Expanded semantic provenance/release guidance in `references/06-semantic-provenance-and-release.md`.

## 1.0.0

Initial AutoSCI design release.

- Added three modes: `REPO_REPRODUCE`, `PAPER_ONLY`, and `REPO_AUDIT`.
- Added claim-first reproduction contract.
- Added paper↔code traceability contract.
- Added conservative repository identity and paper-era revision selection rules.
- Added source-vs-resolved environment separation.
- Added external data/checkpoint provenance requirements.
- Added smoke-before-target execution rule.
- Added append-only run ledger semantics.
- Added claim-scoped reproduction states and conservative reporting language.
- Added conservative remote repository acquisition, repository inspection, environment capture, hashing, execution provenance, preflight, release, and freeze tooling.
- Added workspace templates and schemas.
- Added standard-library regression tests for initialization, clean run provenance, and dirty-worktree protection.
