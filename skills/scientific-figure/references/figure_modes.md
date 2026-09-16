# Figure modes

Choose one primary mode. Hybrid figures are allowed, but one grammar must dominate.

## Method overview / system architecture

Show the main data/control path first. Use 3–7 primary conceptual units. Express internal detail through nested substructure, repeated motifs, annotations, or insets rather than turning every substep into an equal card. Make inputs and outputs visually distinct from processing modules.

## Process / algorithm pipeline

Use stages only when sequence matters. Prefer a strong directional spine with compact stage annotations. If the algorithm loops, show the loop geometrically instead of duplicating stages. Distinguish control flow from data flow when both are present.

## Mechanism / conceptual explanation

Show the transformation or mechanism as the dominant visual, not the names of components. Use before/after states, spatial or causal relationships, magnified insets, field/region encoding, or local annotations. Avoid generic flowchart grammar unless the phenomenon really is a flowchart.

## Model architecture

Treat tensors/data representations and repeated modules as first-class visual elements. Use repetition marks or grouped stacks for repeated blocks. Put losses, conditioning signals, skip connections, and auxiliary branches in secondary visual lanes. Label dimensions only when supported and useful.

## Taxonomy / comparison / design space

Use consistent axes of comparison. Prefer aligned rows/columns, trees, matrices, or nested regions. Do not use a random cluster of cards. If categories overlap, avoid a tree that falsely implies exclusivity.

## Multi-panel scientific story

Assign each panel a job and reading order. A common pattern is: (a) problem/context, (b) proposed method, (c) internal mechanism, (d) consequence or evaluation setup. Maintain shared encodings across panels. Do not repeat titles or legends unnecessarily.

## Quantitative result figure

Do not invent or visually approximate data. Locate the authoritative table/CSV/log/dataframe first. Generate charts from data with a plotting library (Matplotlib or the project's established stack), preserving exact values and uncertainty. Export chart panels as SVG/PDF when possible and compose them with annotations only after the plot is correct.

Use line charts for ordered/time/step trends, bars for discrete comparison, scatter for relationships, heatmaps for dense matrices, box/violin plots for distributions, and uncertainty bands/error bars only when uncertainty values exist. Never infer error bars.

## Reconstruction / redesign

First create a semantic spec from the existing figure and its source context. Separate what must remain invariant (scientific content, labels, data, panel mapping) from what may change (spacing, hierarchy, typography, palette, icon simplification). Redesign without silently changing evidence.
