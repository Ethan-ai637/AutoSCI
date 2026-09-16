# Benchmarking and failure analysis

Use this reference only when evaluating the skill itself. Benchmark machinery is **not part of normal figure production** and must not add gates to draft/standard/release workflows.

## Primary question

Measure whether the scientific-figure workflow improves source-faithful, editable scientific figures compared with a simpler baseline. Do not optimize for pixel similarity to an author's Figure 1: multiple visual grammars can correctly express the same method.

## Recommended tracks

### Blind reconstruction (preferred)

Give the generator the authoritative Method/equations/code/brief, but **withhold the author's figure until generation is recorded**. This tests whether the workflow can construct a useful figure rather than imitate one.

Initialize without a reference figure:

```bash
python scripts/benchmark.py init \
  --case-id paper-a \
  --source paper.pdf \
  --track blind \
  --out benchmarks/paper-a
```

For the baseline, run Codex without this skill using a concise task-equivalent prompt. Record it as `raw-codex`. Then run this skill under the `standard` profile and record it as `skill-v1.9-standard`. Keep the scientific source, target width, and requested figure job the same.

Only after **all intended blind generation variants have been recorded** should the author's original figure be attached for post-hoc analysis:

```bash
python scripts/benchmark.py attach-reference \
  --case benchmarks/paper-a/case.json \
  --reference author-figure1.png
```

The script refuses attachment before the first run, and once a reference is attached it refuses any additional blind-generation run in that case. Create a fresh case if another uncontaminated run is needed.

### Reference-assisted

Use only as a separate track when the actual product requirement includes a reference image. Label it explicitly; never mix it with blind results.

## Recording a run

A skill run can retain hashes and orchestration/critic summaries:

```bash
python scripts/benchmark.py record \
  --case benchmarks/paper-a/case.json \
  --variant skill-v1.8-standard \
  --uses-skill \
  --reference-access withheld \
  --spec figure_spec.json \
  --svg figure.svg \
  --critic critic.json \
  --state workflow_state.json \
  --copy-artifacts
```

A raw baseline can be recorded with only the produced artifact(s):

```bash
python scripts/benchmark.py record \
  --case benchmarks/paper-a/case.json \
  --variant raw-codex \
  --reference-access withheld \
  --artifact baseline.svg \
  --artifact baseline.png \
  --copy-artifacts
```

Do not claim token/cost measurements unless an external source actually provides them. The harness may derive checkpoint wall-time span from orchestration timestamps, but this is not model compute time.

## Post-hoc evaluation

Generate one structured evaluation template per run:

```bash
python scripts/benchmark.py new-eval --run benchmarks/paper-a/runs/skill-v1.8-standard/run.json
```

Complete the evaluation only after inspecting the source and generated artifact. If an author figure is attached, use it to discover missed concepts or useful visual ideas, not as an unquestioned layout ground truth.

Score 0–10 independently:
- scientific correctness
- claim coverage
- structural clarity
- visual hierarchy
- reading order
- final-size legibility
- editability

Record concrete failures with category and severity. Allowed categories include source grounding, semantic, notation, visual grammar, layout, geometry, routing, typography, legibility, style, portability, critic, orchestration, overconstraint, efficiency, and other.

Validate completed evaluation JSON:

```bash
python scripts/benchmark.py validate-eval evaluation.json
```

Compare runs:

```bash
python scripts/benchmark.py compare \
  --case benchmarks/paper-a/case.json \
  --out benchmarks/paper-a/comparison.md
```

## Evaluation hierarchy

Interpret results in this order:

1. **Scientific correctness** — wrong topology/claim/equation is a failure even if visually attractive.
2. **Claim coverage** — determine whether the figure omitted important supported content.
3. **Structural clarity / reading order** — does the chosen visual grammar explain the science efficiently?
4. **Final-size legibility / editability** — can the artifact actually be used in a paper or presentation?
5. **Aesthetics** — useful only after the above pass.

