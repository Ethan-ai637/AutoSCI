---
name: literature-research
description: Search, screen, deduplicate, resolve report-to-study identity, cluster, synthesize, and audit scientific literature with explicit provenance. Use for literature reviews, related-work discovery, evidence mapping, state-of-the-art scans, systematic-review preparation, citation chasing, evidence tables, and citation trails. Keep search decisions, screening history, evidence units, and synthesis claims inspectable; use deterministic scripts for normalization, conservative deduplication, search coverage audit, screening reconciliation, candidate topic clustering, citation-trail audit, claim-level synthesis audit, and cross-artifact QA. Do not claim systematic or exhaustive coverage unless the protocol and search log support it.
---

# Literature Research

Research literature as an auditable pipeline:

**question -> versioned protocol -> search -> normalize -> deduplicate -> screening log -> final screening -> study map -> cluster -> evidence table -> citation trail -> synthesis claims -> QA -> flow report -> evidence graph/brief -> schema validation -> frozen snapshot -> downstream handoff**

The model handles scientific judgment. Deterministic scripts handle mechanical transformations, provenance checks, reconciliation, and cross-file consistency.

## Hard rules

1. Define the research question and scope before broad searching. Record important scope changes instead of silently moving the goalposts.
2. Treat search-result snippets as discovery aids, not final scientific evidence. Verify important claims against the paper, abstract/metadata record, preprint, supplement, or another authoritative source appropriate to the claim.
3. Log every substantive search with source/database, exact query, date, search stage, filters, execution status, and result count when available. An attempted query is not successful source coverage.
4. Normalize and deduplicate before final screening counts. Preserve provenance for every merged duplicate.
5. Use stable identifiers first: DOI, PMID/PMCID, arXiv ID, then conservative title matching. Never merge two records only because they discuss the same topic. Strong identifier conflicts block fuzzy auto-merge.
6. Preserve screening history when there is more than one stage or reviewer. `screening.csv` is the final snapshot; `screening_log.csv` records how the decision was reached.
7. Every screening exclusion must have an explicit reason code. `uncertain` is allowed and preferred to forced judgment, but it must not override a high-precision deterministic exclusion rule explicitly declared in the protocol. Do not erase reviewer conflicts; adjudicate them according to the protocol.
8. Cluster only after basic relevance screening. Clusters organize the corpus; they do not decide inclusion or scientific validity.
9. Evidence tables are claim-specific. Every substantive evidence unit gets a stable `claim_id`; separate what a paper reports from author interpretation and reviewer synthesis.
10. Cross-paper synthesis must remain linked to evidence claim IDs. A prose conclusion without traceable evidence links is not an auditable synthesis. Only `direct`/`derived` evidence with `verified`/`partial` verification may count as substantive support or contradiction for `consistent`, `mixed`, `single_study`, or `single_source` states.
11. Citation-trail edges must be verified and typed. Never invent that paper A cites paper B. Record how the edge was established.
12. Distinguish bibliographic reports from underlying studies. Multiple reports from one study must not be counted as independent replication.
13. Distinguish versions (preprint, accepted manuscript, journal article, correction) and prefer the version appropriate to the research question.
14. Do not fabricate bibliographic metadata, sample sizes, effect sizes, quotes, page numbers, citation relationships, screening rationales, or search counts.
15. Do not call a search “systematic”, “exhaustive”, or “complete” unless the protocol, coverage, dates, databases, screening log, and search audit justify that description.
16. Before downstream reuse, export structured provenance rather than handing off an untraceable prose summary. Generated briefs/graphs may only reorganize recorded review artifacts; they must not invent scientific relationships.
17. Keep protocol version, workspace schema version, and skill version distinct. Never silently interpret an older workspace under a newer structural contract.
18. For a handed-off or archival review, freeze the workspace with a hash manifest only after deterministic QA and workspace-schema validation pass. A manifest proves file identity, not scientific truth or database completeness.
19. Distinguish `full_text_attempted` from `full_text_screened`. Never label an abstract-only or failed-access decision as completed full-text screening.

## 1. Choose a profile

Use `templates/protocol.template.json` and set `profile`:

