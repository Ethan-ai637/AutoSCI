# Changelog

## v2.0

- Declared the v1.9 production + benchmark architecture as the first stable baseline; no new generation, critic, audit, or publication gate was added.
- Added `STABILITY.md` defining the stable production contract, schema/version separation, compatibility policy, and evidence-driven v2.x change policy.
- Fixed stale hard-coded skill-version metadata in deterministic orchestration: new/resumed workflow states now report the installed `VERSION` dynamically.
- Updated the workflow-state template to 2.0.0 while preserving compatibility with historical state files and the existing scientific figure spec schema 1.7.
- Kept historical benchmark variant labels/examples intact so prior v1.x experimental records remain comparable.
- v2.0 intentionally freezes normal production behavior; future production changes should be justified by reproducible benchmark failures or concrete correctness/portability bugs.

## v1.9

- Added optional suite-level benchmarking without changing the production figure workflow or scientific figure spec schema.
- Added `scripts/benchmark_suite.py` for multi-case benchmark registration, coverage matrices, paired variant/version comparison, and structured ablation registration.
- Suite reports compare each evaluation dimension independently; they never collapse scientific and visual quality into one composite score.
- Added paired win/tie/loss counts, per-case deltas, high-priority scientific regressions, and major/critical failure-category deltas so proposed skill changes can be evaluated across heterogeneous papers.
- Ablations are first-class suite variants with an explicit parent/change description, making it possible to test whether machinery such as layout tournament or strict QA is actually helping.
- Added `assets/benchmark_suite.template.json` and expanded `references/benchmarking.md` with a recommended three-case regression suite.
- Kept the production figure schema at 1.7; v1.9 is evaluation infrastructure only.

## v1.8

- Added an optional benchmark/failure-analysis harness without adding any new gate to normal draft/standard/release production.
- Added `scripts/benchmark.py` for case initialization, source fingerprint verification, immutable run recording, post-hoc reference attachment, structured evaluation validation, and comparison reports.
- Blind benchmark cases now refuse author-reference attachment until at least one generation run has been recorded, reducing accidental reference leakage.
- Added a failure taxonomy and independent evaluation dimensions; benchmark reports explicitly avoid a single composite score and pixel-similarity ranking.
- Added `references/benchmarking.md` plus case/evaluation templates for raw-Codex vs skill comparisons and cross-paper regression-driven iteration.
- Kept the scientific figure spec schema at 1.7 because benchmarking is external metadata, not part of scientific semantics. v1.8 is an evaluation-infrastructure update.

## v1.7

- Added deterministic workflow orchestration via `scripts/orchestrate.py`: profile resolution, complexity scoring, layout-tournament policy, ordered milestones, and one explicit next action.
- Added `critic_gate.py`; qualitative critique is now machine-gated for empty blockers, unsupported/inferred core claims, regressions, and profile-specific score floors. Release finalization requires an auditable critic record.
- Added hash-backed checkpoint/resume state so Codex can continue a figure across sessions without reconstructing the full workflow from conversation context.
- Meaningful re-checkpoints invalidate downstream QA/critic/release milestones; changing a checkpointed SVG after QA is detected as stale.
- Added `references/orchestration.md` and `assets/workflow_state.template.json`; the state file stores workflow metadata/hashes only and never changes scientific semantics.
- Bumped the default spec schema to 1.7 and added `workflow.orchestration=deterministic`.
- Kept all v1.6 figure-generation and QA rules intact; v1.7 is an execution-consistency update, not a new aesthetic/critic layer.

## v1.6

- Added `draft`, `standard`, and `release` execution profiles so QA cost is proportional to the task; `standard` is the new default for normal research work.
- Added profile-aware `preflight.py`, `profile_audit.py`, and `set_profile.py`; legacy <=1.5 specs remain release-strict when no profile exists.
- Made layout-tournament recommendations profile-aware instead of routinely branching medium-complexity work.
- Rewrote `SKILL.md` as a thinner workflow router with progressive disclosure; detailed specialist rules stay in `references/`.
- Kept semantic correctness invariant across profiles: profiles only change deterministic QA/release overhead.
- `finalize_figure.py` defaults to release QA and the manifest records the QA profile used.
- Bumped the spec schema to 1.6 and added `references/workflow_profiles.md`.

