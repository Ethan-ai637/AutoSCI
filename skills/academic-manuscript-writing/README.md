# academic-manuscript-writing

`academic-manuscript-writing` is the AutoSCI skill for turning **experimental results, statistical outputs, figures/tables, methods records, and research notes into traceable scientific manuscript text**, while dynamically resolving the target discipline, article type, venue, year, and submission-stage writing requirements from current source-backed guidance.

It is intentionally **not** a generic academic-writing prompt and it does **not** hard-code the rules of individual conferences or journals.

## What it does

- drafts Results, Methods, Discussion, Abstract, captions, or full manuscripts from supplied research artifacts;
- keeps result claims linked to evidence IDs and groups cross-section restatements with `claim_family_id`;
- preserves numbers, uncertainty, scope, negative/null findings, and study-design limitations;
- updates existing manuscripts surgically rather than rewriting everything;
- detects active claims that may be stale after an analysis/figure/source changes and propagates review across Abstract/Results/Discussion/Conclusion claim families;
- preserves historical claims with explicit `active`, `superseded`, and `retired` lifecycle states instead of silently overwriting invalidated conclusions;
- audits cross-section consistency before release, including ledger/manuscript placement and figure/table identity;
- verifies real before/after revision scope and can bind reviewer/editor/user requests to verified manuscript changes through `revision_obligations.jsonl`;
- optionally declares main-result reporting contracts so Methods, qualifiers/limitations, figures/tables, and Abstract eligibility cannot drift independently;
- checkpoints semantic manuscript state so revise/refresh releases can prove exactly which source/evidence/claim state was revised and which final state was actually verified;
- closes traceability in both directions: required ledger claims must reach the manuscript, while covered manuscript paragraphs/citations/figure-table references must resolve back to active claims and declared sources;
- protects multi-claim prose with paragraph composition contracts and claim-level companion requirements so qualifiers/limitations cannot silently drop out while the stronger claim remains;
- classifies unresolved source conflicts by release disposition so disclosed/scoped provenance conflicts need not be confused with scientifically blocking conflicts;
- audits high-risk claim atomicity so several independent propositions cannot be hidden inside one ledger claim;
- audits revision locality so refresh/revise workflows preserve the actual manuscript instead of silently reconstructing it as a QA report;
- closes the claim-to-prose gap with exact start/end claim spans, so numbers, citations, figure/table references, and material prose are owned by the exact claim rather than merely by a shared paragraph.
- resolves `generic`, `discipline`, or `venue` writing contexts dynamically instead of assuming one universal manuscript paradigm;
- keeps venue/style guidance in a separate writing-source provenance chain so author instructions can constrain structure without becoming scientific evidence;
- converts retrieved official guidance into a normalized `writing_profile.json` and a hash-bound operational `manuscript_contract.json`;
- audits venue/year/submission-stage applicability, official-source authority, contract freshness, required/forbidden sections, section order, and generic word-limit checks before claiming venue readiness.

## What it does not do

- invent missing experiments, methods, statistics, references, or mechanisms;
- perform literature discovery in place of `literature-research`;
- recompute statistics in place of `scientific-data-analysis`;
- create conceptual figures in place of `scientific-figure`;
- treat fluent prose, reviewer-response prose, or conversational memory as evidence that a revision happened.
- store permanent ICML/NeurIPS/ACL/CVPR/journal rules that can become stale;
- treat blogs or remembered venue conventions as equivalent to current official author instructions.

## Core workflow

```text
writing_context
  -> runtime retrieval of current official writing guidance
  -> writing_sources.jsonl
  -> writing_profile.json
  -> manuscript_contract.json

scientific sources
  -> evidence ledger
  -> active + historical atomic claims / claim families
  -> exact claim spans in governed manuscript prose
  -> section/reporting/paragraph contracts
  -> manuscript / targeted revision
  -> revision obligations + dependency analysis + revision diff
  -> writing-profile + numeric + scope + lifecycle + manuscript-sync + span + atomicity + composition + locality QA
  -> release snapshot
```