- `exploratory`: quick landscape, terminology discovery, seed papers, rough clusters. Coverage claims must remain modest.
- `standard`: **default**. Multi-source search, logged queries, deduplication, explicit screening, evidence table, citation chasing, claim-linked synthesis, and preflight QA.
- `systematic`: protocol-first workflow intended for systematic/scoping-review preparation. Requires reproducible search strings, source-by-source logs, explicit inclusion/exclusion criteria, screening history, conflict handling, and count reconciliation. This skill can support a systematic review, but does not make one systematic merely by setting this flag.

Read `references/search_strategy.md` when query design, source selection, or stopping logic is non-trivial.

## 2. Write the protocol before searching

Capture:

- `protocol_id`, `protocol_version`, and `created_at` for reproducible handoff;
- `research_question`
- population/domain/system/context if relevant
- concepts and synonyms
- date/language/publication-type limits
- inclusion criteria
- exclusion criteria
- target sources/databases
- outcome/evidence fields to extract
- screening plan, including stages/reviewer count/conflict resolution when relevant
- stopping rule
- high-precision `deterministic_exclusion_rules` when an exclusion can be expressed mechanically without semantic guesswork
- `synthesis_unit` (`study` by default; use `report` only when the research question is genuinely publication/report-level)
- profile

For causal/intervention questions, use a suitable framing such as PICO/PICOS when appropriate. For methods/engineering questions, a concept matrix is often more useful than forcing PICO.

Do not invent criteria after seeing favorable results. If the scope changes, append a structured entry to `protocol_changes` with at least `changed_at`, `field`, and `rationale`; increment `protocol_version` when the change is material.

## 3. Search in layers and measure marginal yield

Use a layered strategy rather than one giant query:

1. **Seed search** — identify canonical terminology, landmark papers, surveys, benchmarks, and key authors/venues.
2. **Structured search** — combine concept blocks with synonyms and exclusions appropriate to each source/database.
3. **Backward citation chasing** — inspect references of high-value included papers.
4. **Forward citation chasing** — find later work citing high-value seeds when the search source supports it.
5. **Gap search** — search concepts underrepresented in the screened corpus.

For every substantive query, append a row to `search_log.csv`. The v2 search contract uses:

`query_id,search_stage,source,interface,query,searched_at,filters,concept_blocks,search_status,result_count,imported_count,new_unique_count,new_screened_count,new_included_count,stopping_evidence,coverage_note,notes`

Use `search_status=succeeded|partial|failed`. A database that returned an HTTP error is **attempted/failed**, not covered. A query that reports 7,000 hits but imports only the first 100 is normally `partial`, not `succeeded`.

For iterative rows that actually import records, record `new_unique_count`, `new_screened_count`, and `new_included_count` when determinable. Tag the rows that justify the final stopping decision with `stopping_evidence=yes`. If those marginal-yield fields are missing, the stopping rule is `not_assessable`, not silently “passed”. Leave unavailable counts blank and explain why rather than inventing them.

Audit protocol-to-search coverage:

```bash
python scripts/audit_search.py \
  --protocol protocol.json \
  --search-log search_log.csv \
  --report review/search_audit.json
```

The audit separately reports planned, attempted, succeeded, partial, and failed target sources, plus whether marginal-yield evidence is complete and whether the stopping rule is mechanically verifiable. A passing structural audit still does not prove that any database itself is complete.

Do not use citation counts as a proxy for truth or relevance. Use them only as one discovery signal.

## 4. Normalize records

Collect retrieved metadata into CSV/JSON/JSONL with as many of these fields as available:

`record_id,title,authors,year,venue,doi,pmid,pmcid,arxiv_id,url,abstract,source,query_id,retrieved_at,publication_type`

Normalize mechanically:

```bash
python scripts/normalize_records.py raw_records.csv -o records.normalized.csv
```

When combining multiple exports, pass multiple inputs:

```bash
python scripts/normalize_records.py source_a.csv source_b.jsonl source_c.json -o records.normalized.csv
```

The script preserves unknown fields under `extra_json` when possible and generates a stable local `record_id` when one is missing.

## 5. Deduplicate conservatively

Run:

```bash
python scripts/deduplicate_records.py records.normalized.csv \
  -o records.deduped.csv \
  --report dedup_report.json
```

Default matching order:

1. exact normalized DOI;
2. exact PMID/PMCID;
3. exact arXiv ID;
4. exact normalized title;
5. high-threshold fuzzy title match with compatible year when available.

A conflicting stable identifier blocks fuzzy auto-merge. Preprint/conference/journal relationships may be version families rather than duplicates; preserve distinct records when they materially differ and link them later when the relationship is verified.

