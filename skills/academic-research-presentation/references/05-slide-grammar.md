# Scientific Slide Grammar — V3

Choose grammar from the scientific object, not from a visual template.

## G1 Problem / Gap
Prefer concrete evidence/example + diagnosis.
Do not use “three challenges” cards.

## G2 Source Method Figure
Use the paper's main method figure when it is faithful and readable.
Adapt/crop only under Source Visual Acquisition rules.
This is preferred over inventing a new flowchart.

## G3 Verified Process Diagram
Use only after Diagram Safety Gate.
Show verified components, side inputs, labeled transformations, and correct arrows.
One diagram overview per short deck is usually enough.

## G4 Mechanism Zoom-in
Use a verified submodule + equation/update rule + input/output labels.

## G5 Equation + Intuition
Equation large and properly rendered.
Variables close to symbols.
Intuition below/beside.
No decorative equation card.

## G6 Iterative Loop
Only when a real loop exists.
Explicitly show state_t, update, state_t+1, feedback, and what changes.
Verify arrow direction after render.

## G7 Algorithm Walkthrough
Pseudocode + highlighted lines + explanation.
Do not convert algorithm into generic boxes.

## G8 Main Result Table
Assertion title + large table + baseline/ours + delta + observations + citation.

## G9 Main Result Plot
Assertion title + complete plot + direct labels + 1–3 annotations + source.

## G10 Ablation
Table/plot + component change + measured effect + mechanism implication.

## G11 Comparison
Aligned mechanism/table/process comparison.
Cards only if categories themselves are the scientific content.

## G12 Qualitative Evidence
Readable examples, direct highlights, success/failure labels, interpretation.

## G13 Failure / Limitation
Concrete failure evidence + explanation + scope.
No ritual “three limitations” cards.

## G14 Experiment Setup
Compact table/timeline/diagram containing only variables needed to interpret results.
Do not connect unrelated metadata boxes with arrows.

## G15 Lab Diagnostic
Aligned plots on shared scale + annotations + competing hypotheses + next test.

## G16 Decision / Next Experiment
Evidence summary + alternatives + decision criterion.
No pricing-card layout.

## G17 Takeaway
3–5 precise findings, optionally one miniature summary visual.
Text may be direct on canvas.

# Selection rules

- If source visual already explains the method, prefer G2 over G3.
- If a flowchart would omit important side inputs, use G4/G5/G7 instead.
- If two figures do not form a direct comparison, do not combine them merely to
  reduce slide count.
- If a source figure is incomplete after crop, fix acquisition before layout.
