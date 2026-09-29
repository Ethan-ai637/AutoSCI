# Report Identity vs Study Identity

## Why this layer exists

A deduplicated bibliographic record is a **report**, not automatically an independent study.

The same underlying study may produce:

- a preprint and later journal article;
- a conference paper and an expanded journal version;
- a trial protocol and primary results paper;
- primary and secondary analyses of one cohort;
- follow-up papers using the same participants/data collection;
- a main paper plus supplement/correction/companion report.

Counting those reports as independent evidence can create false replication and overstate convergence.

## Artifact

Use `review/study_map.csv` with one row per canonical `record_id`:

- `record_id`: report/bibliographic record;
- `study_id`: underlying study/research unit;
- `report_role`: role of this report within that study;
- `linkage_basis`: concrete reason reports were grouped;
- `verification_status`: `provisional`, `verified`, `partial`, or `unverified`;
- `notes`: ambiguity or scope-specific details.

Initialization creates one provisional study per report. This is conservative. Merge two or more reports under one `study_id` only when the linkage is supported.

## Allowed report roles

Recommended values:

- `primary_or_only_report`
- `primary_report`
- `secondary_analysis`
- `follow_up`
- `protocol`
- `preprint_version`
- `conference_version`
- `journal_version`
- `supplement`
- `correction`
- `companion`
- `unknown`

Roles describe the report, not its scientific quality.

## Strong linkage evidence

Useful bases include:

- explicit statement that one report is a version/extension of another;
- shared trial/registry identifier;
- explicit shared cohort/sample with matching recruitment dates/sites;
- publisher/author metadata linking versions;
- correction/supplement links;
- exact study identifiers reported by the source.

Shared authors, similar titles, same institution, same dataset name, or close dates are useful clues but are not by themselves sufficient for a verified multi-report grouping.

## Relationship to deduplication

Deduplication answers: **are these effectively the same bibliographic record for this workflow?**

Study mapping answers: **do these distinct reports draw on the same underlying study/research unit?**

Do not force study-level relationships into deduplication. Preserve materially distinct reports, then group them at the study layer when verified.

## Relationship to citation trail

A verified `same_study_version` citation-trail edge should agree with `study_map.csv`: both reports must share the same `study_id`.

Not every same-study relationship requires a formal citation edge. Secondary analyses may share a study without directly citing each other. Record the grouping basis in `study_map.csv`.

## Synthesis rule

When a study map is available, claims such as `consistent` must be supported by at least two **distinct studies**, not merely two source records.

Two reports from one study can strengthen extraction or provide complementary outcomes, but they do not constitute independent replication.
