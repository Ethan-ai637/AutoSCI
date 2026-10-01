# Changelog

## 1.1.0 — GitHub/public-release hardening

### Added
- public repository documentation: README, MIT license, contribution/security/conduct guidance, and citation metadata;
- OpenAI skill interface metadata in `agents/openai.yaml`;
- GitHub Actions validation plus issue and pull-request templates;
- deterministic release archive builder and development dependency file;
- architecture/evaluation documentation;
- untrusted-content instruction isolation and a security regression fixture.

### Changed
- shortened skill discovery metadata and added explicit use/non-use routing guidance;
- expanded release validation to check public-repo files, front matter, agent metadata, citation metadata, package limits, and symlinks.

### Compatibility
- no audit family, evidence-state meaning, outward disposition, severity class, or revision transition was removed or renamed;
- public-output contracts remain compatible with 1.0.0.

## 1.0.0 — Stable release

This release promotes the v0.12 behavior into a stable contract rather than adding a new audit family.

### Stabilized
- claim–evidence, figure/table/text, numerical, notation, citation, and overclaim audits;
- manuscript-archetype routing and long-document coverage checkpoints;
- inference-chain, provenance, protocol-comparability, and evidence-sufficiency gates;
- finding / author-query / coverage-gap disposition;
- root-cause clustering, stable IDs, canonical finding records, and render invariance;
- revision/rebuttal lineage with residual-only severity recalibration;
- `no_longer_material` for verification gaps that cease to matter in the current revision;
- semantic regression fixtures derived from an independent v0.11 blind run.

### Added for 1.0
- `checks/state_model.md` as the authoritative vocabulary/state registry;
- `checks/output_contract.md` as the stable outward-output contract;
- `maintenance/BLACKBOX_EVAL.md` for independent black-box evaluation;
- `maintenance/RELEASE_GATE.md` for release discipline;
- `scripts/validate_release.py` for package/schema/fixture/reference validation;
- `VERSION` and `RELEASE_NOTES.md`.

### Corrected
- the final-standard section now states nine questions, matching the nine checks actually listed;
- package-level state definitions are centralized to reduce drift between runtime rules and schemas.

### Validation note
The 1.0.0 package includes regression fixtures created from the prior blind evaluation, but the prior v0.11 black-box score is not a 1.0.0 score. A fresh independent run is required to score this release.
