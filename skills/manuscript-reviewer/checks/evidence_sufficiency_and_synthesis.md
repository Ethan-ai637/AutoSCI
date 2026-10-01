# Evidence sufficiency and synthesis fidelity

## Objective

Prevent two high-impact reviewer failures:

1. promoting a plausible concern into a finding before the relevant evidence burden has been met;
2. writing an executive summary or correction checklist that is stronger, broader, or more certain than the verified root findings.

This is a **gate**, not a scoring system. Do not compute a numeric evidence score.

# Part I — Type-specific evidence sufficiency

A candidate may become a severity-bearing `finding` only when its evidence packet is sufficient for the type of defect asserted. If the packet is insufficient, choose `author_query`, `coverage_gap`, or `resolved_no_issue` as appropriate.

## A. Direct contradiction / cross-surface inconsistency

Minimum packet:
- both conflicting statements/objects are actually inspected;
- they refer to the same scientific identity or the review explicitly explains why the manuscript presents them as the same identity;
- protocol/version/provenance differences have been checked when they could explain the mismatch;
- rounding/formatting/extraction artifacts have been excluded where relevant.

If the conflict is real but the correct value/version cannot be adjudicated, report **internal inconsistency**, not “surface X is wrong.”

## B. `missing_required_evidence` / unsupported manuscript-internal claim

Absence is harder to establish than presence. Before assigning this state, perform an **absence check** across the plausible locations available in the manuscript package. Depending on the claim, this can include:
- the claim's local section;
- methods/experimental setup;
- results and primary tables/figures;
- appendix/supplement when available;
- limitations/discussion when the claim may be explicitly qualified there.

Do not require irrelevant sections. The search should be claim-directed, not exhaustive for its own sake.

A failed keyword search alone is insufficient because evidence may be phrased differently, encoded in a table, or presented graphically.

Use:
- `missing_required_evidence` only when the available manuscript itself lacks evidence that tests or substantiates a material claim after the claim-directed absence check;
- `ambiguous_mapping` / `author_query` when evidence may exist in the available package but the mapping/interpretation is genuinely unresolved;
- `unavailable_to_verify` / `coverage_gap` when the relevant supplement/source is missing.

### Reporting-support defect rule

When the manuscript makes an **explicit support-bearing assertion** (for example a significance threshold, equivalence claim, same-protocol assertion, or mathematical/scaling equivalence), a completed absence check can establish a finding about the **current manuscript's substantiation/reporting**, even if the underlying scientific proposition might later prove true.

The finding must be scoped to what is established:
- “significance claim is unsubstantiated by the reported test output,” not “the result is non-significant”;
- “interchangeability is not justified under any stated relation,” not “the two complexities can never be equivalent.”

Do not demote such a verified manuscript-support defect to `author_query` solely because the authors could provide missing details in a response. Use an author query only when the existence of the defect itself still depends on an unknown mapping, protocol fact, or interpretation.

## C. Numerical/arithmetic defect

Minimum packet:
- explicit source values;
- correct metric direction and compatible protocol;
- known denominator/aggregation when material;
- the formula/definition implied by the wording;
- a reconstructable derivation;
- rounding/units/percentage-point alternatives tested.

If the aggregate cannot be reconstructed, do not call it numerically false. Ask for the missing aggregation/denominator or record a coverage gap.

## D. Figure/table/text mismatch

Minimum packet:
- exact objects compared;
- identity/split/metric/model/aggregation checked;
- labels/caption/footnotes inspected;
- exact plot values used only when explicitly readable; otherwise restrict to order/trend.

## E. Citation semantic-support defect

Minimum packet:
- atomic manuscript claim;
- exact citation mapping;
- cited source itself inspected at the relevant passage/analysis;
- enough source context to judge support without relying on abstract/snippet only;
- distinction between “source does not support this claim” and “source support remains unverified.”

If the source cannot be inspected, use a coverage gap, not a semantic citation finding.

## F. Notation/method ambiguity

Minimum packet:
- relevant definitions and later uses inspected;
- local scope considered;
- rendered PDF checked when typography/superscript/subscript/sign changes meaning;
- at least two scientifically plausible interpretations identified for a material ambiguity, or a direct inconsistency established.

If context reliably disambiguates, suppress the concern.

