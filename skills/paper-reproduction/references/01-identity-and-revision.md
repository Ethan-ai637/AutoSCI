# Identity and Revision Resolution

## Goal

Establish which paper version, repository, and repository revision the reproduction actually concerns.

## Repository identity evidence

Prefer evidence in this order when available:

1. repository URL explicitly linked by the paper/supplement/artifact appendix;
2. official project page linking both paper and repository;
3. publisher or artifact-evaluation page linking the repository;
4. author/organization repository that explicitly cites the paper identifier;
5. repository README/citation metadata that matches title/authors/identifier;
6. weaker contextual evidence such as naming similarity.

Do not classify a repository as official from naming similarity alone.

Recommended `official_status` values:

- `author_official`
- `publisher_official`
- `artifact_evaluation`
- `linked_project`
- `third_party`
- `unknown`

Always retain `identity_evidence[]` with URLs/locators and notes.

## Paper version resolution

Record the exact scientific source used for implementation details. Distinguish:

- conference publication;
- journal extension;
- arXiv revisions;
- accepted manuscript;
- supplement;
- correction/erratum.

If Table 2 differs between arXiv v1 and v3, the target claim must identify the version.

## Revision selection

Strongest revision anchors:

- commit SHA stated in the paper/artifact documentation;
- release/tag explicitly tied to the paper;
- archived artifact snapshot;
- publication-era release with matching instructions;
- commit near publication date supported by repository history;
- current head only as an explicitly labeled fallback.

Never rewrite history by calling current `main` the paper implementation when the repository changed materially later.

## Source state vs execution state

Record both:

- `source_revision`: pinned upstream commit/release;
- `execution_state`: clean or patched worktree actually executed.

If patches are required, save the patch and hash it. The run is no longer an unmodified baseline even if the upstream commit is unchanged.
