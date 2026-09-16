# Two-pass render-based critic rubric

Judge rendered output, not SVG source alone. Run semantic and visual audits separately to reduce self-confirming critique.

## Pass A — semantic audit

Compare authoritative source + `figure_spec.json` + rendered figure.

### A1. Scientific correctness — hard target >= 9/10
Verify relation direction/type, equations/symbols, model/dataset names, stage order, causal language, feedback paths, panel implications, and visual encodings. Any major scientific error blocks release.

### A2. Completeness — hard target >= 8/10
Check required claims, entities, relations, conditioning/loss/feedback paths, and labels. Missing a core component is a blocker.

### A3. Evidence discipline
Verify that no visible quantitative result, uncertainty, dimension, trend, relation, or annotation was invented. Verify reference-derived style did not import reference-derived science.

Record evidence, not only scores. Name relevant claim/relation/entity IDs for blockers.

## Pass B — visual audit

### B1. Legibility and integrity — hard target >= 8/10
Inspect both high-resolution and target-size renders: no clipping, overlap, broken glyphs, hidden arrowheads, pixelated assets, illegible labels, or ambiguous connector attachment.

### B2. Visual hierarchy
Can the main story be understood in 5–10 seconds? Is there a dominant spine/object? Are supporting details subordinate?

### B3. Reading order and implication
Does visual order match intended logical order? Could proximity, panel order, color, or arrow routing falsely imply a relation?

### B4. Geometry/layout
Check alignment, spacing, balance, margins, panel rhythm, grouping, and connector routing.

### B5. Scientific visual grammar
Does the form match the science? Penalize generic card/flowchart grammar when a tensor path, cycle, hierarchy, comparison matrix, spatial mechanism, repeated motif, or inset better represents the phenomenon.

### B6. Information density
Penalize both giant sparse boxes and unreadable density. Every major element must earn its space.

### B7. Style consistency
Check typography, palette roles, stroke widths, corners, arrow language, icon abstraction, and panel labels.

### B8. Publication/use readiness
Check aspect ratio, target-size readability, vector cleanliness, grayscale robustness when relevant, excess decoration, and caption/title convention.

## Critic output

Use `assets/critic.template.json`. Every high-priority defect needs a location, evidence, and surgical fix. Avoid vague feedback such as “make cleaner.”

## Iteration discipline

Iteration 1: semantics + macro grammar. Iteration 2: routing + density + target-size typography. Iteration 3: consistency + fine geometry. Continue only when a named high-priority defect remains and the next edit has a clear expected benefit.

## Regression audit

After iteration 1, every critique must include a regression check: previously correct semantics, previously resolved defects, and geometry that should remain stable. A refinement that fixes one issue while reviving an earlier blocker is not progress.

If the same macro-layout/hierarchy problem persists across two targeted iterations, stop micro-adjusting coordinates. Return to the layout plan and choose a different grammar from `pattern_library.md`.

## Source-provenance check (v1.3)

For every visible core scientific assertion, identify the supporting claim ID and source anchor ID. If the critic cannot point to support, treat the content as unsupported even when it looks plausible. Core claims marked `inferred` are blockers.

## Robustness check (v1.3)

When `target.grayscale_safe` is true, inspect the grayscale target preview. Verify that branch identity, state, category, or emphasis does not disappear when hue is removed. Metadata checks catch color-only encodings, but visual inspection is still required for contrast and distinguishability.
