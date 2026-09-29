# Quality Assurance

## Hard failures

Do not finalize when any of these remain:

- fabricated or unverified bibliographic record presented as real;
- duplicate canonical DOI/PMID/PMCID/arXiv IDs after deduplication;
- excluded record without a reason;
- final screening snapshot contains duplicate record IDs;
- unresolved screening conflict in a workflow whose protocol requires adjudication;
- evidence row pointing to a missing source ID;
- standard/systematic report missing from `study_map.csv`;
- evidence `study_id` disagreeing with the report-to-study map;
- verified `same_study_version` edge spanning two different study IDs;
- a supposedly independent/consistent synthesis supported only by multiple reports of one study;
- `consistent`/`mixed` synthesis using only contextual, unclear, or unverified rows as substantive evidence;
- `consistent` synthesis with an eligible contradicting evidence link;
- duplicate or missing claim IDs in a standard/systematic evidence table;
- synthesis claim presented as evidence-backed but linked to no evidence claim;
- citation-trail edge pointing to a missing record;
- citation edge without a verification source;
- systematic-profile search row without exact query/date/source;
- a planned systematic-profile target source absent from the search log without an explicit protocol deviation;
- synthesis claim stronger than the underlying evidence or search coverage;
- versioned final workspace that fails its declared structural schema or lacks a current passing schema audit before freeze/handoff.

## Soft warnings

Investigate, but these may be legitimate:

- many singleton topic clusters;
- many `uncertain` screening rows;
- included record with no extracted evidence row;
- evidence claim with no precise evidence locator;
- provisional or ambiguous multi-report study grouping;
- large difference between retrieved and included counts;
- one search source contributes nearly all included papers;
- protocol concepts never tagged in structured/gap search rows;
- `mixed` synthesis claim without explicit contradictory/supporting links.

## Count reconciliation

Keep these distinct:

- raw retrieved records;
- imported records;
- normalized records;
- duplicates removed;
- unique records screened;
- title/abstract exclusions;
- full-text/full-record exclusions;
- unresolved screening conflicts;
- included reports;
- included underlying studies;
- evidence-table claims;
- cross-paper synthesis claims.

A claim row is not a study count. A search hit is not an imported record. A deduplicated bibliographic record is not always equivalent to one underlying study.

## Recommended audit sequence

1. `audit_search.py`
2. `deduplicate_records.py` report review
3. `reconcile_screening.py` when a screening log is used
4. `audit_citation_trail.py`
5. `audit_studies.py`
6. `audit_synthesis.py --study-map ...` when synthesis claims exist
7. `preflight.py` across the complete artifact set
8. `build_flow_report.py` for count reconciliation
9. `validate_workspace.py --require-final` for the structural contract
10. `snapshot_review.py --require-preflight` and `verify_snapshot.py` for stable handoff/archive milestones

Passing scripts establish internal consistency, not scientific truth. Human/model scientific judgment remains responsible for eligibility criteria, evidence interpretation, and scope-appropriate conclusions.
## v1.6 real-world retrieval gates

- A logged failed query is not successful source coverage.
- A capped/sampled retrieval should be marked partial.
- A stopping rule with missing tagged marginal-yield evidence is not mechanically assessable.
- `full_text_attempted` is not `full_text_screened`; strict full-text inclusion requires documented full-text access.
- A final `uncertain` record must not match an enabled deterministic exclusion rule.
- Synthesis evidence state and verification coverage are separate: a claim may be scientifically `consistent` while verification coverage is `mixed` or `partial_only`.

