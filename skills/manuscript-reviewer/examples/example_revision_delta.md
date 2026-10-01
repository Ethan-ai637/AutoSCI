# Example revision delta

Illustrative only; this is not a real manuscript review.

## Case 1 — Fully resolved prior finding

Prior finding `CE-01` said the abstract/conclusion claimed superiority on all datasets while Table 2 contained a directly comparable exception.

In the revision, all material narrative surfaces now say the method is best on two of three evaluated datasets and competitive on the third. The table and protocol are unchanged.

Correct transition:
- prior root: `CE-01`;
- status: `resolved`;
- current open record: none;
- basis: the root scope mismatch no longer exists on the inspected current surfaces.

```json
{
  "prior_record_id": "CE-01",
  "current_record_id": null,
  "status": "resolved",
  "lineage_confidence": "High",
  "resolution_basis": "The universal wording was narrowed on all material narrative surfaces to match the unchanged per-dataset evidence.",
  "current_disposition": null,
  "current_severity": null
}
```

## Case 2 — Partial repair with surviving dependency

Prior finding `NI-01` traced a wrong relative-improvement calculation from Table 2 into the abstract and conclusion.

The revised table corrects the calculation, but the conclusion still reports the old percentage.

Correct handling:
- do not mark the whole graph resolved;
- the original numerical root is repaired;
- the stale conclusion survives as a current text/cross-surface problem;
- preserve lineage, but re-root the surviving manifestation if it now has its own current scientific basis.

A transition record may therefore be `partially_resolved`, linked to a current canonical record describing the remaining defect.

```json
{
  "prior_record_id": "NI-01",
  "current_record_id": "FT-01",
  "status": "partially_resolved",
  "lineage_confidence": "High",
  "resolution_basis": "The table arithmetic is corrected, but the conclusion still states the superseded improvement value.",
  "current_disposition": "finding",
  "current_severity": "Moderate"
}
```

## Case 3 — Author query becomes a verified finding

Prior `AQ-02` asked whether an imported baseline used the same split and evaluation budget. The revision now explicitly states that the baseline value was imported from a different split while retaining direct same-protocol superiority wording.

Correct transition:
- the ambiguity is resolved;
- the current scientific defect is now verifiable;
- create the appropriate current finding ID;
- retain `AQ-02` as lineage rather than pretending the current finding existed in the prior review.

```json
{
  "prior_record_id": "AQ-02",
  "current_record_id": "CE-03",
  "status": "reclassified",
  "lineage_confidence": "High",
  "resolution_basis": "The revision establishes that the baseline uses a different split, converting the prior provenance ambiguity into a verified comparability defect.",
  "current_disposition": "finding",
  "current_severity": "Major"
}
```

Structured revision transitions should conform to `schemas/revision_delta.schema.json`; current open findings/queries/gaps remain canonical records conforming to `schemas/finding_record.schema.json`.


## Case 4 — Clarification without repair remains persistent

Prior finding `CE-04` says an imported baseline is presented as directly comparable despite a different evaluation budget. The revision explains the imported provenance more explicitly but keeps the same direct-comparison claim.

Correct transition:
- reviewer understanding improved;
- manuscript defect did not materially shrink;
- status is `persistent`, not `partially_resolved`;
- current severity is recalibrated from the current defect.

```json
{
  "prior_record_id": "CE-04",
  "current_record_id": "CE-04",
  "status": "persistent",
  "lineage_confidence": "High",
  "resolution_basis": "The revision clarifies that the baseline is imported under a different budget but retains the material direct-comparison framing.",
  "current_disposition": "finding",
  "current_severity": "Major"
}
```

## Case 5 — Coverage gap becomes no longer material

Prior `CG-01` records that a cited source cannot be semantically inspected. The revision removes the strong claim that depended on that citation, but the source remains unavailable.

Correct transition:
- semantic verification was **not** completed;
- the prior gap no longer bears on a current material claim;
- use `no_longer_material`, not `resolved`.

```json
{
  "prior_record_id": "CG-01",
  "current_record_id": null,
  "status": "no_longer_material",
  "lineage_confidence": "High",
  "resolution_basis": "The source remains unavailable, but the revised manuscript no longer relies on it for a material semantic claim.",
  "current_disposition": null,
  "current_severity": null
}
```
