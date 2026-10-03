---
name: paper-reproduction
description: Reconstruct published research into runnable, traceable, auditable experiments. Use when a user provides a paper, DOI/arXiv/project page, or research repository and wants to locate the authoritative code, verify paper-repository identity, select a revision, reconstruct the declared environment, map paper claims to code/config/data/checkpoints, run smoke or target experiments, record run provenance, compare reproduced outputs with reported claims, diagnose discrepancies, or audit whether a repository is reproduction-ready. Preserve uncertainty and underspecification; never invent missing hyperparameters, silently patch code or dependencies, equate the current default branch with the paper version, or label a paper irreproducible merely because one reproduction attempt is blocked or differs.
---

# Paper Reproduction

Turn a published study and its research artifacts into an inspectable reproduction workspace:

**paper/repository -> identity resolution -> exact target claim -> revision selection -> reproduction contract -> paper↔code traceability -> environment/data/checkpoint reconstruction -> safety/resource preflight -> smoke test -> target runs -> run ledger -> claim reconciliation -> discrepancy analysis -> reproduction assessment -> QA -> frozen handoff**

The model handles scientific interpretation, paper↔code mapping, ambiguity resolution, and discrepancy reasoning. Deterministic scripts handle repository inspection, environment capture, hashing, command execution provenance, provenance-hash binding, scalar claim reconciliation, cross-artifact validation, readiness auditing, and workspace freezing.

This skill reproduces *published claims*. It does not design a new method, optimize a model beyond the published protocol, or replace downstream statistical analysis.

## Hard rules