## Recommended modes

- `build` — create manuscript text from research artifacts.
- `revise` — modify an existing manuscript against authoritative evidence.
- `refresh` — update text after results/figures change, with impact analysis and claim lifecycle updates.
- `audit` — inspect manuscript claims against supplied evidence.

## Requirements and package verification

The deterministic tooling uses only the Python standard library and targets a **Python 3.8 syntax floor**. The packaged self-test mechanically checks every script against the Python 3.8 grammar. This release was runtime-tested on the build interpreter used for packaging; repositories that want to advertise Python 3.8 runtime support should also run CI on Python 3.8 itself. Before relying on a cloned or extracted package, run the built-in smoke test:

```bash
python scripts/self_test.py --quick
```

Maintainers and CI should run the complete fixture + destructive-test suite before release (CI may split it with `--shard INDEX/TOTAL`):

```bash
python scripts/self_test.py --full
```

See `TESTING.md` for the test contract, `STABILITY.md` for supported guarantees and known boundaries, and `RELEASE_CHECKLIST.md` for GitHub/release hygiene. Historical examples intentionally keep older `skill_version` values where they serve as backwards-compatibility fixtures.

## Quick start

```bash
python scripts/init_workspace.py manuscript-workspace
cd manuscript-workspace
# set project.json.writing_context first
# for discipline/venue specificity, retrieve current applicable guidance and populate:
#   writing_sources.jsonl -> writing_profile.json -> manuscript_contract.json
# then populate scientific sources.jsonl, evidence.jsonl, claims.jsonl, manuscript.md
python scripts/preflight.py . --profile standard --report qa_report.json
```

For a venue-specific project, the model resolves the runtime interface before section planning:

```text
project.json.writing_context
  -> writing_sources.jsonl
  -> writing_profile.json
  -> manuscript_contract.json
```

See `examples/dynamic-writing-profile/`, `references/20-dynamic-writing-profile.md`, and `references/21-manuscript-contract.md`. The example uses a fictional venue so package tests do not depend on live web content.

For new v1.8 workspaces, governed manuscript claims use exact span markers:

```markdown
<!-- CLAIM:C001 -->The primary result was 12.4 versus 10.1 (p = 0.03).<!-- END-CLAIM:C001 -->
```

For a full/multi-section release, declare reporting contracts for the main claim families (see `examples/full-release-span/` for v1.8 exact-span usage), then run:

```bash
python scripts/preflight.py . --profile release --report qa_report.json
python scripts/freeze_snapshot.py . --output manifest.json
```

For a reviewer/editor revision with a pre-edit manuscript:

```bash
python scripts/revision_diff.py \
  --old manuscript.before.md \
  --new manuscript.md \
  --claims claims.jsonl \
  --report revision_diff.json

python scripts/preflight.py . --profile release --report qa_report.json
```

`revision_obligations.jsonl` can then prove which request maps to which verified `change_id`, claim, section, and diff result.

For material revise/refresh work, checkpoint the exact pre-edit state **before** editing:

```bash
python scripts/checkpoint_workspace.py . --output workspace_state.previous.json
```

After editing and generating `revision_diff.json`, checkpoint the candidate final state and bind verified revision rows to both state IDs:

```bash
python scripts/checkpoint_workspace.py . --output workspace_state.current.json
python scripts/preflight.py . --profile release --report qa_report.json
```

If the manuscript, scientific evidence/claims/sources, writing sources/profile/contract, reporting contracts, or paragraph contracts change after verification, the previous `verified_state_id` is stale and release preflight fails until the new semantic state is verified.

## Key design idea

The primary unit of scientific control is the **claim**. Paragraphs are treated as a composition layer over claims, not as evidence units themselves. Separately, the primary unit of writing-rule control is the **source-backed writing constraint**; venue guidance never substitutes for scientific evidence.

