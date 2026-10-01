# Dynamic writing profile

## Purpose

`academic-manuscript-writing` v2 does not permanently encode the rules of ICML, NeurIPS, ACL, Nature, a society journal, or any other venue. Venue rules are time-sensitive and submission-stage-sensitive. The skill defines the retrieval and normalization protocol; the model retrieves the applicable current rules at execution time.

The stable interface is:

`writing_context -> writing_sources.jsonl -> writing_profile.json -> manuscript_contract.json`

Scientific evidence remains separate:

`sources.jsonl -> evidence.jsonl -> claims.jsonl -> manuscript`

A writing guideline can constrain how a claim is presented. It cannot make a scientific claim true.

## 1. Resolve the writing context

Record `project.json.writing_context` before venue-specific planning:

```json
{
  "discipline": "computer_science",
  "subfield": "machine_learning",
  "article_type": "conference_paper",
  "venue": "TARGET_VENUE",
  "track": "main",
  "venue_year": 2030,
  "submission_stage": "initial_submission",
  "target_specificity": "venue",
  "language": "en"
}
```

`target_specificity` means:

- `generic`: no discipline/venue-specific readiness claim;
- `discipline`: writing conventions are specialized to a discipline/article type but not a named venue;
- `venue`: a named venue/year/stage must be resolved from current applicable guidance.

Do not infer a venue that the user did not select. If venue or year is unknown, remain at `generic`/`discipline` readiness or explicitly report the missing target.

## 2. Retrieve writing guidance dynamically

For a venue target, prefer sources in this order:

1. official author/submission guidelines for the target venue/year/stage;
2. official manuscript/template/style documentation;
3. official checklist, reproducibility, ethics, artifact, supplement, rebuttal, or camera-ready instructions;
4. official publisher/professional-society guidance delegated by the venue;
5. secondary guidance only to locate official material or label a non-binding convention.

Search for the specific **article type, track (when applicable), year, and stage**. Initial submission, rebuttal, revision, camera-ready, proceedings production, and journal resubmission may have different rules.

Do not use a prior-year page limit, anonymity rule, appendix rule, or checklist requirement merely because it is familiar.

## 3. Register writing sources separately

Use `writing_sources.jsonl`, not `sources.jsonl`, for venue/style guidance.

Recommended record:

```json
{
  "writing_source_id": "WS001",
  "title": "Target Venue 2030 Author Instructions",
  "url": "https://official.example/...",
  "path": null,
  "authority_level": "official",
  "source_class": "official_author_guidelines",
  "retrieved_at": "2030-01-15T12:00:00+00:00",
  "venue": "Target Venue",
  "discipline": "computer_science",
  "subfield": "machine_learning",
  "applicable_article_types": ["conference_paper"],
  "applicable_tracks": ["main"],
  "applicable_years": [2030],
  "applicable_stages": ["initial_submission"],
  "content_sha256": null,
  "notes": ""
}
```

For venue-specific readiness, record which `applicable_article_types` and, when a target track is set, which `applicable_tracks` the source governs. For a local snapshot, use `path` and optionally `content_sha256`. For a remote source, preserve the exact URL and retrieval timestamp. The workspace state tracks these records independently of scientific sources.

## 4. Normalize rules into atomic constraints

`writing_profile.json` is not copied prose from an author-guideline webpage. It is a source-backed normalization of the rules that matter to the manuscript.

Each constraint should express one operational requirement:

```json
{
  "constraint_id": "WC001",
  "category": "abstract",
  "requirement": "The abstract must not exceed 250 words.",
  "strength": "required",
  "basis": "official_guideline",
  "source_ids": ["WS001"],
  "source_locator": "Abstract requirements",
  "applies_to_stages": ["initial_submission"],
  "verification": "verified"
}
```

Use `strength`:

- `required` — mandatory;
- `recommended` — official or discipline guidance that is not mandatory;
- `prohibited` — explicitly disallowed;
- `informational` — context needed to interpret another rule.

Use `basis`:

- `official_guideline`;
- `official_template`;
- `official_checklist`;
- `discipline_convention`;
- `user_instruction`.

A rule labeled as official must cite an `authoritative `official`/`publisher`/`society`` source. Secondary guidance must not be upgraded to an official requirement.

## 5. Handle writing-guideline conflicts explicitly

Official sources can disagree because one is old, stage-specific, delegated, or updated later.

Record such conflicts in `writing_profile.guideline_conflicts`, including the source IDs and a disposition. A venue-ready release cannot keep a `blocking` writing-guideline conflict unresolved.

Prefer the source that is demonstrably more specific to:

1. the exact venue;
2. the exact year;
3. the exact submission stage;
4. the official submission system/template in force.

Do not resolve a conflict by choosing the rule that makes the manuscript easier to fit.

## 6. Readiness levels

`writing_profile.readiness.level` is one of:

- `generic`;
- `discipline`;
- `venue`.

`venue_ready=true` means only that the writing-profile contract is sufficiently resolved for venue-specific compliance checks. It does **not** mean the science is correct or that the paper will be accepted.

If current official instructions cannot be verified, downgrade readiness instead of inventing them.

## 7. Re-retrieve when the context changes

Re-run retrieval when any of these changes materially:

- venue;
- venue year;
- article type;
- track;
- submission stage;
- official template/checklist release;
- publisher/society instruction source;
- a user-provided authoritative correction.

A change to `writing_profile.json` invalidates `manuscript_contract.json` until the contract is regenerated and its `writing_profile_sha256` is updated.

## 8. Boundary with scientific evidence

Writing-source rules may determine:

- section naming/order;
- word/page limits;
- anonymous-review constraints;
- reference/supplement policy;
- required checklists/artifacts;
- rebuttal/camera-ready packaging;
- preferred terminology/style.

They must not determine:

- which result is scientifically primary when the analysis says otherwise;
- which negative result can be hidden;
- a p-value/effect size/sample size;
- causal language unsupported by design;
- a method detail absent from scientific sources;
- a literature citation not actually retrieved.
