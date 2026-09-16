# Source grounding and scientific provenance

A scientific figure is a visual claim surface. Every core claim should be traceable to an authoritative source before layout begins.

## Structured anchors

Use `source.anchors` with stable IDs:

```json
{"id":"S3","locator":"Method §3.2, Eq. (4)","evidence_summary":"The adaptive coefficient combines local and global advantages."}
```

`locator` should make the evidence easy to re-find. Prefer section/equation/table/figure IDs, page + paragraph, code file + line range, data file + columns, or an explicit user-brief item. `evidence_summary` is a concise paraphrase, not a long copied passage.

## Claim support classes

- `direct`: the source explicitly supports the claim.
- `user_provided`: the user explicitly supplied the scientific statement and it is authoritative for this task.
- `inferred`: a reasonable synthesis or interpretation not directly stated by the source.

Core claims must not be merely inferred. If an inferred idea is useful for visual explanation, keep it supporting/optional and make the inference visibly non-authoritative when appropriate.

## What must not happen

Do not convert:
- correlation into causality,
- ordering into data flow,
- shared placement into dependency,
- a reference figure's topology into the current method,
- a convenient visual metaphor into a scientific statement.

If source evidence conflicts, stop and surface the conflict rather than selecting the visually convenient version.

## Grounding audit

Run `scripts/source_audit.py figure_spec.json` before freezing. A frozen spec locks the source anchors and claims together, so later aesthetic edits cannot silently alter provenance.

## Notation provenance

In schema v1.4+, important symbols/equations may consume source anchors through `notation[].source_anchor_ids` even when no standalone scientific claim is attached to that exact anchor. This is intentional: an equation locator can ground exact notation while the surrounding Method paragraph grounds the conceptual claim.

## Source snapshot fingerprints (v1.5)

When the authoritative evidence comes from a concrete local file, optionally record its SHA-256 with `scripts/fingerprint_source.py FILE --id SRC1 --spec figure_spec.json` before semantic freeze. The release stores the fingerprint metadata, not the source file itself. This distinguishes two revisions of a manuscript or dataset that otherwise have the same human-readable name.
