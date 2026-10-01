# Stable output contract

## Purpose

Define how verified review state is exposed to the user. The output layer renders canonical records; it does not perform a second scientific adjudication.

## Default behavior

Unless the user requests another format, use a concise reviewer-style prose report with:

1. scope / evidence boundary / manuscript archetype;
2. executive summary;
3. main comments;
4. secondary findings and cleanup when material;
5. author queries;
6. prioritized correction checklist;
7. coverage gaps;
8. compact audit-coverage summary.

Do not output raw ledgers, temporary candidates, private reasoning, or structured JSON by default.

## Canonical inheritance

For every outward item, the following fields must mechanically inherit from the canonical record:

- public ID;
- disposition;
- severity;
- confidence;
- salience / report section;
- evidence state;
- issue scope;
- remediation class;
- strongest summary-safe statement;
- evidence boundary.

If report drafting reveals that one of these is wrong, update the canonical record first, rerun self-check/validation, and regenerate the prose.

## Executive summary

The executive summary may compress or omit low-salience items. It may not:

- turn a query into a finding;
- turn a gap into unsupported/false;
- increase severity;
- widen scope;
- strengthen causal or generalization language;
- require a stronger remedy than the canonical record;
- synthesize several Moderate findings into a new Major meta-finding unless that meta-finding was itself independently verified and canonically recorded.

## Structured mode

Only emit canonical JSON when the user requests structured or machine-readable output, or when a test prompt explicitly requires it.

- finding/query/gap records should conform to `schemas/finding_record.schema.json`;
- revision transitions should conform to `schemas/revision_delta.schema.json`.

Schema-valid output can still be scientifically wrong; schema validation is necessary, not sufficient.

## Revision / rebuttal mode

When prior issues or manuscript versions are in scope:

1. render transition history from revision-delta records;
2. render current unresolved concerns only from current canonical records;
3. do not count historical resolved items as current findings;
4. do not call a gap `resolved` merely because the current manuscript stopped relying on it; use the state model;
5. do not preserve prior severity unless the residual current defect independently warrants it.

## Report counts

Counts in the executive summary and resolution summary use final deduplicated roots only. Dependent manifestations do not increase counts unless re-rooted as independently material concerns.

## Recommendation / score boundary

Do not provide accept/reject recommendations, paper scores, or publication probabilities by default. If explicitly requested, answer only to the extent supported by the task and available evidence; do not let such a request alter the underlying findings.
