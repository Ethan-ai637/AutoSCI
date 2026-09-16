---
name: scientific-figure
description: Create, reconstruct, critique, and refine editable scientific figures for papers, research reports, posters, and technical presentations. Use for method overviews, architectures, mechanisms, pipelines, taxonomies, comparison diagrams, and multi-panel conceptual figures from a manuscript, equations, code, data, a user brief, or an existing figure. Preserve scientific meaning, use a source-grounded semantic spec, generate traceable SVG, render and critique it, and apply QA proportional to draft, standard, or publication-release use. For quantitative experimental plots, use authoritative data and a data-plotting workflow rather than inventing values or hand-drawing curves.
---

# Scientific Figure

Build scientific figures structure-first: **source -> semantic contract -> visual grammar -> editable SVG -> render -> QA -> targeted refinement**. The current Codex session acts as planner, generator, and critic; no second LLM or image API is required. Use the deterministic orchestrator to keep profile, complexity, milestones, and resume behavior stable across runs.

## Hard rules

1. Science beats aesthetics. Never change a claim, relation, equation, direction, ordering, label, or datum to improve composition.
2. Create `figure_spec.json` before detailed drawing. Core claims must be source-grounded; a core claim cannot be merely inferred.
3. Freeze stable semantics before standard/release work. If meaning changes, intentionally unlock, verify, edit, and re-freeze.
4. Keep important entities/relations traceable from spec to SVG. Preserve exact registered notation.
5. SVG is the editable master. Quantitative evidence comes from authoritative data/code, never visual invention.
6. Judge actual renders, including intended final size. Separate semantic critique from visual critique.
7. Avoid box soup. Containers represent real bounded systems/regions, not places to park text.
8. References supply visual grammar only; never copy their scientific topology, data, or distinctive artwork.
9. A lower QA profile reduces execution cost, never the standard of scientific truth.
10. Default to <=3 refinement rounds. If the same macro-layout defect survives twice, change the visual grammar instead of nudging coordinates again.

## 1. Choose the execution profile and initialize orchestration

Read `references/workflow_profiles.md` only when profile choice is non-obvious. For a persistent figure task, initialize the workflow state after the spec has real content:

```bash
python scripts/orchestrate.py init figure_spec.json --state workflow_state.json
```

On a resumed session, run `orchestrate.py verify` then `orchestrate.py next` before rereading references or rebuilding work. Consult `references/orchestration.md` only when state/checkpoint behavior needs explanation.

- `draft`: rapid exploration or disposable internal sketch.
- `standard`: **default** for normal research work, paper drafting, and presentations.
- `release`: submission/camera-ready/archival handoff or explicit “publication-ready” request.

Start from `assets/figure_spec.template.json`. Set `workflow.profile`. Do not run release-only machinery for an ordinary working figure.

## 2. Establish source authority and figure mode

Identify the authoritative source: manuscript/Method, equations, code, table/data, user brief, or existing figure. Surface conflicts instead of silently choosing. For document/code/data extraction, consult `references/source_grounding.md`.

Classify the figure with `references/figure_modes.md`. Quantitative plots must follow the data-driven path. Record intended placement/physical size early when known.

## 3. Build the semantic contract

Capture at minimum:
- one-sentence `message`
- structured source anchors
- supported `claims` (`direct`, `user_provided`, or `inferred`)
- `entities` and typed `relations`
- exact `required_labels`
- critical `notation`/equations
- `invariants` and `forbidden_inferences`
- target/use constraints and panel jobs if multi-panel

For complex specs consult `references/figure_schema.md`. Fingerprint a concrete local PDF/data/code snapshot before freeze when traceability matters:

```bash
python scripts/fingerprint_source.py paper.pdf --id SRC1 --spec figure_spec.json
```

Validate grounding:

```bash
python scripts/validate_spec.py figure_spec.json
python scripts/source_audit.py figure_spec.json
```

For `standard`/`release`, freeze after scientific verification:

```bash
python scripts/freeze_spec.py figure_spec.json
```

If science must change later: `freeze_spec.py figure_spec.json --unlock`, edit/verify, then freeze again.

## 4. Choose visual grammar before coordinates

The deterministic orchestrator records the same complexity decision and tournament policy. `complexity_gate.py` remains available for a standalone explanation:

```bash
python scripts/complexity_gate.py figure_spec.json
```

Use `references/pattern_library.md` to choose a phenomenon-matched grammar: directional spine, parallel lanes + fusion, hierarchy, cycle, tensor/data path, comparison matrix, spatial mechanism, before/after, overview + inset, or multi-panel story.

Only use `references/layout_tournament.md` when complexity and competing plausible grammars justify it. Under `draft`, normally use one layout. Under `standard`, tournament is optional. Under `release`, compare 2–3 candidates for genuinely medium/high-complexity figures.

Before drawing, decide the dominant visual spine/object, entry/exit reading order, 2–4 primary focal elements, secondary annotations, relation encodings, and whether proximity/lanes/braces/background regions can replace containers. If the plan is “many similar boxes with arrows,” redesign it.

## 5. Use references safely

When reference figures exist, consult `references/reference_policy.md`. Extract typography hierarchy, density, palette roles, stroke/connector language, panel rhythm, abstraction level, and whitespace behavior only. Never let a reference introduce a relation absent from the frozen spec.

## 6. Generate one traceable SVG master

Keep labels editable. Important content uses semantic groups, for example:

```xml
<g id="entity-E1" data-entity-id="E1" data-bounds="80 120 240 96">...</g>
<g id="relation-R1" data-relation-id="R1" data-relation-type="flow"
   data-source-id="E1" data-target-id="E2">
  <path data-route="true" d="..." marker-end="url(#arrow)"/>
</g>
```

For machine-auditable bounds/routes consult `references/geometry_contract.md`. For exact mathematical symbols/equations consult `references/math_fidelity.md`.

Prefer native SVG geometry, consistent alignment/spacing, explicit arrow markers, meaningful whitespace, and restrained styles. Avoid emoji, stock decoration, unnecessary filters/gradients, tiny labels, and ambiguous connector crossings.

## 7. Run profile-aware deterministic QA

```bash
python scripts/preflight.py figure_spec.json figure.svg --profile auto
```

The check set is proportional to the profile:
- `draft`: source/spec integrity, SVG structure, semantic traceability, notation when present.
- `standard`: draft checks + frozen semantics + geometry + final-size legibility.
- `release`: standard checks + publication robustness + self-contained portability.

Fix deterministic failures before aesthetic critique. Do not bypass a hard failure as “just formatting.”

## 8. Render and inspect

For standard/release:

```bash
python scripts/render_package.py figure_spec.json figure.svg --outdir .
```

Inspect high-resolution and target-size renders; inspect grayscale when requested. For a draft, a normal `render_svg.py` preview is sufficient unless final-size density is already a concern. Read `references/publication_robustness.md` only when print/grayscale behavior matters.

## 9. Critique in two passes

Use `references/critic_rubric.md` and `assets/critic.template.json`.

**Semantic pass:** verify visible relations, claims, equations, labels, panel implications, and absence of invented evidence.

**Visual pass:** verify hierarchy, reading order, density, alignment, routing, typography, whitespace, consistency, and final-size readability.

For a release, hard gates are semantic correctness >=9/10, information completeness >=8/10, legibility/integrity >=8/10, release preflight pass, and no clipping, broken glyphs, unsupported claim, or invented data. Averages never compensate for a failed hard gate.

## 10. Refine surgically

List 1–5 concrete defects per round and preserve successful geometry. Fix in this order: scientific error -> missing content -> false implication -> macro-layout -> routing/overlap -> final-size typography -> polish. Rerun the relevant preflight/render after meaningful edits. Do not regenerate from scratch unless the visual grammar itself failed.

## 11. Checkpoint milestones and promote to release only when needed

After a verified milestone, checkpoint it rather than relying on conversational memory. Checkpointing `qa_passed` reruns preflight; checkpointing `critic_passed` runs `critic_gate.py`, so a blank/highly inconsistent critic record cannot be treated as success. At minimum checkpoint `layout_selected`, `qa_passed`, and `critic_passed` for work likely to span sessions. If the SVG changes after QA, re-checkpoint `svg_candidate`; later QA/critic checkpoints are invalidated automatically. Ask for the next deterministic step with:

```bash
python scripts/orchestrate.py next figure_spec.json --state workflow_state.json
```

## 12. Promote to release only when needed

When moving a working figure to submission quality:

```bash
python scripts/set_profile.py figure_spec.json release
python scripts/doctor.py --strict
python scripts/preflight.py figure_spec.json figure.svg --profile release
python scripts/finalize_figure.py figure_spec.json figure.svg --critic critic.json --outdir release
```

`finalize_figure.py` defaults to release QA, renders final derivatives, exports vector PDF when requested, writes SHA-256 manifest metadata, and verifies the package. For a non-archival internal delivery, explicitly use `--profile standard`.

Expected release artifacts include editable SVG, figure spec, QA record, inspection/final-size renders, optional vector PDF, and `manifest.json`. Consult `references/export_policy.md` and `references/release_portability.md` only at this stage.

## 13. Benchmark the workflow only when evaluating the skill

Benchmarking is optional and must not add overhead to ordinary figure production. For a single paper, consult `references/benchmarking.md` and use `scripts/benchmark.py`. Prefer blind reconstruction: initialize the case without the author's figure, record generation runs first, and attach the author figure only for post-hoc evaluation. Compare scientific correctness and coverage before visual quality; do not optimize for pixel similarity or a single composite score.

For skill-version decisions, use `scripts/benchmark_suite.py` across multiple heterogeneous cases. Register baseline/candidate/ablation variants explicitly and compare them pairwise on the same completed cases. Inspect scientific regressions and repeated major/critical failure categories before promoting a change. A useful minimum is raw Codex versus the current skill in `standard` on three qualitatively different methods.

## Resource routing

Load details only when needed:
- workflow cost/profile -> `references/workflow_profiles.md`
- deterministic plan/resume -> `references/orchestration.md`
- figure type -> `references/figure_modes.md`
- semantic schema -> `references/figure_schema.md`
- source provenance -> `references/source_grounding.md`
- visual grammar -> `references/pattern_library.md`
- difficult macro-layout -> `references/layout_tournament.md`
- style/reference use -> `references/reference_policy.md`
- typography/layout principles -> `references/design_system.md`
- math fidelity -> `references/math_fidelity.md`
- geometry audit failure -> `references/geometry_contract.md`
- critic -> `references/critic_rubric.md`
- print/grayscale -> `references/publication_robustness.md`
- final export -> `references/export_policy.md`, `references/release_portability.md`
- skill evaluation / blind reconstruction -> `references/benchmarking.md`

Execute deterministic scripts without reading their source unless modification/debugging is required.