Read `references/screening_dedup.md` for edge cases.

## 6. Initialize review artifacts

```bash
python scripts/init_review_artifacts.py records.deduped.csv --outdir review
```

This creates:

- `review/screening.csv` — final current screening state;
- `review/screening_log.csv` — append-only screening history;
- `review/study_map.csv` — one provisional study per report until relationships are verified;
- `review/evidence_table.csv`;
- `review/citation_trail.csv`;
- `review/synthesis_claims.csv`;
- `review/synthesis_evidence.csv`.

For a trivial single-pass exploratory scan, editing only `screening.csv` is acceptable. For standard/systematic work with multiple stages or reviewers, use the log.

## 7. Screen with explicit history and reconcile conflicts

Allowed decisions:

- `include`
- `exclude`
- `uncertain`

Recommended exclusion codes:

`OUT_OF_SCOPE`, `WRONG_POPULATION`, `WRONG_METHOD`, `WRONG_OUTCOME`, `WRONG_PUBLICATION_TYPE`, `INSUFFICIENT_EVIDENCE`, `SUPERSEDED_VERSION`, `NOT_PRIMARY_SOURCE`, `LANGUAGE_LIMIT`, `DATE_LIMIT`, `OTHER`.

For each screening event, record the stage, access level, reviewer when relevant, criterion/reason, and evidence basis. Use these stage semantics:

- `title_abstract` — decision based on title/metadata/abstract;
- `full_text_attempted` — retrieval was attempted but full text was not necessarily available/reviewed;
- `full_text_screened` — the relevant full text was actually accessed and screened; requires `access_level=full_text`;
- `full_text` — legacy ambiguous value only; it does **not** satisfy a v1.6 full-text requirement until manually resolved.

Recommended `access_level` values are `title_only`, `abstract`, `metadata_plus_abstract`, `full_text`, or `unknown`. A copied title/abstract decision must not be duplicated as a fake full-text event.

Before manual screening in `standard`/`systematic`, **always run the deterministic obvious-exclusion gate once**. It combines enabled explicit `deterministic_exclusion_rules` with a conservative derived-safe publication-type exact-item rule when review/editorial/commentary types are literally named in `exclusion_criteria`:

```bash
python scripts/apply_screening_rules.py \
  --protocol protocol.json \
  --records records.deduped.csv \
  --output review/obvious_exclusions.csv \
  --append-log review/screening_log.csv
```

If no safe rules are available this is a no-op. Derived-safe rules are deliberately limited to structured publication types using delimited exact-item matching; they do **not** infer semantic exclusions such as imaging-only, patient-education-only, wrong population, or wrong clinical task. Use explicit deterministic rules for other genuinely mechanical criteria. Matched deterministic exclusions are appended at `adjudication` stage: they outrank ordinary title/abstract/full-text uncertainty, while a deliberate later `final` event can still override them after the protocol/rule is reviewed. Preflight uses the exact same active rule set and rejects a final `uncertain` record that still matches one of these high-precision exclusions. Use `--no-derived-safe-rules` only when intentionally disabling the conservative publication-type derivation.

After screening events are recorded:

```bash
python scripts/reconcile_screening.py review/screening_log.csv \
  --records records.deduped.csv \
  -o review/screening.csv \
  --conflicts review/screening_conflicts.json
```

The highest decision stage wins, while the reconciled snapshot separately records `evidence_stage` and highest `access_level`. Same-stage disagreements remain `uncertain`/`unresolved` until an adjudication or final event resolves them. A protocol that requires strict full-text screening needs `evidence_stage=full_text_screened` and `access_level=full_text`; a protocol that allows “full text or most complete accessible record” may use `full_text_attempted`, but the limited access remains visible. Do not silently overwrite one reviewer with another.

## 8. Resolve report-to-study identity

A deduplicated `record_id` is a bibliographic report, not automatically an independent study. `init_review_artifacts.py` creates `review/study_map.csv` with one conservative provisional study per report.

After screening, merge reports under the same `study_id` only when the linkage is supported by concrete evidence such as an explicit version statement, registry/study identifier, verified shared cohort/sample, correction/supplement relation, or authoritative version metadata. Shared authorship/title/topic is not sufficient by itself.

Audit the mapping and produce a study-level summary:

