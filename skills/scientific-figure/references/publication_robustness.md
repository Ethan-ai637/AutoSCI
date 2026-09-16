# Publication robustness

A figure should survive conditions different from the author's editing canvas.

## Grayscale and color vision

When `target.grayscale_safe` is true, no scientific distinction may depend only on hue. Reinforce color with at least one non-color channel: position, direct label, shape, pattern, line style, marker, or topology.

Record semantic channels in `visual_encodings`, then run:

```bash
python scripts/robustness_audit.py figure_spec.json
```

The renderer also produces a grayscale target-size preview when Pillow is available. Inspect it manually; the metadata audit does not prove perceptual separability.

## Print / target size

Inspect `figure.target.png` and `figure.target.gray.png` at 100% display scale. Avoid weak hairlines, low-contrast annotations, color-only legends, and dense micro-labels.

## Accessibility principle

Color may reinforce meaning but should not be the sole carrier of core scientific meaning. Direct labels are preferable to legends when space permits.
