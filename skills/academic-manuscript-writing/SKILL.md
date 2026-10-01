---
name: academic-manuscript-writing
description: Generate, revise, and audit scientific manuscripts from authoritative experimental results, statistical outputs, figures/tables, methods, research notes, and dynamically retrieved discipline/venue writing requirements. Resolve discipline, article type, optional track, venue, year, and submission stage into a source-backed writing profile and manuscript contract before claiming venue readiness. Preserve claim-to-evidence traceability, numeric fidelity, study-design-appropriate language, null/negative results, cross-section consistency, and writing-guideline provenance. Do not invent experiments, statistics, methods, citations, mechanisms, interpretations, or venue requirements.
---

# Academic Manuscript Writing

Turn research artifacts into a manuscript through an auditable chain:

**writing context -> dynamic writing-guideline retrieval -> source-backed writing profile -> manuscript contract -> scientific source inventory -> evidence ledger -> active/historical claim ledger + claim families -> exact claim spans -> paragraph/section/reporting contracts -> manuscript draft/revision -> revision obligations + semantic-state lineage -> writing-profile/impact/cross-section/manuscript/span/atomicity/composition/locality/lifecycle audit -> release preflight -> frozen handoff**

This is not a general-purpose prose skill. It is a scientific evidence-to-manuscript skill with a dynamic writing-profile interface. The scientific-governance core is stable; discipline-, article-type-, track-, venue-, year-, and submission-stage-specific writing rules are retrieved at runtime instead of being hard-coded into the package.

The model handles scientific synthesis, argument structure, wording, and revision judgment. Deterministic scripts handle identity, provenance, dependency checks, stale-claim detection, numeric-token checks, and package integrity.

## Hard rules

