# Mathematical and notation fidelity

Scientific notation is semantic content, not decoration. Do not silently rewrite symbols, signs, subscripts, superscripts, qualifiers, or equation terms for layout convenience.

## Notation registry

For figures containing important notation, add `notation` entries to `figure_spec.json`:

```json
{
  "id": "N1",
  "kind": "symbol",
  "canonical_source": "\\lambda_t",
  "required_svg_text": "λₜ",
  "required": true,
  "source_anchor_ids": ["S2"]
}
```

Use `canonical_source` to preserve the source-side representation (often LaTeX/code) and `required_svg_text` for the exact editable text expected in the SVG. For a short equation, the entire displayed expression may be one notation entry. For a long equation, register the critical tokens/terms whose mutation would change meaning.

`notation` is part of the semantic hash lock. `notation_audit.py` verifies required display strings against editable SVG `<text>` content.

## Rendering strategy

Prefer editable SVG text when the target renderer handles the glyphs reliably. If a trusted equation renderer is required, retain the authoritative LaTeX in the spec and keep a reproducible source asset. Do not convert an equation into an unauditable image merely for convenience.

If a formula is converted to paths, `notation_audit.py` cannot verify its visible characters. Treat this as an author-verification item or keep a text/LaTeX source adjacent to the final package.

## Never normalize away meaning

Examples of forbidden visual "simplification":

- changing `≤` to `<`;
- dropping a minus sign;
- omitting a conditioning variable;
- changing `π_θ` into `π` when parameterization matters;
- changing `A_t^local` and `A_t^global` into two unlabeled `A_t` terms;
- replacing an exact method/dataset/model name with a near synonym.
