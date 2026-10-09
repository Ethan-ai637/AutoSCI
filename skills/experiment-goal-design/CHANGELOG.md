# Changelog

## 4.0.0

- Add an explicit per-condition matrix with method role, factor levels, linked goals/protocols, randomness mode, and one-run default.
- Complete evaluation-protocol provenance with separate metric entrypoint, source IDs, and exact scope/loader/evaluator/metric locators.
- Define campaign grouping: combine goals only when one benchmark, stage, condition matrix, question, and decision rule can represent them truthfully; split incompatible groups.
- Require an owner-approved `protocol.md` before execution handoff and add a reusable protocol draft template with an approval section.
- Keep config/source hashes, run IDs, checkpoint policy, manifests, and full-scope resource estimates in execution preparation.

## 3.0.0

- Replace the single benchmark slot with goal-linked evaluation protocol entries, supporting multi-benchmark and non-benchmark study designs.
- Complete the handoff map for campaign stage, research question, decision rule, seed/randomness policy, conditions, runs, benchmark protocol, and execution-owned resource/provenance details.
- Clarify that each official benchmark requires its own full-scope campaign under the current one-benchmark campaign schema.
- Make late seed search for a higher score explicitly optional, with selection disclosure and preservation of all tried outcomes.
- Make threshold template comments operational: identify metric/comparator/population/direction, distinguish source rule from proposed cutoff, and show source-to-input derivation.
- Replace a misleading `claim_type` pseudo-enum string with a blank field and allowed-value comment.
- Use an explicit blank plus allowed-value comments for protocol/source enums so a template placeholder is not mistaken for a chosen value.

## 2.0.0

- Forbid hand-picked subsets of named official benchmarks, including when a narrower claim is asserted; require full official scope or another complete population/official track.
- Add a concrete anchor-source selection and representativeness procedure without imposing a paper-count quota.
- Record the experimental factor, controlled variables, and protocol deviations in the goal and comparison artifacts.
- Align numeric threshold fields and evidence categories with the `experiment-execution` campaign schema and document the one-to-one handoff map.
- Support multiple threshold sources, add a decision owner, and limit resource/repository constraints to operational gates rather than scientific success criteria.
- Clarify that `research-idea-scout` is optional and may not be installed with AutoSCI.

## 1.0.0

- Initial release: define claim-aligned goals using a source-linked comparability map.
- Require evidence and applicability for every numerical decision threshold; unsupported cutoffs are removed rather than guessed.
- Make one run/seed the default and treat additional repeats as optional unless the claim or official protocol requires them.
- Add a reusable experiment goal contract template and threshold-evidence guidance.