```bash
python scripts/audit_studies.py \
  --records records.deduped.csv \
  --study-map review/study_map.csv \
  --screening review/screening.csv \
  --citation-trail review/citation_trail.csv \
  --evidence review/evidence_table.csv \
  --profile standard \
  --summary review/study_summary.csv \
  --report review/study_audit.json
```

It is acceptable to run this once before evidence extraction and again after citation/version relationships are filled in. Read `references/study_identity.md` for report roles and linkage standards.

## 9. Create candidate topic clusters

Cluster only the included or likely-included records:

```bash
python scripts/cluster_records.py review/screening.csv \
  --records records.deduped.csv \
  -o review/clusters.csv \
  --summary review/cluster_summary.md
```

The script builds deterministic TF-IDF similarity groups from title + abstract and proposes top terms. These are **candidate organizational clusters**, not final scientific themes.

Then review each cluster scientifically: rename it, split mixed clusters, merge near-duplicates, and allow papers to be cross-cutting in the narrative even though the mechanical output assigns one primary cluster.

## 10. Build a claim-level evidence table

Use `review/evidence_table.csv`. Minimum provenance for a substantive row:

- `source_id`
- `study_id` from `review/study_map.csv`
- `source_version` when material
- unique `claim_id`
- research-question component
- study/method/context
- comparator/outcome/metric when relevant
- `reported_result`
- uncertainty/variance when reported
- authors' interpretation
- reviewer interpretation
- limitations
- `evidence_location`
- `support_level`
- `verification_status`
- descriptive evidence-strength note

Use one row per evidence unit when necessary. Do not compress conflicting outcomes from one paper into a vague summary.

`support_level` distinguishes direct source support from reviewer derivation/context. `verification_status` prevents a snippet-derived impression from masquerading as fully checked evidence.

Read `references/evidence_and_synthesis.md` before cross-paper conclusions.

## 11. Build and verify the citation trail

Use `review/citation_trail.csv`.

Allowed edge types:

- `backward_reference`: source paper references target paper;
- `forward_citation`: source paper is cited by target paper;
- `same_study_version`: records are verified versions of the same underlying study/work;
- `companion`: paper explicitly points to a companion/supplement/benchmark paper;
- `discovery_from`: target was discovered from source through a documented bibliographic/citation interface.

Each edge includes `verification_source` and, when possible, `verification_url` or another concrete locator.

Audit it:

```bash
python scripts/audit_citation_trail.py review/citation_trail.csv \
  --records records.deduped.csv \
  --report review/citation_trail_audit.json \
  --dot review/citation_trail.dot
```

Never infer citation edges from topical similarity, shared authorship, or chronology.

## 12. Build synthesis claims without breaking provenance

Do not jump directly from the evidence table to free-form prose. Create a second provenance layer:

- `review/synthesis_claims.csv` — one row per cross-paper conclusion;
- `review/synthesis_evidence.csv` — links each conclusion to evidence `claim_id`s using `supports`, `contradicts`, `qualifies`, or `context`.

Use `evidence_state` values such as `consistent`, `mixed`, `single_study`, `gap`, or `descriptive`. `single_source` remains supported for legacy report-level analyses, but prefer `single_study` when a study map exists.

Audit:

```bash
python scripts/audit_synthesis.py \
  --evidence review/evidence_table.csv \
  --claims review/synthesis_claims.csv \
  --links review/synthesis_evidence.csv \
  --study-map review/study_map.csv \
  --report review/synthesis_audit.json \
  --update-claims
```

For each major conclusion distinguish convergence, disagreement, boundary conditions, methodological differences, population/dataset differences, temporal/version differences, and evidence gaps. When a study map exists, independence is counted by distinct `study_id`, not publication count. For state validation, only evidence rows with `support_level` = `direct` or `derived` and `verification_status` = `verified` or `partial` count as substantive support/contradiction. `contextual`, `unclear`, or `unverified` rows may still be linked for framing, but they cannot manufacture convergence. If disagreement cannot be explained from the evidence, preserve it rather than manufacturing a reconciliation. `audit_synthesis.py` also derives `verification_coverage` per synthesis claim: `complete` (all substantive evidence verified), `mixed` (verified + partial), `partial_only`, or `not_applicable`. With `--update-claims`, it persists that value plus verified/partial evidence counts and eligible supporting/contradicting unit counts directly into `synthesis_claims.csv`. These fields do not change the evidence state; they expose how completely the substantive evidence was verified and make the claim ledger itself self-describing.

