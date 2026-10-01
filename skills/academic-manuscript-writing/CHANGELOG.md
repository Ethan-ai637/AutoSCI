# Changelog

## 2.0.0 — 2026-10-01

- Introduced a dynamic writing-profile architecture that separates stable scientific governance from time-sensitive discipline/article-type/track/venue/year/submission-stage writing rules.
- Added `project.json.writing_context` and `writing_profile_policy`; new workspaces can target `generic`, `discipline`, or `venue` specificity without hard-coding any conference/journal rules into the skill.
- Added `writing_sources.jsonl` for runtime author-guideline/template/checklist provenance, explicitly separated from scientific `sources.jsonl` / `evidence.jsonl`.
- Added `writing_profile.json` to normalize source-backed writing constraints, readiness, and writing-guideline conflicts.
- Added hash-bound `manuscript_contract.json` for required/optional/forbidden sections, rule provenance, generic machine checks, manual checks, and unresolved writing items.
- Added explicit `scientific_roles` on contract sections so venue headings such as `Evaluation` or combined sections can still participate in results/methods/discussion semantics without hard-coded section names.
- Manual venue-compliance checks now carry `pending|verified|not_applicable|blocked` status; venue-specific release cannot pass with pending/blocked manual checks.
- Added `audit_writing_profile.py`; venue-specific release now validates official/publisher/society authority, target venue/year/article-type/track/stage applicability, retrieval provenance, constraint verification, guideline conflicts, readiness, profile/contract context agreement, contract freshness, required/forbidden sections, section order, configured word limits, and alignment with `section_plan.json` / `coverage_policy`.
- Added machine-readable schemas for writing sources, writing profiles, and manuscript contracts.
- Added writing sources/profile/contract to semantic state, fingerprints, impact review, and revise/refresh change-provenance governance; revision rows can now declare `writing_source_ids`.
- Added `references/20-dynamic-writing-profile.md` and `references/21-manuscript-contract.md`; repurposed the legacy journal-style reference as a v2 compatibility note.
- Added offline deterministic `examples/dynamic-writing-profile/` using a clearly fictional `ExampleConf` and a noncanonical `Evaluation` results-role section, plus destructive tests for missing official authority, stale contract hashes, context/article-type/track/stage mismatch, missing required sections, and pending manual checks.
- Preserved pre-v2 compatibility: historical workspaces without v2 writing-profile artifacts continue to use their existing manuscript contracts and release semantics.

## 1.8.2 — 2026-10-01

- Fixed the GitHub-readiness compatibility mismatch where v1.8.1 documented Python 3.8+ support but `scripts/self_test.py` used Python 3.9/3.10-only annotation syntax.
- Reworked self-test annotations to `typing.List` / `typing.Optional` / `typing.Tuple` forms that parse on Python 3.8.
- Added a deterministic Python-3.8 grammar check (`ast.parse(..., feature_version=(3, 8))`) for every script so future releases cannot silently raise the runtime syntax floor.
- Added the syntax-floor check to testing/stability/release documentation and distinguished grammar compatibility from interpreter-level CI support.
- Scientific manuscript governance is unchanged from v1.8.1.

## 1.8.1 — 2026-10-01

- Added `scripts/self_test.py` as a single reproducible package-health entry point using only the Python standard library.
- Quick self-test covers representative v1.5/v1.6/v1.7/v1.8/v2.0 release fixtures; full mode runs every packaged positive fixture plus destructive exact-span mutations that must fail release, with `--shard INDEX/TOTAL` support for CI matrices.
- Added version-synchronization, JSON/JSONL parse, clean-workspace initialization, and generated-artifact hygiene checks so packaged health is independently verifiable outside the development conversation.
- Added `TESTING.md` with source-tree/ZIP smoke-test guidance, `STABILITY.md` with supported guarantees/known boundaries, and `RELEASE_CHECKLIST.md` with AutoSCI GitHub integration requirements.
- Added a README for the historical minimal fixture and documented that older example `skill_version` values are intentional compatibility tests.
- No scientific claim, provenance, span, conflict, or revision-governance semantics changed from v1.8.0.

## 1.8.0 — 2026-10-01

- Added exact claim-span traceability with paired `<!-- CLAIM:<id> --> ... <!-- END-CLAIM:<id> -->` markers for v1.8 workspaces.
- Added claim fields `anchor_precision=span|paragraph` and `span_exemption_reason`; new v1.8 claim templates default to exact spans.
- Added configurable `claim_span_policy` with governed sections/claim types, exemption control, uncovered-prose tolerance, exact text matching, and reverse-reference enforcement.
- Added `audit_claim_spans.py` to verify exact span-to-ledger text synchronization, span-local required numeric tokens, citation ownership, figure/table ownership, non-overlap, and visible prose that falls outside governed claim spans.
- Added span-level reverse citation/object closure so a citation or figure/table reference declared by another claim in the same paragraph can no longer satisfy the wrong claim.
- Added material uncovered-prose detection inside governed sections; `SPAN-COVERAGE:EXEMPT` remains available for explicit structural exceptions, while existing `COVERAGE:EXEMPT` blocks are respected.
- Kept pre-v1.8 workspaces backward compatible: projects with `skill_version < 1.8` and no `claim_span_policy` retain paragraph-anchor behavior.
- Added `examples/span-traceability/` and `references/19-claim-span-traceability.md`.
- Integrated the new span audit into deterministic preflight after claim atomicity and before manuscript consistency.
- Upgraded `revision_diff.py` to schema v4 with exact-span comparison for v1.8 claims and automatic paragraph fallback for historical baselines without end markers, preventing neighboring same-paragraph claims from being falsely marked changed.

