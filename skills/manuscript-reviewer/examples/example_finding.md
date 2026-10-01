# Example findings

Illustrative format only; these are not real paper reviews.

## Cross-surface comparative overclaim

```text
[XR-01] Major | High confidence
Location: Abstract, sentence 5; Sec. 4.2, para. 1; Table 3; Conclusion, para. 1
Claim/object: “Our method consistently outperforms all baselines across datasets.”
Evidence state: contradicted
Root cause: universal comparative wording conflicts with one directly comparable evaluation condition
Observed evidence: Table 3 shows the method is best on Datasets A and C, but Baseline-X is higher on Dataset B under the same reported metric and protocol.
Trace path: Abstract/conclusion universal claim → Table 3 per-dataset comparison → Dataset B exception.
Issue: The universal wording “consistently ... across datasets” conflicts with one directly comparable reported condition and is repeated across multiple narrative surfaces.
Why it matters: The statement overstates the central comparative result in the abstract and conclusion-level narrative.
Remediation class: scope_qualification
Recommended fix: Replace the universal wording with a result-faithful summary, e.g. best on two of three datasets and competitive on Dataset B, unless additional directly comparable evidence resolves the exception.
```

## Numerical integrity — percentage points vs relative improvement

```text
[NI-01] Moderate | High confidence
Location: Sec. 4.1, para. 2; Table 2
Claim/object: “Accuracy improves by 10% over Baseline-A.”
Evidence state: contradicted
Root cause: percentage-point difference is described as relative percentage improvement
Observed evidence: Table 2 reports 80% for Baseline-A and 90% for the proposed method. The absolute difference is 10 percentage points; the relative accuracy increase is (90-80)/80 = 12.5%.
Trace path: Sec. 4.1 quantitative claim → Table 2 source values → relative-change formula.
Issue: The phrase “improves by 10%” is numerically ambiguous and does not match the relative percentage change.
Why it matters: The wording changes the quantitative magnitude readers infer from the result.
Remediation class: text_reconciliation
Recommended fix: State “improves by 10 percentage points” or “a 12.5% relative increase in accuracy,” depending on the intended quantity.
```

## Coverage gap — citation semantics blocked by unavailable source

```text
[CG-01] Coverage gap
Location: Sec. 2.1, para. 3
Claim/object: Prior work [17] “demonstrates that the method remains robust under severe domain shift.”
Evidence state: unavailable_to_verify
Observed context: The manuscript cites [17], but only the reference metadata is available; the cited source text was not inspected.
Verification blocked: Semantic support for the robustness/domain-shift attribution cannot be checked from the available materials.
Required material: Relevant full text or source section for [17].
Handling: Do not label the citation unsupported unless the source is inspected and fails to support the claim.
```

## Author query — protocol ambiguity rather than asserted error

```text
[AQ-01] Material clarification
Location: Sec. 4.1, evaluation protocol; Table 2
Question: Were Baseline-A and the proposed method evaluated on the identical test split and with the same evaluation budget?
Observed context: Table 2 presents the values side-by-side, but the method section explicitly states the proposed-method split while the baseline provenance is not specified.
Provenance state: proposed-method result = current-author result; Baseline-A = rerun/imported status unknown.
Why clarification matters: A direct superiority claim depends on protocol comparability, but the available text permits both a same-protocol and imported-baseline interpretation.
What would resolve it: State the split, evaluation budget, and whether baseline values were rerun or imported. If imported under a different protocol, qualify the comparative wording.
```


## Mechanistic inference bridge

```text
[CE-01] Major | High confidence
Location: Sec. 4.3, ablation paragraph; Discussion, para. 2
Claim/object: “Module X improves robustness by suppressing spurious features.”
Evidence state: partial_support
Root cause: ablation supports component contribution but not the stated mechanism
Observed evidence: Removing Module X lowers OOD accuracy, establishing that the component contributes to the reported performance. The manuscript does not present feature-level diagnostics, controlled interventions, or another analysis that tests whether spurious-feature suppression is the operative mechanism.
Trace path: Ablation result → component contributes to OOD performance → mechanistic bridge (“suppresses spurious features”) → robustness explanation.
Issue: The first bridge is supported, but the mechanism-specific bridge is not tested by the presented evidence.
Why it matters: Readers may interpret the discussion as an established explanation rather than a hypothesis consistent with the ablation.
Remediation class: scope_qualification
Recommended fix: Recast the mechanism statement as a hypothesis/interpretation unless mechanism-specific evidence is added.
```


## Canonical-record projection (illustrative)

The public findings above should be rendered from one internal canonical record rather than independently rewritten. A machine-readable export for the first example could preserve the same scientific judgment with fields such as:

```json
{
  "record_id": "XR-01",
  "disposition": "finding",
  "primary_category": "XR",
  "severity": "Major",
  "confidence": "High",
  "salience": "main_comment",
  "locations": [
    {"surface": "Abstract", "locator": "sentence 5"},
    {"surface": "Table 3", "locator": "Dataset B row/condition"},
    {"surface": "Conclusion", "locator": "paragraph 1"}
  ],
  "claim_or_object": "Universal superiority across datasets",
  "evidence_state": "contradicted",
  "evidence_packet": {
    "anchors": ["Abstract sentence 5", "Table 3 Dataset B", "Conclusion paragraph 1"],
    "protocol_comparability": "established",
    "provenance_status": "established",
    "inference_bridge": "comparative",
    "source_values": [],
    "derivation": null,
    "external_source_inspected": null,
    "absence_check_complete": null,
    "rendered_page_checked": null,
    "surface_relation": "One directly comparable condition is an exception to the universal wording"
  },
  "observed_evidence": "The method is best on Datasets A and C, while Baseline-X is higher on Dataset B under the same reported metric/protocol.",
  "assessment": "The universal wording conflicts with one directly comparable reported condition.",
  "scientific_impact": "The abstract/conclusion overstate the central comparative result.",
  "remediation_class": "scope_qualification",
  "recommended_fix": "Narrow the universal wording to match the per-dataset result unless additional directly comparable evidence resolves the exception.",
  "dependencies": ["Repeated conclusion wording"],
  "summary_safe_statement": "The universal superiority claim conflicts with one directly comparable condition and should be narrowed.",
  "evidence_boundary": null
}
```

This example is illustrative; structured exports should conform to `schemas/finding_record.schema.json`.