1. **Authoritative evidence beats prose.** When manuscript text conflicts with a supplied result table, statistical output, figure, methods record, or explicit user correction, surface the conflict and revise from the authoritative source.
2. **Do not invent scientific content.** Never fabricate experiments, cohorts, sample sizes, preprocessing, hyperparameters, statistics, effect sizes, p-values, confidence intervals, figure panels, citations, limitations, mechanisms, or explanations.
3. **Every substantive result claim must be traceable.** Results claims require one or more `evidence_id` links in `claims.jsonl`. A claim without evidence is a draft placeholder, not publishable prose.
4. **Numbers are immutable unless the evidence changes.** Preserve sign, magnitude, unit, denominator, uncertainty, comparison direction, timepoint, and analysis population. Do not silently round across a meaningful threshold.
5. **Statistical significance is not effect importance.** Report effect magnitude and uncertainty when available; do not turn `p < 0.05` into “large”, “important”, “robust”, or “clinically meaningful” without support.
6. **Match causal language to design.** Randomized/interventional designs may support causal language only within the design and analysis limits. Observational/correlational evidence defaults to association language. In vitro, simulation, benchmark, animal, or retrospective evidence must not be generalized beyond its studied system without explicit support.
7. **Null and negative results are first-class evidence.** Do not hide, weaken, or rewrite them into positive findings. Distinguish “no evidence of effect” from evidence of equivalence or no effect.
8. **Do not backfill missing Methods.** If a method detail is absent, mark it as missing or ask for the source when necessary; never infer a publishable method from convention alone.
9. **Figures and tables are scientific sources, not decoration.** Reference exact figure/table/panel IDs and state what the visual supports. Do not claim a pattern that is not visible or documented in the underlying data/analysis.
10. **Separate observation from interpretation.** Results states what was measured. Discussion may interpret, contextualize, and qualify it, but must preserve the observation/interpretation boundary.
11. **Literature claims need literature evidence.** Use citations supplied by the user or an upstream literature workflow. Do not invent references, citation metadata, or “well-known” claims. When citations are absent, leave citation placeholders or make the limitation explicit.
12. **Preserve manuscript-wide consistency.** A changed result can affect title, abstract, highlights, Results, Discussion, conclusion, figure captions, tables, supplement, and reviewer-response text. Link cross-section restatements with `claim_family_id` and run dependency/impact checks before finalizing revisions.
13. **Do not optimize away limitations.** Important boundary conditions, failed replications, missing controls, underpowered comparisons, and conflicting analyses must remain visible when scientifically relevant.
14. **Respect section function.** Methods explains what was done; Results reports what was observed; Discussion interprets; Abstract compresses the same evidence. Do not move unsupported interpretation into Results to make prose stronger.
15. **Revision must be inspectable.** For material edits, record what changed, why, which source triggered it, which claims/sections were affected, and—when a before-draft exists—verify the actual changed spans rather than relying on revision memory.
16. **Release claims require release evidence.** “Submission-ready”, “camera-ready”, or equivalent language is allowed only after standard/release preflight passes, no release-blocking conflict remains, and any non-blocking unresolved conflict is explicitly disclosed and scoped.
17. **Ledger and manuscript must stay synchronized.** In auditable Markdown workspaces, a declared `manuscript_anchor` must identify the section/block that actually expresses the ledger claim. Moving or rewriting prose requires re-checking the linked claim instead of leaving a stale ledger entry.
18. **Figure/table identity is stable.** `object_refs[].source_id` is the scientific object identity; renumbering may change its display label but must not accidentally point the source to a different figure/table number. Source metadata, captions, claim refs, and manuscript text must be updated together.
19. **Primary conclusions need their reporting dependencies.** For multi-section/full release work, every `section_plan.main_claim_families` entry must have a `reporting_contracts.jsonl` entry linking the result evidence to method evidence, material qualifiers/limitations, expected figure/table sources, and required manuscript sections.
20. **Claims have a lifecycle.** A claim that is no longer scientifically current must be marked `superseded` or `retired`, preserved as history, and removed from the current manuscript. Do not silently overwrite or delete invalidated claims merely to make the ledger look clean.
21. **Revision responses must be earned by verified changes.** Reviewer/editor/user obligations that require manuscript changes must point to real `change_id` records and, for release, a before/after `revision_diff.json` demonstrating the affected claim/section change or removal. A response letter is not evidence that the revision happened.
22. **Verified revisions are state-bound.** For material `revise`/`refresh` release work, capture the pre-edit semantic state and bind each verified revision to both `base_state_id` and the exact post-edit `verified_state_id`. Any later semantic edit invalidates that verification until the new state is checked again.
23. **Coverage must close in both directions.** For multi-section/full release work, active claims intended for the manuscript must resolve to real manuscript anchors, and scientific paragraphs in covered sections must resolve back to active claims. Structured citation keys and figure/table references in those paragraphs must also resolve to declared claim/source identities.
24. **Multi-claim prose needs an explicit composition contract.** When two or more active claims share a release paragraph, declare the paragraph identity and intended composition. Material qualifiers/limitations may be declared as required companions; dropping them while retaining the stronger claim is a release failure. A paragraph contract cannot authorize a new unsupported inference—create a new claim for any genuinely new proposition.
25. **Unresolved does not always mean release-blocking.** Classify source conflicts as `blocking`, `disclose_and_scope`, `historical_only`, or `resolved`. A non-blocking unresolved conflict may pass release only when affected/scoped claims and manuscript disclosure are explicitly linked and the conflicting values remain source-specific. For cross-side disclosure, every numeric token must come from a declared conflict side or be explicitly registered as a derived/context numeric exception with provenance. Legacy free-text unresolved conflicts remain blocking by default.
26. **Claims should be atomic propositions.** Do not pack a quantitative result, a provenance conflict, a reproducibility limitation, and an interpretation into one claim merely to avoid paragraph composition. Split materially independent propositions into separate claims and compose them explicitly; use `atomicity_exemption_reason` only for genuinely indivisible cases.
27. **Revision mode preserves the manuscript.** `revise`/`refresh` must preserve valid existing text and structure unless a verified change explicitly authorizes a broader rewrite. Workflow narration such as “this refresh”, “supplied methods notes”, or “allowed sources” belongs in ledgers/response files, not the scientific manuscript.
28. **Release prose needs exact claim-span closure in v1.8+ workspaces.** For configured sections and claim types, use `anchor_precision=span` with matching `<!-- CLAIM:<id> --> ... <!-- END-CLAIM:<id> -->` markers. The exact span—not merely the surrounding paragraph—must match the claim text, contain its required numeric tokens, and own its citations/figure-table references. Material visible prose outside governed spans is a release failure unless explicitly exempted.

29. **Resolve the writing context before claiming venue conformity.** Distinguish discipline, subfield, article type, target venue, optional track, venue year, submission stage, and language. If these are unspecified, remain at `generic` or `discipline` readiness instead of inventing a target.
30. **Venue requirements are runtime evidence, not permanent skill knowledge.** For venue-specific work, retrieve the current applicable official author guidelines/template/checklist at execution time, record them in `writing_sources.jsonl`, and normalize them into `writing_profile.json`. Do not rely on remembered page limits, anonymity rules, checklist requirements, or prior-year conventions when an official current source can be retrieved.
31. **Official writing guidance outranks secondary advice.** Secondary sources may help locate or interpret official instructions, but they must not silently override a current official source. If official sources conflict, record the conflict and scope it by article type/track/year/stage/source rather than choosing the more convenient rule.
32. **Writing rules cannot change scientific truth.** Venue constraints may change structure, length, ordering, terminology, formatting, or submission artifacts; they may not authorize omission of material negative evidence, stronger causal language, fabricated methods, altered numbers, or weaker provenance.
33. **Venue-ready claims require a verified runtime contract.** `submission-ready for <venue>` or equivalent language is allowed only when the requested venue/year/stage writing profile is resolved from source-backed guidance, `manuscript_contract.json` matches that profile, unresolved writing-rule items are cleared, and release preflight passes.

