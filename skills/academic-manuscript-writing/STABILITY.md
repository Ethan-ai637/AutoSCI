# Stability and known boundaries

`academic-manuscript-writing` v2.0.0 is suitable for public use as an auditable evidence-to-manuscript workflow. Its deterministic checks are designed to catch structural/provenance failures; they do **not** replace scientific peer review or domain expertise.

## What is considered stable

The following contracts are covered by packaged compatibility/release fixtures:

- source -> evidence -> claim traceability;
- numeric-token fidelity for declared/required values;
- claim lifecycle (`active`, `superseded`, `retired`);
- cross-section claim families and reporting contracts;
- manuscript coverage and structured citation / figure-table identity checks;
- paragraph composition and required companions;
- source-conflict release dispositions, side-specific provenance, and cross-side numeric disclosure;
- claim atomicity guardrails;
- revise/refresh locality and semantic-state lineage;
- v1.8 exact claim spans and span-aware revision diffs;
- v2 dynamic writing-context -> writing-source -> writing-profile -> manuscript-contract provenance;
- venue/year/article-type/track/submission-stage applicability, official-source requirements, contract hash binding, and generic section/word-limit machine checks;
- backwards compatibility with the packaged v1.5/v1.6/v1.7 fixtures.

## Known boundaries

1. **Mechanical QA is not semantic truth.** A claim can be perfectly traced to a source and still be scientifically weak, confounded, poorly designed, or misinterpreted. Human/model scientific review remains required.
2. **Exact spans are Markdown-oriented.** The current deterministic span contract uses HTML comment markers in `manuscript.md`. Native DOCX/LaTeX AST-level anchoring is not implemented.
3. **Citation reverse-audit is structured-key oriented.** Deterministic citation ownership is strongest for explicit keys such as Pandoc `[@Smith2024]`; free-text citations are not guessed.
4. **Atomicity checks are guardrails, not a semantic parser.** The audit catches obvious compound claims and mixed evidence roles but cannot prove that every proposition boundary is linguistically optimal.
5. **Source-conflict derivations are made visible, not scientifically approved.** Registering a derived cross-side value proves provenance disclosure; it does not prove that averaging/differencing conflicting sources is scientifically justified.
6. **Revision-locality thresholds are configurable heuristics.** A legitimate journal transfer or major restructuring may require an explicitly authorized global rewrite.
7. **The skill consumes authoritative analyses; it is not a statistics engine.** Re-analysis belongs upstream in `scientific-data-analysis` or another validated analysis workflow.
8. **Release PASS means the declared contracts closed.** It does not mean a journal will accept the manuscript or that unrepresented evidence/claims do not exist.
9. **Venue compliance is only as complete as the retrieved official guidance.** The skill verifies the declared writing-source/profile/contract chain; it cannot guarantee that an inaccessible or unrepresented rule does not exist.
10. **The package does not hard-code venue knowledge.** Live venue-specific execution requires the model/tool environment to retrieve current official sources. Offline self-tests use a fictional venue fixture and therefore validate the interface, not any real conference/journal rules.
11. **Generic machine checks are intentionally limited.** Section presence/absence/order and word limits can be checked deterministically; anonymity, template typography, submission-system fields, ethics applicability, and similar requirements may remain manual checks.

## Compatibility policy

Historical packaged fixtures intentionally retain their original `skill_version` values. New releases should not invalidate those fixtures solely because optional newer ledgers or policies exist. A breaking reinterpretation of archived semantic state requires a major compatibility decision rather than a silent patch.

## Verification

Run:

```bash
python scripts/self_test.py --quick
```

before ordinary use of a cloned/extracted package, and:

```bash
python scripts/self_test.py --full
```

before publishing a release or changing deterministic governance behavior. CI may run the full contract as shards (for example `--full --shard 1/4` through `4/4`). See `TESTING.md` and `RELEASE_CHECKLIST.md`.

## Runtime floor

The deterministic toolchain uses only the Python standard library and targets a **Python 3.8 syntax floor**. Release self-test enforces that grammar floor. The packaged release was runtime-tested on the build interpreter available in the release environment; a repository that advertises Python 3.8 runtime support should additionally execute the self-test under Python 3.8 in CI.
