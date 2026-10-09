# Experiment Goal Design

**Version:** 4.0.0

Use this Skill after an idea or hypothesis exists and before implementation. It aligns goals to relevant field literature and official benchmark protocols, and requires strict evidence for numerical gates.

Version 4.0.0 adds explicit condition/randomness rows, full protocol source locators, complete campaign grouping/handoff rules, and a protocol draft that requires owner approval before execution. Multiple evaluation protocols remain linked to goals; each named official benchmark retains its full scope and receives separate campaigns when its scope or decision contract differs. Late seed selection is explicitly optional and must be disclosed.

## Included files

- `SKILL.md` — workflow and handoff
- `references/evidence-and-thresholds.md` — source appraisal and numerical decision rules
- `templates/experiment_goal_contract.template.yaml` — claim and goal contract
- `templates/comparability_matrix.template.csv` — paper/protocol comparison ledger
- `templates/protocol.template.md` — owner-reviewable protocol draft for approval before execution
- `templates/goal_design_note.template.md` — concise decisions and unresolved issues

The Skill defaults to one run/seed per condition. Additional runs are optional unless required by the declared claim or official protocol. It never treats a guessed score gain, p-value, dataset count, or seed count as a valid gate.
