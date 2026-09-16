# AutoSCI

**Local-first Codex skills for scientific figures and academic research presentations.**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Scientific Figure](https://img.shields.io/badge/Scientific%20Figure-v2.0%20stable-2ea44f)](skills/scientific-figure)
[![Research Presentation](https://img.shields.io/badge/Research%20Presentation-v3-blue)](skills/academic-research-presentation)

[中文说明](README_zh.md)

AutoSCI is a small open-source collection of research-oriented **Codex skills**. It does not train a new foundation model and it is not an API wrapper. Instead, it packages explicit research workflows, structured intermediate artifacts, deterministic checks, and review/refinement rules so a local Codex session can produce scientific visuals more reliably.

The project currently contains two complementary but independently usable skills:

| Skill | Purpose | Core output |
| --- | --- | --- |
| [`scientific-figure`](skills/scientific-figure) | Method overviews, architectures, mechanisms, pipelines, taxonomies, conceptual and multi-panel scientific figures | Editable, traceable SVG; optional PDF/PNG release package |
| [`academic-research-presentation`](skills/academic-research-presentation) | Paper reading, lab/group meetings, research updates, technical talks | Source-faithful slide plan/workflow to be paired with a PPTX/slides implementation tool |

## Why AutoSCI?

Research visuals fail in ways that ordinary design prompts do not catch. A figure may look polished while reversing an arrow, inventing a causal relation, dropping a side input, changing notation, clipping a legend, or making the main experimental evidence unreadable at final size.

AutoSCI treats those as **scientific failures**, not cosmetic imperfections.

The shared philosophy is:

- **scientific fidelity before aesthetics**;
- **evidence before decorative diagrams**;
- **structure before coordinates**;
- **editable source artifacts before flattened screenshots**;
- **render, inspect, and refine instead of trusting generation blindly**;
- **use deterministic scripts for checks that should not depend on model judgment**.

## 1. Scientific Figure — v2.0 Stable

`scientific-figure` is a structure-first workflow for creating and reconstructing editable research figures.

```text
source / method / equations / code
                ↓
        source-grounded spec
                ↓
          semantic freeze
                ↓
        scientific visual grammar
                ↓
          traceable SVG master
                ↓
 deterministic preflight + render
                ↓
 semantic critic + visual critic
                ↓
        targeted refinement
                ↓
      SVG / PDF / PNG release
```

Highlights:

- source-grounded claims, entities, relations, notation, and invariants;
- semantic locking so later visual refinement cannot silently change the science;
- traceability between semantic IDs and SVG entities/relations;
- anti-"box soup" scientific visual grammar;
- geometry, relation-endpoint, notation, legibility, portability, and release audits;
- `draft`, `standard`, and `release` execution profiles;
- deterministic checkpoint/resume orchestration;
- optional blind benchmark and paired version-comparison harness;
- no second image/LLM API is required: the active Codex session performs planning, generation, and critique.

For quantitative experimental plots, the skill explicitly prefers authoritative data + plotting code over visually invented curves.

See [`skills/scientific-figure/README.md`](skills/scientific-figure/README.md) and [`STABILITY.md`](skills/scientific-figure/STABILITY.md).

## 2. Academic Research Presentation — V3

`academic-research-presentation` is designed for research decks where scientific information density and evidence integrity matter more than generic presentation aesthetics.

Its default hierarchy is:

```text
scientific fidelity
      ↓
source visual integrity
      ↓
figures / tables / equations
      ↓
technical mechanism
      ↓
narrative and visual polish
```

V3 adds hard safeguards for two recurring automated-slide failures:

1. **invented or directionally wrong custom flowcharts**;
2. **incomplete/contaminated screenshots of paper figures**.

Key rules include:

- evidence before custom diagrams;
- explicit node/edge specs for directed diagrams;
- arrowhead verification after rendering;
- source-visual acquisition checks for axes, ticks, legends, panel labels, and complete scientific content;
- one hero scientific visual per slide by default;
- canvas-first rather than card/box-first layout;
- no clipping scientific meaning merely to satisfy a slide-count target;
- separate modes for paper reading, lab updates, and technical talks.

This is a **presentation reasoning/QA skill**, not a standalone PPTX renderer. Pair it with the slide-generation/rendering toolchain available in your Codex environment.

See [`skills/academic-research-presentation/README.md`](skills/academic-research-presentation/README.md).

## Quick start

Clone the repository:

```bash
git clone https://github.com/Ethan-ai637/AutoSCI.git
cd AutoSCI
```

Copy one or both skill folders into your Codex skills directory. A common local layout is `$CODEX_HOME/skills/`; when `CODEX_HOME` is not set, many setups use `~/.codex/skills/`.

```bash
mkdir -p "${CODEX_HOME:-$HOME/.codex}/skills"
cp -R skills/scientific-figure "${CODEX_HOME:-$HOME/.codex}/skills/"
cp -R skills/academic-research-presentation "${CODEX_HOME:-$HOME/.codex}/skills/"
```

Then start/reload Codex and invoke the skill explicitly, for example:

```text
Use $scientific-figure to turn the Method section of paper.pdf into an editable Figure 1.
Use standard mode, preserve all mathematical notation, and deliver SVG + target-size PNG.
```

```text
Use $academic-research-presentation to build a 15-slide paper-reading presentation from paper.pdf.
Prioritize the paper's main figures/tables and explain each main result instead of filling slides with cards.
```

More installation notes, including Windows examples, are in [`docs/installation.md`](docs/installation.md).

## Repository layout

```text
AutoSCI/
├── skills/
│   ├── scientific-figure/
│   │   ├── SKILL.md
│   │   ├── STABILITY.md
│   │   ├── references/
│   │   ├── assets/
│   │   ├── scripts/
│   │   └── agents/
│   └── academic-research-presentation/
│       ├── SKILL.md
│       ├── references/
│       ├── templates/
│       ├── examples/
│       └── agents/
├── docs/
├── examples/
├── scripts/
└── .github/
```

The top-level repository is intentionally thin. Each skill remains self-contained so it can be copied into a local skills directory without the rest of AutoSCI.

## Local validation

Run the repository checks:

```bash
python scripts/validate_repo.py
```

For the scientific-figure rendering/export environment:

```bash
python skills/scientific-figure/scripts/doctor.py
```

Most scientific-figure audit scripts use only the Python standard library. Deterministic SVG rendering/export can use CairoSVG or Inkscape; grayscale QA can use Pillow or ImageMagick. `doctor.py` reports what is available locally.

## Design docs

- [`docs/architecture.md`](docs/architecture.md) — why the two skills are separated and how they complement each other.
- [`docs/scientific-figure.md`](docs/scientific-figure.md) — production profiles, artifacts, and QA model.
- [`docs/academic-research-presentation.md`](docs/academic-research-presentation.md) — presentation modes and evidence-first slide design.
- [`examples/prompts.md`](examples/prompts.md) — starter prompts for common research tasks.

## Project status

- **Scientific Figure:** `v2.0.0`, stable production contract. Future production changes should be driven by repeatable benchmark failures rather than feature accumulation.
- **Academic Research Presentation:** `v3.0.0`, current workflow. V3 focuses on diagram safety and complete acquisition of paper figures/tables.

## Acknowledgements and attribution

The Scientific Figure skill is an independent workflow implementation. Its iterative **generate → render → evaluate → refine** philosophy was influenced in part by public ideas around scientific-figure agents such as [ResearAI/AutoFigure](https://github.com/ResearAI/AutoFigure) and [ResearAI/AutoFigure-Edit](https://github.com/ResearAI/AutoFigure-Edit). AutoSCI does **not** bundle their code, model weights, hosted services, or API credentials, and is not affiliated with those projects.

The Academic Research Presentation skill documents its public design references in [`references/08-sources-and-rationale.md`](skills/academic-research-presentation/references/08-sources-and-rationale.md), including scientific communication guidance and public skill-design resources.

AutoSCI is an independent community project and is not an official OpenAI project.

## Contributing

Contributions are welcome. Please read [`CONTRIBUTING.md`](CONTRIBUTING.md). For `scientific-figure`, changes to production behavior should ideally include a reproducible failure case or benchmark evidence; for presentation changes, include the concrete slide failure mode the new rule addresses.

## License

MIT License. See [`LICENSE`](LICENSE).
