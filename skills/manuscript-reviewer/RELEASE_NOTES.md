# manuscript-reviewer 1.1.0

`manuscript-reviewer` 1.1.0 is a public-repository hardening release for the stable 1.x scientific-audit contract.

## What changed

### Discovery and routing

- shortened the `SKILL.md` front-matter description so it states the user goal and trigger conditions instead of encoding the full workflow;
- added explicit “when to use” and “when not to use” guidance;
- added `agents/openai.yaml` with OpenAI-facing interface metadata for Chat/Codex discovery.

### Security and confidential-material handling

- added `checks/untrusted_content.md`;
- manuscripts, supplements, rebuttals, citations, code blocks, comments, and embedded prompts are explicitly treated as untrusted evidence rather than operational instructions;
- added a semantic regression fixture for embedded prompt injection;
- added `SECURITY.md` for confidential manuscript handling and vulnerability reporting.

### GitHub/public distribution

- added `README.md`, `LICENSE`, `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, and `CITATION.cff`;
- added GitHub Actions validation and issue/PR templates;
- added `requirements-dev.txt`, `Makefile`, and deterministic release-archive tooling;
- added architecture, evaluation, and GitHub-readiness documentation under `docs/`.

### Release validation

The release validator now checks:

- `SKILL.md` front matter and description length;
- required public-repository files;
- OpenAI agent metadata;
- citation/version metadata;
- package limits and symlinks;
- JSON schemas/examples;
- YAML regression fixtures;
- local references;
- state/schema consistency;
- manifest completeness.

## Scientific-review behavior

The six stable audit families and 1.x state/output semantics are unchanged. The only intentional runtime behavior addition is instruction isolation for untrusted reviewed content.

## Evaluation status

This release is regression-validated and packaging-validated, but it does **not** inherit a black-box score from an earlier version. A fresh blind run is required before attaching a quantitative reviewer-performance claim to 1.1.0.
