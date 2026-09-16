# Export and final-use policy

## Master and derivatives

Keep SVG as the editable master unless the project already has another authoritative vector format. Treat PNG/TIFF as derivatives.

## Final-size sanity check

Always inspect a target-size raster preview in addition to a high-resolution preview. The target-size render should approximate how the figure will actually be consumed (paper column, page width, slide, poster). If labels fail at target size, simplify or restructure rather than relying on reader zoom.

## Paper

Prefer SVG/PDF vector output when venue tooling supports it. Keep a version without an internal figure title when captions are expected outside the artwork. Verify fonts/glyphs and any embedded raster resolution.

## Presentation

Favor larger labels and stronger hierarchy than a paper figure. Do not merely enlarge a dense paper figure. Preserve editability when possible.

## Raster export

Export high-resolution raster only when required. Never upscale a low-resolution embedded image and call it high-resolution. Verify transparency/background requirements.

## Final package

Recommended files:
- `figure.svg`
- `figure.preview.png`
- `figure.target.png`
- `figure_spec.json`
- `critic.json`
- `manifest.json` — hashes + skill/spec version + source fingerprints + toolchain capabilities
- `figure.pdf` when `target.exports` requests `pdf`

Remove temporary crops/debug renders from the delivery folder unless useful to the user.

## Physical target metadata

Prefer storing final intended width (`width_in` or `width_mm`) and `min_text_pt` in `figure_spec.json`. This makes final-size readability reproducible instead of depending on an arbitrary raster preview width. `target_preview_width_px` remains a rendering convenience, not the definition of physical legibility.

## Grayscale derivative

When `target.grayscale_safe` is true, `figure.target.gray.png` is required in the QA package. Pillow is preferred and ImageMagick is a fallback; if neither is available, rendering fails closed. It is a review artifact, not necessarily a publication deliverable. A grayscale failure should be fixed in the SVG encoding, not patched only in the raster derivative.

## One-command finalization

After the final critic pass, prefer:

```bash
python scripts/finalize_figure.py figure_spec.json figure.svg --critic critic.json --outdir release
```

This refuses to package a figure that fails deterministic preflight, renders the QA derivatives, exports vector PDF when requested by `target.exports`, copies the authoritative spec/SVG, writes a SHA-256 artifact manifest, and immediately verifies the release. The manifest records non-identifying toolchain capability metadata and any source fingerprints. Re-run `python scripts/verify_release.py release/` after moving or archiving the package.
