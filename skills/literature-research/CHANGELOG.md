# Changelog

## 1.6.1 — 2026-09-29

Screening-integration patch driven by the v1.6 rerun of the same real-world review case.

- Centralized deterministic screening-rule activation so disabled rules are consistently ignored by preview, append-log, and preflight paths.
- Added conservative automatic publication-type exclusion rules derived only when those publication types are literally named in `protocol.exclusion_criteria`; no semantic task exclusions are inferred.
- `apply_screening_rules.py` now uses explicit + derived-safe rules by default, records rule source, and can disable derivation with `--no-derived-safe-rules`.
- Preflight uses the same rule set, so obvious structured publication-type exclusions cannot remain `uncertain` merely because `deterministic_exclusion_rules` was left empty.
- `synthesis_claims.csv` now carries persisted `verification_coverage`, verified/partial evidence counts, and eligible support/contradiction unit counts.
- `audit_synthesis.py --update-claims` materializes those derived metrics after a passing audit; preflight checks persisted values against current evidence/links and warns when they are absent for backward-compatible v2 workspaces.
- Kept workspace schema v2 compatible: the new synthesis columns are additive rather than newly required, so existing v1.6.0 workspaces still validate and can be upgraded in place.
- Added regression coverage for derived-safe publication-type exclusions, disabled-rule consistency, and synthesis-metric persistence.

## 1.6.0 — 2026-09-29

Real-world retrieval and screening correctness iteration, driven by the first full standard-workflow case study.

- Added workspace schema v2 (`schemas/workspace-v2.json`) while retaining v1 validation support.
- Search logs now distinguish `succeeded`, `partial`, and `failed` query execution; source coverage separately reports not-attempted, failed, partial/unknown, and succeeded protocol targets.
- Added `new_screened_count`, `stopping_evidence`, and stopping-rule verifiability. Missing marginal-yield data now produces `not_assessable` rather than an implicit saturation pass.
- Split screening semantics into `title_abstract`, `full_text_attempted`, and `full_text_screened`, with explicit `access_level`; legacy `stage=full_text` is treated as ambiguous and cannot silently satisfy a full-text requirement.
- `reconcile_screening.py` now preserves final decision stage separately from `evidence_stage` and highest access level, and reports legacy ambiguous full-text events.
- Added protocol-level `deterministic_exclusion_rules` plus `apply_screening_rules.py` for high-precision mechanical exclusions; preflight rejects final `uncertain` records that still match an enabled explicit exclusion rule.
- `audit_synthesis.py` now reports per-claim verification coverage (`complete`, `mixed`, `partial_only`, `not_applicable`) without changing the scientific evidence state; the deterministic synthesis brief surfaces the same limitation.
- `build_flow_report.py` now reports search execution status, `new_screened_count`, screening evidence-stage counts, and access-level counts.
- Migration to v2 is preview-first, adds structural fields without scientific inference, and explicitly refuses to reinterpret legacy `full_text` events as completed full-text screening.
- Expanded self-tests with failure-driven regressions for failed-source coverage, non-verifiable stopping rules, pseudo-full-text screening, and explicit-exclusion-vs-uncertain conflicts.
- Preserved Python-standard-library-only operation.

## 1.5.0 — 2026-09-29

Workspace compatibility and migration iteration.

- Added machine-readable `schemas/workspace-v1.json` defining minimum compatible CSV columns and JSON keys while permitting extensions.
- `init_review_artifacts.py` now creates `review/workspace_meta.json` with explicit workspace-schema identity, creating skill version, timestamp, and migration history.
- Added `validate_workspace.py` for structural validation that is deliberately separate from scientific preflight/semantic audits.
- Added preview-first `migrate_workspace.py`; `--apply` preserves existing values, appends missing structural columns as blanks, backs up rewritten files, records migration history, and never invents scientific judgments.
- Snapshot manifests now record workspace-schema identity and freeze `workspace_meta.json` / `schema_audit.json` when present.
- Versioned workspaces now require a passing schema audit before frozen snapshot creation or downstream handoff.
- Handoff manifests carry workspace-schema identity so downstream consumers can reject or migrate unsupported structures explicitly.
- Expanded self-tests for schema validation, legacy migration, and deterministic rejection of structural drift.
- Preserved Python-standard-library-only operation.

## 1.4.0 — 2026-09-29

Downstream interoperability and structured-handoff iteration.

