# Claim atomicity

The ledger unit should normally be one scientific proposition, not one convenient sentence.

## Why this exists

Paragraph composition protects:

`multiple claims -> one paragraph`

It does not help if the writer hides several independent propositions inside one claim. For example, this is too compound for a Results claim:

> Method A averaged 78.4 versus 76.3; the README and script disagree on the learning rate, so exact reproduction is unresolved.

It contains at least three different obligations:

1. quantitative performance;
2. provenance conflict;
3. reproducibility limitation.

Split them into atomic claims and combine them with paragraph contracts or `required_companions`.

## Default release policy

For `result`, `method`, and `limitation` claims, v1.7 defaults to at most one obvious top-level scientific clause.

The deterministic audit detects conservative high-risk signals such as:

- multiple sentences in one claim;
- top-level semicolons;
- top-level `whereas`, `while`, `however`, or `but` contrasts;
- result claims mixing result evidence with method/limitation evidence;
- method claims mixing non-method evidence.

Parenthetical statistics such as `(p = 0.03; 95% CI ...)` are protected and are not treated as separate propositions merely because they contain semicolons.

## Good splitting pattern

Instead of one compound claim:

```text
performance + task-pattern qualifier + source conflict + reproducibility conclusion
```

prefer:

```text
C_RESULT       quantitative comparison
C_PATTERN      task-level pattern
C_CONFLICT     source discrepancy
C_LIMIT        reproducibility boundary
```

Then use paragraph composition and companion rules to keep the pieces together where required.

## Exemptions

Some scientifically indivisible statements may still trigger a mechanical compound signal. If so, use:

```json
"atomicity_exemption_reason": "Why these clauses form one indivisible scientific proposition."
```

Do not use an exemption merely to avoid splitting a complex sentence. The reason should survive human/model QA.

## Project policy

```json
"claim_atomicity_policy": {
  "enforce_claim_types": ["result", "method", "limitation"],
  "max_top_level_scientific_clauses": 1,
  "allow_exemptions": true
}
```

Atomicity is a guardrail, not a semantic theorem. The model/researcher still decides whether two clauses are genuinely one proposition.
