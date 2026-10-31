# Method Goal Pursuit

**Version:** 1.1.0

`method-goal-pursuit` supports method-paper and autonomous research loops, including AutoSOTA-style goal pursuit. It keeps the contribution, venue target, and evaluation contract active while iterating evidence-grounded method candidates around the main experiment.

Every round produces a falsifiable method hypothesis, the main experiment over the complete official benchmark scope, and a small rationale-selected set of baseline and SOTA comparators under equal budgets. Controlled SOTA comparators must have accessible code under a compatible open-source license and downloadable required artifacts; unavailable methods are replaced with comparable runnable alternatives. One run/seed per condition is the default. Failed candidates inform the next method proposal, and all outcomes remain visible in the research record. The Skill sets no universal comparator count.

The Skill preserves metric, protocol, threshold, benchmark, and API freeze rules. It does not promise score gains or acceptance, authorize costly execution, or permit favorable result selection.

## Included files

- `SKILL.md` — workflow and non-negotiable research invariants
- `references/iteration-policy.md` — continuation, evidence, and reporting boundaries
- `templates/method-iteration.template.md` — reusable per-round record
- `agents/openai.yaml` — Codex UI metadata
- `VERSION` and `CHANGELOG.md` — release identity and changes