## 1. Choose the mode

Select one primary mode:

- `build`: create a manuscript or section from supplied results, figures/tables, methods, notes, and optional literature context.
- `revise`: modify an existing manuscript while preserving valid text and changing only what the evidence or user request requires.
- `refresh`: update the manuscript after one or more results, analyses, figures, tables, or captions changed; perform dependency impact analysis before editing prose.
- `audit`: review a manuscript against its supplied evidence for unsupported claims, inconsistent numbers, overstated language, missing limitations, or stale cross-references.

For a small request (for example, “rewrite this Results paragraph from Table 2”), do not force a full workspace. Apply the same rules locally and keep the result traceable to the supplied evidence.

## 2. Choose the profile

Set `profile` in `project.json`:

- `draft`: fast internal drafting. Traceability is required for substantive results, but unresolved placeholders may remain.
- `standard`: **default**. Full source inventory, evidence/claim ledgers, cross-section consistency checks, and preflight.
- `release`: submission or archival handoff. Requires no release-blocking source conflict, explicit disclosure/scoping for permitted unresolved conflicts, no unexplained placeholders, stricter claim/numeric/locality checks, and a frozen manifest.

A profile changes execution cost, not scientific truth standards.

## 3. Resolve the dynamic writing profile

Before planning a multi-section manuscript, decide the **writing context** in `project.json.writing_context`:

- `discipline` — e.g. computer science, biomedicine, physics;
- `subfield` — e.g. machine learning, NLP, systems, oncology;
- `article_type` — e.g. conference paper, journal article, brief report, methods paper;
- `venue`, optional `track`, and `venue_year` when a specific submission target exists;
- `submission_stage` — initial submission, revision, rebuttal, camera-ready, resubmission, preprint, etc.;
- `target_specificity` — `generic|discipline|venue`;
- `language`.

Do not infer a specific venue merely because the field is obvious. If the user has not selected one, use `generic` or `discipline` specificity and avoid venue-ready claims.

For `discipline` or `venue` specificity, read `references/20-dynamic-writing-profile.md` and `references/21-manuscript-contract.md`. The model must perform the retrieval; deterministic scripts validate the resulting provenance/contract.

### Runtime retrieval protocol

For venue-specific work, search current official sources in this order:

1. official venue/conference/journal author guidelines for the target article type/track/year/submission stage;
2. official submission template or style package documentation;
3. official checklist/reproducibility/ethics/supplement/rebuttal/camera-ready instructions;
4. official publisher or professional-society guidance when the venue delegates rules there;
5. secondary guidance only to locate official material or fill a clearly labeled non-binding convention.

Record each retrieved writing source in `writing_sources.jsonl` with a stable `writing_source_id`, title, URL/path, `authority_level`, source class, retrieval timestamp, venue, discipline/subfield when known, applicable article types/tracks/years/stages, and a locator/notes when useful. Writing-guideline sources are **not scientific evidence** and must not be inserted into `evidence.jsonl` merely because they influence prose.

Normalize the retrieved rules into `writing_profile.json`:

- one atomic constraint per `constraint_id`;
- category, requirement text, `required|recommended|prohibited|informational` strength;
- basis (`official_guideline`, `official_template`, `official_checklist`, `discipline_convention`, or `user_instruction`);
- source IDs + locator;
- applicable submission stages;
- verification state;
- writing-guideline conflicts and readiness level.

Then synthesize `manuscript_contract.json`. This is the operational contract for the current paper, not a permanent venue template. It may specify required/optional/forbidden sections, order, abstract limits, machine-checkable rules, manual checks, and unresolved items. Each section also declares one or more `scientific_roles` (for example `results` for a venue section named `Evaluation`) so scientific QA does not depend on fixed heading names. Every rule derived from a retrieved guideline must point back to `constraint_id` records. The contract stores `writing_profile_sha256`; changing the profile makes the contract stale until regenerated/reverified.

