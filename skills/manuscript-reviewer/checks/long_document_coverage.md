# Long-document coverage checkpoints

Use this module to prevent **locality bias**: a review may be internally correct for the pages it inspected while still missing material evidence, qualifications, or contradictions elsewhere in a long manuscript.

This module governs *where coverage must be established*. It does not create finding quotas and it does not require equal attention to every page.

## Core principle

A manuscript is not adequately reviewed merely because its abstract, main table, and conclusion were checked.

For long or structurally complex papers, maintain an internal **section-coverage ledger** so that central claims, primary result objects, definitions, and qualifications are not evaluated from a narrow subset of the manuscript.

Coverage is claim-driven and object-driven, not page-count-driven.

## Section-coverage ledger

For each material manuscript region, record internally:

- section/subsection or page range;
- functional role: framing / method / experiment / result / discussion / limitation / appendix / supplement;
- coverage state;
- central claims encountered;
- primary result objects encountered;
- definitions/protocol details encountered;
- unresolved dependencies that point elsewhere.

Use these coverage states:

- `checked` — inspected to the level required by the selected review mode;
- `partial` — inspected, but some material dependency remains unresolved;
- `blocked` — relevant material is unavailable, unreadable, or missing from the accessible package;
- `not_material` — present but not consequential to the selected review scope.

Do not use section-coverage states as scientific severity labels.

## Mandatory checkpoints

### Checkpoint C0 — Structure map

Before deep review, identify:
- all top-level sections;
- appendices/supplements referenced by the body;
- all primary tables/figures/equations;
- where evaluation protocol, datasets/populations, and limitations are defined.

If document parsing makes the structure uncertain, inspect the rendered table of contents/headings where available.

### Checkpoint C1 — Central narrative sweep

Inspect the surfaces where central claims are typically stated:
- title;
- abstract;
- introduction/contributions;
- discussion;
- conclusion;
- limitations.

Map central claim variants before deciding their final scope.

### Checkpoint C2 — Primary result sweep

For every primary result object, inspect:
- the object itself;
- caption/notes/legend;
- surrounding results text;
- the protocol/setup needed to interpret it;
- later discussion/conclusion statements that rely on it.

Do not treat a table/figure as self-interpreting if its meaning depends on definitions elsewhere.

### Checkpoint C3 — Method and definition dependency sweep

For every central claim whose interpretation depends on method details, verify the relevant:
- definitions;
- notation;
- population/data construction;
- training/evaluation setup;
- comparator selection;
- assumptions;
- statistical procedure.

Do not infer these from the result section if they are defined elsewhere.

### Checkpoint C4 — Appendix/supplement dependency sweep

When the main text explicitly delegates evidence, derivation, protocol detail, robustness analysis, proofs, or additional experiments to an appendix/supplement, inspect that material if available before declaring evidence missing.

If unavailable, use a coverage gap rather than a defect unless the manuscript body itself is demonstrably insufficient for the claim it makes.

### Checkpoint C5 — Pre-closure unresolved sweep

Before review closure, revisit every `partial` section whose unresolved dependency is connected to:
- a central claim;
- a primary result object;
- a Major/Critical candidate;
- a `missing_required_evidence` judgment;
- a material author query.

Resolve it to `checked`, `blocked`, or an explicit coverage gap where possible.

## Mode-specific burden

### Compact

Do not require whole-document section coverage. At minimum cover:
- central narrative surfaces;
- primary result objects;
- directly linked method/protocol sections.

State the reduced scope when material.

### Standard

Cover all sections that materially affect central claims or primary result interpretation. Peripheral related work and low-risk appendix material may remain `not_material` if they do not bear on the audit.

### Exhaustive

Cover all substantive sections and all appendices/supplements available in the package, while still prioritizing scientifically consequential content.

## Re-entry rule

Coverage is not strictly linear. If a later section changes the interpretation of an earlier claim or result, re-enter the earlier item and update its ledger state, evidence mapping, or disposition.

Examples:
- a limitation section narrows an abstract claim;
- an appendix reveals that a headline baseline used a different split;
- a methods footnote defines an aggregation different from what the results prose implied.

Do not freeze a finding simply because it was created earlier in the reading order.

## Anti-patterns

Do not:
- infer whole-paper completeness from reading only the first/last sections;
- equate percentage of pages read with scientific coverage;
- require equal inspection depth for every section;
- treat `partial` coverage as evidence of a defect;
- declare evidence missing before following explicit appendix/supplement pointers;
- keep an early finding unchanged after later evidence resolves or reframes it.