1. **Define the target claim before expensive execution.** “Reproduce this paper” is not an executable contract. Identify one or more stable `claim_id` targets with a paper locator, metric/observable, reported value or qualitative behavior, dataset/split, model/config, evaluation protocol, and comparison rule when available.
2. **Resolve paper identity and version.** Record DOI/arXiv/project-page identifiers and the exact paper version used. A journal article, conference version, arXiv revision, supplement, and correction may describe different experiments.
3. **Verify repository identity; do not infer it from naming alone.** Classify the repository as `author_official`, `publisher_official`, `artifact_evaluation`, `linked_project`, `third_party`, or `unknown`, and record evidence for that classification.
4. **Pin an exact repository revision before execution.** Record remote URL, commit SHA, branch/tag/release, submodules, Git LFS state, and selection basis. Do not assume the current default branch is the paper version.
5. **Prefer paper-era artifacts.** If the paper predates the current repository state, look first for the commit/tag/release explicitly linked from the paper, README, artifact appendix, release page, or publication period. `current_head_fallback` must remain visibly labeled as a fallback.
6. **Treat research repositories as untrusted code.** Inspect setup files, install scripts, shell scripts, Dockerfiles, hooks, download scripts, and entrypoints before execution. Do not expose secrets, credentials, SSH agents, cloud tokens, or unrelated user files to repository code. `run_with_ledger.py` filters inherited environment variables; use `--env NAME` only for a reviewed, non-secret variable the command requires. The wrapper rejects common credential-like variable names.
7. **Do not use elevated privileges merely to make reproduction work.** Avoid `sudo`, host-level package mutation, destructive shell commands, or disabling security controls. Prefer an isolated virtual environment, container, or disposable workspace when available.
8. **Installing a package is code execution.** `pip install .`, editable installs, build backends, `setup.py`, shell installers, and container builds may execute repository-controlled code. Treat them as execution steps and record them.
9. **Separate author-declared environment from the environment that actually ran.** Preserve source environment files and write the resolved environment separately. Never silently rewrite `requirements.txt`, `environment.yml`, lockfiles, CUDA requirements, or Dockerfiles.
10. **Every environment deviation is provenance.** Dependency substitutions, version pins, compiler changes, CUDA downgrades/upgrades, source patches, disabled accelerators, and alternative datasets/checkpoints must be recorded in `environment_diff.json` or `discrepancies.jsonl` before claiming reproduction.
11. **Baseline runs should use a clean source revision.** If source code is modified, preserve the original commit, save the patch/diff, hash it, and mark affected runs as modified reproduction. A dirty worktree is never equivalent to the pinned source revision.
12. **Paper↔code traceability is a first-class artifact.** Map each target paper object or claim to concrete repository artifacts: entrypoints, functions/modules, config keys, preprocessing scripts, dataset splits, checkpoints, evaluation code, and output files. Use `verified`, `partial`, `inferred`, or `unmapped`; do not present inference as verified mapping.
13. **Unknown implementation details must remain unknown.** In `PAPER_ONLY`, do not fill missing optimizer, tokenizer, schedule, initialization, preprocessing, seed policy, or evaluation details from convention without labeling the assumption. Record unresolved items in `underspecifications.jsonl`.
14. **Mechanically recoverable implementation is allowed; invention is not.** Paper-only implementation may encode equations, pseudocode, explicit hyperparameters, and directly specified preprocessing. Any additional choice must be an explicit, reversible implementation decision with source status and impact.
15. **External artifacts need identity.** Record dataset/checkpoint/model source, version/revision when available, retrieval status, checksum/hash, licensing/access constraints when relevant, preprocessing, and split identity. “Downloaded the dataset” is not sufficient provenance.
16. **Do not substitute inaccessible artifacts silently.** If the original checkpoint, split, dataset version, proprietary component, or preprocessing artifact is unavailable, record the substitution and downgrade the assessment scope.
17. **Run a smoke test before a costly target experiment.** Validate importability, CLI/config resolution, minimal data flow, checkpoint loading, output creation, and evaluation plumbing at the smallest scientifically meaningful scale.
18. **Do not turn a smoke test into scientific evidence.** A smoke test establishes executability, not reproduction of the target claim.
19. **Estimate execution scope before launching expensive runs.** Record expected hardware, wall-time class, memory/storage needs, dataset size, number of seeds, and whether full training is required. If the requested run is infeasible in the current environment, produce an executable plan and preserve the blocker rather than pretending the experiment ran.
20. **Every executed run gets an append-only ledger entry.** Record run ID, target claim IDs, command argv, source commit, dirty/patch state, config hash, dataset/checkpoint identities, seed, timestamps, exit code, logs, output/metric locations, and artifact hashes when available.
21. **Do not overwrite failed runs.** Failed, interrupted, OOM, timeout, dependency, and data-access attempts remain in `run_ledger.jsonl`. A later successful run does not erase earlier evidence.
22. **Metrics must be linked back to runs and claims.** A value in `metrics.csv` must identify the producing `run_id`, `claim_id`, metric name, value, unit, split, and aggregation level when known. When a claim declares `metric`, the metric row must match it; the release preflight rejects mismatches and scalar reconciliation ignores them.
23. **Comparison rules must come from the claim contract, not hindsight.** Use reported uncertainty, deterministic equality, explicitly declared tolerance, or an appropriate qualitative comparison defined before assessment. Do not invent a generous tolerance after observing a mismatch.
24. **Reproduction state is scoped to the tested claim and setup.** Use one of: `exact_reproduction`, `within_reported_variation`, `numerically_different`, `qualitatively_consistent`, `partial_reproduction`, `blocked_by_missing_data`, `blocked_by_missing_artifact`, `blocked_by_environment`, `underspecified`, or `not_attempted`.
25. **Reserve `exact_reproduction` for genuinely exact targets.** It requires a deterministic or explicitly exact comparison contract and no material protocol divergence. Similar-looking numbers are not automatically exact reproduction.
26. **`within_reported_variation` requires a declared variation basis.** The paper must report an interval/variation or the contract must define a scientifically justified comparison region before execution. Otherwise use a more limited state.
27. **A mismatch is not proof of paper irreproducibility.** Report “not reproduced under this recorded setup” or the specific blocker. Do not label the paper, authors, or method “irreproducible” from a single attempt, unavailable artifact, environment drift, or underspecified detail.
28. **Distinguish execution failure from scientific discrepancy.** Dependency resolution failure, OOM, missing checkpoint, inaccessible data, and missing code paths are blockers; a completed matched protocol with a different metric is a result discrepancy.
29. **Keep reproduction and statistical analysis separate.** This skill records run-level outputs and direct claim comparisons. Send multi-run inference, confidence intervals, significance testing, effect sizes, robustness analysis, or new statistical modeling to `$scientific-data-analysis`.
30. **Do not optimize away disagreement.** Hyperparameter tuning, changed seeds, altered preprocessing, checkpoint cherry-picking, or modified evaluation code performed to recover the paper number must be logged as a separate exploratory/diagnostic run, not merged into baseline reproduction.
31. **Preserve negative evidence.** Missing scripts, dead links, obsolete dependencies, undocumented preprocessing, broken checkpoints, and unexplained metric drift are part of the reproduction record.
32. **A frozen manifest proves artifact identity, not scientific truth.** Hash manifests establish what files were handed off; they do not prove that the implementation is correct or that the original claim is true.
33. **Downstream handoff must stay structured.** Export run-level metrics, claim mappings, discrepancies, environment state, and provenance rather than only a prose summary.
34. **Never claim a repository can fully reproduce a paper from README promises alone.** `REPO_AUDIT` reports readiness and missing evidence; it does not manufacture execution evidence.
35. **Bind every scientific target run to the exact contract state used at execution time.** Target-run provenance must include hashes of the reproduction contract and other execution-defining manifests. A later-edited contract must not retroactively govern an earlier run.
36. **Cross-artifact identity must reconcile mechanically where possible.** Target-run commit, dataset/checkpoint IDs, config hash, claim IDs, metric rows, and assessment support must resolve to the corresponding recorded manifests and ledgers.
37. **Reproduction labels have eligibility conditions.** `exact_reproduction` requires an exact comparison rule, successful target evidence, a clean materially matched source state, and no material protocol deviation. `within_reported_variation` requires a predeclared reported-variation or tolerance basis.
38. **Deterministic reconciliation may propose, but must not silently finalize, scientific assessment.** Mechanical scalar rules may generate candidate assessments; the final assessment remains an explicit audited artifact that preserves limitations and deviations.
39. **Semantic regression tests are part of the release surface.** A release-quality skill must fail known-invalid workspaces such as post-run contract mutation, revision mismatch, unknown artifact references, and ineligible reproduction-state assignments.