For v2.0 workspaces, `scripts/audit_writing_profile.py` checks context agreement, source authority, venue/year/article-type/track/stage applicability, constraint provenance, guideline conflicts, profile readiness, contract freshness, required/forbidden sections, configured ordering/word-limit checks, and alignment with `section_plan.json` / `coverage_policy`.

A dynamic profile changes **how the manuscript is written and packaged**, not what the scientific evidence supports.

## 4. Establish source authority before writing

Read `references/01-source-grounding.md` when source priority or conflicts are non-trivial.

Create `project.json` from `templates/project.template.json`, then list source artifacts in `sources.jsonl`. Typical source types:

- `statistical_output`
- `result_table`
- `figure`
- `figure_caption`
- `methods_record`
- `analysis_code`
- `lab_note`
- `manuscript`
- `supplement`
- `literature_context`
- `user_instruction`

For each source capture a stable `source_id`, path/URI or human-readable locator, version/date when known, authority, and notes.

Recommended authority order when the user does not specify otherwise:

1. explicit user correction / declared canonical artifact;
2. final analysis output or validated result table;
3. analysis code + exact data snapshot;
4. figure/table generated from that analysis;
5. methods record / protocol / registered plan;
6. research notes;
7. pre-existing manuscript prose.

Do not silently resolve a meaningful source conflict. Record it in `project.json.unresolved_conflicts` with an explicit release disposition. Read `references/16-source-conflict-disposition.md` for `blocking`, `disclose_and_scope`, `historical_only`, and `resolved` handling. Legacy free-text conflicts are treated as blocking. For value/settings disagreements that must remain source-specific, use `conflict_sides` plus `cross_side_claim_ids` so scoped claims cannot silently span competing provenance streams. If a cross-side disclosure contains a derived difference, ratio, average, year, or other numeric context not listed in a side's `value_tokens`, register it in `cross_side_numeric_exceptions` with `role`, `reason`, and (for derived values) the contributing `source_side_ids`.

## 5. Build the evidence ledger

Use `templates/evidence.template.jsonl` as the contract. One evidence unit should represent one manuscript-relevant observation or method fact, not an entire paper or figure.

Important fields:

- `evidence_id`
- `source_id`
- `locator` such as `Table 2, row AUC`, `Fig. 3b`, `model_summary.txt:L12-L18`
- `evidence_type`: `result|method|figure_observation|limitation|literature_context|user_fact`
- `statement`: source-faithful description
- `comparison`
- `estimate`, `uncertainty`, `p_value`, `n`, `unit` when available
- `value_tokens`: exact numeric/string tokens that should survive into linked claims when applicable
- `design_scope`
- `verification`: `verified|partial|unverified`

Do not collapse multiple populations, outcomes, models, timepoints, or panels into one evidence item when doing so could hide a contradiction.

For figures/tables, read `references/03-figure-table-integration.md`.

## 6. Build the claim ledger before polished prose

Use `templates/claims.template.jsonl`.

Each substantive manuscript claim gets:

- `claim_id`
- `claim_family_id` when the same underlying scientific proposition is restated across sections
- `section`
- `claim_type`: `result|method|interpretation|limitation|literature_context`
- `text`
- `evidence_ids`
- optional `required_value_tokens`: `null` means infer exact evidence tokens for a Results/result claim, `[]` means no exact-token requirement, and a list declares the exact numeric/string tokens that must survive in this claim
- optional `citation_keys` for supplied literature sources
- optional `object_refs` for exact figure/table source + display label
- `source_scope`
- `strength`: `descriptive|associational|causal|speculative`
- `status`: `draft|verified|needs_revision|blocked`
- `lifecycle_state`: `active|superseded|retired` (omitted means `active` for backwards compatibility)
- optional `supersedes_claim_ids`, `superseded_by_claim_ids`, and `retirement_reason` for historical claim provenance
- optional `manuscript_anchor`
- `anchor_precision`: `span|paragraph`; new v1.8 workspaces default to `span` for governed scientific prose
- optional `span_exemption_reason` when a required v1.8 claim cannot reasonably use exact span anchoring and the project policy permits exemptions
- optional `required_companions`: claim IDs that must remain in `same_paragraph`, `same_section`, or the current `manuscript`
- optional `source_conflict_ids` linking the claim to object-style source conflicts in `project.json.unresolved_conflicts`
- optional `atomicity_exemption_reason` only when a mechanically compound-looking claim is scientifically indivisible
- optional `manuscript_presence`: `required|optional|not_in_manuscript`; use `manuscript_presence_reason` when intentionally excluding an active ledger claim from the current manuscript

For `result` and `method` claims, evidence links are mandatory in `standard`/`release`.

