#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
import numpy as np
import pandas as pd
from _common import read_table, write_json, sha256_file, SKILL_VERSION, typed_nunique, typed_row_duplicate_mask, typed_scalar_key, jsonable_level


def main():
    ap = argparse.ArgumentParser(description="Profile a scientific tabular dataset without making cleaning/test decisions.")
    ap.add_argument("input")
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    df = read_table(args.input)
    cols = []
    for c in df.columns:
        s = df[c]
        info = {
            "column": str(c),
            "dtype": str(s.dtype),
            "n": int(len(s)),
            "missing_n": int(s.isna().sum()),
            "missing_fraction": float(s.isna().mean()),
            "unique_n": int(typed_nunique(s, dropna=True)),
        }
        if pd.api.types.is_numeric_dtype(s):
            q = s.dropna().astype(float)
            if len(q):
                info.update({
                    "min": float(q.min()), "q1": float(q.quantile(.25)),
                    "median": float(q.median()), "mean": float(q.mean()),
                    "q3": float(q.quantile(.75)), "max": float(q.max()),
                    "sd": float(q.std(ddof=1)) if len(q) > 1 else None,
                })
        else:
            counts = {}
            first = {}
            for v in s.tolist():
                key = typed_scalar_key(v)
                if key[0] == "missing":
                    continue
                counts[key] = counts.get(key, 0) + 1
                first.setdefault(key, v)
            top = sorted(counts.items(), key=lambda kv: (-kv[1], repr(kv[0])))[:10]
            info["top_values"] = [
                {"value": jsonable_level(first[k]), "value_type": k[0], "count": int(n)} for k, n in top
            ]
        cols.append(info)

    out = {
        "skill_version": SKILL_VERSION,
        "input": str(Path(args.input)),
        "sha256": sha256_file(args.input),
        "rows": int(len(df)),
        "columns": int(df.shape[1]),
        "exact_duplicate_rows": int(typed_row_duplicate_mask(df, keep="first").sum()),
        "column_profiles": cols,
    }
    write_json(out, args.out)
    print(f"Wrote {args.out}")

if __name__ == "__main__":
    main()