## 1. Choose the mode

Select one primary mode.

### `REPO_REPRODUCE`

Use when a paper and a candidate repository are available. This is the default for normal reproduction work.

```text
paper + repository
      ↓
paper/repo identity
      ↓
revision selection
      ↓
target claim contract
      ↓
paper↔code map
      ↓
environment + external artifacts
      ↓
smoke test
      ↓
target run(s)
      ↓
claim reconciliation
```

### `PAPER_ONLY`

Use when the paper is available but no usable repository exists.

```text
paper
  ↓
extract algorithm / preprocessing / hyperparameters
  ↓
separate specified vs missing details
  ↓
reproduction specification
  ↓
implement only recoverable parts
  ↓
record assumptions / underspecification
  ↓
run only within declared scope
```

`PAPER_ONLY` is not permission to invent a conventional implementation and call it the paper implementation.

### `REPO_AUDIT`

Use when a repository is provided and the user wants to know whether it appears capable of reproducing an associated paper.

```text
repository
   ↓
associated-paper resolution
   ↓
revision/artifact inventory
   ↓
entrypoints / configs / data / checkpoints
   ↓
claim traceability readiness
   ↓
environment + execution readiness
   ↓
reproducibility readiness report
```

No scientific reproduction state should be assigned unless the corresponding experiment was actually executed or externally verified.

## 2. Choose the profile

Set `profile` in `reproduction_contract.json`:

- `diagnostic`: identity, revision, traceability, environment/data readiness, and a smoke test or minimal path. Useful for triage.
- `standard`: **default**. Full target-claim contract, traceability, preflight, smoke test, target runs when feasible, discrepancy recording, assessment, and handoff.
- `release`: archival handoff. Requires structural preflight, complete run ledger for attempted targets, explicit blocker/discrepancy state, hash manifest, and no unrecorded source/environment deviation.

A profile changes execution depth, not evidence standards.

## 3. Resolve the paper manifest

Create `paper_manifest.json` before claiming paper/repository correspondence. Record when available:

- title
- authors
- DOI
- arXiv ID and version
- venue/year
- canonical paper URL
- project/artifact URLs stated by the paper
- supplement/correction identifiers
- publication date or accepted date
- exact source used for experiment details

If multiple paper versions disagree on an experiment, either select one version explicitly or split the target into version-scoped claims.

Read `references/01-identity-and-revision.md` for paper/repository/version resolution.

## 4. Resolve repository identity and exact revision

For `REPO_REPRODUCE` or `REPO_AUDIT`:

