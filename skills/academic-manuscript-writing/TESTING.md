# Testing and release verification

The deterministic scripts use the Python standard library only. The declared **syntax floor** is Python 3.8. `scripts/self_test.py` is itself written with Python-3.8-compatible syntax and mechanically parses every deterministic script against the Python 3.8 grammar, so a newer development interpreter cannot silently introduce unsupported syntax. Syntax-floor validation is not a substitute for executing the suite on Python 3.8; if the repository publicly promises Python 3.8 runtime support, CI should include a Python 3.8 job in addition to the current supported interpreter.

## One-command self-test

From the skill root:

```bash
python scripts/self_test.py --quick
```

Quick mode checks package/version hygiene and runs representative `release` preflights for:

- `examples/minimal/` — legacy v1.6 compatibility;
- `examples/revision-lifecycle/` — legacy v1.5 state-lineage compatibility;
- `examples/conflict-disposition/` — v1.7.x source-conflict governance;
- `examples/full-release-span/` — v1.8 exact-span full-release behavior;
- `examples/dynamic-writing-profile/` — v2.0 runtime writing-profile / manuscript-contract behavior.

For release preparation or CI, run:

```bash
python scripts/self_test.py --full
```

Full mode runs every packaged positive fixture and then creates temporary destructive mutations that must be rejected by release QA. For CI matrices or execution environments with short per-command limits, the same suite can be sharded:

```bash
python scripts/self_test.py --full --shard 1/4
python scripts/self_test.py --full --shard 2/4
python scripts/self_test.py --full --shard 3/4
python scripts/self_test.py --full --shard 4/4
```

The positive fixtures are partitioned deterministically across shards; destructive tests run in shard 1 so the union of all shards is equivalent to the full test contract.

The destructive mutations include:

- a missing `END-CLAIM` marker;
- exact claim-span text drift;
- material scientific prose outside governed spans;
- venue specificity without an official writing source;
- a stale `manuscript_contract.json` after `writing_profile.json` changes;
- writing-context/submission-stage mismatch;
- article-type mismatch against the registered official source;
- track mismatch against the registered official source;
- removal of a venue-required section;
- an unresolved/pending manual venue-compliance check.

The destructive tests operate on temporary copies and do not modify the packaged examples.

## Machine-readable report

```bash
python scripts/self_test.py --full --json-report self_test_report.json
```

Do not commit generated `self_test_report.json`, `qa_report.json`, `__pycache__/`, or `.pyc` files.

## Package smoke test

After creating a ZIP, extract it to a fresh directory and run:

```bash
python scripts/self_test.py --quick
```

A release package should not be declared healthy only because the source-tree test passed; the extracted artifact must also pass.

## Expected result

A healthy package exits with status `0`, reports `"ok": true`, and has no warnings in its positive release fixtures. Expected-fail destructive fixtures count as successful tests only when release QA rejects them.
