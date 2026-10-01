# Notation audit

## Objective

Ensure mathematical and technical symbols preserve one interpretable meaning throughout the manuscript and that notation problems are not artifacts of PDF extraction.

## Build a notation ledger

For every important symbol, record:
- rendered symbol;
- first definition location;
- semantic meaning;
- type/dimension when inferable;
- index/range;
- scalar/vector/matrix/set/random variable/operator role;
- local/global scope;
- later redefinitions or variants.

## PDF visual-verification rule

Parsed PDF text may corrupt:
- superscripts/subscripts;
- Greek letters;
- bold/italic vector notation;
- calligraphic symbols;
- minus signs/dashes;
- hats/bars/tildes;
- equation alignment.

Before issuing a High-confidence Major/Critical notation finding, inspect the rendered page whenever extraction could plausibly be responsible.

## Checks

### Definition before use
Flag symbols used materially before any reasonable definition.

Do not over-flag symbols whose meaning is standard and immediately obvious from a tightly scoped equation, unless ambiguity affects implementation.

### Symbol collision
Same symbol used for different concepts without clear local scoping.
Examples:
- `N` = number of nodes, later number of samples;
- `d` = dimension, later distance;
- `p` = probability, later feature vector.

### Silent redefinition
Meaning changes across sections/equations without explicit notice.

### Near-collision
Potentially consequential typography:
- `l` vs `1`;
- `O` vs `0`;
- uppercase/lowercase variants;
- bold vs non-bold vectors;
- calligraphic vs plain sets;
- hat/tilde/bar variants.

Only flag when it can change interpretation.

### Index consistency
Check:
- `i`, `j`, `t`, `k` ranges;
- batch/sample/node/token index changes;
- summation bounds;
- off-by-one conventions;
- free vs bound indices;
- reused index symbols inside nested expressions.

### Dimension/type consistency
Where inferable, check compatible shapes/types:
- matrix multiplication dimensions;
- concatenation dimensions;
- scalar/vector use;
- broadcasting assumptions;
- probability/simplex constraints;
- set vs sequence semantics.

Do not invent missing dimensions. If shape information is insufficient, mark the check unresolved rather than asserting an error.

### Equation-to-prose consistency
Verify prose descriptions such as average, sum, normalize, maximize, minimize, expectation, probability, distance, or similarity match the equation.

### Objective sign / optimization direction
Check `min` vs `max`, loss vs reward, negative signs, temperature/inverse-temperature conventions, and regularization sign.

### Local scope and overload
Symbol reuse can be valid when scope is unambiguous. Do not flag every reuse across distant sections; flag only when readers could reasonably carry the old meaning into the new context.

### Acronyms and named objects
Treat recurring technical abbreviations similarly:
- stable expansion;
- stable model/component name;
- no silent drift between related but different objects.

## Severity guidance

- Cosmetic typography only: usually Minor.
- Ambiguity that affects understanding of a local derivation: Moderate.
- Two plausible implementations of a central method: Major.
- Core equation is internally inconsistent and central conclusions depend on it: potentially Critical, but only with direct verification.
