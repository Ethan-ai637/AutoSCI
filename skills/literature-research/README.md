# literature-research

An AutoSCI skill for auditable scientific literature research: search, screen, deduplicate, distinguish reports from underlying studies, cluster, build claim-level evidence tables, trace citation paths, and synthesize without losing provenance.

## Core idea

LLMs are useful for query expansion, relevance judgment, thematic interpretation, evidence extraction, study-linkage judgment, and synthesis. They are much less reliable when asked to remember exact search histories, merge bibliographic records consistently, preserve multi-stage screening decisions, or maintain cross-file referential integrity. This skill separates those responsibilities.

A central rule is that **one paper is not automatically one independent study**. Preprints, journal versions, protocol papers, secondary analyses, and follow-ups may belong to the same underlying study. The workflow therefore keeps report-level `record_id` and study-level `study_id` separate.

```text
research question
      ↓
protocol + search log ──→ search coverage audit
      ↓
retrieved records
      ↓
normalize → deduplicate reports
      ↓
screening log → reconcile conflicts → final screening
      ↓
report-to-study map ──→ study identity audit
      ↓
cluster + claim-level evidence table ↔ citation trail
      ↓
synthesis claims ↔ evidence claim IDs
      ↓
study-aware deterministic audits + preflight
      ↓
count reconciliation → evidence graph + synthesis brief
      ↓
workspace schema validation
      ↓
frozen hash snapshot → downstream handoff bundle
```

## Quick start

```bash
cp templates/protocol.template.json protocol.json
cp templates/search_log.template.csv search_log.csv

python scripts/normalize_records.py exports/*.csv -o records.normalized.csv
python scripts/deduplicate_records.py records.normalized.csv -o records.deduped.csv --report dedup_report.json
python scripts/init_review_artifacts.py records.deduped.csv --outdir review

# Fill search_log.csv with search_status + marginal-yield fields, then audit attempted vs successful coverage and stopping evidence.
python scripts/audit_search.py --protocol protocol.json --search-log search_log.csv --report review/search_audit.json

# Standard/systematic: run the obvious-exclusion gate before manual screening.
# It also derives conservative publication-type exclusions literally named in exclusion_criteria.
python scripts/apply_screening_rules.py --protocol protocol.json --records records.deduped.csv --output review/obvious_exclusions.csv --append-log review/screening_log.csv

# Fill review/screening_log.csv with explicit access_level and full_text_attempted/full_text_screened semantics, then reconcile.
python scripts/reconcile_screening.py review/screening_log.csv --records records.deduped.csv -o review/screening.csv --conflicts review/screening_conflicts.json

# Resolve report-to-study relationships conservatively, then audit them.
python scripts/audit_studies.py \
  --records records.deduped.csv \
  --study-map review/study_map.csv \
  --screening review/screening.csv \
  --citation-trail review/citation_trail.csv \
  --evidence review/evidence_table.csv \
  --summary review/study_summary.csv \
  --report review/study_audit.json

python scripts/cluster_records.py review/screening.csv --records records.deduped.csv -o review/clusters.csv --summary review/cluster_summary.md
python scripts/audit_citation_trail.py review/citation_trail.csv --records records.deduped.csv --report review/citation_trail_audit.json
python scripts/audit_synthesis.py --evidence review/evidence_table.csv --claims review/synthesis_claims.csv --links review/synthesis_evidence.csv --study-map review/study_map.csv --report review/synthesis_audit.json --update-claims

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


# Build deterministic downstream views before freezing a stable milestone.
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
python scripts/build_synthesis_brief.py --evidence review/evidence_table.csv --claims review/synthesis_claims.csv --links review/synthesis_evidence.csv --records records.deduped.csv --study-map review/study_map.csv --out review/synthesis_brief.md

# Validate the structural contract before freezing a versioned workspace.
python scripts/validate_workspace.py --root . --require-final --report review/schema_audit.json

python scripts/snapshot_review.py --root . --manifest review/review_manifest.json --require-preflight
python scripts/verify_snapshot.py review/review_manifest.json --root .

# Optional: prepare a compact package for the next AutoSCI workflow.
python scripts/build_handoff_bundle.py --root . --outdir handoff/literature-review --target generic
```

The scripts use only the Python standard library. `audit_synthesis.py` counts only direct/derived and verified/partial evidence as substantive support or contradiction for evidence-state checks; contextual or unverified links remain provenance but cannot create false convergence. It separately reports claim-level verification coverage so `consistent` does not imply every supporting source was fully verified.

## Downstream interoperability

`review/evidence_graph.json` is the machine-readable provenance view; `review/synthesis_brief.md` is a deterministic human-readable claim ledger. A handoff bundle can be targeted to `scientific-figure` or `academic-research-presentation` for routing guidance without changing scientific content. See `references/downstream_handoff.md`.

## Workspace compatibility

New v1.6 workspaces declare `autosci-literature-research-workspace-v2` in `review/workspace_meta.json`. `schemas/workspace-v2.json` adds explicit search execution status, marginal-yield/stopping evidence, and full-text access-stage semantics; `workspace-v1.json` remains supported for v1.5 workspaces. Structural schema validation is separate from scientific QA: a schema-valid workspace can still fail search, screening, study-identity, evidence, or synthesis audits.

For v1 workspaces or older unversioned workspaces, preview a conservative migration with `python scripts/migrate_workspace.py --root .`; add `--apply` only after reviewing the proposed actions. Migration can append missing structural columns with blank values and add schema metadata, but it never invents scientific judgments. See `references/workspace_schema_and_migration.md`.
