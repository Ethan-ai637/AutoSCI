> **Revision/rebuttal note:** If prior findings, a prior manuscript version, or an author response letter are being assessed, use `templates/revision_report.md` as the report spine and use this template for the current unresolved-review sections.

# Manuscript consistency review template

Use this template for the default **standard** reviewer-style output. The audit categories are used internally for coverage; the main report is organized by scientific root issue.

## 1. Scope, evidence boundary, and manuscript type

- Manuscript identifier/version/date (if available):
- Review mode: compact / standard / exhaustive
- Manuscript archetype: method_model_system / empirical_study / dataset_benchmark_resource / theory_mathematical / survey_review / application_translational / mixed
- Materials inspected:
- Materials unavailable/unreadable:
- PDF/rendered-page inspection available: yes / no / partial
- Citation verification reached: Level 1 / Level 2 / selective Level 3 / broad Level 3
- Central atomic claims identified:
- Central atomic claims fully checked:
- Primary result objects identified:
- Primary result objects cross-surface checked:
- Material section/dependency coverage checkpoints: complete / partial / blocked
- Central repeated claims surface-drift checked: yes / partial / not material

### Central claim coverage

| State | Count | Notes |
|---|---:|---|
| verified support |  |  |
| partial support |  |  |
| contradicted |  |  |
| missing required evidence |  |  |
| ambiguous mapping |  |  |
| unavailable to verify |  |  |

Do not convert these counts into a paper score.

## 2. Executive summary

Summarize only material review outcomes:
- count of Critical / Major / Moderate / Minor **root findings**;
- the 2–4 highest-salience scientific problems, if present;
- material author queries that block interpretation, if any;
- major verification limitations / coverage gaps;
- audit domains with no material inconsistency.

Do not give an acceptance score, paper ranking, or generic praise.

**Synthesis rule:** every material sentence in this section must inherit from a finalized canonical root-finding, author-query, or coverage-gap record, or from a bounded audit-coverage statement. Prefer the record's `summary_safe_statement` or a weaker equivalent. Preserve uncertainty and scope. Do not introduce new scientific conclusions here.

## 3. Main comments

Use this section for independent high-salience root findings and material author queries. Do not create one subsection per audit category.

### [ID] Severity | Confidence
**Location:**  
**Claim/object:**  
**Evidence state:**  
**Root cause:**  
**Observed evidence:**  
**Provenance/version:** *(include when material to comparison/adjudication)*  
**Trace path:**  
**Issue:**  
**Why it matters:**  
**Remediation class:**  
**Recommended fix:**  

Repeat only for independent main comments. **Placement invariant:** only canonical records with `salience=main_comment` render here. If an item belongs elsewhere, update the canonical record before rendering; do not override salience in prose.

For a material author query, omit severity and use:

### [AQ-ID] Author query | Material
**Location:**  
**Question:**  
**Why clarification matters:**  
**What inspected evidence shows:**  
**What would resolve it:**  

## 4. Secondary findings and cleanup

Use a compact table for verified issues that matter but should not compete with the main scientific comments.

| ID | Severity | Location | Root issue / pattern | Evidence | Minimal fix |
|---|---|---|---|---|---|

For repeated low-risk notation, cross-reference, labeling, or citation-placement problems, prefer one pattern-level item with representative locations over one row per occurrence.

Only canonical records with `salience=secondary_finding` or `cleanup` render here. If none, state that no additional material secondary findings were identified within the inspected scope.

## 5. Additional author queries

List unresolved material ambiguities that survived checking but are not sufficiently established to report as errors.

| ID | Priority | Location | Question | Why clarification matters | What would resolve it |
|---|---|---|---|---|---|

Do not assign scientific severity merely to make a query look consequential.

## 6. Prioritized correction checklist

Reference IDs rather than repeating the full finding narrative.

**Must fix before submission**
- `[ID]` — concise remediation action.

**Should fix**
- `[ID]` — concise remediation action.

