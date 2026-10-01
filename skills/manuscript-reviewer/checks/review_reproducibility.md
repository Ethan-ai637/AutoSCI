# Review reproducibility and deterministic review protocol

## Objective

Reduce avoidable run-to-run variation in what gets checked, how findings are identified, and how the final report is ordered.

This does **not** require identical wording across runs. It requires stable scientific coverage, stable issue identity, and stable severity/disposition when the inspected evidence is unchanged.

## Review-run record

At the start of the review, record internally:
- manuscript identifier/version/date if available;
- review mode;
- dominant manuscript archetype or `mixed`;
- materials inspected;
- materials unavailable/unreadable;
- citation verification ceiling actually reached;
- whether rendered PDF inspection was available for layout-dependent content;
- whether long-document section checkpoints were required and completed;
- whether central claim fingerprints were built for cross-surface drift checking.

If the manuscript version is unknown, say so rather than inventing one.

## Coverage-before-finding rule

Do not let the first interesting anomaly determine the rest of the review.

Before finalizing findings:
1. inventory central claims and primary result objects;
2. complete the selected-mode coverage map;
3. only then finalize severity, salience, and report ordering.

This reduces salience bias and discovery-order bias.

## Stable anchor rule

Use stable internal anchors based on manuscript location/object identity, not the sequence in which the reviewer happened to notice them.

Examples:
- claim anchor = section/page/sentence + atomic proposition;
- evidence anchor = Table 2 row X / Fig. 3b / Eq. 7 / citation [18];
- result anchor = exact metric/condition/value relationship.

Internal temporary IDs may be assigned during reading, but final finding IDs should be assigned **after root-cause clustering**.

## Stable finding-ID rule

After all reportable root concerns are clustered, assign IDs deterministically:
1. choose the root category (`CE`, `FT`, `NI`, `NT`, `CI`, `OC`, or `XR`);
2. sort within category by earliest root manuscript location, then by centrality/severity if the same location contains multiple roots;
3. assign `01`, `02`, ... in that order.

Author-query IDs use `AQ-01`, `AQ-02`, ... and coverage gaps use `CG-01`, `CG-02`, ... using the same stable-location principle.

Do not number by discovery order.

## Stable severity rule

For borderline findings, evaluate in this order:
1. what scientific object is affected? central claim / core method / headline result / secondary result / local presentation;
2. if unfixed, what materially wrong interpretation or reproduction failure could result?;
3. is that consequence directly established or speculative?;
4. does the defect survive adversarial verification?;
5. would the severity remain the same if the defect appeared once instead of repeatedly?

Use `severity_and_evidence.md`; do not infer severity from emotional wording, number of occurrences, or repair effort.

## Stable report ordering

Do not order by discovery sequence.

Default:
1. Critical/Major root findings by central scientific consequence;
2. central Moderate root findings;
3. material author queries;
4. secondary findings;
5. cleanup;
6. coverage gaps.

For ties, prefer earlier causal/root issues over downstream symptoms, then earlier manuscript location.

## Re-review invariants

If the same manuscript/materials are reviewed again under the same mode, the following should be approximately invariant:
- central atomic claims identified;
- primary result objects selected;
- evidence-state assignments for central claims;
- root-cause grouping;
- finding/query/gap disposition;
- severity of material root findings;
- whether a headline comparison passes the comparability/provenance gate;
- section-coverage states for material manuscript regions;
- semantic relation assigned to repeated central-claim surfaces when drift is material.

Exact prose and Minor cleanup coverage may vary, especially in exhaustive mode.

The executive summary should also preserve these invariants across reruns:
- root-finding counts after deduplication;
- disposition of material uncertainty (`finding` vs `author_query` vs `coverage_gap`);
- severity/confidence of headline root findings;
- bounded wording for clean-coverage statements.

If the body is stable but the summary changes these properties, the synthesis layer is unstable and must be normalized using `evidence_sufficiency_and_synthesis.md`.

## Change-aware rule

If a revised manuscript, rebuttal, prior review, or previous manuscript version is supplied, read `checks/revision_tracking_and_resolution.md`. Do not assume a previous finding still applies, and do not assume an author statement that an issue was fixed is proof of resolution.

For each prior material issue that is in scope:
- match prior/current scientific root identity before using location or wording;
- re-check the current manuscript evidence;
- classify the transition as `resolved`, `partially_resolved`, `persistent`, `reclassified`, `not_reassessable`, or `no_longer_material`;
- recalibrate severity from the **current remainder** rather than preserving old severity for continuity; perform this assignment before looking back at the prior severity label;
- propagate resolution to dependencies only when the dependency was entirely caused by the repaired root and does not survive independently;
- distinguish actual repair from mere clarification: more provenance/detail with an unchanged defect is `persistent`, not automatically `partially_resolved`;
- if an old verification gap becomes irrelevant because the current manuscript removes the dependent claim, use `no_longer_material` rather than pretending verification succeeded.

Current open records may preserve prior IDs only under the continuity rules in `revision_tracking_and_resolution.md`. Otherwise record explicit lineage.

Only use this mode when prior review/version evidence is actually available.

## Reproducibility self-check

Before final output ask:
- Would another reviewer using this skill know which central claims/results must be checked?
- Are finding IDs independent of discovery order?
- Are the evidence anchors precise enough to reconstruct each Major/Critical finding?
- Did any severity depend mainly on rhetorical intensity rather than consequence?
- Did any item enter the main comments because it was noticed early rather than because it is scientifically central?
- Would another reviewer know which sections/dependencies must be revisited before declaring evidence absent?
- Would another reviewer reconstruct the same material claim fingerprint even if the wording differs?

If yes, normalize before finalizing.


## Canonical-record reproducibility

Use `checks/canonical_finding_record.md` as the stable comparison layer across reruns. Compare scientific fields before prose:
- disposition;
- primary root category;
- claim/object identity;
- evidence state;
- severity band;
- protocol/provenance status;
- remediation class;
- dependency clustering;
- meaning of `summary_safe_statement`.

Wording may vary without constituting a regression. A change in these scientific fields requires either new evidence, a corrected prior error, or an intentional rule change.

When developing the skill, use `checks/regression_testing.md` and `templates/regression_case.yaml` to capture intentional expectations.


## Rendering reproducibility invariant

Across reruns under the same canonical records, report placement must be stable:
- `main_comment` records stay in main comments;
- `secondary_finding` records stay in secondary findings;
- queries/gaps stay in their dedicated layers.

If wording varies but these placements change without a canonical-record change, treat it as a synthesis/rendering regression.
