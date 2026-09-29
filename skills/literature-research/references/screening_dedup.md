# Screening and Deduplication

## Deduplication boundary

Deduplicate bibliographic reports before final screening counts. Prefer stable identifiers (DOI, PMID/PMCID, arXiv) over title similarity. Strong conflicting stable identifiers block automatic fuzzy merging. A preprint, conference paper, journal extension, protocol, follow-up, or secondary analysis may be related without being a duplicate; preserve report identity and resolve study identity separately in `study_map.csv`.

## Screening decisions

Allowed final decisions are:

- `include`
- `exclude`
- `uncertain`

Every exclusion needs a reason code tied to the protocol where possible. `uncertain` is correct when the available evidence cannot support a safe decision, but it is not a substitute for an explicit high-precision exclusion rule already declared in the protocol.

## Evidence stage is not the same as decision stage

The v2 screening log distinguishes:

- `title_abstract` — evidence comes from title, metadata, or abstract;
- `full_text_attempted` — full-text retrieval was attempted, but the relevant full text was not necessarily obtained/reviewed;
- `full_text_screened` — the relevant full text was actually accessed and screened;
- `adjudication` / `final` — decision-resolution stages, not evidence-access claims;
- `full_text` — legacy ambiguous value from v1 workspaces. It must be manually resolved and does not prove full-text screening.

Use `access_level` values such as `title_only`, `abstract`, `metadata_plus_abstract`, `full_text`, or `unknown`.

Do not duplicate a title/abstract decision into a later row and label it full-text screening when no additional source was accessed. If retrieval failed, record `full_text_attempted` plus the best actual access level and the failure/limitation in `evidence_basis` or `notes`.

## Protocol stage semantics

If the protocol strictly requires `full_text`, included records need `evidence_stage=full_text_screened` and `access_level=full_text`.

If the protocol explicitly allows `full_text_or_most_complete_accessible_record`, an included record may stop at `full_text_attempted` when full text is unavailable, but the limited access must remain visible and should affect verification/caveat language downstream.

## Deterministic obvious-exclusion gate

Some exclusions can be encoded safely without semantic judgment, especially structured publication types using delimited exact-item matching. In v1.6.1 the gate uses enabled explicit `deterministic_exclusion_rules` **and** conservatively derives publication-type exact-item rules when types such as reviews/editorials/commentaries are literally named in `exclusion_criteria`. This derivation is intentionally narrow; semantic task/population exclusions are never inferred mechanically.

Supported operators include `equals`, `contains_any`, `contains_all`, `regex`, `exists`, and `missing`. Rules may target canonical record fields or helper fields such as `title_or_abstract`.

Preview matches:

```bash
python scripts/apply_screening_rules.py \
  --protocol protocol.json \
  --records records.deduped.csv \
  --output review/obvious_exclusions.csv \
  --append-log review/screening_log.csv
```

For standard/systematic work, run this gate before manual screening; if no active/derived-safe rules exist it is a no-op. Preflight rejects a final `uncertain` record that still matches an enabled deterministic exclusion rule.

Do not encode broad semantic keywords as deterministic rules if they can produce false exclusions. The deterministic gate should be conservative and high precision.

## Reconciliation

`screening_log.csv` is append-only history. `screening.csv` is the derived current snapshot. Reconciliation keeps the final decision stage separate from:

- `evidence_stage` — highest evidence-access screening stage reached;
- `access_level` — highest documented source access level.

Same-stage reviewer disagreement remains unresolved until adjudication/final resolution. Never overwrite history to make conflicts disappear.