For `interpretation` claims, link both the underlying result evidence and, when the interpretation depends on external knowledge, the relevant literature-context evidence.

Read `references/06-claim-language-calibration.md` when choosing verbs such as “improved”, “associated”, “mediated”, “demonstrated”, “supports”, “suggests”, or “consistent with”. For multi-section/full-manuscript work, read `references/09-section-contracts-and-claim-families.md` and use one `claim_family_id` for section-specific restatements of the same scientific proposition. When a materially changed analysis invalidates an earlier proposition, read `references/12-revision-obligations-and-claim-lifecycle.md` and preserve the older claim as `superseded`/`retired` rather than silently rewriting history.

For release-oriented multi-section/full manuscripts, read `references/14-manuscript-coverage-closure.md`. Claims in covered core sections are manuscript-required by default unless explicitly marked otherwise with a defensible reason. When a paragraph intentionally combines multiple active claims, also read `references/15-paragraph-composition-and-companions.md` and use a paragraph contract instead of relying on prose adjacency alone.

Before polishing prose, read `references/17-claim-atomicity.md` for high-risk result/method/limitation claims. One claim should normally represent one scientific proposition. If a sentence needs a result plus a qualifier, provenance conflict, or reproducibility boundary, prefer separate claims linked by paragraph/companion contracts.

For v1.8+ workspaces, read `references/19-claim-span-traceability.md` before drafting governed sections. Exact claim spans close the gap between an atomic ledger claim and the paragraph that contains it. Use the existing `<!-- CLAIM:C001 -->` start marker plus `<!-- END-CLAIM:C001 -->`; keep citations, object references, and required numeric tokens inside the claim span they belong to.

## 7. Plan the manuscript from evidence + the resolved writing contract

Before drafting a multi-section/full manuscript, create `section_plan.json` from `templates/section_plan.template.json`. Its scientific coverage must remain evidence-driven **and its section structure must be compatible with the resolved `manuscript_contract.json`**. Do not assume IMRaD, Related Work placement, appendix structure, or abstract format when the active writing profile says otherwise. Keep the plan short:

- central question and study contribution;
- 2–5 main claims that the paper must establish;
- which evidence unit proves each claim;
- figure/table sequence;
- essential methods required to interpret each result;
- limitations that qualify each main claim;
- what is intentionally out of scope.

For important result families in multi-section/full manuscripts, add `reporting_contracts.jsonl` using `templates/reporting_contracts.template.jsonl`. The contract is a dependency map, not another outline. It can declare:

- which result evidence defines the family;
- which method evidence must be represented in Methods;
- which limitation/sensitivity evidence must remain visible in Discussion/Conclusion;
- which figure/table sources are expected to carry the result;
- required sections and whether the family is eligible for the Abstract.

Read `references/11-manuscript-consistency-and-reporting-contracts.md` for this release-stage contract.

When a manuscript paragraph contains two or more active claim anchors, add exactly one `<!-- PARAGRAPH:<id> -->` marker and a matching `paragraph_contracts.jsonl` record. Record the claim IDs, composition type, primary/qualifier claims when relevant, and only high-value literal prose guardrails. Use `required_companions` on a claim when a limitation, exploratory-status statement, population bound, or other qualifier must travel with it during revisions. See `references/15-paragraph-composition-and-companions.md`.

In v1.8+, paragraph composition sits **above** exact spans. Put each atomic proposition in its own non-overlapping claim span, then use a paragraph contract when two or more spans share a paragraph. Do not nest spans or use one span to absorb connective prose plus several independent propositions.

Do not generate an Introduction or Related Work section merely because a generic template usually has one. Follow the active manuscript contract for section structure, and use only literature context supplied by the user or explicitly retrieved by an upstream literature workflow.

## 8. Draft sections with section-specific contracts

The section guidance below is a **scientific-function default**, not a universal venue template. Use it only for sections present in the active `manuscript_contract.json`; venue/discipline structure can rename, combine, reorder, or omit sections while preserving the scientific boundaries below.


### Title

Describe the studied system and contribution without implying a broader population, mechanism, or causal conclusion than the evidence supports.

### Abstract

Mirror the paper’s verified evidence. Include objective/context, design/method, primary results, and appropriately scoped conclusion. Every quantitative abstract result must agree with the body and evidence ledger.

### Introduction

Build only the minimum argument needed to motivate the study: known context -> specific gap -> study question/approach. Citation-dependent statements require supplied literature support.

### Methods

Write only from methods records, protocols, code, configuration, or explicit notes. Preserve enough detail for scientific interpretation and reproducibility. Do not infer absent parameters.

### Results

