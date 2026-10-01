# Claim–evidence audit

## Objective

Determine whether the **strength, scope, and type** of important manuscript claims are matched by direct evidence.

Run this audit on atomic propositions rather than treating multi-clause scientific sentences as indivisible claims.

## Procedure

For each central atomic claim:
1. Identify exact wording, parent sentence, and location.
2. Classify claim type.
3. Preserve explicit scope: dataset/population/domain/model/metric/perturbation/time/operating condition.
4. Identify the evidence the manuscript appears to rely on.
5. Ask whether that evidence directly tests the claim type.
6. Compare evidence scope with claim scope.
7. Check uncertainty/statistical requirements implied by the wording.
8. Consider plausible competing explanations for causal/mechanistic claims.
9. Search nearby text, captions, notes, appendix, and limitations for qualifiers.
10. Assign an evidence state.
11. Cross-check whether sibling atomic claims from the same sentence rely on different evidence.
12. Report only material mismatches after adversarial verification.

## Inference-bridge rule

For causal, mechanistic, extrapolative, proxy-to-construct, deployment/utility, and null/equivalence claims, do not stop after locating a related result. Use `inference_chain_and_traceability.md` to test whether the observed result actually licenses the conclusion.

A result may be valid while the bridge from that result to the stated conclusion is not.

## Common failure patterns

### Clause spillover
A compound statement claims A, B, and C; evidence directly supports A, and the reviewer/manuscript implicitly treats B and C as supported as well.

Assess each proposition independently before recombining the review finding.

### Unsupported universal quantifier
Words such as `all`, `always`, `consistently`, `universally`, `across settings`, `robust to`, `generalizes to` require evidence spanning the stated scope.

Averages do not prove per-condition universality.

### Ranking inflation
Claim: “best”, “state of the art”, “outperforms existing methods”.
Check:
- all relevant rows/columns;
- metric direction;
- uncertainty/significance where relevant;
- direct protocol comparability;
- imported vs rerun baselines;
- whether the claim concerns average rank, mean metric, or every condition.

### Mechanism leap
Ablation/component removal can show contribution but does not automatically establish **why** a component works.

Mechanism claims need mechanism-specific evidence such as controlled interventions, diagnostic analyses, mediation-style evidence, or other designs appropriate to the field.

### Robustness leap
One perturbation, one dataset, one seed, or a few selected examples do not establish broad robustness.

Clarify which axis of robustness was tested: seed, noise, corruption, adversarial perturbation, domain shift, hyperparameter sensitivity, temporal shift, etc.

### Generalization leap
In-domain or closely related benchmark gains do not establish out-of-domain, cross-population, cross-domain, temporal, or real-world generalization unless those conditions are tested.

### Efficiency leap
Parameter count alone does not establish runtime, memory, energy, cost, throughput, latency, or sample efficiency.

Identify the exact efficiency dimension measured.

### Practicality leap
Benchmark gains do not establish deployment readiness, clinical utility, industrial usefulness, safety, cost effectiveness, or human benefit without corresponding evidence.

### Statistical language without statistical evidence
Terms such as `significant`, `stable`, `reliable`, `consistent`, `equivalent`, or `no difference` can imply requirements beyond point estimates.

Check repeated trials, variance, confidence intervals, tests, equivalence/non-inferiority design, and sample size where contextually appropriate.

### Absence-of-evidence leap
“No failure was observed” is not equivalent to “the method is safe/reliable”.
“Not statistically significant” is not equivalent to “the methods are equivalent”.

### Proxy leap
Improvement on a proxy metric does not automatically establish improvement in the underlying broad construct (e.g. usefulness, factuality, fairness, interpretability, clinical benefit).

## Evidence strength matching

Use claim-type-specific reasoning:
- descriptive claim → direct observation/result;
- comparative claim → comparable baseline result;
- causal claim → design capable of supporting causality;
- generalization claim → evaluation outside the development/test scope claimed;
- robustness claim → perturbation/variation aligned to the robustness axis;
- statistical claim → uncertainty/inference evidence appropriate to wording;
- practical/safety claim → task-relevant downstream or real-world evidence.

## Do not over-flag

- Local context may legitimately constrain scope without repeating qualifiers every sentence.
- Do not demand causal evidence for explicitly associative wording.
- Do not require statistical tests in domains/claims where the manuscript is not making inferential or stability claims.
- Do not treat lack of one preferred experiment as fatal if another valid design supports the same claim.
- Do not report a compound sentence as wholly unsupported when only one atomic clause is problematic; identify the affected proposition precisely.
