# Severity and evidence calibration

Use severity to reflect **scientific impact**, not frequency, annoyance, or how easy an issue is to notice.

# Severity

## Critical
Examples:
- Main abstract/conclusion claim is contradicted by the paper's own primary results and materially changes the paper's central message.
- A central reported result uses the wrong metric/dataset/model in a way that changes the main conclusion.
- A core equation/notation defect makes the central method non-interpretable or non-reproducible.
- A central causal/generalization/safety claim has no remotely matching evidence and is foundational to the paper's contribution.

Use sparingly.

## Major
Examples:
- “Outperforms all baselines” is false for a meaningful evaluation condition.
- Main text and primary table disagree on an important value beyond plausible rounding.
- A key comparison silently changes protocol while being presented as direct.
- A central notation collision creates two plausible method interpretations.
- A major abstract/conclusion claim materially exceeds tested scope.

## Moderate
Examples:
- Important result lacks a needed dataset/split qualifier.
- Figure caption and main text disagree in a way that is resolvable but misleading.
- A recurring symbol is defined inconsistently but context often disambiguates it.
- A broad secondary claim needs qualification to match tested settings.

## Minor
Examples:
- Incorrect panel reference with obvious intended target.
- One symbol is used shortly before an otherwise clear definition.
- Citation is attached one sentence too late with little ambiguity.
- Table highlighting convention is locally inconsistent but does not alter interpretation.

# Confidence

## High
Requires direct evidence from inspected material and no material unresolved alternative explanation.

## Medium
Use when:
- PDF extraction/rendering is somewhat ambiguous;
- interpretation depends on an unavailable appendix/source;
- two reasonable readings exist;
- protocol comparability is probable but not fully explicit.

## Low
Use sparingly for a genuine finding whose evidence remains weak but still reportable. If the core issue is unresolved ambiguity rather than an established defect, prefer an `author_query` instead of a Low-confidence error claim.

# Evidence state vs severity

Evidence state and severity are separate:
- `contradicted` can be Minor if it concerns an inconsequential label;
- `partial_support` can be Major if it affects the central abstract claim;
- `unavailable_to_verify` normally maps to a `coverage_gap`, not a severity-bearing finding.

# Evidence-sufficiency precondition

Severity is assigned **after** the concern has passed the defect-type evidence threshold in `evidence_sufficiency_and_synthesis.md`. Do not use high severity to compensate for weak evidence. If the evidence packet is incomplete, reclassify the concern before calibrating severity.

# Severity sanity check

Before marking Major/Critical, ask:
1. If unfixed, could a competent reader reach a materially wrong scientific understanding?
2. Does it affect a central claim, method, result, or reproducibility?
3. Is the mismatch verified rather than speculative?
4. Did the adversarial pass fail to resolve it?
5. Would the same severity still be appropriate if the issue appeared only once rather than repeatedly?

If mostly no, downgrade it.

# Counterfactual impact test

For borderline severity, ask a concrete counterfactual:

> If this issue remained unfixed but every other issue were corrected, what materially wrong scientific belief, comparison, or implementation could a competent reader still take away?

Use the answer to calibrate consequence:
- central conclusion becomes materially false/misleading -> Critical/Major territory;
- secondary interpretation or reproducibility detail is materially distorted -> Major/Moderate depending on centrality;
- local reading remains technically recoverable with low scientific risk -> Moderate/Minor.

Do not use the number of affected sentences as a substitute for this test.

# Repair-cost independence

Do not use effort required to fix the problem as a proxy for severity.

A central abstract overclaim may be Major even if one wording edit fixes it. Conversely, a tedious notation cleanup may remain Minor if scientific interpretation is stable.

# Borderline calibration dimensions

For borderline cases, reason qualitatively across these dimensions without computing a score:
- **centrality** — headline claim/core method vs peripheral detail;
- **reader consequence** — could the issue materially change scientific interpretation?;
- **reproducibility consequence** — could it lead to a materially different implementation/evaluation?;
- **scope of propagation** — does one root defect contaminate several headline surfaces?;
- **evidentiary certainty** — is the defect directly established?;
- **repair type** — record separately, but do not let repair effort determine severity.

Repeated appearance of the same root defect does not automatically increase severity; assess the scientific consequence of the root cause.

# Severity vs presentation salience

Severity describes scientific consequence. Presentation salience describes where the issue belongs in the final reviewer-style report. They are related but not identical.

- A verified Major/Critical issue is normally a main comment.
- A material author query may be a main comment even though it has no severity label.
- A recurring Minor notation pattern can be secondary/cleanup rather than repeated in the main body.
- Do not downgrade scientific severity merely to keep the main-comment section short.

Use `report_policy_and_salience.md` after severity is fixed.

# Revision residual-severity recalibration

In revision/rebuttal review, severity is a **current-state judgment**, not a lineage property.

Before assigning current severity to a `persistent` or `partially_resolved` root:
1. temporarily hide/ignore the prior severity label;
2. describe only the defect that remains in the current manuscript;
3. identify which prior surfaces/claims were actually repaired;
4. apply the counterfactual impact test to the **current remainder**;
5. only then compare with the old severity as a sanity check.

Do not preserve `Major` merely because the lineage was previously Major.

A common partial-repair pattern is:
- abstract/results are corrected;
- one stale conclusion sentence remains;
- the evidence table and local discussion now state the narrower result correctly.

This may reduce severity because a competent reader can recover the correct result from the current evidence and main analysis, even though the stale conclusion still requires correction. It is not automatically Moderate: if the surviving conclusion remains the paper's central public-facing scientific message or still materially changes interpretation, Major can remain. The point is to **recompute**, not inherit.

Conversely, new evidence can make a previously ambiguous or Moderate issue Major. Revision status and severity are independent.
