# Experiment Goal Design — Independent Audit Log

Three separate read-only audit rounds were completed before publication. Each round reviewed that version of the Skill against the research-goal, evidence-threshold, benchmark-scope, seed, and downstream-handoff requirements. Every round was followed by a major-version upgrade and a complete Skill ZIP release.

| Round | Audited version | Main findings | Resulting release |
| --- | --- | --- | --- |
| 1 | 1.0.0 | Close a benchmark-subset loophole; align threshold fields with the execution schema; make anchor-source selection and multi-source evidence explicit; clarify optional upstream Skill routing. | 2.0.0: full official scope, schema-aligned thresholds, controlled-variable mapping, and stronger source selection. |
| 2 | 2.0.0 | Support multiple goal-linked evaluation protocols; map stage, claim/question, decision rule, per-condition randomness/runs, and execution-owned resource fields; make threshold instructions directly usable in the template. | 3.0.0: multi-protocol contract and complete campaign handoff; explicit optional, disclosed seed selection. |
| 3 | 3.0.0 | Add executable condition rows; add metric entrypoint and protocol source locators; define campaign grouping; require an owner-approved protocol artifact before execution. | 4.0.0: condition matrix, source-complete protocols, compatible campaign grouping, and approval-gated protocol draft. |

## Final release checks

- Skill Creator quick validation passed for v4.0.0.
- The goal-contract and Codex interface YAML parse successfully.
- The goal/protocol/condition/source template links and comparability-matrix headers were checked.
- All four versioned ZIP archives pass ZIP integrity and SHA-256 checks; v4.0.0 archive contents match every file in the released Skill directory.
- Both README files resolve their local links and describe the current Skill version.

The audits are design reviews, not scientific validation of any particular experiment. A future study must still resolve sources, benchmark versions, scopes, and thresholds for its own field and claim.
