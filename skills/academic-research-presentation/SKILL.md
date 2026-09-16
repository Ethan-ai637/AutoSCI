---
name: academic-research-presentation
description: >
  Create, redesign, and review research presentations for paper reading,
  lab/group meetings, research updates, and technical talks. Optimizes for
  scientific fidelity, source-visual integrity, figure/table explanation,
  technically correct diagrams, evidence-driven narrative, and dense but
  readable academic slides. Explicitly prevents invented flowcharts,
  incomplete paper screenshots, dashboard/card layouts, and presentation
  aesthetics that destroy scientific information.
---

# Academic Research Presentation — V3

## Mission

Produce slides that behave like slides made by a strong researcher:

- source-faithful;
- evidence-driven;
- technically reconstructable;
- figure/table centered;
- dense but readable;
- visually restrained;
- useful for discussion.

Priority order:

1. scientific fidelity;
2. source visual integrity;
3. figure/table communication;
4. correctness of diagrams and causal/process structure;
5. technical mechanism;
6. experimental evidence;
7. narrative argument;
8. scientific information density;
9. readability;
10. aesthetics.

A beautiful slide with a wrong arrow, invented dependency, clipped axis, or
incomplete source figure is a FAILED slide.

## Supported modes

### PAPER_READING
Paper presentation / literature seminar / reading group.

Default arc:
problem → gap → evidence/observation → method → mechanism → experiment design
→ main results → ablation/analysis → limitation → discussion / our work.

Method + experiments should normally dominate.

### LAB_UPDATE
Group meeting / advisor meeting / weekly research update.

Default arc:
question → hypothesis → experiment → result → diagnosis → failed attempt /
uncertainty → next discriminating experiment → decision.

New evidence dominates. Negative results are first-class evidence.

### TECHNICAL_TALK
Conference-like technical talk.

Prioritize one memorable scientific argument and strongest evidence.
Move secondary details to backup.

## Required references

Read before building:

1. `references/01-core-principles.md`
2. mode guide:
   - `references/02-paper-reading.md`
   - `references/03-lab-update.md`
3. `references/04-figure-table-first.md`
4. `references/05-slide-grammar.md`
5. `references/06-design-system.md`
6. `references/07-qa-rubric.md`
7. `references/09-diagram-safety.md`
8. `references/10-source-visual-acquisition.md`

Use `references/08-sources-and-rationale.md` for rationale.

# NON-NEGOTIABLE RULE 1 — Evidence before diagrams

Do NOT create a flowchart merely because a slide is about a method.

Preferred order:

1. source method figure, if clear and faithful;
2. source algorithm/equation/table;
3. faithful reconstruction from explicitly verified method steps;
4. simple direct text + arrows;
5. only then a custom flowchart.

A custom diagram MUST pass the Diagram Safety Gate in
`references/09-diagram-safety.md`.

If the scientific relation is uncertain, do not draw an arrow.

# NON-NEGOTIABLE RULE 2 — No invented linear pipelines

Never compress a method into:

A → B → C → D

unless the source actually establishes that ordered dependency.

Important side inputs, historical data, training-only inputs, feedback,
calibration windows, or frozen components must not disappear merely to make
the diagram cleaner.

A visually elegant but scientifically incomplete pipeline is worse than
a denser correct explanation.

# NON-NEGOTIABLE RULE 3 — Source figures must be semantically complete

A paper screenshot is NOT automatically a figure asset.

Do not place arbitrary PDF page crops into slides.

Every source visual MUST pass the Source Visual Acquisition Gate:

- full scientific plot/panel visible;
- relevant x/y axes visible;
- tick labels visible;
- legend visible when needed;
- panel labels visible;
- no clipped curves/bars/heatmaps;
- no partial paper body text;
- no partial caption fragments;
- no journal running header/author fragment unless inherently part of figure;
- no unexplained crop that removes comparison conditions.

Semantic completeness is more important than a clean-looking crop.

If a clean complete crop cannot fit:
- split the figure across slides;
- use one panel per slide;
- reconstruct faithfully from exact data;
- or allocate more slide area.

Never crop scientific meaning to satisfy a pre-decided slide count.

# NON-NEGOTIABLE RULE 4 — One hero visual per slide by default

For Tier-A evidence, default to one main scientific visual per slide.

Two main figures may share a slide ONLY when:
- direct side-by-side comparison is the scientific argument;
- both remain fully readable;
- neither requires clipping;
- axes/legends remain visible.

Otherwise split into two slides.

Do not squeeze two paper figures onto one slide to save slide count.

# NON-NEGOTIABLE RULE 5 — Canvas-first, not box-first

Default decorative container count on ordinary research slides: 0.

A box is justified only when its boundary itself carries scientific meaning:
module, memory, environment, processing stage, explicit group, highlighted
region, or other real semantic object.

Text does not need a rectangle.

If a slide contains >=3 large text cards, review and normally redesign.

# NON-NEGOTIABLE RULE 6 — Directional diagrams must be mechanically verified

For left-to-right languages, default process direction is LEFT → RIGHT.

For every directed diagram:
- declare `flow_direction`;
- write an explicit edge list `source -> target`;
- build arrowheads at TARGET;
- render the slide;
- visually verify every arrowhead;
- verify that the spatial order matches the logical order.

A reversed arrow is a hard failure.

Feedback/backward arrows are allowed only when the scientific process actually
contains feedback and the loop is labeled.

# Scientific-object-driven design

