# Topic Clustering

## Purpose

Clustering is for corpus navigation and synthesis structure. It is not a relevance filter, quality score, or substitute for scientific reading.

## Mechanical candidate clusters

`scripts/cluster_records.py` uses title + abstract text, TF-IDF weighting, cosine similarity, and a deterministic similarity graph. Connected components become candidate clusters. Very weakly connected records may remain singleton clusters.

Top terms are lexical cues, not final theme names.

## Review protocol

For each candidate cluster:

1. inspect several representative titles/abstracts;
2. assign a scientific theme name;
3. split if the cluster contains two distinct research questions;
4. merge clusters if they differ only by terminology;
5. identify cross-cutting papers in notes even though the CSV gives one primary cluster.

## Common failure modes

- methods and application domains get mixed because they share vocabulary;
- review papers connect otherwise distinct topics;
- generic terms (“model”, “study”, “analysis”) dominate small corpora;
- very short abstracts create singleton clusters;
- older/newer terminology splits one intellectual theme.

Use clustering as a map, not as a conclusion.