A manuscript sentence can be beautifully written and still be scientifically wrong. This skill therefore treats prose as a rendered view of a more important chain:

```text
source artifact -> evidence unit -> atomic claim -> exact manuscript span -> paragraph/section composition
```

A claim also has a lifecycle. If new evidence changes the scientific proposition, the old claim is not silently erased: it becomes `superseded` or `retired`, the replacement relationship is recorded, and release QA checks that inactive prose no longer remains in the current manuscript.

That makes it possible to answer two crucial revision questions:

1. **If this analysis or figure changes, which current claims and manuscript sections must be re-checked?**
2. **Which old conclusions must disappear or be replaced, and can we prove that the requested revision actually happened?**

## Version

Current version: `2.0.0`

### v2.0.0 dynamic discipline/venue writing profiles

v2.0 separates the stable scientific-governance core from time-sensitive writing paradigms. New workspaces declare a `writing_context` (discipline, subfield, article type, venue, track, year, submission stage, specificity, language). For discipline/venue-specific work, the model retrieves the applicable current guidance at runtime, records it in `writing_sources.jsonl`, normalizes atomic constraints into `writing_profile.json`, and generates a source-linked `manuscript_contract.json`.

The package does **not** contain permanent venue rule tables. `audit_writing_profile.py` instead verifies the interface: official-source authority for venue requirements, year/article-type/track/stage applicability, constraint provenance, guideline conflicts, readiness level, profile/contract context agreement, hash-bound contract freshness, required/forbidden manuscript sections, section order, generic word-limit checks, and alignment with scientific section/coverage planning. Writing-source state is also part of semantic checkpoints, fingerprints, impact review, and revise/refresh provenance.

The v2 test fixture uses a fictional `ExampleConf` so repository self-tests remain deterministic and offline. Live venue-specific execution is expected to retrieve real official guidance at runtime.


### v1.8.2 Python compatibility contract

v1.8.2 fixes a release-engineering mismatch discovered during GitHub-readiness review: v1.8.1 documented Python 3.8+ support, while the new self-test used Python 3.9/3.10-only type-annotation syntax. The self-test now uses Python-3.8-compatible typing and mechanically parses every deterministic script against the declared Python 3.8 syntax floor. This is a compatibility/verification patch; the scientific manuscript contract is unchanged from v1.8.1.

### v1.8.1 release engineering and reproducible package health

v1.8.1 adds a repository/package self-test rather than changing the scientific manuscript contract. `scripts/self_test.py` validates version synchronization, Python/JSON/JSONL syntax, package hygiene, backwards-compatible release fixtures, current v1.8 release fixtures, and (in `--full` mode) destructive span mutations that release QA must reject. `TESTING.md` documents the test contract, `STABILITY.md` documents supported guarantees and known boundaries, and `RELEASE_CHECKLIST.md` makes source-tree, ZIP, and AutoSCI repository integration checks explicit.

### v1.8.0 exact claim-span traceability

v1.8 inserts an exact manuscript-span layer between atomic claims and paragraph composition. New v1.8 workspaces use `anchor_precision=span` with paired `<!-- CLAIM:<id> --> ... <!-- END-CLAIM:<id> -->` markers in configured scientific sections. `audit_claim_spans.py` verifies exact span-to-ledger text synchronization, required numeric tokens inside the span, span-local citation ownership, span-local figure/table ownership, non-overlapping spans, and material visible prose that sits outside any governed span.

This closes a gap left by paragraph-level traceability: a paragraph could previously contain a valid anchored claim while an adjacent unsupported sentence, citation, or number rode along inside the same paragraph. v1.8 makes the claim boundary explicit. Historical pre-v1.8 workspaces keep their existing paragraph-anchor semantics unless they opt into `claim_span_policy`. See `examples/span-traceability/` and `references/19-claim-span-traceability.md`.
`revision_diff.py` is also span-aware in schema v4: exact spans are compared when available, with legacy paragraph fallback for older baselines. This avoids falsely marking neighboring claims changed when only one span in a shared paragraph was edited.