**Polish / low-risk consistency**
- `[ID]` — concise remediation action.

Do not repeat the same root issue in multiple checklist groups. Render each action from the canonical record's remediation fields. Do not escalate a minimal remedy during checklist compression; for example, a `scope_qualification` finding must not become an unconditional request for new experiments.

## 7. Unverified items and coverage gaps

List only checks blocked by missing source material, unreadable figures, unavailable supplements, inaccessible cited papers, or intentionally reduced review scope.

Coverage gaps are not severity-bearing findings.

| ID | Object/check | Why verification is blocked | What would resolve it |
|---|---|---|---|

Useful wording:
- `Unable to verify because ...`
- `Not checked in compact mode: ...`
- `Citation semantic support remains unverified; only metadata was checked.`
- `Aggregate could not be reconstructed because the weighting/denominator is not reported.`

## 8. Audit coverage summary

This section proves coverage without duplicating substantive findings.

| Audit | Status | Material issue IDs / note |
|---|---|---|
| Claim–evidence | checked / partial / blocked |  |
| Figure/table/text consistency | checked / partial / blocked |  |
| Numerical integrity | checked / partial / blocked |  |
| Notation | checked / partial / blocked |  |
| Citation | checked / partial / blocked |  |
| Overclaim / scope | checked / partial / blocked |  |
| Inference-chain traceability | checked / not material / blocked |  |
| Evidence provenance/adjudication | checked / not material / blocked |  |
| Review reproducibility normalization | checked | stable IDs/order after clustering |
| Evidence sufficiency gate | checked / partial / blocked | type-specific thresholds applied |
| Synthesis fidelity gate | checked | summary/checklist inherit final dispositions |
| Long-document coverage checkpoints | checked / partial / not material / blocked | material sections/dependencies covered |
| Claim-surface drift | checked / partial / not material / blocked | central claim fingerprints reconciled |
| Canonical record integrity | checked / partial / blocked | all outward items rendered from one record each |

Optionally state categories with no material issue. Do not invent findings to populate the table.

---

# Exhaustive appendix option

Only in exhaustive mode or when explicitly requested, append detailed category tables after the reviewer-style report.

## A. Claim–evidence detail

| ID | Severity | Location | Atomic claim | Evidence | State | Assessment | Remediation | Fix |
|---|---|---|---|---|---|---|---|---|

## B. Figure/table/text consistency detail

| ID | Severity | Objects compared | Protocol compatible? | Mismatch | Evidence | Remediation | Fix |
|---|---|---|---|---|---|---|---|

## C. Numerical integrity detail

| ID | Severity | Location | Stated quantity | Reconstructed quantity | Basis/formula | Assessment | Remediation | Fix |
|---|---|---|---|---|---|---|---|---|

Include only arithmetic reconstructable from explicit, protocol-compatible source values.

## D. Notation detail

| ID | Severity | Symbol/object | Locations | Problem | Reproducibility impact | Remediation | Fix |
|---|---|---|---|---|---|---|---|

## E. Citation detail

State verification level for every semantic-support judgment.

| ID | Severity | Location | Atomic claim | Citation(s) | Level checked | Support classification | Finding | Remediation | Fix |
|---|---|---|---|---|---|---|---|---|---|

## F. Overclaim detail

| ID | Severity | Location | Evidence scope | Claim scope | Scope jump | Remediation | Minimal fix |
|---|---|---|---|---|---|---|---|

## G. Inference-chain notes for central claims

| Claim/location | Observed result | Bridge type | Bridge status | Material assumption/scope jump | Action |
|---|---|---|---|---|---|

Do not expose private chain-of-thought. Record only manuscript-grounded scientific links necessary to explain the audit.

## H. Evidence provenance / adjudication detail (optional)

Use only when provenance materially affects comparability, version reconciliation, or source adjudication.

| Object/claim | Producer/origin | Version | Protocol | Transformation | Adjudication consequence |
|---|---|---|---|---|---|

Do not include provenance metadata that has no bearing on a scientific judgment.