## G. Overclaim / inference-bridge defect

Minimum packet:
- atomic conclusion claim with scope qualifiers;
- actual tested/observed scope;
- material bridge from observation to conclusion;
- check for nearby qualification, limitations, or additional evidence;
- explicit statement of the unsupported scope jump or bridge.

Do not say “insufficient evidence” generically. State what the evidence establishes and what additional inference the prose adds.

# Evidence threshold by disposition

Use the following logic after the type-specific check:

- **Sufficient and material** → `finding`.
- **Substantial evidence, but multiple plausible interpretations survive** → `author_query`.
- **Required verification artifact unavailable/unreadable** → `coverage_gap`.
- **Concern resolved, immaterial, stylistic-only, or too weak after checking** → `resolved_no_issue`.

For Major/Critical findings, the evidence packet must be complete enough that another reviewer could reconstruct the defect from the cited locations without relying on the original reviewer's intuition.

# Part II — Synthesis fidelity

The executive summary, correction checklist, and closing statements are **views over final dispositions**, not a second round of scientific inference.

## Inheritance rule

Every material summary statement must trace to an already-finalized item or verified coverage statement. During synthesis, preserve:
- disposition (`finding` vs `author_query` vs `coverage_gap`);
- severity;
- confidence;
- evidence state;
- scientific scope;
- provenance/comparability caveats;
- remediation burden.

Compression is allowed. Upgrading is not.

Examples:
- `Major | Medium confidence` may be summarized as a material concern **with the uncertainty retained**, not as an established fact.
- `author_query` must remain a clarification need, not “the protocol is incompatible.”
- `coverage_gap` must remain “not verified,” not “unsupported.”
- `partial_support` must not become “contradicted” in the summary.

## No synthesis-only findings

Do not invent a new umbrella defect merely because several findings sound related. A combined meta-finding is allowed only if it has itself passed evidence checking, adversarial checking, disposition, and root clustering.

Wrong:
> Three Moderate reporting issues show that the entire experimental evaluation is unreliable.

Correct:
> The review identified three Moderate reporting issues affecting X, Y, and Z.

Unless the stronger “evaluation is unreliable” proposition was independently established.

## Count integrity

All counts in the executive summary must be computed **after**:
- disposition;
- duplicate suppression;
- root-cause clustering;
- severity normalization.

Do not count dependent manifestations as independent findings. Do not count author queries or coverage gaps as severity-bearing defects.

## Negative-summary discipline

Use bounded language for clean audit results:

Prefer:
> No material notation inconsistency was identified within the inspected core equations.

Avoid:
> The notation is fully correct.

Prefer:
> No semantic citation mismatch was identified among the sources inspected at Level 3.

Avoid:
> All citations are correct.

A clean audit statement is limited by the actual evidence boundary and review mode.

## Remedy inheritance

The prioritized correction checklist may shorten a remedy but must not escalate it.

If the root finding says `scope_qualification`, the checklist must not silently become “run additional experiments.” If additional experiments are one optional way to retain a broader claim, preserve that conditional structure.

# Canonical rendering invariance

After canonical records are finalized, report rendering is deterministic with respect to judgment-bearing fields.

The prose renderer must inherit, without independent reinterpretation:
- `record_id`;
- `disposition`;
- `severity`;
- `confidence`;
- `salience`;
- `summary_safe_statement` ceiling;
- `remediation_class`.

In particular:
- `salience=main_comment` must render in the main-comment layer;
- `salience=secondary_finding` must not be placed under main comments unless the canonical record is first changed;
- queries and coverage gaps must not be counted as severity-bearing findings;
- executive-summary counts must be computed from canonical records, not prose headings.

If the desired prose organization suggests a different salience/severity/disposition, update the canonical record, rerun the relevant validation, then render again. Do not silently override the record during writing.

# Final synthesis check

Before release, ask:
1. Can every material summary sentence be pointed back to a final root item or verified coverage statement?
2. Did any uncertainty disappear during compression?
3. Did any query/gap become a defect?
4. Did any `partial_support` become `contradicted`?
5. Did any remedy become more burdensome?
6. Are finding counts deduplicated and root-based?
7. Are “no issue” statements bounded by inspected scope?

If any answer is yes to 2–5 or no to 1/6/7, rewrite the synthesis.
