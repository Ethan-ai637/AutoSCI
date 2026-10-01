# Figure / table / text consistency audit

## Objective

Detect disagreements among narrative claims, tables, figures, captions, legends, labels, notes, and cross-references, while avoiding false mismatches from incomparable protocols or unreadable graphics.

## Reconciliation order

For every important prose-reported result:
1. identify the referenced evidence object;
2. verify object identity;
3. verify protocol comparability;
4. reconcile numeric value or qualitative direction;
5. inspect caption/notes for qualifications;
6. inspect uncertainty/statistical annotations;
7. inspect provenance/version when the value may be imported, derived, or stale across revisions;
8. determine whether the prose wording matches the evidence scope.


## No source-of-truth shortcut

A cross-surface mismatch does not by itself reveal which surface is correct.

- Do not automatically privilege the table over prose, or prose over the caption.
- If provenance, raw values, derivation, or another inspected source adjudicates the intended result, state which surface is inconsistent.
- If the available evidence establishes only that the surfaces disagree, report **internal inconsistency requiring reconciliation**.
- The recommended fix should be to reconcile the value/label/interpretation across all affected surfaces, not to copy one surface into another by assumption.

This distinction is especially important after manuscript revisions, where stale text, stale tables, stale captions, supplements, or checkpoints are all plausible. Read `evidence_provenance_and_adjudication.md` when provenance/version could resolve or complicate the conflict.

## Mandatory checks

### Identity
- Figure/Table number exists and refers to the intended object.
- Panel labels `(a)`, `(b)`, etc. match the cited panel.
- Model/variant names are stable.
- Dataset/split/population names are stable.
- Metric names are stable.
- Table row/column semantics are not reversed in prose.

### Protocol comparability gate
Before declaring a mismatch, check:
- same metric and direction (higher/lower better);
- same dataset/population;
- same split and evaluation protocol;
- same model variant/checkpoint;
- same aggregation (mean, median, best run, single run, pooled result);
- same unit/scale;
- same evaluation budget or constraints if material;
- whether baseline numbers were imported from prior work or rerun;
- whether the compared values belong to the same source/manuscript/artifact version when revision drift is plausible.

If these differ, report a protocol/clarity issue rather than a raw numerical contradiction unless the manuscript itself claims direct comparability.

### Numeric values
For important values mentioned in prose:
- locate source cell/label if available;
- compare after reasonable rounding;
- confirm percent vs fraction;
- confirm percentage points vs relative percent change;
- confirm mean/best/median/single-run semantics;
- confirm sample/subgroup aggregation.

Do not flag ordinary rounding. A displayed `91.24` summarized as `91.2` is consistent. A value that requires changing protocol/row/metric to match is not.

### Relative vs absolute improvement
For claims like “improves by 12%” distinguish:
- absolute difference: `new - old`;
- percentage-point difference for percentages;
- relative change: `(new-old)/old × 100%`.

Flag wording only when the intended interpretation materially changes the claim.

### Direction and ranking
Check words such as:
- improves/decreases;
- highest/lowest;
- best/second-best;
- faster/slower;
- more/less robust;
- monotonic/increasing/decreasing.

Account for metric direction before interpreting rank.

### Units and scales
- ms vs s;
- MB vs GB;
- fraction vs percent;
- log vs linear axes;
- normalized vs raw units;
- per-sample vs aggregate;
- absolute vs relative improvement.

### Sample size and denominator
Check whether `n`, subgroup size, number of datasets/tasks, seeds, runs, folds, or trials changes across text/table/caption.

A percentage with a changing denominator can create an apparent contradiction even when arithmetic is correct.

### Uncertainty and statistics
Check:
- what error bars represent;
- meaning of `±`;
- sample size `n`;
- confidence intervals;
- significance markers;
- whether the prose ignores uncertainty while making a strong ordering claim.

Do not infer “no significant difference” merely from overlapping error bars unless the paper/source explicitly justifies that inference.

### Captions and notes
Captions/notes can narrow interpretation. Check whether exceptions, exclusions, or protocol details there invalidate broad prose statements.

### Highlight conventions
If bold/underline/color denotes best, second-best, or significant, verify markings follow the stated rule.

## Plot-value policy

Only compare exact plotted values if explicitly labeled or reliably readable.

If a point is visually estimated:
- use qualitative checks such as ordering, sign, or trend;
- avoid fabricated decimal precision;
- state that exact-value verification was not possible when relevant.

## Typical findings

- Body says 91.2; table says 89.2 under the same row/metric/protocol.
- Body says “all datasets”; table contains an exception.
- Caption says validation set; text says test set.
- Figure legend and prose reverse Method-A/Method-B interpretation.
- Axis is error rate (lower better), but text calls the highest value best.
- Table bolding marks a non-best value as best.
- “12% improvement” is actually 12 percentage points.
- Main text reports best-run performance while caption says mean over seeds.
