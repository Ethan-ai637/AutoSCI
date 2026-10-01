# Finding lifecycle, root-cause clustering, and noise control

## Objective

Prevent the reviewer from dumping every suspicion into the final report. Findings must survive a staged verification process and be organized by root cause.

## Finding lifecycle

Use these internal states:

1. `candidate` — a possible mismatch noticed during reading.
2. `evidence_checked` — relevant local evidence and protocol context inspected.
3. `sufficiency_checked` — the defect-type-specific minimum evidence packet is satisfied, or the concern is downgraded/reclassified.
4. `adversarially_checked` — plausible resolving explanations actively tested.
5. `disposition_assigned` — classified as finding, author query, coverage gap, or resolved-no-issue.
6. `root_clustered` — merged with other manifestations of the same underlying problem and linked to dependencies.
7. `salience_assigned` — placed as main comment, secondary finding, cleanup, query, or coverage gap after scientific disposition is fixed.
8. `stable_id_assigned` — final finding/query/gap ID assigned after root clustering using stable manuscript-location ordering, never discovery order.
9. `canonical_recorded` — one canonical finding/query/gap record is instantiated with its evidence packet and summary-safe statement.
10. `reportable` — passes evidence sufficiency, classification, actionability, deduplication, provenance, reproducibility, canonical-record integrity, synthesis, and report-policy requirements.
11. `suppressed` — terminal state for resolved, duplicate, stylistic-only, too speculative, or immaterial candidates.

Only `reportable` concerns appear in the final review. Read `evidence_sufficiency_and_synthesis.md` before promoting a concern beyond `sufficiency_checked`, `report_policy_and_salience.md` before assigning presentation tier, `review_reproducibility.md` before assigning final IDs, and `canonical_finding_record.md` before `canonical_recorded`.

## Root-cause clustering

Merge multiple manifestations when one correction would fix them together.

Example:
- abstract says "all datasets";
- result paragraph repeats "all datasets";
- conclusion says "universally superior";
- Table 2 contains one exception.

Prefer one cross-surface root finding with all locations. When one defect propagates into later claims, record those as dependent manifestations rather than independent counts.

Keep separate findings when fixes differ materially, even if they involve the same table or claim.


## Dependency-aware clustering

Use a root/dependent relation when one verified defect mechanically propagates into other surfaces.

Examples:
- one wrong denominator propagates into a table percentage, abstract percentage, and conclusion claim;
- one mislabeled dataset split propagates into several comparative statements;
- one unsupported mechanism inference is repeated in the abstract and discussion.

Count the root defect once unless a downstream manifestation creates a scientifically distinct problem requiring a different remedy.

In revision/rebuttal review, dependency edges are **not** automatic resolution edges. Read `checks/revision_tracking_and_resolution.md`: a repaired parent resolves a dependent manifestation only if the dependent no longer survives on the current manuscript surface and has no independent scientific basis. Otherwise detach/re-root the surviving concern.

## Traceability requirement

For every Major/Critical root finding, preserve an internal trace that identifies:
- claim anchor;
- evidence anchor(s);
- material result/value/relationship;
- inference bridge when nontrivial;
- derivation/source anchor when applicable.

A reviewer should be able to reconstruct the finding without searching the entire manuscript again.


## Provenance requirement

For a Major/Critical comparison, result conflict, or citation-semantic finding, record provenance when it can affect validity:
- current-author vs imported result;
- rerun vs copied baseline;
- raw vs derived quantity;
- manuscript/source/artifact version;
- protocol identity.

If provenance remains materially ambiguous, prefer an author query over a confident incompatibility claim.

## Stable-ID rule

Do not finalize public IDs while candidates are still being discovered.

After root clustering:
1. choose the primary root category;
2. sort roots by stable manuscript location within category, breaking ties by centrality/severity;
3. assign category IDs sequentially;
4. assign `AQ-xx` and `CG-xx` similarly.

This prevents discovery order from becoming part of the review result. After the ID is fixed, instantiate exactly one canonical record for that root item; every later prose/table/JSON rendering must inherit from it.

## Precedence rule

When one issue could fit multiple audit categories, choose a primary category based on the root defect and cross-reference mentally rather than duplicating it.

Suggested precedence:
- wrong/reconciled number -> numerical or figure/table consistency;
- evidence too narrow for wording -> claim–evidence or overclaim;
- symbol changes technical meaning -> notation;
- source attribution/support problem -> citation.

Use `XR` for genuinely cross-category root issues when no single category captures the defect.

## No-quota rule

Never force a minimum number of findings.

A high-quality review may legitimately report:
- no Critical issues;
- no citation semantic problems;
- no notation problems;
- or no material problems at all in a category.

Do not manufacture Minor issues to make the report look complete.

## Salience rule

Severity is assigned before presentation salience. Read `report_policy_and_salience.md` for the main-comment gate and issue graph. Prioritize findings that change:
- a central scientific conclusion;
- interpretation of a main result;
- reproducibility of a method;
- correctness of a quantitative statement;
- attribution of prior evidence;
- the scope readers would infer from title/abstract/conclusion.

Cosmetic issues should not displace material ones.

## Reporting density

For standard mode:
- report all verified Critical/Major findings;
- report material Moderate findings;
- report Minor findings selectively, especially recurrent ones.

For exhaustive mode, Minor findings may be broader, but still deduplicate repeated instances when one pattern-level correction suffices.

## Suppression reasons

Suppress a candidate if any apply:
- resolved by nearby qualifier/caption/footnote;
- incomparable protocols explain the apparent mismatch;
- PDF extraction artifact;
- citation source was not inspected and the only concern is semantic support;
- merely stylistic with no technical effect;
- duplicate symptom of a stronger root finding;
- exact value would require plot guesswork;
- concern depends on unstated field convention rather than manuscript evidence;
- impact is too speculative to support the proposed severity.

# Disposition gate

After adversarial checking, assign each surviving concern to exactly one outward-facing class using `disposition_and_remediation.md`:
- `finding`;
- `author_query`;
- `coverage_gap`.

Use `resolved_no_issue` internally when the candidate is explained.

Do not use severity labels to make an author query sound more consequential. If uncertainty is the core problem, report the uncertainty precisely. Conversely, do not use `author_query` merely because the authors could later supply missing support: if a completed absence check verifies that the current manuscript explicitly makes a support-bearing claim without reporting the required support/assumption, the manuscript-level defect may be a finding. See the decision boundary in `disposition_and_remediation.md`.

# Convergence / stop rule

Stop expanding the issue search when all of the following are true for the selected review mode:
- central claims have coverage states;
- primary result objects have been reverse-mapped to narrative uses;
- all current candidates have final dispositions;
- Major/Critical findings have complete evidence packets;
- blocked verification is recorded;
- further searching is producing only duplicate, stylistic, or low-value candidates.

Completeness is measured by **coverage of important scientific objects**, not by number of findings.