Read `references/02-results-to-prose.md`.

Default paragraph grammar:

**question/comparison -> analysis population/condition -> quantitative result -> uncertainty/statistical evidence -> figure/table anchor -> restrained interpretation only if necessary**

Prefer effect + uncertainty over p-value-only prose. Keep primary and sensitivity analyses distinguishable. State null or conflicting results plainly.

### Discussion

Read `references/04-discussion-guardrails.md`.

A strong Discussion separates:

1. what was observed;
2. what it may mean;
3. how it relates to supplied prior literature;
4. alternative explanations;
5. design/data limitations;
6. what remains unresolved.

Never introduce a new empirical result in Discussion.

### Conclusion

Compress verified contributions and boundary conditions. Do not add a stronger claim than appears in the Results/Discussion claim ledger.

### Figure/table captions

Captions must identify the object, population/condition, encodings, statistical annotations, abbreviations, and panel semantics needed for independent reading. Do not use captions to smuggle in unsupported conclusions.

## 9. Integrate figures and tables precisely

For every figure/table reference:

- use the correct object and panel identifier;
- state the scientific point supported by that panel/table;
- keep terminology, group names, units, and sample sizes consistent with the visual/source;
- distinguish visual trend from formally tested effect;
- do not describe hidden or cropped information;
- update captions and in-text references together when numbering changes;
- when a source declares `object_label`, verify that claim-level display labels resolve to the same figure/table number (`Fig. 2` and `Figure 2` are equivalent; `Fig. 2` and `Fig. 3` are not).

If a figure is replaced but keeps the same filename, treat it as changed evidence until its fingerprint is verified.

## 10. Revise an existing manuscript surgically

Read `references/05-revision-mode.md`.

For `revise` mode:

Read `references/10-revision-diff-and-reviewer-response.md` when a before/after audit is involved, and `references/12-revision-obligations-and-claim-lifecycle.md` when reviewer/editor/user obligations or claim retirement/supersession are involved.

1. inventory requested changes and protected facts;
2. convert actionable external/internal requests into `revision_obligations.jsonl` when traceability matters;
3. identify the exact manuscript spans and linked claims;
4. preserve valid surrounding prose;
5. update claims/evidence links and lifecycle state before polishing language;
6. propagate terminology/number/cross-reference changes;
7. record material edits in `revision_log.jsonl` and mark verification only after checking the actual manuscript/diff.

Do not rewrite the whole paper merely because one section needs correction. For v1.7 `revise`/`refresh` work, read `references/18-revision-locality-and-manuscript-preservation.md` and configure `revision_policy` before editing. Preserve the original title and unaffected prose unless a verified obligation explicitly authorizes a broader rewrite.

When a pre-edit manuscript is available, run `scripts/revision_diff.py` after editing to verify which sections and anchored claims actually changed or disappeared. For new reviewer/editor workflows, use `revision_obligations.jsonl`; `reviewer_response_map.jsonl` remains a backwards-compatible legacy mapping. Response prose comes only after the linked change is verified.

For material `revise`/`refresh` work, read `references/13-version-lineage-and-change-provenance.md`. Capture the pre-edit semantic state before changing the workspace:

```bash
python scripts/checkpoint_workspace.py . --output workspace_state.previous.json
```

After the candidate revision is complete, capture the exact state being verified:

```bash
python scripts/checkpoint_workspace.py . --output workspace_state.current.json
```

A verified `revision_log.jsonl` row should bind `base_state_id` to the previous checkpoint and `verified_state_id` to the candidate/current checkpoint. Also list changed scientific `source_ids`, dynamic `writing_source_ids`, evidence IDs, claim IDs, sections, and governed contract artifacts. If any semantic artifact changes afterward, re-verify against the new state.

For major revisions, prefer a change table with:

`change_id -> base_state_id -> verified_state_id -> trigger/source -> affected evidence/claims/sections -> action -> verification`

## 11. Refresh after results or figures change

This is a first-class workflow, not ordinary proofreading.

Create a fresh source/evidence fingerprint:

```bash
python scripts/fingerprint_workspace.py . --output fingerprints.current.json
```

Compare with the previous snapshot:

```bash
python scripts/impact_analysis.py \
  --old fingerprints.previous.json \
  --new fingerprints.current.json \
  --claims claims.jsonl \
  --sources sources.jsonl \
  --report impact_report.json
```

The report identifies claims linked to changed/missing sources and propagates review to all claims sharing an affected `claim_family_id`. Manually inspect those claims and every downstream section that depends on them, especially Abstract and Conclusion.

