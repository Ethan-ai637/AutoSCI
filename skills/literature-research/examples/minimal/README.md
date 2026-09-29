# Minimal example

From the `literature-research` directory:

```bash
python scripts/normalize_records.py examples/minimal/raw_records.csv -o /tmp/records.normalized.csv
python scripts/deduplicate_records.py /tmp/records.normalized.csv -o /tmp/records.deduped.csv --report /tmp/dedup_report.json
python scripts/init_review_artifacts.py /tmp/records.deduped.csv --outdir /tmp/review
# fill /tmp/review/screening_log.csv, then reconcile it
python scripts/reconcile_screening.py /tmp/review/screening_log.csv --records /tmp/records.deduped.csv -o /tmp/review/screening.csv --conflicts /tmp/review/screening_conflicts.json
# review /tmp/review/study_map.csv before treating multiple reports as independent studies
python scripts/audit_studies.py --records /tmp/records.deduped.csv --study-map /tmp/review/study_map.csv --screening /tmp/review/screening.csv --profile standard --summary /tmp/review/study_summary.csv --report /tmp/review/study_audit.json
python scripts/cluster_records.py /tmp/review/screening.csv --records /tmp/records.deduped.csv -o /tmp/review/clusters.csv --summary /tmp/review/cluster_summary.md
```

The first two input rows should collapse to one canonical DOI record. For a complete executable fixture covering search audit, screening reconciliation, report-to-study identity, study-aware synthesis provenance, citation audit, and preflight, run:

```bash
python scripts/self_test.py
```
