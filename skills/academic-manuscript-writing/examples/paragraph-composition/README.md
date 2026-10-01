# Paragraph composition example

Synthetic release-profile example showing a multi-claim Discussion paragraph. `C003` requires `CQ1` in the same paragraph, and `P001` records the intended `qualified` composition.

Run:

```bash
python ../../scripts/preflight.py . --profile release --report qa_report.json
```

Removing `CLAIM:CQ1`, deleting `PARAGRAPH:P001`, or removing the required qualifier text should make release preflight fail.
