# Issue disposition and minimal-sufficient remediation

## Objective

Separate verified manuscript defects from unresolved questions and blocked verification, then recommend the **least burdensome scientifically sufficient remedy**.

A reviewer should not turn uncertainty into an error claim, and should not turn a wording defect into an unnecessary new-experiment request.

# Output disposition classes

Every surviving concern must end in exactly one of these outward-facing classes:

## 1. `finding`
Use when inspected evidence is sufficient to establish a material defect, mismatch, unsupported manuscript-internal claim, or technically meaningful ambiguity.

Typical cases:
- direct contradiction between prose and a table;
- central claim broader than the manuscript's own tested scope;
- reproducibility-relevant notation collision;
- reconstructable arithmetic error;
- citation metadata/reference-list inconsistency;
- semantic citation mismatch after the cited source was actually inspected.

Findings receive severity and confidence.

## 2. `author_query`
Use when a material ambiguity remains after reasonable checking and more than one scientifically plausible interpretation survives.

Typical cases:
- evaluation protocol is not explicit enough to establish whether two numbers are directly comparable;
- denominator/aggregation rule is unclear, so a headline aggregate cannot be reconstructed;
- the manuscript may use a local symbol convention, but the scope is not explicit enough to disambiguate;
- source attribution may be correct, but the exact mapping between claim and cited evidence remains unclear despite available context.

Do **not** phrase an author query as an established error. Author queries do not need a paper-style severity label; optionally mark priority as `material` or `low-priority`.

## 3. `coverage_gap`
Use when verification is blocked by unavailable or unreadable material rather than by the manuscript's demonstrated defect.

Typical cases:
- unavailable supplement;
- inaccessible cited paper needed for semantic-support verification;
- unreadable figure panel;
- missing code/data that the review scope intended to inspect.

Coverage gaps do not receive Major/Critical severity merely because verification is impossible.

## 4. `resolved_no_issue`
Internal-only. Use when a candidate concern is explained by a caption, footnote, alternate protocol, rounding, local notation scope, rendering artifact, or other valid explanation.

Never output these as problems.

# Evidence state vs disposition

Evidence state describes the **claim-evidence relationship**. Disposition describes **how the reviewer reports the concern**.

Examples:
- `contradicted` -> usually `finding`;
- `partial_support` -> `finding` when material, otherwise no issue;
- `missing_required_evidence` -> `finding` when the manuscript itself makes the claim without testing it;
- `ambiguous_mapping` -> often `author_query`, unless the ambiguity itself makes a central method/result non-interpretable, in which case it can be a `finding`;
- `unavailable_to_verify` -> usually `coverage_gap`, not `finding`.

Do not collapse these concepts.



# Finding vs author-query decision boundary

Use the following distinction before dispositioning a concern:

## A. Unknown scientific truth can still coexist with a verified manuscript defect

A reviewer does **not** need to prove that the underlying scientific proposition is false in order to establish that the current manuscript does not substantiate an explicit material claim.

If all are true:
1. the manuscript explicitly asserts a material proposition (for example `p<0.05`, equivalence, asymptotic interchangeability, same-protocol comparison, or a named mechanism);
2. the claim requires a specific kind of support or stated assumption;
3. the relevant available manuscript locations and supplement have been checked;
4. that required support/assumption is not reported;
5. no unavailable artifact is the reason verification is blocked;

then the reportable defect can be a `finding` framed narrowly as **unsubstantiated / insufficiently reported in the current manuscript**.

Do not overstate it. For example:
- correct: “The manuscript asserts paired-test significance but does not report the paired unit, test statistic, p-values, or other output needed to substantiate that assertion.”
- incorrect: “The gains are not significant.”

Likewise, if two asymptotic expressions are asserted to be interchangeable but the manuscript never states the relationship that makes the substitution valid, the verified defect is the missing justification/reporting in the manuscript; the reviewer need not guess whether the authors possess an unstated proof.

## B. Use `author_query` when the defect itself still depends on unknown facts

Prefer `author_query` when, after reasonable checking, more than one scientifically plausible manuscript interpretation remains and **the existence of a defect cannot yet be established from the available manuscript package**.

