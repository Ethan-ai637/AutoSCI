# Citation audit

## Objective

Check citation integrity without pretending to know the content of sources that were not inspected.

# Verification levels

## Level 1 — manuscript-internal checks

Can be performed from the manuscript alone.

### Placement
- Citation should be close enough to identify which claim it supports.
- A citation at the end of a multi-clause sentence may not support every clause.
- Poor placement should not make a prior-work citation appear to support the authors' new result.

### Coverage
Look for claims likely requiring external support:
- historical/factual claims;
- dataset provenance;
- prior method descriptions;
- novelty/first claims;
- benchmark/protocol provenance;
- external numerical facts;
- claims about prior limitations or consensus.

Do not demand citations for the manuscript's own newly reported results.

### Reference integrity
When visible:
- in-text citation has a reference-list entry;
- reference-list entry is cited in text where required by style/context;
- numbering/year/author form is internally consistent;
- duplicates are not accidentally split;
- figure/table sources are cited where needed.

## Level 2 — metadata verification

If external lookup is available and scientifically useful, verify:
- title;
- authors;
- venue;
- year;
- DOI/arXiv/identifier;
- whether the cited version is the intended work.

Report metadata mismatch separately from semantic-support mismatch.

## Level 3 — semantic support verification

Only after inspecting the cited source itself, assess whether it supports the local claim.

Record what was inspected: abstract only, relevant section, results, methods, or full paper.

Classify semantic support only when enough of the source was actually inspected:
- `supports directly`;
- `supports partially / narrower scope`;
- `background only`;
- `does not support local claim`;
- `contradicts local claim`.

If the source cannot be inspected sufficiently, use manuscript evidence state `unavailable_to_verify` and report it as a **coverage gap**, not as a semantic-support finding.

### Entailment discipline

Ask:
1. What exact proposition is the manuscript attributing to the source?
2. Does the inspected source explicitly state or demonstrate that proposition?
3. Is the manuscript broadening population/domain/causality/time/scope?
4. Is the source primary evidence, a review, a commentary, or a secondary citation?
5. Did the source evaluate the same object/setting implied by the manuscript?
6. Is the inspected source the primary work/version actually intended by the citation, or a secondary/older/different version?

Do not upgrade “related background” to “supports directly”.

# Common citation problems

### Citation laundering
A secondary/review source is used for a strong primary empirical fact when primary evidence is expected.
Treat as context-dependent, not automatically wrong. When precise attribution matters, record primary vs secondary source provenance.

### Scope laundering
The source supports a narrower claim while the manuscript states a broader one.

### Causal laundering
The source reports association/observation but the manuscript cites it for a causal claim.

### Multi-citation bundle ambiguity
A cluster such as `[3–12]` follows a precise claim, but it is unclear which source supports which component.
Flag only when this materially blocks verification or creates misattribution risk.

### Novelty claim
“First”, “no prior work”, “unique” requires literature-wide evidence. A manuscript-internal review cannot prove novelty.
Without a dedicated literature search, mark `not verified`, not false.

### Abstract-only limitation
An abstract may be enough to verify broad metadata or a clearly stated headline result, but not fine-grained methods/results claims absent from the abstract. Do not overstate Level 3 confidence from partial source access.

# External-search priority

When citation verification is selective, prioritize:
1. sources supporting central novelty claims;
2. sources supporting strong causal/generalization/safety claims;
3. citations used to justify benchmark/protocol choices;
4. citations whose alleged result materially affects interpretation;
5. suspicious metadata or unusually precise external facts.


# Disposition rule

- Verified metadata/placement/reference-integrity defects -> `finding`.
- Verified semantic mismatch after source inspection -> `finding`.
- Material ambiguity in which citation supports which proposition -> `author_query` when more than one plausible mapping survives.
- Source inaccessible or insufficiently readable for semantic verification -> `coverage_gap`.

Do not assign Major/Moderate severity to a coverage gap merely because the attributed claim is important. Importance may affect verification priority, not whether an unverified claim becomes an error.