Never collapse all dimensions into a single number for deciding whether a skill change is valid. A visual gain must not hide a semantic regression.

## Minimal benchmark set

Before changing the production skill again, prefer at least three qualitatively different cases:

1. LLM/RL method with branching/feedback and mathematical notation.
2. Neural/model architecture with repeated modules or tensor/data paths.
3. Multi-panel mechanism or local-to-global scientific process.

For each case, compare at least a raw Codex baseline and the current skill under `standard`. Use the same target width and source snapshot.

## Change policy

Promote a proposed skill change only when it addresses a repeated failure category or a critical failure without creating regressions on prior cases. If a rule helps one paper but hurts other grammars, prefer a conditional/reference-level rule over a new global hard gate.

If benchmark results show excessive workflow overhead with no quality gain, remove or demote machinery rather than adding more.

## Suite-level regression benchmark

Use a suite only when deciding whether a skill change/version should be promoted. It is external evaluation infrastructure and must not affect normal figure production.

Create a suite and register heterogeneous cases:

```bash
python scripts/benchmark_suite.py init \
  --suite-id core-regression \
  --title "Scientific Figure Core Regression" \
  --out benchmarks/core/suite.json

python scripts/benchmark_suite.py add-case \
  --suite benchmarks/core/suite.json \
  --case benchmarks/paper-a/case.json
```

Register named variants. An ablation must declare its parent and the exact mechanism removed/changed:

```bash
python scripts/benchmark_suite.py add-variant \
  --suite benchmarks/core/suite.json \
  --variant raw-codex \
  --role baseline

python scripts/benchmark_suite.py add-variant \
  --suite benchmarks/core/suite.json \
  --variant skill-v1.9-standard \
  --role candidate

python scripts/benchmark_suite.py add-variant \
  --suite benchmarks/core/suite.json \
  --variant skill-v1.9-no-tournament \
  --role ablation \
  --parent skill-v1.9-standard \
  --change "Disable layout tournament"
```

Check which case/variant cells have complete evaluations:

```bash
python scripts/benchmark_suite.py matrix \
  --suite benchmarks/core/suite.json \
  --out benchmarks/core/matrix.md
```

Run a paired comparison only when the same cases contain complete evaluations for both variants:

```bash
python scripts/benchmark_suite.py compare \
  --suite benchmarks/core/suite.json \
  --baseline skill-v1.8-standard \
  --candidate skill-v1.9-standard \
  --out benchmarks/core/v18-v19.md
```

The suite report includes, per metric:
- baseline/candidate mean across paired cases
- mean and median paired delta
- win/tie/loss counts
- per-case deltas
- scientific-correctness / claim-coverage regressions
- critical/major/minor failure totals
- major+critical failure-category deltas

It deliberately computes **no composite score**. Do not promote a change merely because visual metrics improved on average. Investigate any scientific-correctness or claim-coverage regression and any new critical failure first.

## Ablation policy

Use ablations to decide whether expensive machinery deserves to remain. Good ablation questions include:
- layout tournament on vs off
- source grounding/freeze workflow vs a lighter prompt-only path
- geometry/final-size QA on vs off for standard work
- full critic loop vs one-pass render

Keep all other conditions constant within a paired comparison. Register the changed mechanism in the suite metadata. If removing a mechanism preserves scientific quality and reduces repeated `overconstraint`, `orchestration`, or `efficiency` failures, prefer simplification.

## Suite promotion rule

Do not use a single numeric promotion threshold. Before promoting a new production version:

1. Run the same baseline and candidate on the same case set.
2. Require complete structured evaluations for every compared cell.
3. Inspect scientific correctness and claim coverage first.
4. Investigate every high-priority case-level regression.
5. Prefer changes that reduce repeated major/critical failure categories across more than one case.
6. Treat one-paper wins as hypotheses, not evidence for a new global hard rule.
7. Keep the previous suite report so later versions can detect regression rather than resetting the benchmark narrative.