Examples:
- it is unclear whether a baseline was rerun or imported and the available text does not settle provenance;
- an aggregate may be correct under one of several plausible denominators, none of which is specified;
- a symbol may be local or global and the manuscript scope markers are genuinely ambiguous.

## C. Use `coverage_gap` when the blocker is outside the available manuscript package

If the needed appendix/source/artifact is unavailable, use `coverage_gap`, not a finding about missing manuscript support, unless the manuscript itself explicitly demonstrates that the material was never provided.

## Operational test

Ask:
> “Can I establish a defect in what the current manuscript **states or substantiates**, without knowing the hidden scientific truth?”

- **Yes** -> finding, calibrated to the reporting/support defect actually established.
- **No; author intent/mapping/protocol fact is still genuinely ambiguous** -> author query.
- **No; required evidence is unavailable outside the supplied boundary** -> coverage gap.

This test is especially important for statistical-significance claims, equivalence/non-inferiority wording, complexity/scaling assertions, and protocol/provenance statements.

# Minimal-sufficient remediation classes

Assign one primary remediation class internally to each reportable finding:

- `text_reconciliation` — correct prose so it matches already-present evidence.
- `scope_qualification` — narrow wording to the population, datasets, settings, metrics, or inference actually tested.
- `label_or_crossref_repair` — repair panel/table/equation/section references, labels, units, or highlights.
- `notation_repair` — define, rename, scope, or standardize symbols without changing the method.
- `citation_repair` — move/add/correct citation metadata or replace an attribution with one that is actually supported.
- `reporting_detail` — state missing protocol, denominator, aggregation, uncertainty, split, sample size, or implementation detail already known to the authors.
- `reanalysis_or_recalculation` — recompute a reported quantity from existing data/results because current arithmetic/aggregation is incorrect.
- `additional_analysis` — analyze already-available data/results in a way necessary to test the stated claim (for example subgroup, sensitivity, or uncertainty analysis).
- `additional_experiment` — collect/run genuinely new empirical evidence because the manuscript intends to retain a claim that existing evidence does not test.
- `claim_removal` — remove a claim that cannot be supported and is not essential to retain.

# Minimal-remedy rule

Choose the smallest remedy that restores scientific correctness and reader interpretability.

Examples:
- If evidence supports “2 of 3 datasets” but prose says “all datasets”, prefer `text_reconciliation` or `scope_qualification`, not `additional_experiment`.
- If the authors want to keep a robustness claim but only nominal-condition results exist, either narrow/remove the robustness claim **or**, if retaining it is important, request robustness evidence.
- If an aggregate cannot be reconstructed because the denominator is omitted, request `reporting_detail` before demanding reanalysis.
- If the arithmetic is demonstrably wrong from explicit inputs, request `reanalysis_or_recalculation`, not a new experiment.

# Fix-burden independence

Scientific severity and repair cost are independent.

- A Major overclaim may be fixable by changing one sentence.
- A labor-intensive formatting or notation cleanup may still be Minor.
- Do not upgrade severity because a fix is expensive.
- Do not downgrade severity because a fix is easy.

# Evidence packet for reportable findings

Before a concern becomes a `finding`, read `evidence_sufficiency_and_synthesis.md` and satisfy the defect-type-specific minimum packet. Then build a compact internal evidence packet:

1. exact claim/object;
2. exact manuscript location(s);
3. source evidence object(s);
4. protocol/comparability context when relevant;
5. provenance/version context when imported, derived, external, or cross-revision evidence is material;
6. explicit value/text/relationship that establishes the problem;
7. strongest plausible resolving explanation tested;
8. why that explanation did not resolve the concern;
9. disposition;
10. severity/confidence;
11. remediation class and minimal sufficient fix;
12. compact trace path linking claim → evidence/result → material inference or derivation, when nontrivial.

If this packet cannot be completed for a proposed Major/Critical issue, the concern is not ready to be reported at that level.


# Absence-claim safeguard

A `missing_required_evidence` finding additionally requires a claim-directed absence check across the plausible available manuscript locations. A failed string search, abstract-only scan, or memory-based impression is not sufficient evidence of absence.