Choose the dominant object before layout:

figure | table | equation | algorithm | architecture | qualitative example |
diagnostic plot | comparison | text-only only when necessary.

The dominant object determines the layout.

Never begin by selecting:
- three cards;
- four panels;
- dashboard grid;
- infographic template.

# Figure/Table-first for PAPER_READING

Before storyboarding identify:

- MAIN_METHOD_FIGURE
- MAIN_RESULT_FIGURE_OR_TABLE
- MAIN_ABLATION_OR_ANALYSIS
- 2–5 HERO_EVIDENCE items

Do a `Visual Inventory` before slide planning.

The main evidence should receive substantial canvas area and speaking time.

# Scientific information density

Do not optimize word count.

Optimize compatible scientific information units:

claim + evidence + comparison + number + annotation + interpretation + caveat
+ provenance.

High density does NOT mean tiny text.
High density does NOT mean a screenshot of a whole paper page.

# Mandatory workflow

## Phase A — Source inspection
Read paper/report/notes/supplement/repository/results and existing visuals.

## Phase B — Evidence ledger
Use `templates/evidence-ledger.md`.

## Phase C — Visual inventory
Use `templates/visual-inventory.md`.

For every Tier-A/B source visual determine acquisition method:
- embedded extraction;
- exact panel crop;
- faithful reconstruction;
- original image asset.

Do NOT postpone figure extraction until slide layout.

## Phase D — Source visual preflight
Acquire important visuals into an asset workspace BEFORE slide generation.

For every acquired visual:
1. render/open the asset by itself;
2. check semantic completeness;
3. check for page/caption/header contamination;
4. check resolution;
5. record pass/fail in `templates/source-visual-preflight.md`.

Only PASS assets may enter the main deck.

## Phase E — Argument / storyboard
Use `templates/storyboard.md`.

Every substantive slide declares:
- scientific question;
- assertion/message;
- dominant scientific object;
- source/evidence;
- acquisition status if using source visual;
- visual treatment;
- reading path;
- interpretation;
- caveat;
- transition.

Any custom diagram also declares:
- necessity;
- source basis;
- node list;
- edge list;
- flow direction;
- side inputs;
- feedback;
- diagram verification status.

## Phase F — Build
Use base PPTX/slides tooling for implementation.

Prefer native editable tables/plots when exact data are available.
Prefer original source visual when reconstruction risks scientific distortion.

For nontrivial equations use proper equation rendering (e.g. LaTeX/SVG or
equivalent), not approximate plain-text Unicode composition.

## Phase G — Render ALL slides
Never approve from source code alone.

## Phase H — Mechanical QA
Clipping, overlap, fonts, images, equations.

## Phase I — Scientific visual QA
Inspect every source figure/table/chart at full slide render size.

## Phase J — Diagram QA
Trace each directed path from source to destination.
Check arrowheads and semantics.

## Phase K — Anti-dashboard QA
Remove unjustified boxes/cards/panels.

## Phase L — Narrative QA
Read titles only; verify scientific argument and transitions.

# Titles

Prefer message-oriented titles.

Weak:
“Results”

Strong:
“Denser quantile grids reduce price forecast error in the QR setting”

Do not overclaim beyond evidence.

# Source visual handling

Paper page furniture must not leak into figure crops.

Forbidden crop artifacts include:
- partial author names;
- journal title fragments;
- page numbers;
- partial captions;
- surrounding body text;
- severed axis labels;
- clipped legends;
- plots cut off at top/bottom.

If any appear, reacquire the visual.

# Flowchart necessity test

Before making a diagram ask:

1. Is there a real process/dependency to explain?
2. Is this better explained by an existing source figure?
3. Can every node be tied to the source?
4. Can every edge be justified?
5. Are side inputs omitted?
6. Is sequence direction unambiguous?
7. Does a diagram add understanding beyond a sentence/table?

If answers 3–6 are not confidently satisfied, do not make the flowchart.

# Figure explanation protocol

For every major visual:

1. scientific question;
2. reading grammar;
3. where to look;
4. literal observation;
5. interpretation;
6. caveat.

Annotate evidence directly where helpful.

# Tables

For important tables explicitly preserve:
- metric + direction;
- strongest baseline;
- proposed method;
- relevant columns;
- uncertainty when present;
- exceptions;
- exact values.

Rebuild from exact data when practical.

# LAB_UPDATE

Do not make “progress report cards.”

Show:
- plots;
- tables;
- failure traces;
- diagnostic examples;
- experiment configurations;
- uncertainty;
- next discriminating tests.

A failed experiment with a useful diagnosis is stronger content than a polished
“completed tasks” slide.

# Hard failures

Do NOT deliver if any of the following occur:

- reversed process arrows;
- invented method dependency;
- diagram omits a scientifically necessary side input and thereby changes meaning;
- incomplete hero figure;
- clipped axis/legend/panel;
- journal/header/caption fragments inside a supposed figure asset;
- fabricated values/citations;
- misleading crop;
- unreadable main evidence;
- important equations rendered incorrectly;
- deck dominated by card grids;
- results summarized in prose while source evidence is available but absent.

# Definition of done

The deck is finished only when:
- claims are traceable;
- source visuals pass preflight;
- hero visuals are complete and readable;
- diagrams pass edge-direction and semantic checks;
- method is reconstructable;
- results/ablations are visible and explained;
- boxes are rare and semantic;
- all slides have been rendered and inspected;
- scientific QA passes.
