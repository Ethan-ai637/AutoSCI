# False-positive traps

These examples teach what **not** to report as an established error.

## Trap 1 — Different protocols, different numbers

Text reports 84.1 on the test set. A table reports 83.6 on the validation set.

Wrong conclusion: "The text contradicts the table."

Correct handling: first recognize that the protocols differ. Only flag if the manuscript presents the values as the same result or obscures the split distinction.

## Trap 2 — External citation not available

The manuscript says prior work [12] showed cross-domain robustness, but the source cannot be accessed.

Wrong conclusion: "Citation [12] does not support the claim."

Correct handling: semantic support is `unavailable_to_verify` and should be listed as a **coverage gap**, not as a citation error. A manuscript-internal placement or metadata defect may still be reported if independently visible.

## Trap 3 — Rounded value

Table: 91.24. Text: 91.2.

Wrong conclusion: numerical inconsistency.

Correct handling: consistent under ordinary rounding.

## Trap 4 — Error bars overlap

Two plotted means have overlapping error bars.

Wrong conclusion: "There is no significant difference."

Correct handling: overlapping bars alone do not establish non-significance unless the paper's statistical definition supports that inference.

## Trap 5 — Valid local notation reuse

`i` indexes samples in Sec. 3 and independently indexes iterations in a self-contained algorithm in Sec. 5.

Wrong conclusion: notation collision.

Correct handling: do not flag if local scope is clear and readers cannot reasonably confuse the roles.

## Trap 6 — Evidence supports one clause only

"The method is more accurate, robust, and faster." The table directly supports accuracy only.

Wrong conclusion: mark the whole sentence `verified_support` because one clause is supported.

Correct handling: split into atomic propositions and assess each separately.

## Trap 7 — Plot value guessed from geometry

A curve appears visually near 0.83.

Wrong conclusion: "The paper reports 0.84 in text but the figure shows 0.83."

Correct handling: unless the point is labeled or reliably readable, restrict the check to qualitative direction/order.

## Trap 8 — No issue does not mean incomplete review

After checking a notation-heavy section, no consequential inconsistency is found.

Wrong behavior: invent Minor notation complaints to populate the section.

Correct handling: state that no material notation inconsistency was identified within the inspected scope.


## Trap 9 — Ambiguity promoted into an error

The table shows baseline and proposed-method results side by side, but the manuscript does not say whether the baseline was rerun or imported.

Wrong conclusion: "The comparison uses incompatible protocols."

Correct handling: if both same-protocol and imported-baseline interpretations remain plausible after checking, ask an `author_query` about provenance/protocol. Do not assert incompatibility without evidence.

## Trap 10 — Unnecessary new experiment request

The manuscript says "outperforms all baselines," while one directly comparable condition is an exception.

Wrong fix: "Run more experiments to prove universal superiority."

Correct handling: the minimal sufficient remedy is usually to reconcile/narrow the wording. New experiments are needed only if the authors insist on retaining the broader claim.


## Trap 11 — Treating the table as automatic ground truth

The abstract reports 91.2 while Table 2 reports 90.8 under what appears to be the same protocol. No raw result, derivation, or revision history establishes which value is intended.

Wrong conclusion: “The abstract value is wrong; replace it with 90.8.”

Correct handling: report a cross-surface internal inconsistency and ask the authors to reconcile the intended value across all surfaces. Do not assign truth to the table by format alone.

## Trap 12 — Real evidence, unsupported bridge

An ablation shows that removing component X reduces performance.

Wrong conclusion: “This proves X works by filtering noisy features,” merely because the discussion offers that explanation.

Correct handling: the ablation supports contribution, not necessarily mechanism. Trace the inference bridge and qualify the mechanistic claim unless mechanism-specific evidence exists.

## Trap 13 — Non-significance converted to equivalence

A comparison yields p > 0.05.

Wrong conclusion: “The two methods perform equivalently.”

Correct handling: failure to reject a difference is not, by itself, an equivalence result. Check confidence intervals, power, and any pre-specified equivalence/non-inferiority margin before accepting the stronger conclusion.

## Trap 14 — Importing the wrong manuscript-type expectation

A survey paper claims to organize and synthesize a defined literature set.

Wrong conclusion: "The paper lacks ablation experiments and model baselines."

Correct handling: route the paper as `survey_review`. Audit scope/completeness claims, taxonomy consistency, citation support, and synthesis evidence. Do not demand method-paper artifacts unless the survey itself makes a claim that requires them.

