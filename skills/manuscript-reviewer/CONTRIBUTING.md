# Contributing

Contributions are welcome when they improve scientific audit quality without turning the skill into a generic reviewer persona or a finding-maximization prompt.

## Before opening a pull request

1. Identify the failure mode or maintenance problem.
2. For behavior changes, reduce it to the smallest reproducible semantic case.
3. Add or update a fixture under `regressions/` when applicable.
4. Update rules at the most general level that fixes the failure; do not hardcode paper names, datasets, literal values, or exact sentences.
5. Update schemas/examples/templates together when a compatibility-sensitive state or output contract changes.
6. Run:

```bash
python -m pip install -r requirements-dev.txt
python scripts/validate_release.py
```

## Behavioral pull requests

A behavioral PR should explain:

- observed failure mode;
- current behavior;
- desired behavior;
- evidence that the new rule generalizes;
- regression fixture(s) added or changed;
- expected effect on precision and recall;
- whether a fresh black-box run is needed before release.

Do not use exact-output string equality as the primary test. Fixtures should assert scientific behavior such as `must_find`, `must_not_find`, expected disposition, allowed severity, transition state, or forbidden synthesis.

## Documentation-only pull requests

Documentation, examples, packaging, and CI improvements that do not alter runtime review behavior may be merged without a new black-box evaluation, but must still pass release validation.

## Versioning

- patch: no intended behavior change or narrowly compatible correction;
- minor: compatible behavior/routing/evaluation change in the 1.x contract;
- major: incompatible state/output contract or major workflow boundary change.

## External material

Do not commit copyrighted paper PDFs, proprietary manuscripts, private reviewer reports, or unlicensed benchmark material. Use minimal synthetic or properly licensed fixtures and document provenance where external material is included.
