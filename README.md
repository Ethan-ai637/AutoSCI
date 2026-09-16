# AutoSCI

<p align="center">
  <img src="assets/readme/autosci-hero-en.webp" alt="AutoSCI — open-source Codex skills for scientific figures and research presentations" width="100%">
</p>

<p align="center"><strong>Spend more time thinking about science, less time formatting it.</strong></p>

<p align="center">
  Open-source, local-first Codex skills for scientific figures, paper reading, group meetings, research updates, and technical presentations.
</p>

<p align="center">
  <a href="README_zh.md">中文</a> ·
  <a href="#quick-start">Quick Start</a> ·
  <a href="#skills">Skills</a> ·
  <a href="CONTRIBUTING.md">Contributing</a>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="MIT License">
  <img src="https://img.shields.io/badge/Scientific%20Figure-v2.0%20stable-2ea44f" alt="Scientific Figure v2.0">
  <img src="https://img.shields.io/badge/Research%20Presentation-v3-blue" alt="Research Presentation v3">
</p>

## Why AutoSCI?

Research time is expensive. Too much of it is still spent on work that is necessary but repetitive: redrawing method diagrams, aligning arrows, rebuilding figures, cropping paper screenshots, arranging slides, checking legends, and repeatedly fixing presentation layouts.

**AutoSCI exists to reduce that mechanical cost.** We want researchers to spend more attention on the scientific question, the method, the experiment, the interpretation, and the next idea — while reusable Codex skills handle more of the tedious production work around scientific communication.

This is not about replacing scientific judgment. It is about removing friction between an idea and a clear scientific artifact.

> **Automate the tedious. Preserve the science. Leave more room for imagination.**

AutoSCI is not a new foundation model and not an API wrapper. It is a collection of explicit, inspectable workflows: structured intermediate artifacts, source-grounding rules, deterministic QA scripts, and render → inspect → refine loops designed for local Codex environments.

## Skills

AutoSCI currently contains two complementary, independently installable skills:

| Skill | Best for | Main output |
| --- | --- | --- |
| [`scientific-figure`](skills/scientific-figure) | Method overviews, architectures, mechanisms, pipelines, taxonomies, conceptual and multi-panel figures | Editable, traceable SVG; optional PDF/PNG release package |
| [`academic-research-presentation`](skills/academic-research-presentation) | Paper reading, group/lab meetings, research updates, technical talks | Evidence-first presentation workflow, slide plan, figure/table usage and QA |

They can be used separately or together. A typical workflow is:

```text
paper / method / results
        │
        ├── need a custom scientific figure?
        │          ↓
        │   $scientific-figure
        │          ↓
        │      editable SVG
        │
        └──────────┬──────────
                   ↓
      $academic-research-presentation
                   ↓
          research presentation
```

## What we want to automate — and what we do not

**Good candidates for automation**

- repetitive figure construction and reconstruction;
- diagram layout, alignment, routing, and export;
- paper-figure/table extraction and completeness checks;
- slide organization and repetitive presentation layout;
- deterministic checks for notation, geometry, clipping, readability, and portability;
- repeated render / inspect / refine cycles.

**Still belongs to the researcher**

- choosing the scientific problem;
- deciding assumptions and methodology;
- validating experiments and evidence;
- interpreting results;
- deciding what claims are scientifically justified;
- making the final communication choices.

The goal is simple: **reduce the mechanical work around research without reducing the researcher’s agency.**

## Scientific Figure — v2.0 Stable

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

Highlights include source-grounded claims, semantic locking, Spec ↔ SVG traceability, anti-"box soup" visual grammar, geometry/notation/legibility/portability audits, `draft` / `standard` / `release` profiles, checkpoint/resume orchestration, and an optional blind benchmark harness.

For quantitative experimental plots, the skill prefers authoritative data + plotting code over visually invented curves.

See [`skills/scientific-figure/README.md`](skills/scientific-figure/README.md) and [`STABILITY.md`](skills/scientific-figure/STABILITY.md).

