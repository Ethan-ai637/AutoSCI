# GitHub readiness — 1.1.0

## Verdict

**Ready for public GitHub publication as an open-source Agent Skill.**

This verdict means the repository is installable, documented, licensed, contribution-ready, CI-validated, release-buildable, and explicit about evaluation limits. It does **not** mean that 1.1.0 has a release-specific benchmark score or that the reviewer has been validated across all scientific domains.

## Release checks

| Area | Status | Evidence |
|---|---|---|
| Agent Skill structure | PASS | one root `SKILL.md`, valid YAML front matter |
| Discovery metadata | PASS | concise trigger-oriented description; `agents/openai.yaml` |
| Public documentation | PASS | README, architecture, evaluation, changelog, release notes |
| License and citation | PASS | MIT license and `CITATION.cff` |
| Contribution hygiene | PASS | CONTRIBUTING, Code of Conduct, issue/PR templates |
| Security posture | PASS | untrusted-content isolation, SECURITY.md, security regression fixture |
| Structured output contracts | PASS | JSON Schemas plus validating examples |
| Regression infrastructure | PASS | semantic YAML fixtures; no exact-prose contract |
| CI | PASS | GitHub Actions runs validation and archive build |
| Release packaging | PASS | deterministic single-top-level-folder ZIP builder |
| OpenAI bundle limits | PASS | package is far below file-count and size limits |
| Release-specific blind benchmark | PENDING | required before claiming quantitative 1.1.0 reviewer performance |

## Known limitations that are not publication blockers

1. `SKILL.md` remains deliberately detailed (~50 KiB). It is below current platform limits, but future work may compact duplicated runtime guidance after black-box equivalence testing.
2. Regression fixtures are not a multi-domain scientific benchmark. They protect known failure modes; they do not estimate broad precision/recall.
3. The repository does not bundle copyrighted/private manuscript PDFs. Full blind-evaluation packs should remain separately distributed with clear licensing/provenance.
4. `CITATION.cff` uses the collective author name `manuscript-reviewer contributors`. A maintainer may replace or extend this with repository-specific contributor metadata before publication.

## Recommended publication sequence

1. Publish the repository at tag `v1.1.0`.
2. Let GitHub Actions pass on the public commit.
3. Attach the archive produced by `python scripts/build_release.py` to the GitHub Release.
4. Run a fresh blind black-box test against the tagged release.
5. Publish the score only if the oracle remained hidden from the reviewer and document the evaluation bundle/version.
