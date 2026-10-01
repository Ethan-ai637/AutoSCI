# Report policy, salience, and issue graph

## Objective

Turn a complete audit into a concise reviewer-style report that foregrounds scientifically important root problems without hiding real independent issues.

This layer controls **presentation and issue topology**, not scientific truth. It must never suppress a verified independent Major/Critical defect merely to make the report shorter.

## Issue graph

After root-cause clustering, represent surviving concerns internally as an issue graph.

Each node is one of:
- `root_finding` — independent verified defect;
- `dependent_manifestation` — downstream surface caused by a root defect;
- `author_query` — unresolved material ambiguity;
- `coverage_gap` — verification blocked by missing/unreadable evidence.

Useful edges:
- `causes` — root defect mechanically produces a downstream mismatch;
- `repeats_as` — same defect restated on another manuscript surface;
- `supports` — one issue establishes why another consequence matters;
- `blocked_by` — verification depends on an unavailable artifact.

Do not expose this internal graph by default.

## Dominance / subsumption rule

A stronger root finding subsumes a weaker manifestation when all are true:
1. the same underlying defect explains both;
2. fixing the root would fix the manifestation;
3. the manifestation does not add a distinct scientific consequence;
4. the manifestation does not require a different remediation.

Retain a separate finding when it has an independent cause, independent scientific consequence, or materially different remedy.

Example:
- wrong denominator -> table percentage -> abstract percentage -> conclusion wording: usually one root numerical finding;
- wrong denominator **and** an independent unsupported causal interpretation of that same table: two findings may be warranted because the second survives even after correcting the denominator.

## Salience tiers

Assign one internal presentation tier after severity/confidence are fixed:

### `main_comment`
Use when at least one applies:
- Critical/Major root finding;
- material Moderate issue affecting a central claim/result/reproducibility;
- cross-surface root defect that substantially shapes reader interpretation;
- material author query that blocks interpretation of a headline result.

### `secondary_finding`
Use for:
- verified Moderate issues with local or secondary impact;
- Minor technical inconsistencies that recur or affect reproducibility/interpretability;
- useful corrections that should be visible but should not compete with central problems.

### `cleanup`
Use for:
- low-risk Minor corrections;
- repeated notation/cross-reference/label patterns that can be fixed together;
- issues best summarized as one pattern rather than itemized individually.

Salience is not a paper score and is not the same as severity. A Major usually belongs in `main_comment`, but an author query can also be a main comment without carrying severity.

## Main-comment eligibility gate

Before placing an issue in the main body, ask:
1. Does this change interpretation of a central contribution, result, method, or claimed scope?
2. Could it materially mislead a competent reader or impede reproduction?
3. Does it block verification of a headline claim?
4. Is it a root cause rather than a symptom already covered elsewhere?

If all are no, it normally belongs in secondary findings or cleanup.

## Density diagnostic — not a hard cap

There is **no maximum number** of genuine main comments.

However, in standard mode, if the draft contains more than roughly 6 independent main comments, perform a diagnostic pass:
- check for root-cause over-splitting;
- check category duplication;
- check whether some Moderate/Minor items are crowding out central issues;
- check whether author queries are being inflated into findings;
- check whether one broad root problem can be stated once with dependent manifestations.

If the issues are truly independent and material, keep them. Never suppress a real Major/Critical issue to meet a target count.

## Reviewer-style ordering

Default ordering inside the final report:
1. Critical/Major root findings by scientific consequence;
2. material central Moderate findings;
3. material author queries;
4. secondary verified findings;
5. cleanup/pattern-level items;
6. coverage gaps.

Within equal severity, prefer:
- root before dependent symptom;
- central before peripheral;
- reader/reproducibility consequence before cosmetic consequence;
- earlier stable manuscript location as a final tie-breaker.

Do not order by discovery sequence. Assign public IDs only after root clustering and stable ordering using `review_reproducibility.md`.

## Category audits are coverage evidence, not the report spine

The six audit categories are how the reviewer **checks** the paper. They do not have to be how the reviewer **writes** the final report.

In standard mode:
- organize substantive comments by scientific root issue;
- use IDs/prefixes to retain category provenance;
- summarize audit coverage once at the end;
- do not repeat the same issue under claim-evidence, overclaim, and figure/table sections.

In exhaustive mode, detailed category tables may be included as an appendix after the reviewer-style main report.

## Correction checklist rule

A correction checklist should reference finding/query IDs and remediation actions rather than restating full findings.

Good:
- `CE-02 — narrow the abstract generalization claim to the three evaluated datasets.`

Avoid repeating the entire evidence narrative in both the finding and checklist.

## Compression rule for repeated Minor issues

When several low-risk issues share one correction pattern, report one pattern-level item with representative locations and state that the pattern recurs.

Example:
> `NT-04 Minor — vector boldface is inconsistent for x, z, and h across Eqs. 4–9; standardize the convention throughout this block.`

Do not enumerate every occurrence unless the user requests exhaustive line editing.

## No category quota

Do not preserve one issue from every audit category merely for balance. A reviewer-style report may have several claim-evidence findings and no citation finding, or vice versa.

Completeness comes from audit coverage, not category symmetry.


# Synthesis inheritance rule

After ordering the report, apply `evidence_sufficiency_and_synthesis.md` before writing the executive summary or correction checklist. These sections may compress final root items but may not strengthen disposition, severity, confidence, scope, or remediation. Counts must use final deduplicated root findings only.


# Canonical-to-prose placement invariant

Report section placement is a rendering of canonical `salience`, not a fresh editorial decision:
- `main_comment` -> main comments;
- `secondary_finding` -> secondary findings;
- `cleanup` -> cleanup/pattern section;
- `query` -> author queries;
- `coverage_gap` -> coverage gaps.

Do not write the prose first and then leave a conflicting salience in structured output. Do not move an item between report layers for aesthetics without updating the canonical record and any summary counts.

As a pre-release check, compare every outward item against its canonical record. Any mismatch in ID, severity, confidence, disposition, or salience must be corrected before release.
