# Source Visual Acquisition Gate

A paper figure is a scientific asset, not an arbitrary screenshot.

## 1. Acquisition priority

Prefer:

1. original figure/image asset from paper repository/supplement;
2. embedded PDF figure extraction if clean;
3. screenshot exact figure bounding box from high-resolution rendered PDF page;
4. faithful reconstruction from exact tabular/source data;
5. source crop only as last practical option.

Do not start with a random page screenshot.

## 2. Separate extraction from slide layout

Acquire important source visuals BEFORE laying out slides.

Store each visual as a standalone asset and inspect it independently.

Do not discover crop problems only after the PPT is finished.

## 3. Semantic completeness

A plot/figure asset is PASS only when all relevant elements are present:

- complete data region;
- x axis;
- y axis;
- axis titles where needed;
- tick labels;
- legend where needed;
- panel labels;
- annotations intrinsic to source;
- uncertainty marks/error bars;
- relevant comparison lines/bars;
- color scale for heatmaps;
- labels necessary to understand categories.

A clean crop missing the x-axis is a FAILED crop.

## 4. Page-furniture contamination

A figure asset should normally exclude:

- journal running headers;
- author names;
- page number;
- DOI header;
- body paragraph fragments;
- partial caption text;
- neighboring figure fragments.

If crop edges contain isolated serif text that is not part of the figure,
assume contamination and inspect the source.

## 5. Never crop by aesthetics alone

Cropping must follow semantic boundaries.

Bad:
crop until the image “fits nicely”.

Good:
identify figure boundary + required labels, then design the slide around it.

## 6. Safe padding

When screenshot-cropping a figure:
- include a small safety margin around scientific labels;
- inspect all four edges;
- reduce padding only after confirming no required label will be cut.

Do not crop exactly against tick labels or legend boundaries.

## 7. Multi-panel figures

For a multi-panel source figure:

If only one panel supports the current claim:
- extract that complete panel;
- preserve its panel label when useful;
- identify it in the slide citation.

If multiple panels form one argument:
- keep them together only if readable;
- otherwise split across slides.

## 8. Two-figure rule

Do not place two full scientific figures on one slide merely to save space.

Two figures are allowed when direct comparison is the argument and both pass:
- readable axes;
- readable legends;
- complete data region;
- no crop damage.

Otherwise use two slides.

## 9. Presentation adaptation

Allowed:
- crop irrelevant panels;
- enlarge;
- direct-label curves;
- add arrows/circles/shaded regions;
- simplify duplicated legend information;
- faithfully reconstruct from exact data.

Not allowed:
- approximate values;
- hide a losing condition;
- remove error bars that matter;
- cut off axes;
- erase context that changes interpretation.

## 10. Asset preflight

For each Tier-A/B source visual, record:

- source;
- acquisition method;
- resolution;
- semantic completeness PASS/FAIL;
- contamination PASS/FAIL;
- readability PASS/FAIL;
- reconstruction fidelity if applicable.

Do not use a FAIL asset in the main deck.

## 11. Slide-level visual verification

After placing the asset:
- render the slide;
- inspect at normal slide size;
- ensure labels remain readable;
- ensure slide masks/crops do not re-introduce clipping.

An asset can pass standalone preflight and still fail slide-level placement.

## 12. Failure policy

If source visual cannot be made complete and readable:
- allocate another slide;
- split panels;
- move secondary visual to backup;
- reconstruct faithfully;
- or replace with a simpler verified evidence representation.

Never “make it fit” by cutting scientific content.
