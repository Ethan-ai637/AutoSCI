# Geometry contract

Deterministic geometry checks complement visual inspection. They do not replace the render critic.

## Entity semantic bounds

For each important entity group, record its intended root-viewBox footprint:

```xml
<g id="entity-E1" data-entity-id="E1" data-bounds="80 120 240 96">
  ...
</g>
```

`data-bounds` is `x y width height` in root `viewBox` coordinates, after any layout decision. Prefer generating important entity geometry directly in root coordinates. If transforms are used internally, `data-bounds` must still be expressed in root coordinates.

The bound should cover the meaningful visual object, including its label, but not unrelated whitespace. It is an audit annotation, not a replacement for the visible SVG shape.

## Relation route

Put the visible connector inside the traceable relation group and mark the principal route when the group contains multiple paths:

```xml
<g id="relation-R1" data-relation-id="R1" data-relation-type="flow"
   data-source-id="E1" data-target-id="E2">
  <path data-route="true" d="M 320 168 C 380 168, 410 168, 470 168"
        marker-end="url(#arrow)"/>
</g>
```

`geometry_audit.py` supports ordinary `path`, `line`, and `polyline` routes. Keep the main semantic route simple enough to audit even if decorative micro-paths are more complex.

## What the deterministic audit checks

When `qa.geometry_audit` is `required`, primary entities must expose valid semantic bounds. The audit checks:

- semantic bounds remain inside the SVG viewBox;
- unrelated primary semantic bounds do not overlap beyond the configured ratio;
- relation route endpoints remain near the bounds of the declared source/target entities;
- directed relations use source→target endpoint orientation;
- relations expose a parseable principal route.

Intentional containment is exempt from the primary-overlap rule when represented by an explicit `contains` relation. Group/annotation entities are also excluded from that overlap gate.

## Limits

The geometry contract cannot prove that text is not visually colliding with every path or that a routing choice looks elegant. Visual QA on actual renders remains mandatory. If `data-bounds` no longer matches the visible object after an edit, update it as part of the same edit; stale audit metadata is a defect.
