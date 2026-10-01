# Figure and table integration

## Figure/table evidence contract

For each object record:

- object ID and version;
- panel IDs;
- population/condition;
- axes/units/encodings;
- statistical annotations;
- what each panel directly supports;
- what requires an external statistical test;
- caption source and status.

## Visual trend vs tested effect

A visual separation is not automatically a statistically supported difference. Conversely, a statistically estimated effect may be difficult to see in a compressed figure. Keep those evidence types distinct.

## Cross-reference safety

Treat the source ID as object identity and the figure/table number as a display label. When `sources.jsonl` provides `object_label`, claim-level `object_refs` must resolve to the same object number. `Fig. 2` and `Figure 2` are equivalent labels for one object; `Fig. 2` and `Fig. 3` are not.

When figure/table numbering changes, search and update:

- main text;
- abstract/highlights when they mention the object;
- captions;
- supplement;
- reviewer-response text;
- cross-references such as “above/below/left/right”.

## Captions

A good scientific caption should make the visual interpretable without forcing the reader to recover basic definitions from Methods. Include panel mapping, groups, units, summary-statistic conventions, error-bar meaning, statistical annotations, and abbreviations as needed.

Do not add a conclusion to the caption that is stronger than the analysis.
