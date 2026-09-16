# Release portability and reproducibility

The editable SVG master should survive being moved to another machine or submitted to a publisher without silently losing assets.

## Self-contained SVG

Prefer internal SVG geometry and text. Internal fragment references such as `url(#arrow)` or `<use href="#symbol">` are fine. Embedded `data:` images may be used when a scientific raster inset is genuinely necessary, but record provenance and resolution. Do not depend on remote HTTP(S) images, local relative/absolute file paths, CSS `@import`, scripts, event handlers, or remote font resources.

Run `scripts/portability_audit.py figure_spec.json figure.svg` through preflight. `qa.portability_audit=required` makes violations release-blocking.

## Fonts

Typography can reflow across systems. Prefer broadly available families and a sensible fallback stack. Set `qa.require_generic_font_fallback=true` when maximum cross-machine resilience matters. For final publisher PDF, inspect the exported PDF visually and follow venue font-embedding requirements.

## Source fingerprints

When the figure is derived from a concrete manuscript PDF, source code snapshot, or data file, use `fingerprint_source.py` before semantic freeze. The spec stores only filename/size/SHA-256 metadata; the source itself is not redistributed. This makes source version drift detectable without copying copyrighted or sensitive material into the release.

## Capability check

`doctor.py` reports available SVG→PNG renderers, SVG→PDF renderers, grayscale conversion, and fontconfig. A working SVG→PNG renderer is the minimum hard requirement. PDF/grayscale become hard requirements when the spec requests them.

## Release verification

`finalize_figure.py` creates a manifest and immediately calls `verify_release.py`. Run `verify_release.py release/` again after copying, archiving, or handing the package to another system. Any changed or missing artifact must fail hash verification.