Prefer “In the included studies…” over universal claims when search coverage is limited.

## 13. Run cross-artifact preflight before delivery

```bash
python scripts/preflight.py \
  --protocol protocol.json \
  --records records.deduped.csv \
  --screening review/screening.csv \
  --screening-log review/screening_log.csv \
  --study-map review/study_map.csv \
  --evidence review/evidence_table.csv \
  --citation-trail review/citation_trail.csv \
  --search-log search_log.csv \
  --synthesis-claims review/synthesis_claims.csv \
  --synthesis-evidence review/synthesis_evidence.csv \
  --report review/preflight.json
```

Preflight checks include:

- protocol completeness appropriate to profile;
- duplicate stable identifiers among canonical records;
- final screening uniqueness, exclusion reasons, unresolved conflict flags, evidence stage, and access level;
- screening-log referential integrity, true full-text semantics, and copied pseudo-full-text warnings when supplied;
- deterministic protocol exclusions taking precedence over final `uncertain`;
- complete report-to-study mapping for standard/systematic work;
- multi-report study linkage basis and verification status;
- agreement between study map, evidence `study_id`, and `same_study_version` edges;
- unique evidence claim IDs and source references;
- evidence extracted from excluded records;
- included records with no evidence rows;
- citation-trail IDs, relation types, and verification fields;
- search-log query/source execution status, successful/partial/failed source coverage, marginal-yield completeness, and stopping-rule verifiability;
- synthesis links back to evidence claim IDs and independent-study counts;
- count consistency across records and screening.

Run dedicated audits before preflight when their artifact exists. Fix deterministic failures before presenting conclusions.

## 14. Reconcile counts before reporting a flow

Generate a machine-readable flow/count report:

```bash
python scripts/build_flow_report.py \
  --search-log search_log.csv \
  --records records.deduped.csv \
  --dedup-report dedup_report.json \
  --screening review/screening.csv \
  --screening-log review/screening_log.csv \
  --study-map review/study_map.csv \
  --evidence review/evidence_table.csv \
  --synthesis-claims review/synthesis_claims.csv \
  --synthesis-evidence review/synthesis_evidence.csv \
  --out review/flow_report.json
```

This distinguishes summed search hits, imported records, canonical reports, included reports, included studies, evidence claims, and synthesis claims. It intentionally does **not** label itself a PRISMA flow diagram: a count-reconciliation report is not proof that all PRISMA reporting requirements or database-specific retrieval steps were satisfied.

## 15. Build structured downstream views

After synthesis audit and preflight, create two deterministic routing artifacts without adding new scientific claims:

```bash
python scripts/build_evidence_graph.py \
  --records records.deduped.csv \
  --screening review/screening.csv \
  --study-map review/study_map.csv \
  --evidence review/evidence_table.csv \
  --citation-trail review/citation_trail.csv \
  --synthesis-claims review/synthesis_claims.csv \
  --synthesis-evidence review/synthesis_evidence.csv \
  --clusters review/clusters.csv \
  --out review/evidence_graph.json

python scripts/build_synthesis_brief.py \
  --evidence review/evidence_table.csv \
  --claims review/synthesis_claims.csv \
  --links review/synthesis_evidence.csv \
  --records records.deduped.csv \
  --study-map review/study_map.csv \
  --out review/synthesis_brief.md
```

`evidence_graph.json` exposes report -> study -> evidence -> synthesis provenance plus verified citation/version edges and optional topic-cluster membership. `synthesis_brief.md` is a human-readable rendering of the same recorded claim ledger. Neither tool may infer missing citation, causal, study-identity, or agreement relationships.

Read `references/downstream_handoff.md` before sending review outputs into another AutoSCI skill.

## 16. Validate the workspace contract and migrate legacy workspaces conservatively

New workspaces created by `init_review_artifacts.py` contain `review/workspace_meta.json` declaring `autosci-literature-research-workspace-v2`. The current structural contract lives in `schemas/workspace-v2.json`; `schemas/workspace-v1.json` remains available for v1.5 workspaces. It defines minimum CSV headers and JSON keys while allowing compatible extensions.

Before freezing a stable standard/systematic workspace, run:

```bash
python scripts/validate_workspace.py \
  --root . \
  --require-final \
  --report review/schema_audit.json
```

