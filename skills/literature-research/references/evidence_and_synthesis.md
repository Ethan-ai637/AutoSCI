# Evidence Table and Synthesis

## Evidence unit

Prefer one row per claim/evidence unit rather than one row per paper when a paper contains several materially different results.

Every evidence-bearing row should have a stable `claim_id`. This ID is the bridge from source extraction to cross-paper synthesis.

Separate:

- `reported_result`: what the source explicitly reports;
- `authors_interpretation`: the source authors' explanation;
- `reviewer_interpretation`: your synthesis/interpretation;
- `limitations`: reported or reviewer-identified limits, clearly distinguished.

## Claim provenance fields

Use the following fields to make a claim independently checkable:

- `source_id`: canonical report/record ID;
- `study_id`: underlying study ID from `study_map.csv`;
- `source_version`: the exact version used when materially relevant (preprint, journal, supplement, etc.);
- `claim_id`: unique evidence-unit ID;
- `evidence_location`: page/section/table/figure/equation/result locator;
- `support_level`: `direct`, `derived`, `contextual`, or `unclear`;
- `verification_status`: `verified`, `partial`, or `unverified`.

`direct` means the reported result/claim is directly supported at the cited location. `derived` means the reviewer computed or inferred something from reported source data and must explain the transformation. `contextual` means the source informs framing rather than directly supporting the focal claim.

Do not mark a row `verified` solely because the abstract or a search-result snippet looked plausible if the conclusion depends on details unavailable there.

## Quantitative evidence

Preserve metric name, direction, comparator, units, uncertainty, and evaluation context. Do not compare numbers across studies when metrics, datasets, populations, or protocols are not commensurate without explaining the mismatch.

If a value is reviewer-derived, record that fact and enough information to reproduce the derivation.

## Qualitative evidence

Record the phenomenon, context, data basis, and how the conclusion was established. Avoid upgrading descriptive observations into causal claims.

## Synthesis as a second provenance layer

Do not let the final narrative become detached from the evidence table. Use two normalized files:

- `synthesis_claims.csv`: one row per cross-paper conclusion;
- `synthesis_evidence.csv`: many-to-many links from synthesis claims to evidence `claim_id`s.

Allowed link relations:

- `supports`
- `contradicts`
- `qualifies`
- `context`

Recommended `evidence_state` values for synthesis claims:

- `consistent`
- `mixed`
- `single_study`
- `single_source` (legacy/report-level label; prefer `single_study` when a study map exists)
- `gap`
- `descriptive`

Then audit:

```bash
python scripts/audit_synthesis.py \
  --evidence review/evidence_table.csv \
  --claims review/synthesis_claims.csv \
  --links review/synthesis_evidence.csv \
  --study-map review/study_map.csv \
  --report review/synthesis_audit.json \
  --update-claims
```

A `consistent` claim should map to at least two distinct underlying studies when `study_map.csv` is available. The audit also derives a separate `verification_coverage` for every synthesis claim and, with `--update-claims`, writes it plus verified/partial evidence counts and eligible support/contradiction unit counts back into `synthesis_claims.csv`: `complete` when all substantive support/contradiction links are verified, `mixed` when verified and partial evidence are both present, `partial_only` when all substantive evidence is only partially verified, and `not_applicable` when no substantive evidence is counted. This field does not change the scientific evidence state; it exposes how completely the underlying substantive evidence was checked. Multiple reports from one study do not count as independent replication. In addition, only evidence rows with `support_level` of `direct` or `derived` and `verification_status` of `verified` or `partial` count toward substantive support/contradiction. `contextual`, `unclear`, or `unverified` evidence can remain linked for provenance, but it cannot satisfy convergence or disagreement gates. A `mixed` claim requires eligible evidence on both the supporting and contradicting sides rather than hiding disagreement in prose.

## Report-aware versus study-aware synthesis

Evidence is extracted from reports, but independence is assessed at the study level. If two evidence claims come from different papers that map to the same `study_id`, treat them as multiple reports of one study unless the research question explicitly calls for report-level analysis.

Use `audit_synthesis.py --study-map review/study_map.csv` so `consistent` and `single_study` states are checked against independent studies rather than publication count. The protocol defaults `synthesis_unit` to `study`; choose report-level synthesis only for questions where publications/reports themselves are the intended unit of analysis.

## Cross-paper synthesis

Synthesize by question/theme:

- convergence;
- disagreement;
- boundary conditions;
- methodological differences;
- population/dataset differences;
- temporal/version differences;
- evidence gaps.

Do not use vote counting (“7 positive, 3 negative”) as the only synthesis when study quality and comparability differ.

Do not manufacture reconciliation. If studies disagree and the available evidence does not identify why, preserve the disagreement as an unresolved finding.

## Evidence strength notes

`evidence_strength_note` is descriptive, not a universal score. Good notes explain relevant features: design, sample/data scale, replication, benchmark breadth, uncertainty, external validation, or obvious confounding.
