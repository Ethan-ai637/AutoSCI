# Workflow profiles

Use profiles to keep the workflow proportional to the task. Profiles change **execution/QA cost**, not scientific truth. Never use a lower profile to excuse a known semantic error.

## `draft`

Use for rapid ideation, early layout exploration, or a disposable internal sketch.

Required path:
- build a source-grounded spec
- validate source/claim structure
- SVG lint
- semantic traceability
- notation fidelity when notation exists
- render and visually inspect the working preview

Not required by integrated preflight:
- geometry endpoint/bounds audit
- physical-size typography audit
- portability audit
- publication robustness audit
- release manifest/PDF

A `draft` artifact must not be called publication-ready or final. Freeze semantics only when the scientific content has stabilized.

## `standard` — default

Use for normal research work, internal reports, lab meetings, paper drafting, and most presentation figures.

Adds:
- frozen semantic contract
- geometry audit
- physical-size legibility audit
- normal render–critique–refine loop

Portability is advisory by default. Layout tournament is used only when complexity or genuine competing grammars justify it.

## `release`

Use before submission, camera-ready export, archival handoff, or when the user explicitly asks for a publication-ready package.

Adds:
- all standard gates
- publication robustness audit
- required portability audit
- self-contained SVG constraints
- final derivatives and hashed manifest
- release verification

Run `python scripts/set_profile.py figure_spec.json release` before release preflight. This changes QA policy only and leaves the semantic lock untouched.

## Profile commands

Set a profile:

```bash
python scripts/set_profile.py figure_spec.json draft
python scripts/set_profile.py figure_spec.json standard
python scripts/set_profile.py figure_spec.json release
```

Run profile-aware preflight:

```bash
python scripts/preflight.py figure_spec.json figure.svg --profile auto
```

`auto` reads `workflow.profile`. Legacy specs from schema <=1.5 without a profile retain the old release-strict preflight behavior.

Final release defaults to release QA even if the working profile was standard:

```bash
python scripts/finalize_figure.py figure_spec.json figure.svg --critic critic.json --outdir release
```

For a non-archival internal delivery, explicitly use `--profile standard`.

## Progressive disclosure

Do not load every reference document up front. The main skill is a router:
- source extraction problem -> `source_grounding.md`
- layout choice problem -> `pattern_library.md` and, only if needed, `layout_tournament.md`
- equations/symbols -> `math_fidelity.md`
- deterministic geometry failure -> `geometry_contract.md`
- final submission/handoff -> `publication_robustness.md`, `release_portability.md`, `export_policy.md`

Scripts should normally be executed without reading their source.