This is structural validation, not scientific validation. Keep running the domain audits and `preflight.py`; neither layer replaces the other.

For a v1 workspace or an older unversioned workspace, preview migration first:

```bash
python scripts/migrate_workspace.py --root .
```

Only after reviewing the plan:

```bash
python scripts/migrate_workspace.py --root . --apply
```

Migration preserves existing values, appends missing required CSV columns as blanks rather than guessing content, adds an empty deterministic-rule list when absent, backs up files before rewriting, and records migration history. Legacy `stage=full_text` entries are intentionally left ambiguous and require manual relabeling; migration never promotes them to `full_text_screened`. Rerun schema validation and scientific QA after any migration. Read `references/workspace_schema_and_migration.md` for compatibility policy.

## 17. Freeze and verify a review snapshot for handoff

For a stable milestone, archive, collaborator handoff, or final review package, first ensure `review/preflight.json` passes, generate the structured downstream views when applicable, then fingerprint the standard workspace artifacts and the exact skill package used:

```bash
python scripts/snapshot_review.py \
  --root . \
  --manifest review/review_manifest.json \
  --require-preflight

python scripts/verify_snapshot.py review/review_manifest.json --root .
```

The manifest stores SHA-256 hashes for existing standard artifacts, protocol identity/version metadata, and a digest of the `literature-research` skill package. If any frozen artifact or the skill implementation changes, verification fails. Create a new snapshot after intentional edits; do not overwrite history and pretend the earlier snapshot still applies. Read `references/reproducibility_and_flow.md` when handoff, archival, living-review updates, or count reporting matters.

## 18. Build a downstream handoff bundle

After snapshot verification, create a compact bundle for another workflow:

```bash
python scripts/build_handoff_bundle.py \
  --root . \
  --outdir handoff/literature-review \
  --target generic
```

Supported targets are `generic`, `scientific-figure`, and `academic-research-presentation`. Target choice adds routing guidance only; it does not rewrite claims or alter evidence. Frozen handoff is preferred. Use `--allow-unfrozen` only for an explicitly provisional working transfer.

The handoff carries provenance, not permission to reproduce copyrighted source figures/full text. Downstream work must preserve scope, caveats, evidence-state distinctions, and source traceability.

## 19. Deliverables

For `standard`, the recommended package is:

- `protocol.json`
- `search_log.csv`
- `review/search_audit.json`
- `records.normalized.csv`
- `records.deduped.csv`
- `dedup_report.json`
- `review/screening_log.csv` when multi-stage/reviewer screening is used
- `review/screening.csv`
- `review/screening_conflicts.json` when reconciliation is used
- `review/study_map.csv`
- `review/study_summary.csv` + `review/study_audit.json`
- `review/clusters.csv` + `review/cluster_summary.md`
- `review/evidence_table.csv`
- `review/citation_trail.csv` + audit output
- `review/synthesis_claims.csv`
- `review/synthesis_evidence.csv` + synthesis audit
- `review/preflight.json`
- `review/workspace_meta.json` + `review/schema_audit.json`
- `review/flow_report.json`
- `review/evidence_graph.json`
- `review/synthesis_brief.md`
- `review/review_manifest.json` for stable handoff/archive milestones
- optional downstream `handoff/` bundle
- final narrative synthesis/report

For `exploratory`, use only the artifacts needed for the question, but preserve enough provenance to avoid presenting guesses as verified literature facts.

For `systematic`, retain the complete protocol/search/screening history and explicitly describe deviations, inaccessible full text, unresolved uncertainties, and coverage limitations.

## Resource routing

Load detail only when needed:

- search design / coverage / stopping -> `references/search_strategy.md`
- dedup / version families / screening history / conflicts -> `references/screening_dedup.md`
- report identity vs underlying study identity -> `references/study_identity.md`
- topic clustering -> `references/clustering.md`
- evidence extraction / claim-level synthesis -> `references/evidence_and_synthesis.md`
- citation edge semantics -> `references/citation_trail.md`
- hard failures / count reconciliation -> `references/quality_assurance.md`
- reproducible handoff / flow report / frozen snapshot -> `references/reproducibility_and_flow.md`
- downstream evidence graph / synthesis brief / AutoSCI handoff -> `references/downstream_handoff.md`
- workspace schema / legacy migration / compatibility -> `references/workspace_schema_and_migration.md`

Execute deterministic scripts without reading their source unless modification or debugging is required.