1. locate candidate repositories from the paper, project page, author organization/profile, artifact appendix, publisher artifact page, or repository documentation;
2. collect evidence that the repository corresponds to the paper;
3. classify official status conservatively;
4. inspect releases/tags/commits near publication;
5. select and record an exact commit;
6. acquire the repository without automatically initializing submodules or large LFS payloads;
7. initialize submodules/LFS only when needed and record their state;
8. save `repository_manifest.json`.

After identity/revision selection, acquire a remote repository conservatively:

```bash
python scripts/acquire_repo.py \
  --url https://github.com/owner/repo.git \
  --dest work/repo \
  --ref <commit-or-tag> \
  --output reproduction/artifacts/repository_acquisition.json
```

This acquisition step does **not** prove that the selected repository belongs to the paper. It deliberately skips submodule initialization and LFS smudge so large or nested code/data are not pulled implicitly.

Useful deterministic inspection after checkout:

```bash
python scripts/inspect_repo.py \
  --repo /path/to/checkout \
  --output reproduction/repository_manifest.json
```

The script records observable Git/repository facts. The model/user still decides `official_status` and `revision_selection_basis` from source evidence.

Recommended `revision_selection_basis` values:

`paper_linked_tag`, `paper_linked_release`, `paper_documented_commit`, `artifact_documented_commit`, `publication_period_commit`, `user_pinned`, `current_head_fallback`, `unknown`.

## 5. Write the reproduction contract

Create `reproduction_contract.json` from `templates/reproduction_contract.template.json` **before target execution**.

Each target claim needs at least:

- `claim_id`
- `type`: `table_result|figure_result|ablation|benchmark|algorithm_behavior|runtime|resource|other`
- paper locator (`Table 2`, `Figure 4b`, `Sec. 5.2`, etc.)
- exact population/dataset/split
- model/method/condition
- metric or observable
- reported value/ordering/behavior when available
- aggregation level (single run, mean over seeds, best checkpoint, etc.)
- seed policy when reported
- target configuration
- comparison rule

Example:

```json
{
  "claim_id": "claim_table2_ours_cifar10",
  "type": "table_result",
  "paper_locator": "Table 2 / Ours / CIFAR-10",
  "metric": "accuracy",
  "reported": {"value": 84.7, "unit": "%", "variation": {"kind": "std", "value": 0.3}},
  "scope": {
    "dataset": "CIFAR-10",
    "split": "official test",
    "model": "paper model",
    "config": "configs/main.yaml",
    "seed_policy": [1, 2, 3]
  },
  "comparison_rule": {
    "kind": "reported_variation",
    "predeclared": true
  }
}
```

If a required field is absent from the paper/repository, record it under `unknowns` or `underspecifications.jsonl`; do not guess it into the contract as fact.

## 6. Build paper↔code traceability

Create `claim_code_map.jsonl`. One paper object may map to multiple code artifacts and one code artifact may serve multiple claims.

Recommended fields:

- `mapping_id`
- `claim_id`
- `paper_object`
- `paper_locator`
- `repo_artifacts[]` with path, symbol/config key when known, role, and revision
- `input_artifacts[]`
- `output_artifacts[]`
- `mapping_status`: `verified|partial|inferred|unmapped`
- `basis`
- `notes`

Example conceptual chain:

```text
paper claim
   ↕
experiment config
   ↕
entrypoint / code path
   ↕
data + checkpoint
   ↕
run_id
   ↕
metric row / output artifact
```

A valid final report should be able to move both directions: from a reported claim to the run artifact, and from a run artifact back to the claim it tests.

Read `references/02-paper-code-traceability.md` when mapping is non-trivial.

## 7. Reconstruct the environment without erasing drift

Inventory author-declared environment artifacts first:

- `requirements*.txt`
- `environment*.yml|yaml`
- `pyproject.toml`
- lockfiles
- `setup.py` / `setup.cfg`
- `Dockerfile*`
- compiler/CUDA notes
- CI workflows
- installation scripts

Preserve those sources under or by reference from `environment/source/`.

Create the actual isolated environment. After a successful or partially successful setup, capture the resolved state:

```bash
python scripts/capture_environment.py \
  --outdir reproduction/environment/resolved
```

Maintain `environment/environment_diff.json` with every material difference between declared and resolved state.

Do not treat a solver-produced environment as proof that it matches the original machine. Record OS, Python, GPU/CUDA visibility, package versions, compiler/runtime details when relevant, and only a safe allowlist of environment variables.

