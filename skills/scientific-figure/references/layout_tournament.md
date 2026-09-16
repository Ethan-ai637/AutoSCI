# Layout tournament for medium/complex figures

Do not commit a complex scientific graph to the first plausible composition. For medium/high complexity, compare low-fidelity macro-layouts before detailed drawing.

## When to use

Run:

```bash
python scripts/complexity_gate.py figure_spec.json
```

For `medium`, usually compare 2 candidates. For `high`, compare 3 candidates. Skip the tournament when one grammar is scientifically forced or the figure is simple.

## Candidate rules

Candidates must preserve exactly the same frozen semantics. Change only macro visual grammar, e.g.:
- left-to-right spine vs. central aggregation,
- overview + inset vs. two aligned panels,
- nested hierarchy vs. lane-based decomposition.

Keep candidates low fidelity: major groups, labels, flow, and panel geometry only. Do not spend time on icons, fine typography, or decoration.

## Render and choose

Render candidate thumbnails at approximate target aspect ratio. Compare on:
1. semantic faithfulness / risk of false implication,
2. 5–10 second story clarity,
3. connector complexity and crossing risk,
4. target-size information density,
5. how clearly the novelty receives visual emphasis,
6. whether the grammar matches the scientific relation graph.

Choose one winner and record why in `layout_plan.md`. Do not average candidates together into a compromised hybrid unless the hybrid has a clear scientific rationale.

## Anti-cherry-picking rule

Do not select the prettiest candidate if it creates a weaker or misleading scientific reading. Semantic risk dominates aesthetics.
