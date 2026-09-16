# Scientific Figure v2.0 Stable Contract

v2.0 is the first stable baseline. It freezes the production behavior developed through v1.9 and separates future changes into two classes.

## Stable production contract

The following are considered stable in v2.0:

- Skill name and install folder: `scientific-figure`.
- The three execution profiles: `draft`, `standard`, and `release`.
- The source-grounded `figure_spec.json` workflow and semantic freeze/change-control model.
- Traceable editable SVG as the master figure artifact.
- Profile-aware deterministic preflight, rendering, semantic/visual critique, and surgical refinement.
- Deterministic orchestration/checkpoint/resume behavior.
- Release packaging with SVG/PDF/PNG, manifest hashes, and release verification.
- Benchmarking as an optional sidecar workflow that does not add gates to normal figure production.

## Schema stability

The scientific figure spec schema remains `1.7`. Skill version and figure-spec schema are intentionally independent. A future skill release must not bump the scientific schema unless the scientific contract itself changes.

## Compatibility policy

- Existing v1.7-v1.9 projects should remain usable under v2.0.
- Existing workflow state files may retain their historical `skill_version`; orchestration derives current behavior from the active skill and does not invalidate checkpoints solely because the installed skill version changed.
- Historical benchmark variant names such as `skill-v1.9-standard` remain valid experiment labels.
- A future change that alters scientific semantics, profile meaning, hard QA gates, or release artifact meaning requires an explicit migration note and benchmark evidence.

## Change policy after v2.0

Do not add production rules because they merely sound useful. Production changes should be driven by repeated failures in the benchmark suite or by a concrete portability/correctness bug. Prefer ablation and simplification when machinery has no measurable benefit.

Evaluation-only additions may evolve independently as long as they do not modify normal production behavior.

## Recommended v2.x development rule

1. Reproduce the failure on a fixed blind benchmark case.
2. Classify the failure using the benchmark taxonomy.
3. Make the smallest targeted change.
4. Run paired comparison against v2.0 on the full regression suite.
5. Reject the change if it introduces scientific-correctness or claim-coverage regressions that are not explicitly justified.
6. Use ablation to remove mechanisms that do not show reliable benefit.

This file is a maintainer contract, not an extra generation prompt. Normal Codex figure tasks do not need to read it.