A dependency report identifies what must be reviewed; it does not decide the scientific replacement text. If the scientific proposition itself changed, create/update the replacement claim and mark the older claim `superseded`; if the conclusion should disappear without replacement, mark it `retired` with a reason. Then remove inactive claim prose from the current manuscript and rerun lifecycle/manuscript QA.

## 12. Run deterministic preflight

Initialize a workspace when needed:

```bash
python scripts/init_workspace.py manuscript-workspace
cd manuscript-workspace
```

Validate core records:

```bash
python scripts/validate_workspace.py . --profile standard
```

Run preflight:

```bash
python scripts/preflight.py . --profile standard --report qa_report.json
```

Preflight checks include:

- parseable project/source/evidence/claim records;
- v2 dynamic writing-profile closure: context, writing-source authority/applicability, constraint provenance, writing-guideline conflicts, readiness, contract hash, section presence/order, and configured machine checks;
- duplicate IDs;
- dangling source/evidence/citation/object-reference links;
- result/method claims without evidence;
- claims linked only to unverified evidence;
- blocked/needs-revision claims;
- manuscript anchors missing from `manuscript.md` when declared;
- claim-level `required_value_tokens` absent from claim text (with Results/result claims inheriting evidence tokens by default);
- obvious causal-language/design-scope mismatches;
- source-conflict disposition: blocking conflicts fail release; `disclose_and_scope` conflicts require active scoped/disclosure claims and manuscript disclosure; optional `conflict_sides` require one-side scoped claims and explicitly attributed cross-side disclosure;
- unresolved placeholders under release profile;
- stale claims whose linked source fingerprints changed;
- cross-section `claim_family_id` strength/evidence inconsistencies;
- claim anchor uniqueness, declared-section placement, and ledger-to-manuscript text synchronization;
- bidirectional manuscript coverage: required active claims missing from the manuscript and uncovered scientific paragraphs in configured core sections;
- reverse structured-citation coverage (`[@key]`) against source `citation_key` and paragraph claim `citation_keys`;
- reverse figure/table coverage so manuscript object references resolve to declared source identities and paragraph claim `object_refs`;
- claim atomicity for high-risk result/method/limitation claims so several independent propositions cannot be hidden inside one claim;
- exact claim-span closure for v1.8 workspaces: matching start/end markers, exact span-to-ledger text synchronization, span-local numeric tokens, citation/object ownership, non-overlap, and material-prose coverage outside spans;
- paragraph-composition closure for multi-claim paragraphs, including stable `PARAGRAPH:<id>` markers, exact contract membership, required claim companions, and optional literal prose guardrails;
- figure/table source identity versus manuscript display labels;
- `section_plan.json` coverage mismatches;
- main-result `reporting_contracts.jsonl` coverage of required method evidence, qualifiers, objects, and sections;
- active/superseded/retired claim lifecycle consistency and inactive-claim residue in the current manuscript;
- `revision_obligations.jsonl` resolution against verified `revision_log.jsonl` changes and, for release manuscript changes, `revision_diff.json`;
- semantic-state lineage for `revise`/`refresh`: baseline presence, source/evidence/claim/contract changes, revision-log coverage, and exact `base_state_id`/`verified_state_id` binding;
- `revision_diff.json` manuscript hashes against baseline/current state so a stale diff cannot certify a later edit;
- revision locality/preservation for `revise`/`refresh`: schema-v4 diff with exact-span comparison when available, v3 locality metrics, paragraph preservation, title stability, explicit global-rewrite authorization, and removal of workflow/meta-writing from scientific prose;
- release result/method claims whose linked evidence has no `verified` evidence item;
- legacy reviewer-response mappings that do not point to real revision changes.

Mechanical checks are warning systems, not substitutes for scientific review.

## 13. Perform a human/model scientific QA pass

Use `references/08-qa-rubric.md` after deterministic preflight.

Review in this order:

1. scientific correctness;
2. completeness of primary evidence;
3. claim strength calibration;
4. numeric/statistical fidelity;
5. design/population scope;
6. figure/table fidelity;
7. cross-section consistency;
8. limitations and alternatives;
9. logical flow;
10. language and style.

Do not polish sentences before fixing scientific contradictions.

## 14. Re-validate the dynamic writing profile before release

Read `references/07-journal-style-adaptation.md`, `references/20-dynamic-writing-profile.md`, and `references/21-manuscript-contract.md` after scientific content is stable.

If the target venue/year/stage was added or changed after drafting, rerun official-guideline retrieval and regenerate the writing profile/contract before structural polishing. Do the same when a stored profile is known to be stale or a submission moves from initial review to rebuttal, revision, or camera-ready.

