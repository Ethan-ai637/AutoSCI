# Revision, rebuttal, and resolution tracking

## Objective

Support evidence-grounded re-review of revised manuscripts and rebuttals without carrying prior findings forward mechanically or losing issue identity when text moves.

Revision review is a **delta audit**, not a fresh report with old comments pasted on top.

The reviewer must determine, for each prior material root issue, whether the underlying scientific concern is:

- `resolved` — the prior root no longer holds under the current manuscript/evidence;
- `partially_resolved` — the change addresses part of the root, but a material remainder survives;
- `persistent` — the same scientific root remains materially unchanged;
- `reclassified` — the same lineage remains relevant, but new evidence changes disposition/category/severity (for example, an author query becomes a verified finding, or a finding becomes an author query);
- `not_reassessable` — the issue remains material, but current materials do not permit a reliable resolution judgment;
- `no_longer_material` — the old concern/verification was not substantively adjudicated, but the revised manuscript no longer depends on it for a material current claim;
- `new` — a current root issue is not traceable to a prior root.

Do not assign these states from author assertions alone. Re-inspect the current manuscript evidence.

## Activation

Use revision tracking only when at least one of the following is available:

- a prior manuscript version;
- a prior reviewer report or canonical records;
- an author rebuttal/response letter linked to reviewer concerns;
- explicit version-to-version review instructions.

If no prior evidence or prior issue description is available, run a normal review. Do not invent historical lineage.

When prior material is prose-only rather than canonical records, reconstruct prior issue identity cautiously and mark lineage confidence internally as `partial` if exact mapping is uncertain.

## Review-context types

Use one internal context label:

- `initial_review` — no prior review lineage is being evaluated;
- `revision_check` — compare a revised manuscript against prior findings/version;
- `rebuttal_check` — assess whether an author response plus current manuscript evidence resolves prior concerns;
- `version_delta` — compare manuscript versions even when no prior review exists.

This context changes the workflow, not the scientific evidence standard.

## Lineage identity

Match prior and current concerns by **scientific root identity**, not literal wording or page number.

Use, in order:
1. atomic claim/object identity;
2. scientific root cause;
3. evidence/result object identity;
4. remediation target;
5. stable manuscript location as supporting evidence, not the sole key.

A moved paragraph or renumbered table does not create a new issue if the same root survives.

A superficially similar sentence is not the same issue if the underlying scientific object or evidentiary defect changed.

## Stable-ID continuity

Preserve a prior public ID when all of the following hold:
- the scientific root is the same;
- the outward disposition class remains compatible;
- the primary category remains materially appropriate;
- preserving the ID will not mislabel the current issue.

Examples:
- `CE-02 Major` becomes `CE-02 Moderate` after partial repair -> keep `CE-02`.
- `NI-01` moves from Table 2 to Table 3 after revision but the same wrong aggregate remains -> keep `NI-01`.

Do **not** force ID preservation when the outward class or category changes materially.

Examples:
- `AQ-01` is clarified and now proves a numerical defect -> create the appropriate current finding ID and record `AQ-01` as prior lineage.
- `CG-01` becomes verifiable and reveals a citation-semantic defect -> create the current `CI-xx` finding and retain `CG-01` in lineage.

Never use ID continuity to preserve a stale severity or stale assessment.

## Canonical lineage fields

For current canonical records in revision/rebuttal contexts, use the optional lineage fields defined in `schemas/finding_record.schema.json`:

- `review_context`;
- `revision_status`;
- `prior_record_ids`;
- `lineage_confidence`;
- `resolution_basis`.

For initial review, these may be omitted or use `initial_review` / `new` where structured export consistency is useful.

`resolution_basis` should be a concise manuscript-grounded statement such as:
- "Abstract claim narrowed to evaluated datasets; Table 2 unchanged."
- "Baseline provenance now reports identical split/budget, resolving AQ-01."
- "Arithmetic corrected in table, but conclusion still uses the old percentage."

Do not put private chain-of-thought into lineage metadata.

## Resolution evidence gate

A prior issue may be marked `resolved` only when the current evidence shows the **root defect** is gone. Resolution means the scientific/reporting defect was actually repaired, not merely explained more clearly.

Do not mark resolved merely because:
- the author says "fixed";
- the response letter promises a change;
- one cited location changed while another dependent surface remains stale;
- the wording changed but the scientific scope problem remains;
- the table value changed but the derivation/protocol problem remains;
- the prior issue is no longer easy to locate because text moved.

For each prior material root, inspect the smallest current evidence bundle that can adjudicate the repair.

## Rebuttal evidence rule

Treat an author response letter as:
- a pointer to changed manuscript evidence;
- an explanation of intended interpretation;
- or new evidence only if the response itself contains scientifically sufficient material within the review scope.

Do not treat "we have corrected this" as proof of correction. Verify the referenced current manuscript location when available.

If the rebuttal explanation resolves an ambiguity but the manuscript remains ambiguous to future readers, distinguish:
- `rebuttal_check`: the reviewer may understand the intent;
- publication-readiness: the manuscript may still need the clarification incorporated.

## Dependency propagation

A root issue may have dependent manifestations. When the root changes, propagate status carefully.

### Safe propagation to resolved

A dependent manifestation may inherit `resolved` only if:
- it was entirely caused by the repaired root;
- its current surface has been updated or no longer asserts the defective content;
- it has no independent evidence or separate remedy requirement.

Example:
A wrong denominator caused an incorrect table percentage and identical abstract percentage. Both are corrected from the same recalculation -> the dependent abstract symptom can resolve with the root.

### No blind propagation

Do not auto-resolve a downstream item merely because its parent root was fixed.

