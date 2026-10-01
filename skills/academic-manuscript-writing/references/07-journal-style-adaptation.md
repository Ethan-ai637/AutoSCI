# Journal / venue style adaptation (v2 compatibility note)

In v2.0, venue style is no longer treated as a late, static “journal formatting” step.

Use:

- `references/20-dynamic-writing-profile.md` for runtime retrieval of discipline/article-type/venue/year/submission-stage guidance;
- `references/21-manuscript-contract.md` for converting that guidance into the operational manuscript contract.

This file remains as a compatibility reminder for older workflows.

## Stable rule

Formatting and venue conventions may alter presentation, structure, length, ordering, terminology, and submission packaging. They must not alter scientific evidence, numbers, claim strength, study scope, or required limitations.

## If no specific target exists

Use a neutral scientific style and set `writing_context.target_specificity` to `generic` or `discipline`. Do not invent a journal/conference profile.

## If a specific target exists

Retrieve the current official rules for the exact venue, year, article type, and submission stage. Record source provenance and build `writing_profile.json` plus `manuscript_contract.json` before claiming venue readiness.
