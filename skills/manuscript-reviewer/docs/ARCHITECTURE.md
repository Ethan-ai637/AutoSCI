# Architecture

`manuscript-reviewer` separates scientific review into four layers.

## 1. Evidence acquisition and coverage

The reviewer establishes an evidence boundary, manuscript archetype, section coverage, result-object inventory, provenance, and protocol comparability. Long documents use explicit checkpoints so “not noticed” cannot become “missing.”

## 2. Scientific adjudication

Central claims are decomposed into atomic propositions. The reviewer checks claim→evidence, evidence→narrative, inference bridges, numerical derivations, notation, citations, and overclaim. Candidate concerns must satisfy type-specific evidence sufficiency and adversarial checking.

## 3. State and root-cause model

Surviving concerns become exactly one of `finding`, `author_query`, or `coverage_gap`. Findings receive severity and all records receive canonical salience. Related manifestations are merged by scientific root. The authoritative vocabulary is `checks/state_model.md`.

## 4. Rendering and revision lineage

Every outward concern is first stored as a canonical record. Prose reports, summaries, checklists, and structured exports inherit from that record rather than re-adjudicating it. Revision review matches prior and current scientific roots, recalculates severity from the current remainder, and checks dependency propagation.

## Design invariant

The skill is optimized for **precision under evidence constraints**, not for producing a large number of reviewer comments. Missing evidence, unavailable evidence, contradictory evidence, and ambiguous mapping are intentionally distinct states.
