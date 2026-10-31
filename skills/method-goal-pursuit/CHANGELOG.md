# Changelog

## 1.2.0

- Add evidence-led benchmark selection for task relevance, real-world grounding, documented difficulty, evaluation validity, and access.
- Require benchmark choice to be recorded and frozen before outcome access; preserve the full official scope across every condition.
- Add benchmark selection evidence and rationale to the iteration record template.
- Self-audit finding: v1.1.0 protected full scope after selection but did not explain how to choose conclusion-relevant, challenging, real-world benchmarks.

## 1.1.0

- Make the main experiment the center of every method-pursuit iteration.
- Require a small, rationale-selected set of relevant baselines and SOTA methods, without a universal comparator-count rule.
- Require public code under a compatible open-source license and downloadable required artifacts for controlled SOTA comparisons; replace inaccessible methods with a comparable open-source alternative.
- Record comparator selection and omission rationale while keeping the full official benchmark scope and equal-budget comparison.

## 1.0.0

- Initial release for persistent, evidence-led method-paper goal pursuit.
- Require a concrete method candidate, falsifiable hypothesis, complete-scope experiment, and equal-budget baseline in every iteration.
- Preserve the declared contribution, venue target, benchmark contract, metrics, thresholds, and API freeze rules across method revisions.
- Keep one seed per condition as the default and preserve every outcome, including failures.
- Prevent diagnosis-only or NO-GO-only reports from serving as the sole iteration deliverable.
