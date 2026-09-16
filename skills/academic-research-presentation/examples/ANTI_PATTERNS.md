# Anti-patterns — What V3 Must Catch

## A. Reversed-arrow pipeline

Visual order:
A   B   C   D

But arrows point:
A <- B <- C <- D

while the intended scientific process is A -> B -> C -> D.

This is a HARD FAIL, not a cosmetic issue.

## B. Magic pipeline

A clean linear chain omits historical actuals, calibration data, side inputs,
feedback, or training-only signals.

Even if every arrow points the right way, the diagram is scientifically wrong.

## C. Figure crop with page debris

A supposed figure includes:
- half of an author name;
- journal title at the top;
- partial caption/body text below.

FAIL. Reacquire the figure.

## D. Clean crop that removes science

The image looks neat but cuts off:
- x-axis categories;
- y-axis title;
- legend;
- color scale;
- lower part of plotted curves.

FAIL. Scientific completeness wins over neat cropping.

## E. Two incomplete figures on one slide

Two plots are clipped to fit beside explanation text.

Split into separate slides unless direct comparison requires both and both
remain fully readable.

## F. Flowchart by reflex

The slide says “method overview”, so the generator creates boxes and arrows even
though the source method is better explained by an equation/table/source figure.

Reject the diagram. Choose a scientific-object-driven grammar.
