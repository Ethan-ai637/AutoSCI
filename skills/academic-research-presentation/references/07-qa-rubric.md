# QA Rubric — V3

Run after rendering ALL slides.

## A. Mechanical QA
Fail:
- clipped text;
- unintended overlap;
- missing image;
- broken font;
- broken equation;
- low-resolution hero image.

## B. Scientific fidelity — must be 5/5
Fail:
- invented values;
- invented citations;
- invented dependencies;
- misleading omission/crop.

## C. Source visual integrity — must be 5/5 for Tier-A evidence
Check every source figure:
- axes complete?
- labels complete?
- legend complete?
- heatmap scale complete?
- data region complete?
- panel label complete?
- no partial author/journal/caption/body fragments?
- source traceable?

Any clipped hero visual = hard fail.

## D. Diagram correctness — must be 5/5
For every custom directed diagram:
- diagram was necessary;
- node provenance verified;
- edge provenance verified;
- flow direction declared;
- arrowhead at target;
- side inputs represented;
- feedback only if real;
- training/inference not conflated.

ANY reversed forward arrow = hard fail.

## E. Figure/Table communication — 0–5
5: main evidence dominates, readable, annotated, explained.
0: screenshot dumping or evidence absent.

## F. Technical depth — 0–5
Can audience reconstruct mechanism?

## G. Evidence quality — 0–5
Are claims connected to actual evidence?

## H. Scientific information density — 0–5
Dense with compatible scientific objects, not cards.

## I. Anti-dashboard — 0–5
Target 5:
- decorative containers rare;
- hierarchy from evidence/type/space;
- no repeated card grids.

Trigger review if >=3 large text cards.

## J. Narrative — 0–5
Titles reconstruct the argument.

## K. Lab usefulness — 0–5 for LAB_UPDATE
Does evidence expose uncertainty and enable decisions?

# Visual red flags

Hard or near-hard failures:
- reversed arrow;
- full/partial paper page screenshot used as figure;
- journal header/author fragment around figure;
- missing x/y axis;
- plot cut off by crop;
- missing legend needed to interpret;
- multiple unreadable figures squeezed on one slide;
- screenshot caption fragment;
- figure tiny because text cards consume canvas;
- nontrivial equation typed approximately as plain text;
- experiment discussed without displaying available evidence.

# Final thresholds

Scientific fidelity = 5
Source visual integrity = 5 for Tier A
Diagram correctness = 5
No other core category below 4.