## Trap 15 — Category-driven duplicate findings

The abstract says "generalizes across all domains," while the experiments cover only three domains. The same scope jump can be described as both claim–evidence mismatch and overclaim.

Wrong behavior: report one `CE` Major and one `OC` Major for the same root defect.

Correct handling: choose one primary root finding, preserve the cross-category reasoning internally, and report the dependent wording locations together.

## Trap 16 — Hard-cap suppression

A standard-mode review contains seven genuinely independent Major defects after root clustering.

Wrong behavior: suppress the seventh issue because the report should contain "no more than six main comments."

Correct handling: use the density threshold only as a diagnostic for over-splitting and duplication. If the issues remain independent and material, keep all of them.


## Trap 17 — Imported baseline treated as a rerun baseline

A proposed method is evaluated by the current authors. A baseline number is copied from a prior paper and placed in the same table, but the exact evaluation protocol is not established as identical.

Wrong conclusion: “The proposed method directly outperforms the baseline under the same protocol.”

Correct handling: record baseline provenance first. If compatibility is established, the comparison may be valid; if material details remain unclear, use an author query. Do not infer same-protocol rerunning from table layout.

## Trap 18 — Version drift turned into a false adjudication

The manuscript body reports one value while a supplement or older preprint reports another, and the inspected materials do not establish whether they belong to the same revision/checkpoint.

Wrong conclusion: “The newer-looking table is correct and the other value is wrong.”

Correct handling: check version provenance. If revision alignment cannot be established, report version-linked internal inconsistency or ask the authors to reconcile it; do not choose a truth source by appearance.

## Trap 19 — Discovery order becomes report priority

A reviewer notices a Minor notation issue before later finding a central Major claim–evidence defect.

Wrong behavior: assign `NT-01` first, structure the review around it, or let early discovery influence salience/severity.

Correct handling: complete coverage and root clustering first. Assign final IDs and ordering only afterward according to root category, scientific consequence, and stable manuscript location.

## Trap 20 — “Not found” treated as “not present”

A reviewer searches for the phrase “robustness experiment,” finds no exact match, and concludes that the manuscript provides no robustness evidence.

Wrong conclusion: `missing_required_evidence` based on the failed phrase search.

Correct handling: perform a claim-directed absence check across methods, results, relevant tables/figures, and available supplement. Evidence may use different terminology or appear only in a result object. Only then can absence from the available manuscript support `missing_required_evidence`.

## Trap 21 — Executive summary upgrades uncertainty

A root item is an `author_query`: baseline provenance is unclear, so same-protocol comparability is unresolved.

Wrong summary: “The paper compares against baselines using incompatible protocols.”

Correct handling: preserve the disposition: “Baseline provenance/protocol comparability requires clarification before the headline comparison can be fully verified.”

## Trap 22 — Several Moderate issues become a synthetic Major

Three independent Moderate reporting issues are verified. None establishes that the overall evaluation is invalid.

Wrong behavior: summarize them as “Major: the experimental evaluation is unreliable.”

Correct handling: report the three root issues at their calibrated severity unless the stronger umbrella claim is independently evidence-checked and established.

## Trap 23 — Harmless paraphrase treated as claim drift

Results: “The method improves AUROC on the three evaluated datasets.” Conclusion: “Across the evaluated datasets, the method yields higher AUROC.”

Wrong behavior: report a cross-section inconsistency because the wording is not identical.

Correct handling: compare semantic fingerprints. The subject, metric, scope, comparator burden, and quantifier are materially equivalent, so this is normal paraphrase rather than drift.

## Trap 24 — Long-manuscript locality bias

The abstract and main results appear to lack a robustness test, but Section 7 points to Appendix D, where the perturbation evaluation is reported and qualified.

Wrong conclusion: `missing_required_evidence` after reading only the abstract, main method, and primary table.

Correct handling: follow the material appendix dependency under the section-coverage checkpoints. If Appendix D is available, inspect it before disposition. If it is unavailable, use a coverage gap; do not infer absence from the partial read.


## Trap 25 — Summary bypasses the canonical finding record

A final root record is `AQ-02`: baseline provenance is unclear, so same-protocol comparability is unresolved.

Wrong behavior: the executive summary independently rereads the table and states, “The baseline comparison is invalid because protocols differ.”

