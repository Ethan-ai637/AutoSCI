# Contributing to AutoSCI

Thanks for contributing.

## General rule

A new rule should correspond to a concrete failure mode. Avoid adding prompt text merely because it sounds like good advice.

## Scientific Figure changes

For changes that alter production behavior:

1. provide a reproducible case or benchmark failure;
2. classify the failure;
3. make the smallest targeted change;
4. run existing validation and, when possible, paired benchmark comparison;
5. check for regressions in scientific correctness and claim coverage;
6. prefer removing machinery that does not show reliable benefit.

Do not change the meaning of `draft`, `standard`, `release`, the figure-spec schema, or release artifacts without an explicit migration note.

## Academic Research Presentation changes

Describe the concrete slide failure the change is intended to prevent, for example: a reversed/invented dependency arrow, clipped legend/axis/panel, unreadable main figure, excessive card/box layout, loss of side inputs/experimental conditions, or a narrative that hides negative/uncertain evidence.

## Validation

Before opening a pull request:

```bash
python scripts/validate_repo.py
```

If changing scientific-figure scripts, also run relevant script-level tests or a representative preflight.

## Pull requests

Keep PRs focused. Include the problem/failure mode, changed behavior, validation performed, known tradeoffs, and before/after examples when the change is visual.
