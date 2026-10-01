# Regression testing protocol

## Objective

Turn real reviewer failures into durable tests so later skill revisions improve behavior without reintroducing earlier false positives, false negatives, severity inflation, duplicate findings, or synthesis drift.

Regression testing is for **skill development and evaluation**, not ordinary manuscript-review output unless the user asks for it.

## Core principle

Test scientific behavior, not exact prose.

A good regression case specifies:
- what evidence is available;
- what the reviewer must inspect;
- what root issue, if any, should survive;
- what disposition is expected;
- what must **not** be claimed;
- what summary-level strengthening is forbidden.

Do not use exact sentence matching as the primary success criterion.

## Test levels

### Level A — Micro / synthetic

Small controlled cases testing one failure mode.

Examples:
- rounded value vs true mismatch;
- imported baseline vs rerun baseline;
- p > 0.05 vs equivalence;
- harmless paraphrase vs semantic drift;
- unavailable citation vs unsupported citation.

`examples/false_positive_traps.md` is the seed Level-A suite.

### Level B — Manuscript slice

A bounded real or synthetic section/table/figure bundle that tests interaction among several rules.

Use this when a bug depends on context such as:
- caption + table + result prose;
- abstract + conclusion + one main table;
- equation + method prose + algorithm block.

### Level C — Full manuscript

End-to-end review using the intended review mode.

Evaluate:
- central claim coverage;
- root-finding identity;
- false positives/false negatives;
- severity/disposition stability;
- deduplication;
- main-comment density;
- synthesis fidelity;
- coverage gaps;
- stable IDs/order where the evidence boundary is unchanged.

### Level D — Version-delta

Two manuscript revisions or two skill versions.

Use this to test whether:
- a corrected issue disappears;
- an unchanged issue remains stable;
- new evidence changes disposition appropriately;
- a skill change causes an intended behavior delta without unrelated regressions.

## Regression fixture fields

Use `templates/regression_case.yaml`.

Each case should record:
- `case_id` and short title;
- test level;
- source/origin and manuscript version if applicable;
- review mode and archetype;
- evidence boundary;
- relevant anchors/objects;
- `must_find` assertions;
- `must_not_find` assertions;
- expected disposition and allowed severity range where appropriate;
- expected coverage/checkpoint behavior;
- forbidden synthesis statements;
- notes explaining the scientific reason for the expectation.

## Assertions

Prefer semantic assertions such as:

- a root concern with category `CE` or `OC` must exist;
- it must be an `author_query`, not a finding;
- severity must not exceed `Moderate`;
- no citation-semantic finding may exist because the source is unavailable;
- the executive summary must not claim incompatible protocols;
- the same denominator error must not appear as three independent roots.

Avoid brittle assertions such as:
- exact wording must equal a sentence;
- an issue must be numbered `CE-02` unless stable ordering is itself the tested behavior;
- the report must contain exactly N total issues unless count is the property being tested.

## Converting a real failure into a regression case

When a manuscript review exposes a reviewer failure:

1. identify the smallest evidence bundle that reproduces the failure;
2. classify the failure type: false positive, false negative, wrong disposition, wrong severity, duplicate root, coverage miss, provenance error, or synthesis drift;
3. define the correct scientific behavior;
4. add a `must_not_find` or `forbidden_synthesis` assertion for the bad behavior;
5. add a `must_find` assertion only when the correct behavior genuinely requires a positive finding/query/gap;
6. keep only short necessary excerpts or paraphrases; do not copy large copyrighted manuscript sections into the fixture;
7. note whether the case depends on rendered PDF inspection, external citation access, appendix access, or version provenance.

## Release gate for skill revisions

For the stable 1.x package-level gate, also follow `maintenance/RELEASE_GATE.md`.


Before accepting a behavior-changing revision:

1. run the Level-A seed suite;
2. rerun representative Level-B cases for each major audit family affected;
3. rerun at least one Level-C full-manuscript case when the change touches coverage, clustering, severity, synthesis, or report policy;
4. compare canonical finding records rather than prose alone;
5. inspect all intentional behavior deltas;
6. reject the revision if it fixes one case by introducing unrelated false positives or by weakening a valid prior finding.

When a test changes intentionally, document **why the scientific expectation changed** rather than silently editing the expected output.

## Canonical-record comparison

For reruns with the same evidence boundary, compare these fields first:
- disposition;
- root category;
- atomic claim/object identity;
- evidence state;
- severity band;
- protocol/provenance decision;
- remediation class;
- dependency clustering;
- summary-safe statement meaning.

Wording may vary. Scientific identity should not vary without new evidence or an intentional rule change.

## Overfitting guard

Do not fix a regression by hardcoding:
- author names;
- paper titles;
- dataset names;
- literal metric values;
- exact sentence strings;
- venue-specific phrases;

unless the behavior truly depends on that semantic property.

Generalize the rule to the scientific failure mode.

## Pass criteria

A release passes when:
- all required positive assertions are met;
- all forbidden assertions are absent;
- no new unsupported Major/Critical finding appears;
- query/gap uncertainty is preserved;
- summary text does not outrun canonical records;
- root-cause deduplication is preserved;
- coverage behavior matches the evidence boundary;
- intentional deltas are documented.


## Version-delta transition assertions

For `test_level: version_delta`, read `checks/revision_tracking_and_resolution.md`. Test prior-to-current transitions in addition to current findings. Allowed transition expectations include `resolved`, `partially_resolved`, `persistent`, `reclassified`, `not_reassessable`, and `no_longer_material`.

Prefer assertions such as:
- a prior root becomes `resolved`;
- a prior root remains `persistent` with recalibrated severity;
- a prior root is `partially_resolved`;
- an `author_query` becomes a verified finding and is marked `reclassified`;
- a moved persistent issue is **not** emitted again as a new issue;
- repairing a parent does **not** auto-resolve a stale independent downstream statement.

Do not require historical/current IDs to be identical when disposition/category changes. Require lineage to be explicit instead.


# Bundled black-box regression fixtures

The `regressions/` directory contains minimal semantic fixtures distilled from an independent blind run of the skill. These cases are regression targets, not paper-specific rules.

Future behavior-changing revisions should preserve the following invariants:
- an explicit significance/scaling claim with completed manuscript-level absence checking can yield a reporting/support finding rather than an automatic author query;
- partial resolution requires actual defect reduction;
- severity is recalibrated from the residual current defect without historical inertia;
- clarification of an unchanged imported-baseline defect remains persistent;
- a still-unverifiable citation dependency that is removed from the current manuscript becomes `no_longer_material`, not falsely `resolved`;
- prose placement matches canonical `salience`.

Do not hardcode the fixture's names or literal values into reviewer logic. Generalize to the scientific failure mode.