## Academic Research Presentation — V3

`academic-research-presentation` is designed for research decks where scientific evidence and information density matter more than generic presentation aesthetics.

Its priorities are:

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

V3 specifically addresses two recurring automated-slide failures: invented or directionally wrong custom flowcharts, and incomplete/contaminated screenshots of paper figures. It emphasizes evidence-first slides, complete source visuals, one hero scientific visual per slide by default, canvas-first composition, and rendered QA instead of trusting the source layout blindly.

This is a presentation reasoning/QA skill rather than a standalone PPTX renderer; pair it with the slide-generation toolchain available in your Codex environment.

See [`skills/academic-research-presentation/README.md`](skills/academic-research-presentation/README.md).

## Quick Start

```bash
git clone https://github.com/Ethan-ai637/AutoSCI.git
cd AutoSCI

mkdir -p "${CODEX_HOME:-$HOME/.codex}/skills"
cp -R skills/scientific-figure "${CODEX_HOME:-$HOME/.codex}/skills/"
cp -R skills/academic-research-presentation "${CODEX_HOME:-$HOME/.codex}/skills/"
```

Then reload Codex and invoke a skill explicitly:

```text
Use $scientific-figure to turn the Method section of paper.pdf into an editable Figure 1.
Use standard mode, preserve mathematical notation, and deliver SVG + target-size PNG.
```

```text
Use $academic-research-presentation to build a 15-slide paper-reading presentation from paper.pdf.
Prioritize the paper's main figures and tables, and explain the evidence rather than filling slides with cards.
```

Windows and additional installation notes are in [`docs/installation.md`](docs/installation.md).

## Design Principles

- **Scientific fidelity before aesthetics.**
- **Evidence before decorative diagrams.**
- **Structure before coordinates.**
- **Editable source artifacts before flattened screenshots.**
- **Render, inspect, and refine instead of trusting generation blindly.**
- **Use deterministic scripts for deterministic failure modes.**
- **Add workflow complexity only when a reproducible failure justifies it.**

## Repository Layout

```text
AutoSCI/
├── assets/readme/
├── skills/
│   ├── scientific-figure/
│   └── academic-research-presentation/
├── docs/
├── examples/
├── scripts/
└── .github/
```

Each skill is intentionally self-contained so it can be copied into a local skills directory independently.

## Validation

```bash
python scripts/validate_repo.py
python skills/scientific-figure/scripts/doctor.py
```

Most audits use only the Python standard library. SVG rendering/export can use CairoSVG or Inkscape; grayscale QA can use Pillow or ImageMagick.

## Project Status

- **Scientific Figure:** `v2.0.0`, stable production contract. Future behavior changes should be driven by repeatable benchmark failures rather than feature accumulation.
- **Academic Research Presentation:** `v3.0.0`, focused on evidence-first presentation design, diagram safety, and complete acquisition of paper figures/tables.

## Acknowledgements

The Scientific Figure skill is an independent workflow implementation. Its iterative **generate → render → evaluate → refine** philosophy was influenced in part by public work on scientific-figure agents such as [ResearAI/AutoFigure](https://github.com/ResearAI/AutoFigure) and [AutoFigure-Edit](https://github.com/ResearAI/AutoFigure-Edit). AutoSCI does not bundle their code, model weights, hosted services, or API credentials and is not affiliated with those projects.

The Academic Research Presentation skill documents its public design references in [`references/08-sources-and-rationale.md`](skills/academic-research-presentation/references/08-sources-and-rationale.md).

AutoSCI is an independent community project and is not an official OpenAI project.

## Contributing

Issues and pull requests are welcome. Please read [`CONTRIBUTING.md`](CONTRIBUTING.md). A useful rule for this repository is:

> **A new rule should correspond to a concrete, reproducible failure mode.**

## License

MIT License. See [`LICENSE`](LICENSE).
