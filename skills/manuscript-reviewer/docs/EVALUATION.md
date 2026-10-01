# Evaluation

## Principle

Evaluate the skill as a black box: the reviewer sees only the skill, blind manuscript materials, and a fixed task prompt. The oracle and scorecard remain outside the review session.

## Recommended dimensions

- true-positive root recall;
- false-positive resistance;
- finding vs author-query vs coverage-gap calibration;
- severity calibration;
- root-cause deduplication;
- citation-verification boundary discipline;
- protocol/provenance handling;
- revision lineage and dependency propagation;
- canonical-record / prose rendering invariance;
- security behavior for instruction-like content embedded in reviewed artifacts.

## Regression hierarchy

1. **Micro fixtures** — minimal synthetic failure patterns under `regressions/`.
2. **Manuscript slices** — small bundles testing cross-surface reasoning.
3. **Full blind manuscripts** — end-to-end review with an external oracle.
4. **Revision deltas** — prior review + rebuttal + revised manuscript.

Do not score exact prose. Score semantic outcomes such as root identity, disposition, allowed severity, evidence state, transition state, duplicate suppression, and forbidden synthesis.

## Release evidence

A release may be published without a fresh benchmark if it makes only packaging/documentation changes. A behavior-changing release should preferably receive an independent blind run before performance claims are attached to that version. Older-version scores must not be presented as current-version scores.

See `maintenance/BLACKBOX_EVAL.md` for the operational protocol and `maintenance/RELEASE_GATE.md` for release requirements.
