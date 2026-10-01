# Blind-run regression fixtures

These fixtures were distilled from an independent black-box run of manuscript-reviewer v0.11. They are **behavioral regression tests**, not paper-specific heuristics.

Targets:
1. finding vs author-query calibration for explicit support-bearing claims;
2. current-state severity recalibration after partial repair;
3. persistent vs partially-resolved semantics when only clarification improves;
4. `no_longer_material` for unresolved verification gaps removed from current scientific dependency;
5. canonical-record to prose placement invariance.

Future revisions should generalize the governing rule and retain these cases. Do not hardcode paper names, values, or literal sentences.


## 1.0.0 baseline

These fixtures are mandatory compatibility checks for the 1.x line. They encode general scientific behaviors, not expected prose. A future rule change that intentionally changes one of these outcomes should update the fixture, schemas/state model when necessary, and release notes in the same change.

## Security regression

`security_embedded_prompt_injection.yaml` guards a public-use safety boundary: instruction-like text inside a manuscript or supporting artifact is evidence content, not a directive to the reviewing agent. It should remain invariant across the 1.x line unless the surrounding product security model provides a strictly stronger guarantee.
