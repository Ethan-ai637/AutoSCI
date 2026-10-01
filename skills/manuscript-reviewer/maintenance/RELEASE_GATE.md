# Release gate for manuscript-reviewer 1.x

A behavior-changing release should not ship until all applicable checks pass.

## Package integrity

- `VERSION` exists and matches release notes/changelog.
- `manifest.txt` exactly covers packaged files.
- all referenced local support files exist.
- JSON schemas parse.
- bundled JSON examples validate against their schemas.
- regression YAML fixtures parse.
- release ZIP passes integrity testing.

## Behavioral integrity

- state names match `checks/state_model.md` and schemas;
- canonical-record rendering invariance is preserved;
- finding/query/gap boundaries do not regress on bundled fixtures;
- revision transitions do not treat clarification alone as repair;
- residual severity is recalculated from current defect;
- coverage gaps distinguish `resolved`, `not_reassessable`, and `no_longer_material` correctly;
- old verified hard-negative protections remain intact.

## Evidence discipline

- no source-semantic citation finding without source inspection;
- no `missing_required_evidence` finding without completed plausible-location checking;
- no plot-value guessing;
- no truth-source preference based only on surface format;
- no same-protocol comparison without material comparability/provenance checking.

## Release evidence

For patch releases, bundled regression validation may be sufficient when behavior is unchanged.

For behavior-changing minor/major releases, prefer at least one independent black-box run. If none has been run, state that explicitly in release notes rather than implying benchmark validation.

## Public repository readiness

For a public GitHub release:

- `README.md` explains scope, non-scope, installation, usage, evaluation status, and confidential-material posture;
- `LICENSE`, `CONTRIBUTING.md`, `SECURITY.md`, `CODE_OF_CONDUCT.md`, and `CITATION.cff` are present;
- `.github/workflows/validate.yml` runs the deterministic validator and release builder;
- `agents/openai.yaml` contains valid skill interface metadata;
- `SKILL.md` front matter stays within supported limits and its description focuses on trigger conditions rather than duplicating the workflow;
- no copyrighted/private manuscript fixtures are bundled without explicit rights and provenance;
- no release-performance score is claimed without a release-specific blind evaluation.

## Untrusted-content safety

- reviewed manuscripts/supplements/rebuttals/citations cannot override the task or evidence boundary;
- embedded instructions cannot trigger disclosure, uploads, unrelated network access, or tool execution;
- `regressions/security_embedded_prompt_injection.yaml` remains passing in semantic evaluation.