## 1.7.2 — 2026-10-01

- Closed the remaining cross-side numeric provenance loophole for `disclose_and_scope` conflicts.
- Added `cross_side_numeric_exceptions` with `derived` / `context` roles, reasons, and contributing side IDs.
- Release now rejects undeclared numeric tokens inside cross-side disclosure claims.
- The same closure is checked against the anchored manuscript paragraph, while allowing numbers contributed by other registered claims in that paragraph.
- Preserved backward compatibility: v1.7/v1.7.1 conflict records without `conflict_sides` retain their previous behavior.
- Fixed escaped-newline formatting in the source-conflict reference introduced in v1.7.1.

## 1.7.1 — 2026-09-30

- Strengthened `disclose_and_scope` with optional `conflict_sides` records that bind each competing provenance stream to explicit source/evidence/value tokens and attribution tokens.
- Added `cross_side_claim_ids` so only designated disclosure claims may intentionally represent more than one conflict side.
- Release now requires ordinary scoped claims to resolve to exactly one conflict side when `conflict_sides` is used, preventing silent blending of competing source/evidence streams.
- Cross-side disclosure claims must be active manuscript disclosure claims, represent at least two sides, and visibly attribute each represented side.
- Extended the project schema and conflict-disposition example; legacy v1.7 conflict records without `conflict_sides` remain valid and retain their existing behavior.
- Added destructive tests for multi-side scoped claims, missing side attribution, and fake cross-side disclosure.

## 1.7.0 — 2026-09-30

- Replaced the v1.6 all-or-nothing unresolved-conflict release gate with explicit source-conflict disposition auditing: `blocking`, `disclose_and_scope`, `historical_only`, and `resolved`.
- Added `audit_source_conflicts.py`; legacy string conflicts remain conservatively blocking, while `disclose_and_scope` requires active scoped/disclosure claims, bidirectional `source_conflict_ids`, and optional literal disclosure tokens.
- Added claim-level `source_conflict_ids` and `atomicity_exemption_reason` fields.
- Added `audit_claim_atomicity.py` and configurable `claim_atomicity_policy` to detect obvious high-risk compound propositions in result/method/limitation claims while protecting parenthetical statistical bundles.
- Upgraded `revision_diff.py` to schema v3 with prose-token similarity, paragraph-preservation fraction, per-section similarity, title change, and changed-section metrics.
- Added `audit_revision_locality.py` and `revision_policy` to prevent targeted manuscript revisions from silently becoming global reconstructions/audit reports; explicit verified authorization is required for global rewrites.
- Added deterministic detection of common workflow/meta-writing phrases in release manuscripts (`this refresh`, `supplied methods notes`, `allowed sources`, etc.) when revision preservation policy is active.
- Made `project.json` a governed semantic artifact for revise/refresh provenance coverage, so conflict-disposition/policy edits participate in state-bound revision verification.
- Added references 16–18 covering source-conflict disposition, claim atomicity, and revision locality/manuscript preservation.
- Regression-tested v1.6 minimal/full-release/paragraph-composition/revision-lifecycle examples and destructive-tested conflict disposition, compound claims, title/global rewrites, and audit-report-style prose.

## 1.6.0 — 2026-09-30

- Added `paragraph_contracts.jsonl` plus `audit_paragraph_composition.py` to make multi-claim prose an explicit auditable composition layer over claim-level evidence grounding.
- Release paragraphs containing two or more active claims now require exactly one `PARAGRAPH:<id>` marker and a matching contract whose `claim_ids` exactly match the manuscript paragraph.
- Added composition contracts for `additive`, `comparison`, `contrast`, `qualified`, `result_interpretation`, `synthesis`, and `method_context` paragraphs.
- Added claim-level `required_companions` with `same_paragraph`, `same_section`, and `manuscript` scopes so material qualifiers/limitations cannot silently disappear while a stronger claim remains.
- Added optional literal `required_text_tokens` and `forbidden_terms` for high-value paragraph-level release invariants.
- Added paragraph contracts to semantic state/fingerprints/change-provenance governance and release handoff; pre-v1.6 archived state IDs remain stable when the new optional ledger is absent.
- Added `examples/paragraph-composition/` and `references/15-paragraph-composition-and-companions.md`.

## 1.5.0 — 2026-09-30