### v1.7.2 cross-side numeric provenance closure

Cross-side conflict disclosures now close the remaining numeric-provenance loophole. When `conflict_sides` are active, every numeric token in a `cross_side_claim_id` must either be declared in one of the represented side `value_tokens` or be explicitly registered in `cross_side_numeric_exceptions`. Derived values require at least two `source_side_ids` plus a reason; contextual numbers require an explicit reason. The audit also checks the anchored manuscript paragraph, allowing numeric tokens from other registered claims in that paragraph but rejecting unregistered prose-level numbers.

This means a disclosure such as `v1 reports 74.7 and the repository reports 76.3, therefore the unified value is 75.5` fails unless `75.5` is explicitly registered as a derived value with its provenance and rationale. The system does not decide whether that derivation is scientifically justified; it makes the derivation visible and auditable instead of silent.

### v1.7.1 conflict-side provenance closure

For `disclose_and_scope` conflicts, v1.7.1 can declare explicit `conflict_sides` (source/evidence/value provenance) plus `cross_side_claim_ids`. Release then requires ordinary scoped claims to resolve to exactly one side, while cross-side disclosure claims must visibly attribute every competing side. This closes the v1.7 gap where a conflict could be disclosed yet its competing evidence streams could still be silently blended inside a current claim.

## v1.7 additions

- Added `audit_source_conflicts.py` and structured conflict dispositions: `blocking`, `disclose_and_scope`, `historical_only`, and `resolved`. Legacy free-text conflicts remain release-blocking.
- `disclose_and_scope` can pass release only when conflict/scoped/disclosure claims are explicitly linked with `source_conflict_ids` and the disclosure is present in the manuscript.
- Added `audit_claim_atomicity.py` plus `claim_atomicity_policy`; release now catches obvious compound result/method/limitation claims that bundle independent propositions into one claim.
- Added `atomicity_exemption_reason` for rare scientifically indivisible compound-looking claims.
- Upgraded `revision_diff.py` to schema v3 with prose-token similarity, exact paragraph preservation, per-section similarity, changed-section fraction, and title-change metrics.
- Added `audit_revision_locality.py` and `revision_policy` so `revise`/`refresh` can enforce manuscript preservation, explicit authorization for global rewrites, title stability, and removal of workflow/meta-writing from scientific prose.
- `project.json` is now a governed semantic artifact in revise/refresh change-provenance auditing, so changing conflict disposition or revision policy after a baseline cannot bypass revision verification.
- Added `references/16-source-conflict-disposition.md`, `17-claim-atomicity.md`, and `18-revision-locality-and-manuscript-preservation.md`.

## v1.6 additions

- Added `paragraph_contracts.jsonl` and `audit_paragraph_composition.py` for explicit multi-claim paragraph composition.
- Release paragraphs containing two or more active claim anchors now require exactly one stable `PARAGRAPH:<id>` marker and a matching contract.
- Added composition types such as `qualified`, `result_interpretation`, `contrast`, and `synthesis`; contracts must exactly match the active claims actually present in the paragraph.
- Added claim-level `required_companions` with `same_paragraph`, `same_section`, and `manuscript` scopes to protect material qualifiers/limitations during revision.
- Added optional literal `required_text_tokens` / `forbidden_terms` paragraph guardrails for high-value release invariants without pretending to perform semantic inference.
- Added paragraph contracts to semantic state, fingerprints, change-provenance governance, initialization, and release handoff.
- Preserved archived pre-v1.6 semantic-state compatibility when `paragraph_contracts.jsonl` is absent.
- Added `examples/paragraph-composition/` and `references/15-paragraph-composition-and-companions.md`.

## v1.5 additions