## v1.5

- Added `doctor.py` to detect local SVG→PNG, SVG→PDF, grayscale, and fontconfig capabilities before a run fails late.
- Added source-file fingerprinting (`fingerprint_source.py`) so exact manuscript/data/code snapshots can be tied to the semantic lock without copying the source into the release.
- Added `portability_audit.py` and a v1.5 QA contract to reject scripts, event handlers, CSS imports, and unapproved local/remote SVG dependencies; optional font-fallback and embedded-raster policies are configurable.
- Made grayscale QA fail closed when `grayscale_safe=true`: Pillow is preferred, ImageMagick is a fallback, and absence of both now fails rendering rather than silently skipping the artifact.
- Added deterministic vector-PDF export (`export_vector.py`) and `target.exports`; `finalize_figure.py` includes PDF when requested.
- Upgraded release manifests with source fingerprints and non-identifying toolchain capability metadata.
- Added `verify_release.py`; finalization now verifies all artifact hashes immediately, and releases can be re-verified after transfer.
- Added `release_portability.md` and bumped the default spec schema to 1.5.


## v1.4

- Added a deterministic geometry contract: root-coordinate semantic bounds on important entities and principal relation routes.
- Added `geometry_audit.py` to catch out-of-viewBox semantic objects, excessive unrelated primary overlap, and connectors whose physical endpoints disagree with declared source/target topology.
- Added a source-grounded notation registry and `notation_audit.py` for exact mathematical/technical text fidelity; notation is included in the semantic hash lock.
- Added one-command `finalize_figure.py` packaging after preflight, plus `artifact_manifest.py` with SHA-256 hashes, skill version, schema version, and semantic-lock metadata.
- Added `geometry_contract.md` and `math_fidelity.md`; updated schema/export guidance and the default schema to 1.4.
- Integrated notation and geometry checks into deterministic preflight.

## v1.3

- Added structured source grounding: stable source-anchor IDs, claim support classes (`direct`, `user_provided`, `inferred`), and deterministic `source_audit.py`.
- Made unsupported core claims a hard failure for v1.3 specs; source anchors are included in the existing semantic hash lock.
- Added a complexity gate and layout-tournament workflow so medium/complex figures compare 2–3 low-fidelity macro-layouts before polishing the first plausible composition.
- Added publication-robust semantic encoding metadata and `robustness_audit.py`; grayscale-safe targets reject color-only scientific distinctions.
- `render_package.py` now emits a target-size grayscale preview when Pillow is available.
- Added dedicated source-grounding, layout-tournament, and publication-robustness references plus a layout tournament scorecard template.
- Updated the default spec schema to 1.3 and integrated grounding/robustness checks into preflight.

## v1.2

- Made semantic freeze executable with `freeze_spec.py` and a SHA-256 semantic lock; preflight now detects scientific changes after freeze.
- Added relation endpoint traceability (`data-source-id` / `data-target-id`) and stronger topology audit.
- Added physical final-size typography auditing with `target_legibility.py` using intended figure width and minimum point size.
- Added `render_package.py` for one-command working-size + final-use preview rendering.
- Added a concrete scientific visual pattern library so “avoid box soup” has actionable alternatives.
- Added core-claim coverage warnings and physical target metadata to the figure spec.
- Added revision/regression logging and a stop rule: persistent macro defects trigger grammar replanning instead of endless coordinate tweaks.
- Expanded critic output with explicit regression checks.

## v1.1

- Added semantic freeze/change-control rule.
- Added spec-to-SVG traceability convention for entities, relations, and panels.
- Added deterministic `semantic_audit.py` and one-command `preflight.py`.
- Added target-size rendering via `render_svg.py --width`.
- Split critic into semantic audit and visual audit with evidence-based defects.
- Added explicit reference-figure policy to prevent topology/content leakage.
- Added panel-decomposition rules and target-context planning.
- Added export/final-use policy.
- Added layout-plan and critic templates.
- Strengthened spec validation, SVG portability checks, and standalone skill validation.
