# Paper ↔ Code Traceability

## Principle

A reproduction record should connect a scientific claim to the exact implementation and run artifacts used to test it.

```text
paper locator
   ↕
claim_id
   ↕
config + entrypoint + code path
   ↕
data / split / checkpoint
   ↕
run_id
   ↕
output artifact / metric
```

## Mapping statuses

- `verified`: direct evidence connects the paper object and repository artifact.
- `partial`: some elements are verified but the chain is incomplete.
- `inferred`: mapping is plausible from code/context but not directly documented.
- `unmapped`: no defensible mapping found.

Do not promote `inferred` to `verified` because a run succeeds.

## Mapping examples

| Paper object | Repository artifact | Role |
| --- | --- | --- |
| Algorithm 1 | `src/model.py::forward` | implementation |
| Eq. 4 λ | `loss.lambda` in YAML | hyperparameter |
| Table 2 / Ours | `configs/table2/ours.yaml` | experiment config |
| dataset preprocessing | `scripts/preprocess.py` | data transform |
| 5 random seeds | `scripts/run_all.sh` | aggregation policy |
| Figure 3 | `analysis/plot_ablation.py` | postprocessing |

## Traceability traps

- A config filename can resemble a table number without proving correspondence.
- README “reproduce results” commands may have been updated after publication.
- Evaluation scripts may use a different split than the paper text.
- Checkpoint names can be stale or regenerated.
- One entrypoint may branch on hidden defaults or environment variables.

Record these uncertainties rather than smoothing them over.
