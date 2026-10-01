# Reproducible scientific plotting

## General grammar
- Plot the analysis-ready data, not hand-copied summary numbers.
- Label axes with units.
- Show raw observations when feasible.
- Show uncertainty visually when it supports the estimand.
- Use deterministic jitter/seed.
- Preserve pairing visually for paired designs when helpful.
- Avoid bar charts as the default for continuous distributions.
- Avoid 3D effects and decorative encodings.
- Do not use dual y-axes unless the scientific relationship truly requires them and the mapping is explicit.

## Group comparison
Preferred default: raw points + group mean + 95% CI for mean-comparison analyses.
For paired analyses: points/lines per subject + summary of changes.

## Correlation/regression
Show raw points. For OLS, show fitted line only when the fitted relation is actually being reported. Do not imply confidence bands that were not calculated by the same model.


## Model-cohort fidelity
For ANCOVA, multivariable OLS, and Poisson regression, a plot must use the same complete-case cohort as the fitted model. Do not reintroduce a row merely because the displayed outcome and report predictor are observed when another declared covariate/predictor/exposure field was missing.

Raw group summaries in ANCOVA are descriptive among the ANCOVA-complete cases; they are not covariate-adjusted marginal means. Raw x-y views from multivariable regression are likewise descriptive; the adjusted coefficient remains the inferential object in the results table.

## Statistical annotation
Prefer a compact annotation of the effect and CI. If p-values are shown, report the value or threshold consistently with multiplicity correction. Stars should not be the main result.

## Export
For publication workflows, retain an editable/vector source when practical (SVG/PDF) and a raster preview. The v1 helper exports PNG and SVG.
