# Scientific figure design system

## Hierarchy

Design for three levels: (1) message/spine at thumbnail size, (2) main mechanism at normal use size, (3) supporting detail on inspection. If all elements share the same size, stroke, fill, and weight, hierarchy has failed.

## Anti-box-soup rule

A container is justified only for a real module, state, subsystem, region, or grouping. Text alone does not justify a box.

Before adding a box, test proximity, shared baseline, lane/band, brace, repeated motif, direct annotation, boundary around a true subsystem, or an inset.

Warning signs:
- >7 equally prominent containers in one panel
- every noun becomes a rounded card
- arrows connect box centers without scientific visual meaning
- container padding dominates canvas area
- deleting box text destroys all visual meaning

## Panel decomposition

Split by scientific question/job, not by equal visual quadrants. Share encodings across panels. Avoid repeating legends/titles. Prefer one dominant panel plus supporting panels when the method has a clear center of gravity.

## Composition

Use a dominant reading path. Left→right usually suits processes/architectures; top→bottom suits hierarchy/causality; cycles only suit true recurrence/feedback. Keep outer margins and panel gutters larger than internal gaps. Avoid long diagonal connectors and unnecessary crossings.

## Typography

Use one type family by default and 2–3 sizes. Keep labels short and sentence case unless convention requires otherwise. Do not solve overcrowding by continuously shrinking fonts; simplify, widen, or split instead.

The target-size render is authoritative for readability. A label that works only in the high-resolution preview fails.

## Color

Start with grayscale + 1–3 semantic accents. Use color consistently and never as the sole carrier of a crucial distinction when avoidable. Avoid rainbow palettes unless encoding a genuine ordered scalar. Avoid decorative gradients by default.

## Relations

Use visual style semantically:
- solid arrow: primary directed flow/relation
- dashed arrow: only for source-justified secondary/optional/indirect relation
- line without arrow: association/shared boundary
- double arrow: genuinely bidirectional relation

Do not invent semantic differences to make the figure look varied.

## Scientific motifs

Prefer domain-appropriate visual abstractions—tensor stacks, token sequences, distributions, grids, trajectories, spatial fields, layered materials, networks, signal traces, state snapshots, repeated blocks—when supported by the source. Use generic UI cards only when the scientific object truly is a bounded module.

## Connectors

Keep arrowheads visible and off text. Route around labels and primary objects. Use orthogonal routing for modular architectures when appropriate; use curved paths only when they improve disambiguation. Avoid spaghetti edges; introduce lanes, ports, aggregation nodes, or panel decomposition instead.

## Reference transfer

Transfer only a compact style fingerprint: background, palette roles, stroke character, typography hierarchy, density, icon abstraction, panel labels, connector language, whitespace rhythm. Do not transfer topology or distinctive artwork.

## Physical-size typography

Reason in physical output size, not raw SVG px. Record intended `target.width_in` (or `width_mm`) and `min_text_pt` in the spec. A nominal 18-unit SVG label can become unreadably small when a wide viewBox is scaled into a paper column. Use `target_legibility.py` as a hard preflight signal, then verify the target render visually.

Do not fix failed point size by blindly enlarging every label. First reduce text, remove low-value annotations, widen the target placement if allowed, or restructure the panel.

## Layout tournament before polish

For medium/high-complexity figures, do not let coordinate work lock in the first plausible structure. Compare low-fidelity candidates that preserve identical semantics but use different macro grammars. Select on semantic risk, reading clarity, edge complexity, density, and novelty emphasis before fine styling.

## Redundant semantic encoding

If color carries a scientific distinction, pair it with a non-color channel when the target may be printed, projected poorly, or viewed with color-vision differences. Good redundancy: direct labels + position, line style + marker, shape + label, pattern + boundary. Do not create redundant decorative signals that imply extra science.