Correct handling: render the summary from the canonical query record: comparability requires clarification. If later evidence establishes incompatibility, update the canonical record first; do not let the summary become a second adjudication layer.

## Trap 26 — Regression test overfits exact prose

Two reruns identify the same root numerical error, same severity, same evidence state, and same remediation, but phrase the explanation differently.

Wrong behavior: mark the second run as a regression because the wording is not identical, then hardcode the first sentence into the skill.

Correct handling: regression tests should compare scientific identity and forbidden behaviors, not exact prose. Only material changes in disposition, severity, root identity, evidence/provenance decision, dependency structure, or synthesis meaning should fail the test.

## Trap 27 — Author says “fixed,” reviewer marks resolved

A rebuttal says “We corrected the robustness claim in the revision,” but the conclusion still contains the original universal wording.

Wrong behavior: mark the prior issue `resolved` from the response letter alone.

Correct handling: inspect the current manuscript surfaces. If the root survives in the conclusion, classify it as persistent or partially resolved depending on the remaining scope and impact.

## Trap 28 — Parent repair blindly resolves a surviving dependency

A wrong table percentage is corrected, but the abstract still reports the old derived improvement.

Wrong behavior: resolve the entire prior issue graph because the numerical root in the table was fixed.

Correct handling: verify every material dependent surface. If the stale abstract statement survives independently, detach/re-root it as a current text/consistency issue rather than hiding it under a resolved parent.

## Trap 29 — Moved persistent issue emitted as new

A revision moves the same unsupported generalization claim from Section 5 to Section 6 and rewrites it stylistically without narrowing the scope.

Wrong behavior: mark the old issue resolved and create a brand-new issue because the page/section changed.

Correct handling: match scientific root identity before location. Preserve lineage and, when category/disposition continuity permits, preserve the prior public ID.

## Trap 30 — Old severity survives after meaningful repair

A prior Major overclaim is narrowed substantially, but one local Moderate mismatch remains.

Wrong behavior: keep `Major` solely because the prior review used Major.

Correct handling: classify the transition as `partially_resolved` and recalibrate severity from the current remaining defect.


## Trap 31 — Verified support/reporting defect demoted to author query

The manuscript explicitly states that all discussed gains satisfy a named significance threshold, but after checking the methods, results, tables, and available supplement, no test statistic, p-value, paired unit, or test output is reported.

Wrong behavior: use only an author query because the authors might later provide the missing statistics.

Correct handling: the underlying significance truth remains unknown, but the **current manuscript's substantiation/reporting defect is verified**. Report a calibrated finding such as “the significance assertion is not substantiated by reported test output.” Do not claim the gains are non-significant.

## Trap 32 — More explanation mistaken for partial resolution

A prior concern is that an imported baseline is presented too broadly as directly comparable. The revision explains provenance more clearly but still uses the incompatible/imported comparison in the same material claim.

Wrong behavior: `partially_resolved` because the reviewer now understands the provenance better.

Correct handling: `persistent` if the scientific/reporting defect itself was not reduced. Information gain for the reviewer is not repair progress for the manuscript.

## Trap 33 — Historical Major severity persists after a real partial repair

A prior Major universal claim appears in the abstract, results, and conclusion. The revision correctly narrows the abstract and results, leaving only one stale conclusion statement while the current evidence and main analysis are now correctly scoped.

Wrong behavior: keep Major automatically because the lineage was previously Major.

Correct handling: temporarily ignore the historical label and severity-calibrate the current remainder. A stale conclusion may now be Moderate if a competent reader can recover the correct result from the revised evidence/analysis, though Major remains possible when the surviving conclusion still materially dominates the paper's message.

## Trap 34 — Unverifiable source called resolved after claim removal

A citation's full text is unavailable, so its semantic support could not be checked. In the revision, the strong citation-dependent claim is removed and the source is no longer used materially.

Wrong behavior: mark the prior coverage gap `resolved` as though semantic verification succeeded.

Correct handling: use `no_longer_material`. The verification was never completed; it simply no longer bears on a current material claim.

## Trap 35 — Canonical salience disagrees with prose placement

A canonical record has `salience: main_comment`, but the final report places it under “Secondary findings” while the JSON remains unchanged.

Wrong behavior: accept the prose/JSON mismatch as harmless formatting.

Correct handling: canonical salience controls report placement. Either render it as a main comment or update/revalidate the canonical record before rendering. Report writing is not a second salience adjudication step.
