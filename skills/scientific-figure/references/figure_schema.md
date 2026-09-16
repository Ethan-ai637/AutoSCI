# Figure semantic contract and traceability

Treat a scientific figure as a typed graph + evidence links + reading plan, not as a collection of boxes.

## Required concepts

### `message`
One sentence stating what the reader should understand in 5–10 seconds. It is not the caption.

### `source` and `source.anchors`
Record the authoritative origin. In schema v1.3, anchors are structured objects with stable IDs, precise locators, and concise evidence summaries. See `source_grounding.md`.

### `claims`
Each claim gets an ID (`C1`, `C2`, ...), concise text, priority, `support` class, and `source_anchor_ids`.

Support classes:
- `direct`: explicitly supported by the source.
- `user_provided`: explicitly supplied as authoritative by the user.
- `inferred`: synthesis/interpretation; never use as an unsupported core claim.

### `entities`
Each visible scientific entity gets an ID (`E1`, ...), type, label, importance, and optional supporting claim IDs. Common types: `input`, `output`, `module`, `state`, `variable`, `dataset`, `loss`, `agent`, `environment`, `stage`, `group`, `annotation`.

### `relations`
Each relation gets an ID (`R1`, ...), source entity, target entity, type, optional label, and supporting claim IDs.

Use types deliberately:
- `flow`: information/material/control moves
- `causes`: source explicitly asserts causality
- `depends_on`: dependency without causal claim
- `contains`: structural nesting
- `maps_to`: representation/transformation mapping
- `compares_with`: symmetric comparison
- `feeds_back`: explicit feedback loop
- `precedes`: order/time only
- `shares`: shared resource/parameter

Never upgrade `depends_on` to `causes` for visual convenience.

### `notation`
For mathematically or terminologically sensitive figures, register canonical source notation plus the exact editable SVG display text. Notation is source-grounded and included in the semantic hash. See `math_fidelity.md`.

### `required_labels`
Preserve exact spellings for variables, equations, model/dataset names, stages, and terminology. Store labels as objects with IDs when practical so they can be audited.

### `invariants`
List scientific facts the visual refinement process may not change: topology, relation direction, equation form, stage ordering, panel mapping, data values, uncertainty, etc.

### `forbidden_inferences`
List plausible-looking but unsupported statements that the generator must not encode.

### `panels`
Each panel needs an ID and scientific role. A panel should answer a question or perform a job, not merely hold content.

### `visual_encodings`
Declare semantics carried by appearance. In v1.3, add `channels`, e.g. `shape`, `direction`, `position`, `label`, `line-style`, `pattern`, `color`. When `target.grayscale_safe` is true, a scientific distinction may not use only color-family channels.

### `semantic_status`
Use `draft` while extracting science and `frozen` once verified. If scientific meaning changes after freeze, update the spec first and document the reason.

## QA metadata

Schema v1.4 adds a non-semantic `qa` block for deterministic layout tolerances. `qa.geometry_audit` may be `required`, `recommended`, or `off`; use `required` for normal publication figures. Schema v1.5 adds `qa.portability_audit` plus explicit external-resource/raster/font-fallback policies. QA tolerances are deliberately not part of the semantic hash.

Schema v1.5 also permits `source.artifacts`: optional SHA-256 fingerprints for the exact PDF/data/code files used as authoritative inputs. Because `source` is semantic, these fingerprints are included in the freeze lock. Create them with `fingerprint_source.py` before freezing.

## SVG traceability convention

Important objects should map back to the spec:

```xml
<g id="entity-E3" data-entity-id="E3" data-bounds="80 120 240 96">...</g>
<g id="relation-R2" data-relation-id="R2" data-relation-type="depends_on"
   data-source-id="E1" data-target-id="E3">...</g>
<g id="panel-B" data-panel-id="B">...</g>
```

Decorative micro-elements need no semantic IDs. The goal is auditability, not tagging every path.

## Semantic verification

Before drawing, verify every relation and required label against the source. After rendering, verify again visually: arrowhead placement, proximity, panel order, color, and grouping can imply semantics not apparent from SVG structure alone.

## Semantic hash lock

Freezing is executable, not rhetorical. `scripts/freeze_spec.py` hashes the semantic fields—including source anchors and claims—and stores the digest in `semantic_lock`. `preflight.py` rejects a frozen spec whose semantic content no longer matches the lock. Scientific changes require explicit unlock → verify/edit → re-freeze.

## Claim coverage

Core claims should be represented by at least one entity or relation through `claim_ids`. A claim in the spec that maps to no visual object is a warning: either it does not belong in the figure or the figure is incomplete. `source_audit.py` independently checks whether claims themselves are grounded.


## Schema v1.6: workflow profile

Schema v1.6 adds a non-semantic `workflow` block. `workflow.profile` is `draft`, `standard`, or `release`; the default template uses `standard`. `workflow.layout_tournament` is `auto|on|off`, and `workflow.max_refine_rounds` is 1–5. These fields control execution cost and QA routing and are deliberately excluded from the semantic hash. See `workflow_profiles.md`.

Legacy schema <=1.5 specs that omit a workflow profile retain the prior release-strict integrated preflight behavior.
