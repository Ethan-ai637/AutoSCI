# Downstream Handoff

`literature-research` should hand off **structured provenance**, not an untraceable prose summary.

## Three downstream views

1. `review/synthesis_brief.md` — human-readable claim ledger generated only from recorded synthesis/evidence rows. It adds no new interpretation.
2. `review/evidence_graph.json` — machine-readable graph linking reports, underlying studies, evidence claims, synthesis claims, verified citation/version edges, and optional topic clusters.
3. a handoff bundle — a compact copy of audited artifacts plus routing notes for another AutoSCI workflow.

Generate the graph and brief before freezing a stable milestone:

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

Then freeze and verify the workspace. Build a downstream bundle only after preflight passes; frozen handoff is preferred. The bundle builder re-checks frozen artifact hashes and the skill-package digest before packaging:

```bash
python scripts/build_handoff_bundle.py --root . --outdir handoff/review --target generic
```

Targets `scientific-figure` and `academic-research-presentation` add routing guidance but do not alter scientific content.

## Safety boundary

The graph serializes only relationships already recorded in review artifacts. It must never infer an unverified citation, study identity, causal relationship, or agreement relationship.

The synthesis brief is not a new literature review. It is a deterministic rendering of the existing claim ledger. Exact values, quotes, and causal wording still require verification against the recorded evidence locator and, when appropriate, the original source.

A handoff bundle carries provenance, not reproduction rights. Original source figures/tables/full text remain subject to their licenses and permissions.