Example:
The table percentage is corrected, but the conclusion still reports the old improvement. The numerical root may be resolved while the stale conclusion becomes a current cross-surface/text reconciliation issue.

### Re-rooting rule

If a dependent manifestation survives after the original parent root is resolved, ask whether it now has an independent scientific basis.

If yes:
- detach it from the resolved parent;
- create/reclassify the appropriate current root;
- assign current severity based on current consequence;
- preserve lineage to the prior parent when useful.

Do not keep a zombie dependency under a resolved root.

## Partial resolution

Use `partially_resolved` when a revision materially reduces the defect but leaves a scientifically meaningful remainder.

Examples:
- "all datasets" becomes "most datasets," but the actual evidence supports only a narrower named subset;
- protocol reporting improves, but baseline provenance remains unknown;
- notation is fixed in equations but remains inconsistent in the algorithm pseudocode;
- one inference-heavy mechanism statement is qualified in Discussion but remains unqualified in the Abstract.

State what changed and what remains. Recalibrate severity from the remaining current defect; do not inherit prior severity by default.

### Clarification is not partial repair

Use `partially_resolved` only when the defect itself is materially reduced. More information, better provenance disclosure, or a clearer rebuttal does **not** count as partial resolution if the same scientific defect remains.

Examples:
- imported-baseline provenance becomes clearer, but the manuscript still presents the incompatible comparison as direct -> `persistent`, not `partially_resolved`;
- authors explain what they intended by “all baselines,” but the current conclusion still uses the same unsupported universal scope -> `persistent` unless the current scope is actually narrowed;
- ambiguity is removed and the new disclosure proves a real incompatibility -> `reclassified` from query to finding.

Ask:
> “Has the magnitude/scope/consequence of the defect decreased, or do I merely understand the unchanged defect better?”

Only the former supports `partially_resolved`.

## Reclassification

Use `reclassified` when new evidence changes the correct outward treatment while preserving lineage.

Examples:
- prior `author_query` -> current `finding` after authors disclose incompatible evaluation protocols;
- prior `finding` -> current `author_query` because a revision removes the contradiction but leaves ambiguous provenance;
- prior `coverage_gap` -> `resolved` because the previously unavailable supplement/source becomes available and supports the claim, completing the verification;
- prior `coverage_gap` -> current `finding` because the now-available source contradicts the attribution.

The current disposition controls the current report. Prior labels are historical context only.

## No-longer-material state

Use `no_longer_material` when a prior verification problem or concern is **not scientifically resolved**, but the revised manuscript no longer relies on the affected claim/source/object for any material current conclusion.

Typical case:
- a cited source remained inaccessible, so its semantic support was never verified;
- the revision removes the citation-dependent strong claim entirely;
- therefore the old verification gap no longer needs action in the current manuscript.

This is different from:
- `resolved` — the prior defect/gap was actually adjudicated or repaired;
- `not_reassessable` — the issue remains material to the current manuscript but required evidence is still unavailable.

`no_longer_material` normally has no current canonical record and no current severity/disposition. Keep it only in the revision-delta lineage.

## New issues in revised manuscripts

A revision may introduce a new problem. Report it as `new` only after checking that it is not:
- a moved prior issue;
- a dependent manifestation of an existing lineage;
- an artifact of changed numbering/rendering;
- a consequence already covered by a current root finding.

Do not avoid reporting genuinely new Major/Critical issues merely because they were absent from the prior review.

## Delta report discipline

For revision/rebuttal review, report two layers:

1. **Resolution delta** — what happened to prior material issues;
2. **Current unresolved review** — the canonical current findings/queries/gaps that still require action.

Resolved items should usually appear only in the delta summary, not be repeated as current findings.

A revision delta should make it possible to answer:
- Which prior issues are resolved?
- Which remain, and at what current severity/disposition?
- Which were reclassified?
- Which cannot be reassessed?
- Which prior gaps/concerns are no longer material even though they were not substantively adjudicated?
- What genuinely new issues appeared?

Use `templates/revision_report.md` when a revision-focused report is requested.

## Structured delta output

If machine-readable revision output is requested, use `schemas/revision_delta.schema.json` for transition records and `schemas/finding_record.schema.json` for current canonical records.

A delta transition is not a replacement for the current canonical record. It records lineage between prior and current scientific judgments.

## Regression implications

Version-delta regression cases should test transitions, not only current findings.

Useful expectations:
- `prior CE-01 -> resolved`;
- `prior AQ-02 -> current CE-03, reclassified`;
- `prior NI-01 -> partially_resolved, severity Major -> Moderate`;
- no duplicate "new" finding for a moved persistent root;
- no automatic resolution of stale dependent narrative text.

See `checks/regression_testing.md` and `templates/regression_case.yaml`.

## Revision self-check

Before closing a revision/rebuttal review, verify:
- every prior material root in scope has a transition state;
- no issue is called resolved solely from author assertion;
- persistent issues were rechecked against current evidence;
- severity was recalibrated from the current remainder;
- moved text did not generate duplicate new IDs;
- dependent manifestations were not blindly resolved with their parent;
- surviving dependencies were re-rooted when scientifically independent;
- new issues were checked for lineage before being called new;
- current report prose is rendered from current canonical records, not historical wording;
- resolved items do not inflate current issue counts;
- `partially_resolved` reflects an actual reduction in defect magnitude/scope, not merely increased explanation;
- current severity was assigned blind to the prior severity label and then sanity-checked against history;
- prior verification gaps removed from current claim dependencies use `no_longer_material` rather than false `resolved`;
- current prose placement matches canonical salience exactly.
