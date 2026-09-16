# Scientific visual pattern library

Use these as composition grammars, not templates to copy. Select the pattern that matches the scientific relation graph.

## Parallel branches → aggregation

Use when two or more independently computed signals/representations are combined.

```text
input ─┬─ branch A ─┐
       └─ branch B ─┴─ aggregation ─ output
```

Make the branches visibly parallel and make the aggregation node distinct. Do not serialize the branches unless the method actually does.

## Main path + conditioning lane

Use when one stream is transformed while a secondary signal conditions several stages.

```text
x → stage 1 → stage 2 → stage 3 → y
      ↑           ↑
      └── condition / context ──────┘
```

Keep conditioning visually subordinate. Do not make it look like primary data flow.

## Iterative / recurrent loop

Use only for genuine repeated update, feedback, or recurrence.

```text
state_t → operation → state_t+1
   ↑                    │
   └──── update loop ───┘
```

Use one geometric loop rather than duplicating the same stage many times.

## Overview + mechanism inset

Use when the full system is simple enough for an overview but one local operation is the scientific novelty.

```text
[ system overview ]  ── zoom/callout ──>  [ mechanism detail ]
```

The inset should explain the novelty, not repeat the overview at a smaller scale.

## Before → intervention → after

Use for mechanisms that change a state, representation, distribution, structure, or field.

```text
before state  →  intervention/mechanism  →  after state
```

Prefer scientific objects/states over three generic cards.

## Hierarchy / nested decomposition

Use when relations are containment or abstraction, not temporal flow. Prefer nested regions, tree structure, or indentation. Do not add arrows merely because elements are related.

## Comparison matrix / aligned alternatives

Use when methods or conditions should be compared along common dimensions. Align the same semantic dimension across rows/columns. Avoid disconnected comparison cards.

## Train / inference split

Use when training-only losses, teachers, labels, or auxiliary branches disappear at inference. Share the common path and visually separate phase-specific elements rather than drawing two full duplicated architectures.

## Repeated module / depth

Use stacked motifs, repetition marks, or braces for N identical blocks. Draw individual blocks only when their differences matter.

## Spatial/local-to-global mechanism

Use concentric regions, neighborhood/field views, zoomed local windows, or aggregation from local motifs into a global representation when the science genuinely has spatial/local-global structure. This is usually more informative than a linear flowchart.

## Pattern selection test

Before committing, ask:
1. Does the geometry match the relation types in the semantic graph?
2. Is concurrency shown as concurrency, hierarchy as hierarchy, recurrence as recurrence, and comparison as alignment?
3. Can the main novelty be perceived without reading every label?
4. Would replacing the figure with boxes and arrows destroy meaningful visual information? If not, the grammar may still be too generic.
