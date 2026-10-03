# PAPER_ONLY Reconstruction

## Objective

Build the smallest explicit implementation needed to test a selected paper claim when no usable author repository exists.

## Classification of implementation details

Every material implementation element should be one of:

- `paper_specified`
- `mechanically_derived`
- `assumption_required`
- `unknown_unimplemented`

Examples:

- Eq. 3 directly translated into code → `mechanically_derived`.
- learning rate explicitly stated in Methods → `paper_specified`.
- optimizer chosen because “Adam is common” → `assumption_required`.
- tokenization rule absent and left unresolved → `unknown_unimplemented`.

## Assumption discipline

For each assumption record:

- affected component;
- chosen value/behavior;
- why the paper does not determine it;
- rationale for the temporary choice;
- expected impact;
- whether it is reversible/parameterized.

Do not hide assumptions inside code defaults.

## Language

Call the result an “independent reconstruction under recorded assumptions” when material details are not author-specified. Avoid language implying execution of the original implementation.