- Added `build_evidence_graph.py` to serialize report, study, evidence-claim, synthesis-claim, verified citation/version, and optional topic-cluster relationships without inferring missing edges.
- Added `build_synthesis_brief.py` to render the audited claim ledger into human-readable Markdown while introducing no new scientific claims.
- Added `build_handoff_bundle.py` to package audited review artifacts for generic, `scientific-figure`, or `academic-research-presentation` downstream workflows; frozen handoffs re-verify the snapshot before packaging.
- Added `references/downstream_handoff.md` with routing, copyright, and provenance boundaries.
- Snapshot manifests now include `review/evidence_graph.json` and `review/synthesis_brief.md` when present, so downstream views are frozen with the review milestone.
- Added downstream routing guidance that preserves caveats/evidence states and forbids turning narrative extraction into quantitative plots without authoritative numeric data.
- Expanded self-tests to validate graph construction, deterministic brief rendering, snapshot coverage, and handoff packaging.
- Preserved Python-standard-library-only operation.

## 1.3.0 — 2026-09-29

Reproducibility, count-reconciliation, and synthesis-evidence eligibility iteration.

- Added protocol identity metadata (`protocol_id`, `protocol_version`, `created_at`) and structured protocol-change validation for reproducible handoff.
- Added `build_flow_report.py` to reconcile search, deduplication, screening, study, evidence, and synthesis counts without falsely claiming PRISMA completeness.
- Added `snapshot_review.py` to freeze standard workspace artifacts with SHA-256 hashes plus the exact skill-package digest.
- Added `verify_snapshot.py` to detect changed/missing artifacts or a different skill implementation after handoff.
- Added `references/reproducibility_and_flow.md` for archival, living-review update, and count-reporting guidance.
- Tightened synthesis semantics: only `direct`/`derived` evidence with `verified`/`partial` verification can count as substantive support or contradiction.
- `consistent` now requires >=2 eligible independent supporting units and rejects eligible contradictory units.
- `mixed` now requires eligible support and contradiction rather than merely any linked relations.
- `gap`, `single_study`, and `single_source` states now receive stronger substantive-evidence checks.
- Expanded regression tests to reject context-only/unverified false convergence and to detect post-snapshot workspace edits.
- Preserved Python-standard-library-only operation.

## 1.2.0 — 2026-09-29

Study-identity and independence iteration.

- Added explicit report-level `record_id` versus underlying-study `study_id` modeling.
- `init_review_artifacts.py` now creates conservative one-report-per-study provisional mappings in `study_map.csv`.
- Added `references/study_identity.md` with linkage standards and report-role semantics.
- Added `audit_studies.py` to validate report-to-study mappings, cross-check `same_study_version` citation edges, verify evidence study IDs, and emit study-level summaries.
- Added `study_id` to the evidence-table schema so claim provenance reaches the independent-study layer.
- Made synthesis auditing study-aware with optional `--study-map`; `consistent` evidence now requires at least two distinct studies when study identity is available.
- Added `single_study` synthesis state while retaining `single_source` for legacy/report-level analyses.
- Strengthened preflight to require a study map in standard/systematic workflows and detect false independence from multiple reports of one study.
- Expanded counts to distinguish included reports from included underlying studies.
- Preserved Python-standard-library-only operation.

## 1.1.0 — 2026-09-29

Auditability and provenance iteration.

- Added expanded search-log schema with search stage, concept coverage, interface, imported count, new unique count, and new included count.
- Added `audit_search.py` to verify protocol target-source coverage, query IDs, concept tags, and systematic-profile reproducibility fields.
- Added append-only `screening_log.csv` for multi-stage/multi-reviewer screening.
- Added `reconcile_screening.py` to derive the final screening snapshot and surface unresolved same-stage reviewer conflicts instead of overwriting them.
- Expanded final screening schema with reviewer, decision-basis, and conflict-status provenance.
- Upgraded evidence rows with source version, support level, verification status, and stable claim IDs.
- Added normalized `synthesis_claims.csv` + `synthesis_evidence.csv` so cross-paper conclusions remain linked to evidence claim IDs.
- Added `audit_synthesis.py` for claim-link integrity and basic consistency checks on `consistent`, `mixed`, `single_source`, and `gap` synthesis states.
- Strengthened cross-artifact preflight checks for PMCID duplication, reviewer conflicts, evidence from excluded records, missing evidence for included records, target-source coverage, and synthesis provenance.
- Preserved Python-standard-library-only operation.

## 1.0.0 — 2026-09-29

Initial public version.

- Added protocol-first exploratory, standard, and systematic profiles.
- Added layered search workflow with reproducible search logging.
- Added deterministic record normalization and conservative deduplication.
- Added explicit screening decisions and exclusion reason codes.
- Added deterministic candidate topic clustering with TF-IDF similarity.
- Added evidence-table and citation-trail schemas.
- Added citation-trail audit and DOT export.
- Added cross-artifact preflight QA.
