# Section contracts and claim families

## Why claim families exist

The same scientific conclusion often appears in several places: a compressed form in the Abstract, a quantitative form in Results, an interpreted form in Discussion, and a bounded form in the Conclusion. Those sentences should not be independent copies.

Assign them one `claim_family_id` when they express the same underlying scientific proposition. Each sentence still receives its own `claim_id` because section function and wording differ.

Example:

- `C021` / `F004` / Results — quantitative primary result;
- `C044` / `F004` / Abstract — compressed quantitative result;
- `C071` / `F004` / Discussion — interpretation of that result;
- `C090` / `F004` / Conclusion — bounded takeaway.

A family is a dependency relation, not permission to copy the same sentence everywhere.

## Section contracts

### Abstract
Only report results that have a body counterpart. Quantitative statements must remain traceable to the same evidence family as Results. Do not introduce a new subgroup, endpoint, or mechanism for the first time.

### Results
This is the authoritative prose home for empirical findings. Keep comparator, population, endpoint, timepoint, estimate, uncertainty, and figure/table reference unambiguous.

### Discussion
Interpret a Results family; do not create a new empirical family unless it is explicitly non-empirical literature context. Link interpretations to the result evidence and any literature evidence that the interpretation requires.

### Conclusion
Use the narrowest accurate family-level takeaway. Do not upgrade descriptive or associational evidence to causal language and do not omit a limitation that materially changes the takeaway.

## `section_plan.json`

For full-manuscript work, use `section_plan.json` to declare which claim families each section must cover. The plan is an audit aid, not a prose outline. It should stay short and evidence-driven.

When the evidence changes, impact analysis first marks directly linked claims, then propagates review to every member of the affected claim family. Propagation means “must be re-checked,” not “must be rewritten.”
