# Seed and Stage Policy

Every condition declares `randomness_mode`: `seeded_stochastic`, `uncontrolled_stochastic`, or `deterministic`. Do not invent a seed when the method/API cannot control randomness.

## Pilot/screening

- Use exactly one predeclared run per condition: one seed for `seeded_stochastic`, one `replicate_id` for `uncontrolled_stochastic`, and one seedless run for `deterministic`.
- The one-run pilot rule is a repository policy for limiting screening cost and preventing seed shopping; it is not a statistical recommendation for estimating performance or variance. Follow a stricter local policy if present, and never use the pilot as confirmatory evidence.
- Run the complete official benchmark scope even in a pilot. The pilot economizes on seeds and conditions, not examples/tasks.
- Use the pilot only for gross execution checks and a predeclared continue/stop decision. Do not report its single-seed result as robust, statistically significant, or confirmatory.
- Do not launch a seed grid before deciding which conditions merit confirmation.

## Confirmatory runs

- Freeze the condition/config set and seed list in the protocol before confirmatory outcomes are observed.
- Use at least two distinct seeds for `seeded_stochastic` conditions and at least two declared replicate IDs for `uncontrolled_stochastic` conditions. This is only the mathematical floor for obtaining a between-run sample-variance estimate; it is not enough by itself to establish adequate power or precision. Choose the actual count from a benchmark-mandated protocol or a predeclared power/precision analysis based on the estimand, effect of interest, and variance evidence. Document assumptions and cite the basis. If that count is unaffordable, reduce conditions before seed count or mark the confirmatory claim underpowered/incomplete; do not imply the two-run floor is statistically sufficient.
- Run each planned seed over the full benchmark scope. Seeds are not a license to average away incomplete tasks or failed attempts.
- For `deterministic` conditions, declare why one run is sufficient and keep all other sources of randomness controlled/recorded. If one campaign mixes deterministic and stochastic conditions, apply the appropriate rule to each condition separately.

## Seed identity

Record the seed at every source of stochasticity that the method exposes: model initialization, data order, augmentation, environment/task randomness, and evaluation sampling when part of the official benchmark. For APIs/models with non-controllable randomness, record `uncontrolled_stochastic`, use distinct replicate IDs, and record available sampling parameters, model/version identifiers, and request settings.

Use a fixed seed list rather than “try seeds until the result looks good.” Preserve every failed/interrupted/OOM attempt and every completed run. Never select the best seed unless the paper's comparison protocol explicitly requires best-of-N and that rule was declared before execution.
