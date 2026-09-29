# Reproducibility, Flow Counts, and Frozen Snapshots

## Why this layer exists

A literature review can be internally consistent yet still be difficult to hand off because collaborators cannot tell which protocol version, search log, screening state, evidence table, or synthesis file produced the conclusions they received.

Use three separate ideas:

1. **count reconciliation** — confirm that the workspace's reported counts make sense together;
2. **workspace-schema validation** — confirm that the files expose the minimum structural fields expected by this workflow version;
3. **snapshot verification** — confirm that the files being inspected are byte-for-byte the files that were frozen at a named milestone.

None proves scientific correctness or exhaustive database coverage. Structural compatibility and scientific validity are deliberately separate.

## Protocol identity

For standard/systematic work, prefer a stable local `protocol_id`, a human-readable `protocol_version`, and `created_at`. When eligibility criteria, target sources, outcomes, or synthesis rules change materially, increment the version and append a structured `protocol_changes` record with:

- `changed_at`;
- `field`;
- `rationale`;
- optionally old/new values and who authorized the change.

Do not silently rewrite protocol history after seeing results.

## Flow/count reconciliation

`build_flow_report.py` keeps distinct quantities distinct:

- summed search hits across query rows;
- imported records;
- deduplication input records;
- canonical bibliographic reports;
- final screening decisions;
- included reports;
- included underlying studies;
- evidence claims;
- synthesis claims and links.

Search-hit totals can overlap heavily across queries and databases, so they are reported as sums rather than unique-record counts. Missing counts stay missing rather than being imputed.

The flow report is **not automatically a PRISMA flow diagram**. PRISMA reporting can require additional distinctions such as records removed before screening, reports sought/retrieved, reports not retrieved, and identification through other methods. Use the deterministic flow report as a reconciliation substrate, then prepare any framework-specific reporting explicitly.

## Frozen review snapshots

After preflight and workspace-schema validation pass, run `snapshot_review.py --require-preflight`. Versioned workspaces must have a current passing `review/schema_audit.json`; the manifest fingerprints all existing standard artifacts plus the exact `literature-research` package implementation.

The manifest records:

- timestamp;
- skill version and package digest;
- protocol identity/version/profile/question;
- workspace schema identity;
- relative artifact paths;
- SHA-256 hashes;
- byte sizes.

`verify_snapshot.py` recomputes those values. A changed or missing artifact fails verification. A different skill package also fails unless `--ignore-skill-package` is explicitly used.

## Living reviews and updates

Do not reuse an old manifest after a scheduled literature update. Preserve the old manifest as a milestone, run the new searches, reconcile screening/studies/evidence/synthesis, rerun QA, and create a new manifest. The pair of manifests then gives a clean boundary between review states.

A manifest should never be described as evidence that external databases are immutable. Search providers can reindex content, change metadata, or alter ranking after the recorded search date. Exact query/source/date logs remain essential.
