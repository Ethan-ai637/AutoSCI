# Source grounding and authority

## Goal

Prevent fluent manuscript prose from outranking the actual research artifacts.

## Build a source inventory first

For every input, identify:

- what it is;
- which scientific facts it can authoritatively support;
- whether it is canonical, derived, provisional, or contextual;
- version/date when known;
- whether another artifact conflicts with it.

## Default authority logic

Use explicit user-declared authority when available. Otherwise prefer validated analysis/result artifacts over derived visuals and prose. Existing manuscript text is usually a downstream artifact, not the scientific source of truth.

A figure can be authoritative for visible structure or qualitative pattern, but exact numeric reporting should prefer the underlying validated data/statistical result when available.

## Conflict handling

When two authoritative-looking sources disagree:

1. do not choose the more convenient value;
2. record the conflict;
3. identify whether the disagreement is versioning, population, preprocessing, model, endpoint, rounding, or error;
4. classify the conflict disposition before release: `blocking`, `disclose_and_scope`, `historical_only`, or `resolved`;
5. keep affected claims blocked unless the conflict is explicitly eligible for `disclose_and_scope` and the manuscript preserves source-specific values plus an auditable disclosure.

See `16-source-conflict-disposition.md` for release rules. Legacy free-text conflicts remain blocking.

## Missing evidence

Use explicit markers such as `[METHOD DETAIL NEEDED]`, `[VERIFY VALUE]`, or `[CITATION NEEDED]` during draft work. In release work, unresolved markers are failures unless intentionally disclosed outside the manuscript.
