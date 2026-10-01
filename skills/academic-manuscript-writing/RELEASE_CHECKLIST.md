# Release checklist

Use this checklist before publishing a new version or updating the AutoSCI GitHub repository.

## Version and documentation

- [ ] `VERSION`, `templates/project.template.json`, README current-version text, and CHANGELOG agree.
- [ ] Declared Python syntax floor is consistent with executable syntax (`self_test.py` enforces Python 3.8 grammar).
- [ ] If the repository advertises a minimum runtime version, CI executes the self-test on that interpreter (for Python 3.8 claims, include a Python 3.8 job).
- [ ] CHANGELOG explains the user-visible reason for the version bump.
- [ ] New behavior has a reference/example when it changes the scientific or writing-profile contract.
- [ ] `writing_source.schema.json`, `writing_profile.schema.json`, and `manuscript_contract.schema.json` remain aligned with templates/audits.
- [ ] Historical compatibility fixtures retain their historical `skill_version` intentionally.

## Deterministic QA

- [ ] `python scripts/self_test.py --full` passes, or all configured `--full --shard INDEX/TOTAL` CI shards pass.
- [ ] Positive release fixtures pass with zero warnings.
- [ ] Expected-fail destructive tests are rejected, including dynamic writing-profile authority/staleness/context/article-type/track/section/manual-check mutations.
- [ ] `scripts/init_workspace.py` initializes a clean workspace with the current template version.

## Package hygiene

- [ ] No `__pycache__/`, `.pyc`, `qa_report.json`, temporary reports, or editor artifacts are included.
- [ ] JSON/JSONL/schema/template files parse successfully.
- [ ] New v2 workspaces initialize `writing_sources.jsonl`, `writing_profile.json`, and `manuscript_contract.json`.
- [ ] The ZIP extracts cleanly.
- [ ] `python scripts/self_test.py --quick` passes from the freshly extracted ZIP.
- [ ] The release ZIP checksum is recorded in the release notes when distributing a standalone archive.

## AutoSCI repository integration

- [ ] Place the skill at `skills/academic-manuscript-writing/`.
- [ ] Confirm the repository root `LICENSE` applies to the added skill.
- [ ] Update root `README.md` and `README_zh.md` so the skill is discoverable.
- [ ] Keep benchmark/evaluator gold data outside the installable skill directory unless intentionally published as tests.
- [ ] If repository CI is enabled, run `python skills/academic-manuscript-writing/scripts/self_test.py --full` on changes to this skill.

## Release claim

Only call the package GitHub-ready/release-ready after the source tree and freshly extracted package both pass the self-test and there are no known release-blocking defects.
