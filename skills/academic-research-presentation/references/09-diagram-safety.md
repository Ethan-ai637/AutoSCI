# Diagram Safety Gate

Custom diagrams are HIGH-RISK scientific objects.

Their purpose is to clarify verified structure, not invent structure.

## 1. Diagram necessity gate

Before drawing a custom flowchart, answer:

- What scientific question requires a diagram?
- Which source section/figure/equation defines the process?
- Why is the source visual insufficient?
- What understanding is gained versus plain text/table/equation?

If the answer is only “an overview would look nice”, do not draw it.

## 2. Diagram provenance contract

Create a diagram spec before implementation.

Required fields:

```yaml
diagram_id:
scientific_question:
source_basis:
flow_direction: LR | RL | TB
nodes:
  - id:
    label:
    source_basis:
    role:
edges:
  - from:
    to:
    relation:
    source_basis:
side_inputs:
feedback_edges:
frozen_components:
train_only_components:
inference_only_components:
```

Every node and every edge must be source-supported.

## 3. Ordered-process rule

Do not infer ordering from how nodes are visually arranged.

Write the explicit sequence first:

`point forecast -> probabilistic post-processing -> quantile features -> price model`

Then render exactly that direction.

For LR flow:
- upstream node is left;
- downstream node is right;
- arrowhead touches/points toward downstream target.

For TB flow:
- upstream node is above;
- arrowhead points downward to target.

## 4. Arrowhead hard check

After rendering:
- inspect every arrow;
- say aloud/read `A -> B`;
- verify arrowhead is at B;
- verify B is the scientific target.

If a single forward arrow is reversed, the slide FAILS.

Do not assume connector libraries interpret start/end in the expected direction.

## 5. Side-input completeness

Methods often have non-linear dependencies.

Examples:
- historical actuals calibrate probabilistic post-processing;
- training data enters a model from the side;
- reward/evaluator feeds back into an update;
- frozen backbone is not “produced” by the previous step.

Do not force these into a fake single chain.

Represent side inputs explicitly or use another visual grammar.

## 6. No mysterious transformation

An arrow is a scientific claim.

Label transformations when not obvious:
- calibrate;
- fit;
- sample;
- aggregate;
- optimize;
- retrieve;
- update;
- select with LASSO.

Do not connect boxes with unlabeled arrows when the operation itself is important.

## 7. Avoid redundant overview diagrams

Do not create multiple generic overview pipelines in the same short deck.

One verified overview + later zoom-in slides is usually enough.

## 8. Diagram alternatives

Prefer alternatives when appropriate:

- two-column “input / role” table;
- equation + annotation;
- timeline;
- source method figure;
- algorithm excerpt;
- before/after comparison;
- aligned text with simple arrows, no containers.

## 9. Semantic box rule

Boxes represent entities/components, not paragraphs.

Valid:
`Probabilistic post-processor`, `Price model`, `Memory`.

Invalid:
a box containing “Advantages: robust, flexible, efficient”.

## 10. Diagram QA checklist

[ ] diagram is necessary
[ ] all nodes source-supported
[ ] all edges source-supported
[ ] flow_direction declared
[ ] source/target edge list exists
[ ] arrowheads verified after render
[ ] side inputs shown
[ ] feedback shown only if real
[ ] training vs inference not conflated
[ ] no scientifically meaningful input omitted for aesthetic simplicity
[ ] no redundant duplicate overview
