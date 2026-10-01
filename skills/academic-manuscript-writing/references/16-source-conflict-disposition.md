# Source-conflict disposition

A source conflict is not automatically the same thing as an unsafe manuscript.

## Why disposition matters

Use four release dispositions:

- `blocking`: the unresolved conflict changes which scientific result, method fact, or conclusion should be believed. Release must stop.
- `disclose_and_scope`: the conflict cannot be factually resolved from allowed evidence, but the manuscript can remain correct by keeping the competing provenance separate, scoping affected claims, and explicitly disclosing the unresolved discrepancy.
- `historical_only`: the conflict affects only superseded/retired claims that are no longer part of the current manuscript.
- `resolved`: the conflict has been resolved with an authoritative source or correction.

Legacy free-text entries in `project.json.unresolved_conflicts` are treated as `blocking` at release.

## Recommended record

```json
{
  "conflict_id": "CF001",
  "status": "unresolved",
  "release_disposition": "disclose_and_scope",
  "summary": "README and reproduction script disagree on the learning rate.",
  "reason": "The reported score remains usable if the exact-run setting is not asserted.",
  "affected_source_ids": ["SRC_TABLE", "SRC_SCRIPT"],
  "affected_claim_ids": ["C_RESULT", "C_DISCLOSURE"],
  "scoped_claim_ids": ["C_RESULT"],
  "disclosure_claim_ids": ["C_DISCLOSURE"],
  "required_disclosure_text_tokens": ["unresolved"]
}
```

Every claim named by an object-style conflict should include:

```json
"source_conflict_ids": ["CF001"]
```

This gives bidirectional traceability.

## `disclose_and_scope` is not conflict suppression

Release is allowed only when:

1. the conflict remains explicitly `unresolved`;
2. the reason for allowing scoped release is recorded;
3. disclosure claims are active and actually represented in the manuscript;
4. scoped current claims are active/current manuscript claims;
5. all linked claims declare the conflict ID;
6. optional required disclosure tokens survive in the exact disclosure block;
7. no prose merges conflicting values into a single source-independent fact.

Use separate source-specific comparisons when provenance differs. Do not average, subtract across, or harmonize incompatible source values merely to simplify prose.

## `historical_only`

Use only when every affected claim is inactive (`superseded` or `retired`). If an active claim still depends on the conflict, `historical_only` is invalid.

## Release command

`audit_source_conflicts.py` is included in `preflight.py`. A non-blocking unresolved conflict can therefore coexist with a release PASS, but only after the disclosure/scoping contract is satisfied.


## v1.7.1 conflict-side provenance closure

`disclose_and_scope` is safest when each competing provenance stream is machine-readable rather than described only in free text. Add `conflict_sides` when the conflict contains source-specific values/settings/results that must never be silently blended.

```json
{
  "conflict_id": "CF001",
  "status": "unresolved",
  "release_disposition": "disclose_and_scope",
  "conflict_sides": [
    {
      "side_id": "v1",
      "source_ids": ["SRC_V1"],
      "evidence_ids": ["E_V1"],
      "value_tokens": ["74.7"],
      "attribution_tokens": ["arXiv v1", "v1"]
    },
    {
      "side_id": "repo",
      "source_ids": ["SRC_REPO"],
      "evidence_ids": ["E_REPO"],
      "value_tokens": ["76.3"],
      "attribution_tokens": ["current repository", "repository"]
    }
  ],
  "scoped_claim_ids": ["C_REPO_RESULT"],
  "disclosure_claim_ids": ["C_CONFLICT_DISCLOSURE"],
  "cross_side_claim_ids": ["C_CONFLICT_DISCLOSURE"]
}
```

With `conflict_sides` present, release adds three deterministic invariants:

1. A normal `scoped_claim_id` must resolve to **exactly one** side through its evidence/source linkage or side-specific value tokens. If it spans both sides, split it into source-specific claims.
2. A claim intentionally representing multiple sides must be listed in `cross_side_claim_ids`, and every cross-side claim must also be a manuscript `disclosure_claim_id`.
3. A cross-side disclosure claim must visibly attribute every represented side using that side's `attribution_tokens`.

This does not mathematically prove that no derived cross-source quantity could ever be invented. It does close the important ledger-level loophole: current scientific claims cannot silently depend on competing evidence streams while the conflict record merely says that disclosure exists.


## v1.7.2 cross-side numeric provenance closure

A cross-side disclosure can legitimately mention both competing provenance streams, but that permission must not become a way to introduce an unregistered average, difference, ratio, or other numeric synthesis. When `conflict_sides` are present, every numeric token in each `cross_side_claim_id` must be attributable to either:

1. a represented side's `value_tokens`; or
2. an explicit `cross_side_numeric_exceptions` entry.

Example:

```json
{
  "cross_side_numeric_exceptions": [
    {
      "claim_id": "C_CONFLICT_DISCLOSURE",
      "value_token": "1.6",
      "role": "derived",
      "reason": "Arithmetic difference between the two explicitly attributed source-specific values.",
      "source_side_ids": ["v1", "repo"]
    }
  ]
}
```

Allowed roles are:

- `derived`: a number calculated from multiple conflict sides. It must name at least two valid `source_side_ids` and provide a reason.
- `context`: a numeric token needed for context (for example, a year) that is not itself a conflicting scientific value. It still requires a reason.

The release audit checks both the claim ledger text and the anchored manuscript paragraph. Numeric tokens contributed by other registered active claims in the same paragraph are allowed; extra prose-level numbers that belong to neither a conflict side nor an explicit exception are rejected. This is a provenance gate, not a mathematical-validity engine: registering a derived number makes the derivation inspectable, but scientific correctness of the derivation must still be judged from the evidence.\n