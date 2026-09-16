# AutoSCI

**Open-source Codex skills for scientific figures, research presentations, and the repetitive work around research communication.**

> **Spend more time thinking about science, less time formatting it.**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Scientific Figure](https://img.shields.io/badge/Scientific%20Figure-v2.0%20stable-2ea44f)](skills/scientific-figure)
[![Research Presentation](https://img.shields.io/badge/Research%20Presentation-v3-blue)](skills/academic-research-presentation)

**English** · [中文](README_zh.md)

## Why AutoSCI?

Research time is limited. Too much of it is still spent on work that is necessary but repetitive: drawing method diagrams, adjusting arrows and labels, rebuilding figures, cropping paper screenshots, arranging slides, aligning objects, checking whether a legend is missing, and repeatedly polishing a group-meeting deck.

These tasks matter because scientific communication matters. But they should not become the bottleneck that limits how quickly researchers can explore, explain, and share ideas.

**AutoSCI is an open-source collection of local-first Codex skills designed to take part of that production burden off researchers' hands.** Our goal is not to replace scientific thinking or automate away the researcher. It is to make the tedious parts of research communication easier to delegate while keeping scientific meaning under explicit control.

We hope researchers can spend more of their attention on:

- asking better questions;
- developing and challenging new ideas;
- designing stronger experiments;
- understanding unexpected results;
- discussing science with collaborators;
- and imagining better ways to communicate the work.

Instead of spending that same attention nudging boxes by two pixels, redrawing the same pipeline, or rebuilding a presentation the night before a lab meeting.

## What is AutoSCI?

AutoSCI is not a new foundation model and not an API wrapper. It is a growing collection of **research-oriented Codex skills**: explicit workflows, structured intermediate artifacts, deterministic checks, references, scripts, and review/refinement rules that help a local Codex session perform common scientific-production tasks more reliably.

The project currently contains two complementary but independently usable skills:

| Skill | What it helps with | Main output |
| --- | --- | --- |
| [`scientific-figure`](skills/scientific-figure) | Method overviews, architectures, mechanisms, pipelines, taxonomies, conceptual and multi-panel scientific figures | Editable, traceable SVG; optional PDF/PNG release package |
| [`academic-research-presentation`](skills/academic-research-presentation) | Paper reading, lab/group meetings, research updates, technical talks | Evidence-first research presentation workflow for PPTX/slides toolchains |

They can be installed separately or used together.

```text
                    Research idea / paper / project
                               │
                ┌──────────────┴──────────────┐
                │                             │
                ▼                             ▼
       $scientific-figure        $academic-research-presentation
                │                             │
       method / mechanism              paper / group meeting
       architecture / pipeline         research update / talk
                │                             │
                ▼                             ▼
         editable scientific            research-oriented
              figure                      presentation
                │                             ▲
                └──────────────┬──────────────┘
                               │
                     Scientific communication
```

## The principle behind the project

AI can make a figure or a slide look polished while still making the science wrong. AutoSCI therefore treats research artifacts differently from generic graphic design.

Our shared principles are:

- **scientific fidelity before aesthetics**;
- **evidence before decorative diagrams**;
- **structure before coordinates**;
- **figures, tables, equations, and results before generic card layouts**;
- **editable source artifacts before flattened screenshots when possible**;
- **render, inspect, and refine instead of trusting generation blindly**;
- **deterministic checks for failures that should not depend on model judgment**;
- **automation should remove repetitive work, not remove researcher control**.

The goal is not one-click science. The goal is a better division of labor:

```text
Researcher
├── scientific question
├── assumptions and judgment
├── method and experiment
├── interpretation
└── final scientific decisions

AutoSCI + Codex
├── figure construction
├── repetitive layout work
├── slide production
├── source-visual handling
├── deterministic QA
└── iterative presentation refinement
```

## Scientific Figure — v2.0 Stable

`scientific-figure` is a structure-first workflow for creating and reconstructing editable research figures while protecting the underlying scientific semantics.

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

Highlights include:

- source-grounded claims, entities, relations, notation, and invariants;
- semantic locking so visual refinement cannot silently rewrite the method;
- traceability between semantic IDs and SVG entities/relations;
- scientific visual patterns designed to avoid generic AI "box soup";
- geometry, relation-endpoint, notation, final-size legibility, portability, and release audits;
- `draft`, `standard`, and `release` execution profiles;
- checkpoint/resume orchestration for longer workflows;
- optional blind benchmark, regression-suite, and ablation tooling;
- no second image/LLM API is required: the active Codex session can perform planning, SVG generation, and critique.

For quantitative experimental plots, the skill prefers authoritative data and plotting code over visually invented curves.

See [`skills/scientific-figure/README.md`](skills/scientific-figure/README.md) and [`STABILITY.md`](skills/scientific-figure/STABILITY.md).

## Academic Research Presentation — V3

`academic-research-presentation` is designed for the slides researchers actually need: paper reading, lab meetings, group meetings, research updates, proposal discussions, and technical talks.

It prioritizes scientific content over generic presentation templates:

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

V3 specifically addresses two recurring automated-slide failures:

1. invented or directionally wrong custom flowcharts;
2. incomplete or contaminated screenshots of paper figures and tables.

Key rules include:

- evidence before custom diagrams;
- explicit node/edge specifications for directed diagrams;
- arrowhead verification after rendering;
- checks for complete axes, ticks, legends, panel labels, and scientific content;
- one hero scientific visual per slide by default;
- canvas-first rather than card/box-first composition;
- no clipping of scientific meaning merely to satisfy a slide-count target;
- separate reasoning modes for paper reading, lab updates, and technical talks.

This is a **presentation reasoning and QA skill**, not a standalone PPTX renderer. Pair it with the slide-generation/rendering toolchain available in your Codex environment.

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

Then restart/reload Codex and invoke the skills explicitly.

For example:

```text
Use $scientific-figure to turn the Method section of paper.pdf into an editable Figure 1.
Use standard mode, preserve the mathematical notation, and deliver SVG + target-size PNG.
```

```text
Use $academic-research-presentation to build a 15-slide paper-reading presentation from paper.pdf.
Prioritize the paper's main figures and tables, and explain the evidence instead of filling slides with generic cards.
```

More installation notes, including Windows examples, are in [`docs/installation.md`](docs/installation.md).

## Who is this for?

AutoSCI is intended for graduate students, researchers, engineers, and anyone who regularly turns technical work into figures and presentations. You do not need to adopt the entire workflow: each skill is self-contained, and individual references/scripts can also be reused or adapted.

We especially hope it is useful when you are thinking:

- “I understand my method, but I do not want to spend another evening rebuilding Figure 1.”
- “I need to present this paper at group meeting tomorrow.”
- “The result figure is the important part of this slide; why did the generated deck make it tiny?”
- “I want the AI to help with production without inventing scientific relationships.”

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

The top level is intentionally thin. Each skill remains self-contained so it can be copied into a local skills directory without the rest of AutoSCI.

## Local validation

Run repository checks with:

```bash
python scripts/validate_repo.py
```

For the scientific-figure rendering/export environment:

```bash
python skills/scientific-figure/scripts/doctor.py
```

Most scientific-figure audit scripts use only the Python standard library. Deterministic SVG rendering/export can use CairoSVG or Inkscape; grayscale QA can use Pillow or ImageMagick. `doctor.py` reports what is available locally.

## Project philosophy and future skills

AutoSCI is intentionally starting small. We would rather maintain a few workflows that genuinely remove repetitive research work than publish a long list of shallow prompts.

Future skills are welcome when they solve a concrete research workflow well. The long-term direction is simple: **make the mechanical parts of research production easier, while leaving more room for scientific creativity.**

A new feature or rule should ideally correspond to a reproducible failure mode. For the Scientific Figure skill in particular, production changes should be benchmarked instead of accumulated indefinitely.

## Acknowledgements and attribution

The Scientific Figure skill is an independent workflow implementation. Its iterative **generate → render → evaluate → refine** philosophy was influenced in part by public ideas around scientific-figure agents such as [ResearAI/AutoFigure](https://github.com/ResearAI/AutoFigure) and [ResearAI/AutoFigure-Edit](https://github.com/ResearAI/AutoFigure-Edit). AutoSCI does **not** bundle their code, model weights, hosted services, or API credentials, and is not affiliated with those projects.

The Academic Research Presentation skill documents public design references in [`references/08-sources-and-rationale.md`](skills/academic-research-presentation/references/08-sources-and-rationale.md).

AutoSCI is an independent community project and is not an official OpenAI project.

## Contributing

Issues, examples, benchmark cases, workflow improvements, and pull requests are welcome. Please read [`CONTRIBUTING.md`](CONTRIBUTING.md).

If AutoSCI saves you time, one of the most useful contributions is to show what you used it for, where it failed, and what would have made the workflow better for real research.

## License

MIT License. See [`LICENSE`](LICENSE).
