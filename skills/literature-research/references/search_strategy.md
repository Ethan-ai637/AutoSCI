# Search Strategy

## Goal

Maximize useful coverage while preserving reproducibility and avoiding false claims of completeness. Search quality is not measured by hit count alone; it is measured by whether the planned concepts, sources, dates, and discovery routes were actually attempted, whether retrieval succeeded, and whether the marginal yield supporting a stopping decision is recorded.

## Concept blocks

Represent the question as 2–5 concept blocks. For each block collect canonical terms, abbreviations, historical names, spelling variants, broader/narrower terms when justified, and controlled vocabulary terms when the database supports them.

Combine synonyms within a block using OR and concepts across blocks using AND. Add exclusions only when they clearly improve precision without removing plausible relevant work.

Use the exact concept `name` values from `protocol.json` in the `concept_blocks` column of `search_log.csv`. This lets `audit_search.py` check which parts of the protocol were exercised.

## Search sources

Use sources appropriate to the field and task. Typical roles include broad scholarly indexes, discipline-specific databases, publisher/full-text search, preprint servers, citation indexes, and software/dataset/project pages.

`target_sources` is a protocol commitment, not a list of names that merely need to appear in a log. Distinguish:

- **not attempted** — no query row exists;
- **failed** — a real attempt was made but retrieval failed;
- **partial** — some retrieval succeeded but was capped, sampled, rate-limited, or mixed with failed routes;
- **succeeded** — the logged query execution completed as intended for that route.

A source that returned HTTP 503 is attempted/failed, not “covered”. A query with 7,000 reported hits and only 100 imported records is normally partial even if the API call itself succeeded.

## Layered search

### Seed search

Find 3–10 high-information items to discover terminology and citation routes. Seed papers do not define inclusion by themselves.

### Structured search

Translate concept blocks into database-specific syntax. Preserve the exact submitted string and retrieval status.

### Citation chasing

Use included high-value papers for backward and forward chasing. Record each chasing round as a search-log row rather than invisible browsing.

### Gap search

After initial screening/clustering, inspect thin themes and missing concept combinations. Run targeted gap searches and label them with `search_stage=gap`.

## Search log and marginal yield

The v2 search log records:

`query_id,search_stage,source,interface,query,searched_at,filters,concept_blocks,search_status,result_count,imported_count,new_unique_count,new_screened_count,new_included_count,stopping_evidence,coverage_note,notes`

Use `search_status` = `succeeded`, `partial`, or `failed`.

Count fields are deliberately separate:

- `result_count`: source-reported hits when meaningful;
- `imported_count`: records actually imported from this query;
- `new_unique_count`: records still new after deduplication against the current corpus;
- `new_screened_count`: records newly entering screening from this route;
- `new_included_count`: newly eligible records after screening.

Do not fabricate unavailable counts. Missing counts remain blank and are surfaced as a limitation.

## Stopping evidence

A prose stopping rule is not mechanically verified merely because it exists in `protocol.json`. Mark the search rows that actually justify stopping with `stopping_evidence=yes`.

For those rows, `new_unique_count`, `new_screened_count`, and `new_included_count` should be recorded when the workflow claims marginal-yield saturation. If they are missing, the audit reports `stopping_rule_status=not_assessable` rather than implying saturation.

One zero-yield query is not universal saturation. Prefer repeated low/zero marginal yield across the relevant routes named in the protocol.

## Coverage audit

Run:

```bash
python scripts/audit_search.py --protocol protocol.json --search-log search_log.csv --report review/search_audit.json
```

The audit reports source-level execution coverage, concept tags, missing marginal-yield counts, and stopping-rule verifiability. A passing standard-profile audit may still contain explicit warnings for failed or partial sources; systematic-profile work treats key coverage failures more strictly.

A search audit proves internal logging consistency only. It does not prove database completeness, indexing quality, or exhaustive literature coverage.
