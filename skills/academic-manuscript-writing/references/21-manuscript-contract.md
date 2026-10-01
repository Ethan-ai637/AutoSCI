# Manuscript contract

## Purpose

`manuscript_contract.json` is the operational bridge between a runtime writing profile and the actual paper. It exists because raw venue instructions are often heterogeneous: some rules are structural, some are formatting constraints, some are manual checks, and many are stage-specific.

The contract is generated **for the current project context**. It is not a reusable hard-coded template for a venue.

## 1. Contract identity and staleness

Minimum structure:

```json
{
  "schema_version": 1,
  "contract_status": "verified",
  "context": {},
  "writing_profile_sha256": "...",
  "enforce_section_order": true,
  "sections": [],
  "rules": [],
  "machine_checks": [],
  "manual_checks": [],
  "unresolved_items": []
}
```

The `context` must match `project.json.writing_context`.

`writing_profile_sha256` must equal the current `writing_profile.json` hash when the policy requires profile/contract binding. If the profile changes, the old contract becomes stale even if the manuscript text did not change.

A venue-specific release requires `contract_status=verified` and no unresolved contract items.

## 2. Sections are profile-driven

Do not assume that all manuscripts use the same IMRaD section set.

Each contract section can declare:

```json
{
  "name": "Results",
  "presence": "required",
  "claim_coverage": "required",
  "scientific_roles": ["results"],
  "purpose": "Primary empirical findings",
  "constraint_ids": ["WC003"]
}
```

`presence`:

- `required`;
- `optional`;
- `forbidden`.

`scientific_roles` maps the **actual venue section name** to one or more scientific functions (`abstract`, `methods`, `results`, `discussion`, etc.). This keeps claim-family/reporting semantics working when a venue uses headings such as `Experiments`, `Evaluation`, or a combined `Results and Discussion`.

`claim_coverage`:

- `required` — the section participates in claim/coverage closure;
- `optional` — claims may appear but coverage is not structurally required;
- `none` — front matter or other non-claim section.

Sections with `claim_coverage=required` must also be represented in `section_plan.json` and `project.coverage_policy.required_sections` for release.

A venue may combine or rename scientific functions. Preserve the underlying scientific boundaries even when headings differ.

## 3. Rules and provenance

Every venue-derived contract rule should cite the `constraint_id` records that justify it.

```json
{
  "rule_id": "MR001",
  "scope": "Abstract",
  "rule": "Use an unstructured abstract.",
  "strength": "required",
  "constraint_ids": ["WC007"]
}
```

User-requested constraints may be represented by a `user_instruction` writing-profile constraint rather than pretending the venue requires them.

## 4. Generic machine checks

v2.0 intentionally supports only a small venue-agnostic set of deterministic checks:

- `section_presence`;
- `section_absence`;
- `section_order`;
- `max_words`.

Example:

```json
{
  "check_id": "MC001",
  "type": "max_words",
  "section": "Abstract",
  "max_words": 250,
  "constraint_ids": ["WC001"]
}
```

Do not encode a venue-specific parser into the skill merely because a venue has a one-off formatting rule. Put non-generic requirements in `manual_checks`.

## 5. Manual checks are first-class

Some requirements cannot be safely inferred by a simple text parser, for example:

- double-blind deanonymization risk;
- whether supplementary files reveal author identity;
- template typography/line-number compliance;
- artifact/reproducibility forms;
- ethics/data statements whose applicability depends on the study;
- submission-system fields;
- PDF visual overflow.

Represent these explicitly:

```json
{
  "check_id": "MN001",
  "rule": "Inspect the submission artifact for author-identifying content.",
  "constraint_ids": ["WC014"],
  "status": "verified",
  "verification_notes": "Checked the submission PDF and supplement."
}
```

A manual check is not “done” merely because it exists in the contract. Use `pending|verified|not_applicable|blocked`. Venue-specific release requires `verified` or a reasoned `not_applicable`; the model/human must actually inspect the relevant artifact before claiming venue readiness.

## 6. Interaction with scientific contracts

The writing contract controls manuscript form. Existing scientific contracts remain authoritative for content:

- `section_plan.json` — scientific coverage;
- `reporting_contracts.jsonl` — result/method/qualifier dependencies;
- `claims.jsonl` — scientific propositions;
- `paragraph_contracts.jsonl` — multi-claim composition;
- claim spans — exact prose ownership.

If the writing profile says a section is absent, relocate valid scientific content without dropping its required claim/reporting dependencies.

Example: if a venue does not use a separate Discussion heading, Discussion-type interpretation/limitations may be integrated into another permitted section, but the corresponding claims and qualifiers must remain traceable.

## 7. Submission-stage transitions

A manuscript can move through:

`preprint -> initial_submission -> rebuttal -> revision -> camera_ready`

Do not assume the same contract applies across stages. A track/article-type or stage transition can change:

- anonymity;
- page limits;
- appendix/supplement rules;
- response/rebuttal limits;
- author metadata;
- checklist requirements;
- formatting/template version.

Update the relevant `writing_context` fields (including `article_type`, `track`, and/or `submission_stage`), re-retrieve the applicable guidance, regenerate the profile/contract, and record the semantic change in revision provenance.

## 8. Release semantics

A normal `release` preflight proves deterministic workspace closure.

A **venue-ready** release additionally requires:

- venue specificity in `writing_context`;
- at least one applicable official writing source when policy requires it;
- resolved writing profile with venue readiness;
- verified non-stale manuscript contract;
- no blocking writing-guideline conflict;
- required/forbidden section checks passing;
- configured machine checks passing;
- manual checks actually reviewed before the user claims final submission readiness.

This is compliance evidence, not an acceptance prediction.