Read `references/03-environment-and-execution.md`.

## 8. Resolve data, checkpoints, and external artifacts

Create `data_manifest.json` and `checkpoint_manifest.jsonl` where relevant.

For every required external artifact, record:

- stable local ID
- source URL/repository/dataset registry
- version/revision/date when known
- retrieval status
- file or directory identity/hash where practical
- expected vs observed size when known
- split identity
- preprocessing path/config
- access/license limitation when material
- whether it is original, mirrored, substituted, or reconstructed

Hash a local artifact deterministically:

```bash
python scripts/hash_artifact.py path/to/file_or_directory \
  --output reproduction/artifacts/dataset_hash.json
```

For very large datasets, a manifest of stable file hashes or authoritative version identifiers may be more appropriate than one expensive recursive hash; record the chosen identity method.

## 9. Create the run plan and preflight

Create `run_plan.json` before target execution. Separate stages such as:

- environment/setup validation
- data/checkpoint validation
- import/CLI smoke test
- tiny-batch or minimal inference smoke test
- paper-declared evaluation command
- paper-declared training command when needed
- repeated seeds only when required by the target claim
- diagnostic follow-ups after a discrepancy

Estimate resource class and expected outputs. Mark which plan items are `scientific_target=true` versus setup/diagnostic work.

Run structural + semantic preflight:

```bash
python scripts/preflight.py reproduction --output reproduction/preflight.json
```

A passing preflight means the workspace is internally consistent for the declared stage, including provenance bindings that can be checked mechanically. It does not prove that the repository is safe, that the paper mapping is scientifically correct, or that the run will succeed.

## 10. Run the smoke test

The smoke test should exercise the shortest meaningful path without pretending to reproduce the target metric. Examples:

- import package and resolve config;
- load one batch;
- instantiate the model;
- load the declared checkpoint;
- run one forward/evaluation step;
- produce an output file in the expected format.

Record the smoke test in `run_ledger.jsonl` with `run_kind=smoke`.

If smoke fails, diagnose the blocker before launching full training/evaluation. Preserve the failed run and discrepancy/blocker record.

## 11. Execute target runs with provenance

Prefer the author-documented command exactly as written once the correct revision/environment/data are established. If the command needs path substitution or non-scientific adaptation, record it.

The deterministic wrapper can record execution provenance:

```bash
python scripts/run_with_ledger.py \
  --ledger reproduction/run_ledger.jsonl \
  --workspace reproduction \
  --run-id run_001 \
  --claim-id claim_table2_ours_cifar10 \
  --run-kind target \
  --cwd /path/to/checkout \
  --config configs/main.yaml \
  --logs-dir reproduction/logs \
  -- python evaluate.py --config configs/main.yaml
```

By default the wrapper refuses a dirty Git worktree. Use `--allow-dirty` only when an intentional patch is already documented; the wrapper records a diff fingerprint. For target runs it also records SHA-256 bindings for the current reproduction contract, run plan, repository manifest, data/checkpoint manifests, and claim↔code map. These bindings prevent a later-edited contract from silently governing an earlier run.

The wrapper passes only a small runtime-variable allowlist by default. To pass an additional non-secret variable that the reviewed command needs, add `--env VARIABLE_NAME`; do not pass credentials or tokens. Environment filtering is not a filesystem sandbox: run untrusted code in a disposable/isolated environment without sensitive files or mounts.

Do not use the wrapper as a substitute for security review: it executes the supplied argv.

## 12. Extract metrics without losing run identity

Write direct run outputs to `metrics.csv` with fields such as:

`run_id,claim_id,metric,value,unit,dataset,split,condition,aggregation,source_artifact,notes`

Do not compute new cross-run inference here unless it is merely reproducing an explicitly published aggregation rule. For fresh statistical analysis, hand the run-level data to `$scientific-data-analysis`.

## 13. Reconcile reproduced results with reported claims

For each `claim_id`, compare the recorded output against the **predeclared** comparison rule.

Recommended primary states:

- `exact_reproduction` — exact/deterministic target satisfied under materially matched protocol;
- `within_reported_variation` — result lies within a reported/predeclared variation region;
- `numerically_different` — target protocol completed but numeric result differs outside the declared comparison rule;
- `qualitatively_consistent` — directional/ordering/qualitative claim matches but numeric reproduction is not established;
- `partial_reproduction` — only part of the contracted condition set completed;
- `blocked_by_missing_data`;
- `blocked_by_missing_artifact`;
- `blocked_by_environment`;
- `underspecified`;
- `not_attempted`.

For simple scalar claims, deterministic reconciliation can generate a **candidate** assessment from the predeclared rule:

```bash
python scripts/reconcile_claims.py reproduction \
  --output reproduction/reproduction_assessment.candidate.json
```

Supported mechanical rules include exact equality, absolute tolerance, relative tolerance, and reported variation. Candidate output does not overwrite `reproduction_assessment.json`; review deviations and limitations before promoting any result to the final assessment.

Record the final state, supporting `run_id`s, comparison rule, observed values, material deviations, and confidence/limitations in `reproduction_assessment.json` or the report.

Do not collapse multiple target claims into one global paper verdict.

Read `references/04-assessment-and-discrepancies.md`.

## 14. Diagnose discrepancies without result chasing

Append every material issue to `discrepancies.jsonl`. Distinguish categories such as:

- `paper_repo_mismatch`
- `revision_mismatch`
- `environment_drift`
- `dependency_failure`
- `data_version_mismatch`
- `split_mismatch`
- `checkpoint_missing_or_mismatch`
- `config_mismatch`
- `preprocessing_ambiguity`
- `seed_or_aggregation_ambiguity`
- `evaluation_mismatch`
- `source_patch_required`
- `resource_limit`
- `numeric_discrepancy`
- `artifact_link_dead`
- `other`

Diagnostic modifications should produce new run IDs. Never overwrite the baseline target run with a tuned run that better matches the paper number.

## 15. PAPER_ONLY implementation protocol

When no usable repository exists:

1. extract all explicit implementation details from paper/supplement;
2. create `underspecifications.jsonl` for unresolved details;
3. separate algorithmic invariants from engineering choices;
4. create `implementation_decisions.jsonl` for every added choice;
5. implement the smallest code path needed to test the target claim;
6. mark whether each code element is `paper_specified`, `mechanically_derived`, or `assumption_required`;
7. keep assumptions parameterized where possible;
8. run sensitivity only if the target question requires it, and hand statistical interpretation downstream.

A paper-only run with material assumptions should normally be described as an *independent reconstruction under explicit assumptions*, not an exact execution of the authors' implementation.

## 16. REPO_AUDIT readiness dimensions

Audit these dimensions separately rather than giving one opaque score:

- paper identity evidence;
- paper-era revision availability;
- installation/environment specification;
- dataset availability and versioning;
- checkpoint/pretrained artifact availability;
- experiment entrypoint discoverability;
- config/hyperparameter traceability;
- evaluation command discoverability;
- claim↔code mapping coverage;
- expected output/metric traceability;
- license/access blockers;
- smoke-test evidence, if execution was authorized/performed.

Use `ready`, `partial`, `missing`, `blocked`, or `not_checked` per dimension. Do not convert these to a universal numeric reproducibility score. A deterministic readiness snapshot can be generated with:

```bash
python scripts/audit_repo_readiness.py reproduction \
  --output reproduction/repository_readiness.json
```

This output is dimension-level evidence only; it deliberately contains no aggregate score.

## 17. Standard workspace

A standard/release reproduction workspace should converge toward:

```text
reproduction/
├── reproduction_contract.json
├── paper_manifest.json
├── repository_manifest.json
├── claim_code_map.jsonl
├── data_manifest.json
├── checkpoint_manifest.jsonl
├── underspecifications.jsonl
├── implementation_decisions.jsonl
├── run_plan.json
├── run_ledger.jsonl
├── metrics.csv
├── discrepancies.jsonl
├── reproduction_assessment.json
├── reproduction_report.md
├── reproduction_assessment.candidate.json   # optional mechanical candidate
├── repository_readiness.json                 # REPO_AUDIT / optional
├── preflight.json
├── environment/
│   ├── source/
│   ├── resolved/
│   │   ├── system.json
│   │   ├── resolved_environment.json
│   │   └── pip_freeze.txt
│   └── environment_diff.json
├── patches/
├── logs/
├── artifacts/
└── manifest.sha256
```

Not every file is required for every mode. `REPO_AUDIT` may stop before run artifacts; `PAPER_ONLY` may have no repository manifest until an implementation workspace exists.