- Added `audit_manuscript_coverage.py` for bidirectional ledger-to-manuscript and manuscript-to-ledger/source closure.
- Added claim-level `manuscript_presence=required|optional|not_in_manuscript` plus an explicit reason for intentional exclusion.
- Multi-section/full release work now fails when a core active claim intended for the manuscript has no anchor.
- Covered Abstract/Methods/Results/Discussion/Conclusion prose paragraphs now require an active claim anchor unless an allowed, reasoned `COVERAGE:EXEMPT` marker is present.
- Added reverse figure/table identity auditing so in-text object references cannot bypass source identity or claim `object_refs`.
- Added reverse structured-citation auditing for Pandoc-style `[@key]` references against source `citation_key` and paragraph claim `citation_keys`.
- Added configurable `coverage_policy` to the project template and `references/14-manuscript-coverage-closure.md`.
- Integrated manuscript coverage into standard/release preflight without breaking v1.4 examples.

## 1.4.0 — 2026-09-30

- Added semantic workspace checkpoints with deterministic `state_id` values for revision lineage.
- Added declared local source-file hashes to semantic state so same-path result/figure replacement is detectable.
- Added `audit_change_provenance.py` to compare a pre-edit baseline with current source/evidence/claim/reporting-contract/manuscript state.
- Extended revision records with `base_state_id`, `verified_state_id`, `affected_evidence_ids`, and `changed_artifacts`.
- Release `revise`/`refresh` now requires material semantic changes to be covered by verified revision records bound to both the exact baseline and exact current state.
- Post-verification semantic edits now invalidate stale revision verification instead of silently inheriting it.
- Upgraded `revision_diff.py` to schema v2 with old/new manuscript SHA-256 hashes and audited those hashes against baseline/current state.
- Made missing verified evidence a release error for active result/method claims rather than a warning.
- Upgraded release manifests to schema v2 with `workspace_state_id` and `parent_workspace_state_id`; freezing also writes `workspace_state.current.json`.
- Added `references/13-version-lineage-and-change-provenance.md` and updated the revision-lifecycle example for state-bound verification.

## 1.3.0 — 2026-09-30

- Added explicit claim lifecycle: `active`, `superseded`, and `retired`, with replacement/history fields.
- Added `audit_claim_lifecycle.py` to catch broken supersession chains, missing retirement rationale, and inactive claim residue in the current manuscript.
- Updated manuscript consistency, claim-family, reporting-contract, stale-source, and impact analysis logic to distinguish current active claims from historical inactive claims.
- Added `revision_obligations.jsonl` and `audit_revision_obligations.py` for reviewer/editor/user/internal-audit requests.
- Release manuscript-change obligations now require verified `revision_log.jsonl` entries plus `revision_diff.json` evidence of an affected claim change/removal and section change.
- Refined `revision_diff.py` to distinguish changed claims, added claim anchors, removed claim anchors, and anchors absent from both drafts while retaining the legacy transition union.
- Added lifecycle-aware refresh guidance and `references/12-revision-obligations-and-claim-lifecycle.md`.
- Kept `reviewer_response_map.jsonl` supported as a legacy backwards-compatible mapping.

## 1.2.0 — 2026-09-30

- Added `audit_manuscript_consistency.py` to verify claim-anchor uniqueness, declared section placement, and ledger-to-manuscript text synchronization.
- Added deterministic figure/table identity checks so a source object cannot silently be cited under a conflicting figure/table number.
- Added optional `reporting_contracts.jsonl` plus template and `audit_reporting_contracts.py` for main-result dependencies: result evidence, required method coverage, material qualifiers, expected scientific objects, required sections, and Abstract eligibility.
- Made full/multi-section release preflight require reporting-contract coverage for `section_plan.main_claim_families`; standard profile reports missing coverage as a warning.
- Added reporting contracts to workspace fingerprints and initialized workspaces.
- Replaced the weaker release-only global claim-text drift warning with anchor-local synchronization checks.
- Added `references/11-manuscript-consistency-and-reporting-contracts.md` and updated release guidance.

## 1.1.0 — 2026-09-30

- Added `claim_family_id` to connect section-specific restatements of the same scientific proposition.
- Added `section_plan.json` and section-contract guidance for full/multi-section manuscripts.
- Added deterministic cross-section claim-family audit.
- Made refresh/impact analysis propagate changed evidence to all claims in an affected family.
- Added optional `citation_keys` and figure/table `object_refs` to the claim contract and corresponding validation/preflight checks.
- Replaced over-broad all-section numeric-token enforcement with claim-level `required_value_tokens`; Results/result claims inherit evidence tokens by default while compressed/interpretive sections opt in explicitly.
- Added `revision_diff.py` for before/after changed-section and anchored-claim verification.
- Added optional reviewer-response mapping tied to real `revision_log.jsonl` change IDs.
- Updated source fingerprints, schemas, templates, examples, README, and release guidance for v1.1.0.

## 1.0.0 — 2026-09-30

Initial release.

- Added evidence-to-claim-to-manuscript workflow.
- Added `build`, `revise`, `refresh`, and `audit` modes.
- Added draft/standard/release execution profiles.
- Added source, evidence, claim, and revision record templates.
- Added deterministic workspace validation and preflight.
- Added source/evidence fingerprinting and change-impact analysis.
- Added release manifest generation.
- Added manuscript-specific guidance for Results, figure/table integration, Discussion, revisions, claim calibration, journal adaptation, and QA.
