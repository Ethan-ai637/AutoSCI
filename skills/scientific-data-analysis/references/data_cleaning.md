# Data cleaning rules

## Raw data immutability
Keep raw input immutable. Derivatives must be new files. Record hashes before and after analysis.

## Analysis-ready serialization fidelity

The raw input format and the analysis-ready format are separate scientific contracts. XLSX/XLSM input is read from native workbook cell values so boolean, numeric, and string category identities are visible before cleaning. Ordinary homogeneous tables can remain CSV/TSV. If a plan-relevant identifier/category column contains scalar distinctions that CSV/TSV cannot round-trip faithfully (for example boolean `true`, numeric `1`, and string `"1"`), cleaning must stop rather than silently change those identities. Use `.jsonl`/`.ndjson` for the analysis-ready derivative in that case.

The cleaner verifies this mechanically by writing the requested derivative, reloading it through the same table reader, and comparing plan-relevant identity columns. Do not bypass a fidelity failure by manually editing the derivative; either normalize the source coding deliberately or use the type-preserving analysis-ready format.

## Missing data
- Normalize explicit missing tokens (`NA`, `N/A`, blank, sentinel values) only when declared.
- Report missingness by outcome and relevant group/timepoint.
- Do not default to mean/median imputation for inferential analysis.
- Complete-case analysis changes the target population when missingness is informative; state this limitation. In v1.2 every inferential result records candidate units, analyzed units, and exclusions caused by missing/invalid analysis variables.
- If missingness is substantial or plausibly not completely at random, consider a specialist model / multiple imputation plan.

## Outliers
An outlier is not automatically an error.

Acceptable exclusion bases include:
- known acquisition failure;
- impossible physical value;
- protocol-defined QC failure;
- duplicated/contaminated sample confirmed by metadata.

Weak bases include:
- extreme but plausible value;
- high residual alone;
- exclusion because p-value improves.

Prefer retaining plausible observations and adding robust/sensitivity analyses.

## Duplicates
Distinguish:
- accidental duplicate rows;
- repeated measurements that are scientifically real;
- technical replicates;
- biological/participant replicates.

Only exact duplicate-row removal can be automated safely by default. Identifier duplicates should be audited, not automatically dropped. From v1.4.6, both checks use typed scalar identity rather than raw pandas equality, so boolean/numeric aliases are not silently treated as the same scientific identifier.

## Technical replicates
Technical replicates estimate measurement variability; they are usually not independent biological units. Aggregate them only when the plan declares the aggregation function and grouping keys.

## Leakage
Never compute cleaning thresholds, normalization parameters, or feature selection using held-out outcome information in predictive workflows. This v1 skill is focused on classical scientific inference; prediction-specific train/test leakage needs its own explicit protocol.

## Cleaning log
Every removed row should contain:
- `_row_id` or stable source identifier;
- rule ID;
- reason code;
- relevant observed value when safe;
- timestamp/tool version if available.

## v1.2 structural guardrails

### Numeric coercion is an audited decision

If a column is declared in `require_numeric` or `numeric_ranges`, a non-missing value that cannot be parsed numerically is treated as invalid data and logged. It is not silently converted to NaN only when the statistical test runs.

### Independent-ID duplicates

`id_duplicate_policy` controls what happens when the declared independent-unit ID remains duplicated after cleaning:

- `audit`: preserve rows but report duplicate IDs for scientific review;
- `error`: stop the pipeline;
- `allow`: preserve duplicates deliberately (appropriate only when the ID is not expected to be row-unique for the planned analysis).

Do not use `allow` to bypass pseudoreplication concerns. Identifier duplicate auditing uses typed scalar identity: numeric `1` and `1.0` are the same numeric ID, while boolean `True`, numeric `1`, and string `"1"` remain distinct if the source table preserves those types.

### Technical-replicate metadata must be invariant

When technical replicates are aggregated, every carried non-measurement column must have a single value within a replicate group. If one subject's replicate rows contain conflicting group labels, timepoints, batches, conditions, or covariates, aggregation must stop. Taking the first metadata value would make the result depend on row order and can silently corrupt the design.

In v1.2.1, successful aggregation also writes `_source_row_ids` (semicolon-delimited contributing raw `_row_id` values) and `_technical_replicate_n` into the analysis-ready table. These are provenance fields, not scientific variables. Raw inputs are not allowed to pre-use these reserved names.

### Pair × condition duplicates are not a cleaning convenience

For paired long-format inference, more than one observation for the same pair and condition means the data still contain an unresolved replicate/repeated-measure structure. Resolve it explicitly before paired inference; the statistics runner intentionally refuses to select an arbitrary first row. Pair identifiers are matched with typed identity, and rows with missing `pair_id` are never combined into a synthetic missing-ID pair. The result records `n_rows_missing_pair_id` so this invalid-ID loss remains visible.


## v1.2 missing-data contract

The deterministic core accepts only `missing_data.strategy = complete_case`. This restriction is intentional: single-value imputation and ad-hoc missingness rules should not be hidden behind convenience defaults. Multiple imputation or explicit missingness models require a separate specialist workflow.