Initialize a workspace:

```bash
python scripts/init_workspace.py reproduction --mode REPO_REPRODUCE --profile standard
```

## 18. Preflight and release

Before a `release` handoff:

1. validate required contract/manifests for the selected mode;
2. ensure target runs are bound to the exact contract/run-plan/manifest hashes used at execution time;
3. reject post-run mutation of execution-defining artifacts unless a new target run is performed;
4. ensure target-run commits match the pinned repository revision, and dataset/checkpoint IDs resolve to their manifests;
5. ensure every metric row resolves to a known run **and** a claim linked to that run;
6. enforce eligibility conditions for `exact_reproduction` and `within_reported_variation`;
7. ensure dirty/modified runs have patch provenance and cannot support an exact state;
8. preserve failed attempts and unresolved discrepancies;
9. capture the resolved environment;
10. run semantic regression tests for the skill package;
11. freeze the workspace.

Run:

```bash
python scripts/release_check.py reproduction
python scripts/freeze_workspace.py reproduction --output reproduction/manifest.sha256
```

If release check fails, report the failed conditions; do not simply delete the evidence that caused failure.

## 19. Handoff interfaces

### From `$literature-research`

Accept:

- selected study/report identity;
- verified paper/source URLs;
- DOI/arXiv/version metadata;
- relevant claim/evidence IDs when available;
- candidate project/repository links.

Do not assume a bibliographic report and a code repository are already version-aligned.

### To `$scientific-data-analysis`

Export:

- `metrics.csv` and/or raw output tables;
- `run_ledger.jsonl`;
- target claim metadata;
- seed/aggregation policy;
- dataset/split identity;
- deviations/discrepancies that may affect inference.

Let data analysis compute new confidence intervals, significance tests, effect sizes, robustness, and multi-run summaries.

### To `$scientific-figure`

Export only traceable results/artifacts plus the exact run/claim IDs that support a figure.

### To `$academic-manuscript-writing` or `$manuscript-reviewer`

Export claim-scoped reproduction states, observed values, blockers, environment/revision scope, and discrepancy evidence. Avoid a global “reproducible/not reproducible” label when the evidence is claim-specific.

## 20. Reporting language

Prefer scoped statements:

- “The Table 2 CIFAR-10 result was within the paper's reported standard-deviation range under commit `<sha>` and the recorded environment.”
- “The target evaluation completed, but the reproduced accuracy differed by 0.8 percentage points under the recorded setup.”
- “Reproduction was blocked by an unavailable checkpoint referenced by the repository.”
- “The optimizer schedule was not specified in the paper or available artifacts, so this claim remains underspecified.”

Avoid unearned statements:

- “The whole paper is reproduced.”
- “The paper is irreproducible.”
- “The official code proves the result.”
- “The current main branch is the paper implementation.”

## 21. Minimal invocation examples

```text
Use $paper-reproduction in REPO_REPRODUCE mode to reproduce Table 3 of this paper using its official repository. Pin the paper-era code revision, build a claim↔code map, run a smoke test first, and preserve all run provenance.
```

```text
Use $paper-reproduction in PAPER_ONLY mode. Extract exactly what the paper specifies, list all missing implementation details, and implement only the mechanically recoverable parts needed to test Figure 4b.
```

```text
Use $paper-reproduction in REPO_AUDIT mode on this GitHub repository. Identify the associated paper, inspect whether paper-era code/config/data/checkpoints/evaluation commands are available, and produce a readiness report without claiming reproduction unless an experiment is actually run.
```

## 22. Definition of done

A standard reproduction is complete only when the user can answer, from the workspace itself:

1. Which exact paper version and claim were tested?
2. Which repository and exact source revision were used?
3. How does the paper claim map to code, config, data, checkpoint, and evaluation artifacts?
4. What environment actually executed the run, and how did it differ from the author's declaration?
5. What exact command ran, under what seed/config/data identities, and what happened?
6. Which output artifact produced the reported reproduction metric?
7. How does that result compare with the paper under a predeclared rule?
8. What discrepancies, blockers, substitutions, patches, and unknowns remain?
9. Can the entire handoff be audited later without relying on the model's memory?

If those questions cannot be answered, the workflow may have produced a run, but it has not yet produced an AutoSCI-grade reproduction record.
