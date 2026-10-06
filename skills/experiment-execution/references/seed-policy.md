# Seed and Stage Policy

Every condition declares `randomness_mode`: `seeded_stochastic`, `uncontrolled_stochastic`, or `deterministic`. Do not invent a seed when the method/API cannot control randomness.

## Pilot/screening

- Use exactly one predeclared run per condition: one seed for `seeded_stochastic`, one `replicate_id` for `uncontrolled_stochastic`, and one seedless run for `deterministic`.
- The one-run pilot rule is a repository policy for limiting screening cost and preventing seed shopping; it is not a statistical recommendation for estimating performance or variance. Never use the pilot as confirmatory evidence.
- Run the complete official benchmark scope even in a pilot. The pilot economizes on seeds and conditions, not examples/tasks.
- Use the pilot only for gross execution checks and a predeclared continue/stop decision. Do not report its single-seed result as robust, statistically significant, or confirmatory.
- Do not launch a seed grid before deciding which conditions merit confirmation.

## Confirmatory runs

- One seed/replicate is sufficient for an ordinary run unless the benchmark protocol or the claim being tested requires repeated-run uncertainty estimates. Multiple seeds are optional, not a default requirement. If the analysis will estimate between-run variation or compare stochastic methods statistically, choose the count from the benchmark protocol or a predeclared power/precision design and cite the assumptions; do not invent a universal count.
- If additional seeds are used to search for a higher-scoring final run, classify the work as score optimization/selection, predeclare a finite seed set and selection rule, preserve every tried seed and outcome, and disclose the selection. Do not present the selected run as an unbiased estimate, robustness result, or confirmatory evidence. For claim-bearing reporting, follow the benchmark's official aggregation/selection protocol; never choose a favorable seed after seeing scores unless the research question explicitly studies that selection strategy.
- Freeze any multi-run statistical analysis and run count before observing those outcomes. A later seed search is a separate exploratory optimization stage, not a retroactive confirmatory campaign.
- Run each planned seed over the full benchmark scope. Seeds are not a license to average away incomplete tasks or failed attempts.
- For `deterministic` conditions, declare why one run is sufficient and keep all other sources of randomness controlled/recorded. If one campaign mixes deterministic and stochastic conditions, apply the appropriate rule to each condition separately.

## Seed identity

Record the seed at every source of stochasticity that the method exposes: model initialization, data order, augmentation, environment/task randomness, and evaluation sampling when part of the official benchmark. For APIs/models with non-controllable randomness, record `uncontrolled_stochastic`, use distinct replicate IDs, and record available sampling parameters, model/version identifiers, and request settings.

Use a fixed seed list rather than “try seeds until the result looks good.” Preserve every failed/interrupted/OOM attempt and every completed run. Never select the best seed unless the paper's comparison protocol explicitly requires best-of-N and that rule was declared before execution.
