# Overclaim audit

## Objective

Find places where manuscript wording expands beyond the evidence actually presented or verified.

## Compare these surfaces

- title;
- abstract;
- introduction/contributions;
- result narration;
- discussion;
- conclusion;
- limitations.

Claims often broaden as they move away from the primary result object.

## Required reasoning structure

For each overclaim finding identify:
1. **evidence scope** — what was actually tested or established;
2. **claim scope** — what the manuscript wording asserts;
3. **scope jump** — the exact extra inference;
4. **minimal fix** — qualifier, narrower wording, or additional evidence needed.

## Overclaim patterns

### Sample → population
Limited dataset/population becomes a broad population-level claim.

### Benchmark → real world
Offline benchmark performance becomes deployment/clinical/industrial effectiveness.

### Association → causation
Correlation/observational difference becomes “causes”, “leads to”, “drives”, or “explains”.

### Ablation → mechanism
Component removal hurts performance, therefore the proposed internal mechanism is asserted as proven.

### Metric → broad quality
One metric becomes “better model”, “higher quality”, “more useful”, “more reliable”, “more fair”, or “more interpretable” without direct evidence for the broader construct.

### Average → universal
Mean improvement becomes “consistently”, “always”, or “across all settings” despite exceptions or untested conditions.

### In-domain → generalization
Similar benchmark performance becomes broad OOD/cross-domain/cross-population/general-world generalization.

### Limited perturbation → robustness
One or two perturbation types become broad robustness.

### Parameter count → efficiency
Smaller model becomes faster/cheaper/greener without measuring the relevant efficiency dimension.

### Non-significance → equivalence
Failure to detect a difference becomes proof of equivalence, parity, or “no difference”.

### No observed harm → safety
Absence of observed failures becomes safe/reliable/risk-free.

### Proxy → construct
A proxy score is treated as direct evidence of a broader latent property.

### Selected examples → typical behavior
A few qualitative examples become claims about general or typical performance without systematic evidence.

### Short horizon → durability
Short-term results become claims about long-term persistence, stability, or downstream effect.

## Minimal correction preference

Prefer the smallest scientifically correct repair:
- “on the evaluated datasets”;
- “under the tested settings”;
- “is associated with” instead of “causes”;
- “reduces parameter count” instead of “is more efficient”;
- “we did not observe X in these experiments” instead of “the method is safe from X”.

If the broader claim is central and scientifically important, adding appropriate evidence may be preferable to weakening the wording.
