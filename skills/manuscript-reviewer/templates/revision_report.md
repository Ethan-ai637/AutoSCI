# Revision / rebuttal review report

Use this template only when prior findings, a prior manuscript version, or a rebuttal is actually available.

## 1. Review context

State:
- prior and current manuscript/version identifiers if available;
- materials compared;
- whether an author response letter was inspected;
- review mode;
- any material evidence boundary.

Do not invent version identifiers.

## 2. Resolution summary

Give counts only after lineage matching and deduplication.

Example structure:

- Prior material issues reassessed: N
- Resolved: N
- Partially resolved: N
- Persistent: N
- Reclassified: N
- Not reassessable: N
- No longer material: N
- New current issues: N

Do not count resolved issues as current open findings.

## 3. Prior-issue delta

| Prior ID | Current ID | Status | Current severity/disposition | Evidence of change | Remaining action |
|---|---|---|---|---|---|

Use `—` for Current ID when a prior issue is fully resolved and no current canonical record is needed.

For `partially_resolved`, say exactly what was fixed and what remains.

For `not_reassessable`, identify the blocking material rather than implying persistence.

For `no_longer_material`, state that the prior verification/concern was not substantively adjudicated but no longer bears on a current material claim. Do not call it resolved.

## 4. Current unresolved main comments

Render only current reportable canonical records.

For a persistent/partial issue, include prior lineage briefly:

```text
[CE-02] Major | High confidence | partially resolved from prior CE-02
Location: ...
Claim/object: ...
Evidence state: ...
Observed evidence: ...
Issue: ...
Why it matters: ...
Remediation class: ...
Recommended fix: ...
```

Do not repeat the full historical finding unless needed to explain the delta.

## 5. New current issues

List genuinely new findings/queries/gaps only after lineage checking.

## 6. Resolved items

Keep concise. One line per prior item is usually sufficient:

- `[NI-01] resolved` — the aggregate and all dependent narrative values are now reconciled.

Do not reproduce resolved issues as active concerns.

## 7. Items not reassessable

| Prior ID | Block | Consequence for re-review |
|---|---|---|

## 8. No-longer-material prior items

Keep this concise and separate from resolved items. Example:

- `[CG-01] no longer material` — source text remains unavailable, but the revised manuscript no longer relies on that citation for a material semantic claim.

## 9. Current prioritized action list

Reference **current** canonical IDs. Do not include already resolved items.

## 10. Revision audit coverage

State whether the review checked:
- prior root-to-current lineage;
- rebuttal claims against current manuscript locations;
- dependency propagation;
- new-issue lineage;
- current canonical record integrity;
- revision delta schema, if structured output was requested.
