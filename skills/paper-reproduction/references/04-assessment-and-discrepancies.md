# Assessment and Discrepancies

## Claim-scoped assessment

Assess each target claim separately. A paper can have one claim reproduced, another blocked, and another numerically different.

## Primary states

### `exact_reproduction`

Use only when the target is exact/deterministic or has an explicitly exact comparison rule, with no material protocol divergence.

### `within_reported_variation`

Use when the result satisfies a predeclared region grounded in reported variation or another justified rule set before observing the reproduction result.

### `numerically_different`

Use when the target experiment completed under a sufficiently matched protocol but the numeric result falls outside the declared comparison rule.

### `qualitatively_consistent`

Use for preserved trend/order/behavior when numeric reproduction is not established.

### `partial_reproduction`

Use when only part of the contracted condition set completed.

### blocker/unknown states

- `blocked_by_missing_data`
- `blocked_by_missing_artifact`
- `blocked_by_environment`
- `underspecified`
- `not_attempted`

## Discrepancy reasoning

A discrepancy record should answer:

- What differs?
- Where was it observed?
- Is it an execution blocker, protocol deviation, or completed-result mismatch?
- What evidence supports the diagnosis?
- Which claims/runs are affected?
- Was a diagnostic modification attempted?
- Did that modification change the scientific protocol?

## No result chasing

If a diagnostic change improves agreement, record it as evidence about sensitivity—not as permission to replace the baseline run. Preserve both runs and explain the protocol difference.

## Reporting scope

Prefer “not reproduced under commit X, environment Y, and data version Z” over a global claim about the paper.