- Added `audit_manuscript_coverage.py` for bidirectional ledger/manuscript coverage closure.
- Multi-section/full-manuscript core sections now treat active claims as manuscript-required by default unless explicitly marked `optional` or `not_in_manuscript`.
- Added `manuscript_presence` and `manuscript_presence_reason` to the claim contract.
- Covered Abstract/Methods/Results/Discussion/Conclusion paragraphs must resolve to active claim anchors at release; explicit `COVERAGE:EXEMPT` markers require a reason and remain visible in the audit report.
- Added reverse figure/table auditing: manuscript `Fig./Figure/Table` references must map to declared source object identity and to `object_refs` of an active claim in the same paragraph.
- Added reverse structured-citation auditing for Pandoc-style `[@citation_key]` references against both source metadata and paragraph claim `citation_keys`.
- Added configurable `project.json.coverage_policy` and `references/14-manuscript-coverage-closure.md`.

## v1.4 additions

- Added `checkpoint_workspace.py` and semantic `state_id` snapshots for exact pre-edit/post-edit revision lineage.
- Semantic state includes declared local source-file hashes, so replacing a result/figure under the same filename is still detected.
- Added `audit_change_provenance.py` to compare the baseline with the current source/evidence/claim/reporting-contract/manuscript state.
- `revision_log.jsonl` now supports `base_state_id`, `verified_state_id`, `affected_evidence_ids`, and `changed_artifacts`.
- Release `revise`/`refresh` requires verified revision coverage of material semantic changes; silent ledger edits or post-verification edits invalidate the prior verification.
- `revision_diff.py` schema v2 records old/new manuscript SHA-256 values, preventing a stale diff from certifying a later draft.
- Release result/method claims now require at least one linked evidence item with `verification=verified`; partial/unverified-only support is no longer merely a warning.
- `freeze_snapshot.py` now emits `workspace_state.current.json` and manifest schema v2 with current/parent workspace-state IDs.

## v1.3 additions

- Added explicit claim lifecycle with `lifecycle_state=active|superseded|retired`, `supersedes_claim_ids`, `superseded_by_claim_ids`, and `retirement_reason`.
- Added `audit_claim_lifecycle.py` to detect broken replacement chains and inactive claims that still remain in the current manuscript.
- Made claim-family, reporting-contract, stale-source, and manuscript-consistency audits operate on **active claims** while preserving inactive claims as historical provenance.
- Added `revision_obligations.jsonl` and `audit_revision_obligations.py` for reviewer/editor/user/internal-audit requests.
- Release-level manuscript-change obligations must resolve to verified `revision_log.jsonl` changes and a `revision_diff.json` showing an affected claim change/removal and section change.
- `revision_diff.py` now distinguishes added and removed claim anchors, which makes intentional claim replacement auditable instead of treating it as a generic missing-anchor condition.
- Kept `reviewer_response_map.jsonl` as a backwards-compatible legacy format.
- Made impact analysis report historical inactive claims separately instead of treating them as current manuscript dependencies.

## v1.2 additions

- Deterministic ledger-to-manuscript anchor audit: unique anchor, correct section placement, and anchored-text synchronization.
- Figure/table identity gate that catches source/display-number mismatches such as a `Fig. 2` source cited as `Fig. 3`.
- Optional `reporting_contracts.jsonl` for main result families, linking result evidence to required Methods coverage, material qualifiers/limitations, expected figure/table sources, required sections, and Abstract eligibility.
- Full/multi-section release preflight requires reporting-contract coverage for `section_plan.main_claim_families`.

## v1.1 additions

- Cross-section `claim_family_id` dependency model.
- First-class `section_plan.json` for multi-section/full manuscripts.
- Deterministic claim-family audit and family-aware refresh propagation.
- Claim-level `required_value_tokens` so exact numeric fidelity is strict where needed without forcing every statistic into Abstract/Discussion/Conclusion.
- Explicit literature `citation_keys` and figure/table `object_refs` in the claim contract.
- `revision_diff.py` to verify changed sections and anchored claim spans.
