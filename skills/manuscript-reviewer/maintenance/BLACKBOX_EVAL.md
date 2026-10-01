# Independent black-box evaluation protocol

## Goal

Evaluate the installed skill without exposing expected findings or scoring logic to the reviewing agent.

## Required separation

Keep three roles logically separate:

1. **reviewer** — Codex/agent with the installed skill;
2. **blind input** — manuscript/test materials plus a fixed evaluation prompt;
3. **scorer/oracle** — expected scientific roots, hard negatives, transition expectations, and scoring rubric kept outside the reviewer context.

## Procedure

1. Start a clean Codex session.
2. Install the exact skill release being evaluated.
3. Provide only the blind test archive and fixed test prompt.
4. Do not provide mutation manifests, expected findings, scorecards, oracle files, prior dry-run outputs, or discussion revealing planted defects.
5. Disable external web lookup when the benchmark defines a closed evidence boundary.
6. Preserve the generated result unchanged.
7. Score the result externally against the oracle.
8. Classify failures as at least: false positive, false negative, disposition, severity, duplicate/root clustering, coverage, provenance/comparability, revision lineage, or synthesis/render drift.
9. Convert the smallest generalizable failure into a regression fixture before changing runtime rules.
10. Rerun old regression fixtures after the change.

## Metrics

At minimum track:
- material root recall;
- false-positive rate / hard-negative pass rate;
- disposition accuracy;
- severity agreement or allowed severity band;
- duplicate-root rate;
- provenance/comparability correctness;
- revision-transition accuracy;
- synthesis/render fidelity;
- structured-output validity when requested.

Do not compare exact prose as the main metric.

## Version honesty

A score from an earlier skill version is not a score for a later release. A release may cite inherited regression coverage, but performance claims require a fresh independent run of that release.
