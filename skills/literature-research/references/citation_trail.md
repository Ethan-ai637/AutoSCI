# Citation Trail

## Why keep a trail

A citation trail explains how the review moved from seed literature to later evidence and lets another researcher audit discovery paths.

## Edge direction

- `backward_reference`: `source_id -> target_id` means the source paper's reference list points to the target paper.
- `forward_citation`: `source_id -> target_id` means the target paper cites the source paper.
- `discovery_from`: `source_id -> target_id` means the target record was discovered while inspecting the source through a documented search/citation interface. This does not itself assert a formal citation.
- `same_study_version`: source and target are verified versions of the same underlying work/study. When `study_map.csv` exists, both reports must map to the same `study_id`.
- `companion`: source explicitly identifies target as a companion, supplement, benchmark, dataset, or paired paper.

## Verification

Prefer direct verification from:

- paper reference list/full text;
- publisher bibliographic page;
- DOI metadata/citation service;
- trusted scholarly index with citation relation;
- explicit author/project page for companion/version relations.

Record `verification_source`, `verification_url` when available, and `verified_at`.

## What not to do

Do not infer a citation edge from topical similarity, shared authorship, or chronological plausibility. If two papers are related but the exact relation is unknown, describe that relation in notes rather than inventing an edge type.