Late adaptation may change headings, ordering, abstract structure, page/word limits, anonymity handling, reference style, terminology conventions, supplements, checklists, or required submission artifacts. It must not change evidence strength or scientific meaning.

If current official venue instructions cannot be verified, downgrade readiness to `discipline` or `generic`; do not invent venue-specific requirements or claim venue readiness.

## 15. Freeze a release handoff

For `release`, run:

```bash
python scripts/preflight.py . --profile release --report qa_report.json
python scripts/freeze_snapshot.py . --output manifest.json
```

`freeze_snapshot.py` also writes `workspace_state.current.json`. Manifest schema v2 records the frozen `workspace_state_id` and, when `workspace_state.previous.json` exists, its `parent_workspace_state_id`. This gives the handoff an explicit semantic lineage in addition to file hashes.

A release handoff should normally include:

- `manuscript.md` or the edited manuscript file;
- `project.json`;
- `sources.jsonl`;
- `evidence.jsonl`;
- `claims.jsonl`;
- `section_plan.json` for multi-section/full-manuscript work;
- `writing_sources.jsonl`, `writing_profile.json`, and `manuscript_contract.json` for v2 discipline/venue-specific work;
- `reporting_contracts.jsonl` for important multi-section/full-manuscript result families;
- `paragraph_contracts.jsonl` when paragraphs intentionally combine multiple active claims;
- `revision_log.jsonl` when revisions occurred;
- `revision_obligations.jsonl` when reviewer/editor/user/internal-audit requests were tracked;
- `revision_diff.json` for release revisions that claim verified manuscript changes;
  - v1.8 `revision_diff.py` schema v4 compares exact claim spans when possible and records paragraph fallback for legacy baselines;
- legacy `reviewer_response_map.jsonl` when still used;
- `qa_report.json`;
- `workspace_state.previous.json` for material revise/refresh releases;
- `workspace_state.current.json` for the frozen semantic state;
- `manifest.json`.

The manifest proves file identity and change state. It does not prove that the study is correct, the analysis is valid, or the literature is complete.

## Resource routing

Load details only when needed:

- source priority/conflicts -> `references/01-source-grounding.md`
- quantitative Results prose -> `references/02-results-to-prose.md`
- figure/table integration -> `references/03-figure-table-integration.md`
- Discussion interpretation -> `references/04-discussion-guardrails.md`
- manuscript modification/refresh -> `references/05-revision-mode.md`
- claim verbs and certainty -> `references/06-claim-language-calibration.md`
- legacy journal/style adaptation notes -> `references/07-journal-style-adaptation.md`
- final scientific QA -> `references/08-qa-rubric.md`
- section contracts / cross-section claim families -> `references/09-section-contracts-and-claim-families.md`
- before/after revision proof / reviewer-response linkage -> `references/10-revision-diff-and-reviewer-response.md`
- ledger/manuscript synchronization, figure/table identity, Methods/result/qualifier dependencies -> `references/11-manuscript-consistency-and-reporting-contracts.md`
- reviewer/editor/user revision obligations and claim supersession/retirement -> `references/12-revision-obligations-and-claim-lifecycle.md`
- semantic checkpoints, revision-state binding, stale-verification detection, and release lineage -> `references/13-version-lineage-and-change-provenance.md`
- bidirectional manuscript/ledger coverage, claim anchors, reverse citation coverage, and reverse figure/table identity -> `references/14-manuscript-coverage-closure.md`
- multi-claim paragraph contracts, qualifier companions, and composition guardrails -> `references/15-paragraph-composition-and-companions.md`
- source-conflict release disposition and scoped disclosure -> `references/16-source-conflict-disposition.md`
- one-proposition claim design / compound-claim audit -> `references/17-claim-atomicity.md`
- revision locality, title/prose preservation, and anti-audit-report manuscript rules -> `references/18-revision-locality-and-manuscript-preservation.md`
- exact claim-span markers, span-local numeric/citation/object closure, and uncovered-prose detection -> `references/19-claim-span-traceability.md`
- dynamic discipline/article-type/venue/year/stage retrieval protocol -> `references/20-dynamic-writing-profile.md`
- source-backed writing profile -> operational manuscript contract and venue-compliance audit -> `references/21-manuscript-contract.md`

Use upstream AutoSCI skills when their job is required:

- literature discovery/synthesis -> `literature-research`
- statistical re-analysis / effect sizes / uncertainty / plots -> `scientific-data-analysis`
- scientific conceptual figures -> `scientific-figure`
- paper or research talk slides -> `academic-research-presentation`

Do not duplicate those workflows inside this skill.
