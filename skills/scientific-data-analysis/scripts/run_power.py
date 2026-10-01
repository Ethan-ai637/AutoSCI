#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
import pandas as pd

from _common import read_json, sha256_file, write_json, SKILL_VERSION, POWER_PLAN_SCHEMA_VERSION
from validate_power_plan import validate
from _power import expand_and_calculate


def main():
    ap = argparse.ArgumentParser(description="Run prospective power/sample-size planning")
    ap.add_argument("--plan", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--out-json")
    args = ap.parse_args()

    plan = read_json(args.plan)
    errors, warnings = validate(plan)
    for w in warnings:
        print(f"WARNING: {w}")
    if errors:
        for e in errors:
            print(f"ERROR: {e}")
        raise SystemExit(1)

    plan_hash = sha256_file(args.plan)
    rows = expand_and_calculate(plan)
    for row in rows:
        row["plan_sha256"] = plan_hash
        row["skill_version"] = SKILL_VERSION
        row["power_plan_schema_version"] = POWER_PLAN_SCHEMA_VERSION
        if row.get("type") == "independent_proportions":
            adequacy = row.get("normal_approximation_adequacy")
            m = row.get("min_expected_cell_count")
            if adequacy == "poor_extreme_sparsity":
                print(
                    f"WARNING: {row.get('planning_item_id')}::{row.get('scenario_id')} has extreme sparsity "
                    f"for the two-proportion normal approximation (minimum expected count={float(m):.6g} < 1); "
                    "power preflight will fail this result for release"
                )
            elif adequacy == "caution_sparse":
                print(
                    f"WARNING: {row.get('planning_item_id')}::{row.get('scenario_id')} has sparse expected counts "
                    f"for the two-proportion normal approximation (minimum expected count={float(m):.6g} < 5)"
                )

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_csv(out, index=False)
    if args.out_json:
        write_json(rows, args.out_json)
    print(f"Wrote {out} ({len(rows)} planning scenario row(s))")


if __name__ == "__main__":
    main()
