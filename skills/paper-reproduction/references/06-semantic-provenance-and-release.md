# Semantic provenance and release gates

`paper-reproduction` v1.1 distinguishes **recorded provenance** from **validated provenance**.

A target run is valid evidence only for the execution-defining state that existed when it ran. `run_with_ledger.py` therefore records SHA-256 bindings for the reproduction contract, run plan, repository manifest, data manifest, checkpoint manifest, and claim↔code map. Preflight requires every binding and recomputes every hash. If an execution-defining artifact changes or disappears after a target run, the old run does not silently inherit the new contract; rerun the target or preserve the older artifact state explicitly.

Cross-artifact release checks should close these links where mechanically possible:

```text
claim_id
  ↕
claim_code_map
  ↕
repository commit + config
  ↕
data/checkpoint identities
  ↕
target run
  ↕
metric row
  ↕
reproduction assessment
```

`exact_reproduction` is deliberately narrow. It requires an exact/deterministic equality rule, successful target evidence, no material deviation, and a clean source state matching the pinned revision. A dirty or patched run may still be useful evidence, but it is not exact execution of the pinned source.

`within_reported_variation` requires a comparison region that existed before assessment: reported variation from the paper or a predeclared absolute/relative tolerance. Hindsight tolerances are invalid.

`reconcile_claims.py` may create a candidate assessment for simple scalar rules only when the metric row's metric name matches the claim's declared metric (case-insensitively). It never overwrites the final assessment automatically. Scientific interpretation, protocol deviations, and limitations remain explicit review responsibilities.

Semantic regression fixtures should include intentionally invalid cases. The release surface is stronger when the skill proves that it rejects known-bad provenance, rather than only proving that happy-path examples pass.
