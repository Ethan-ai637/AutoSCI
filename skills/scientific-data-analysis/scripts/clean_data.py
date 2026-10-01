#!/usr/bin/env python3
from __future__ import annotations

import argparse
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

from _common import (
    read_json, read_table, write_table, table_roundtrip_identity_mismatches, sha256_file, write_json, SKILL_VERSION,
    categorical_level_key, categorical_level_mask, categorical_levels_mask, jsonable_level,
    typed_duplicate_mask, typed_nunique, typed_row_duplicate_mask,
)
from validate_plan import validate


def log_drop(logs, row_id, rule_id, reason, column=None, value=None):
    logs.append({
        "_row_id": row_id,
        "rule_id": rule_id,
        "reason": reason,
        "column": column or "",
        "value": "" if value is None else value,
    })


def _check_columns(df, columns, label):
    missing = [c for c in columns if c not in df.columns]
    if missing:
        raise KeyError(f"{label} column(s) not found: {missing}")


def _coerce_numeric_with_audit(df, col, logs, rule_prefix):
    _check_columns(df, [col], rule_prefix)
    original = df[col]
    numeric = pd.to_numeric(original, errors="coerce")
    bad = original.notna() & numeric.isna()
    for _, r in df.loc[bad, ["_row_id", col]].iterrows():
        log_drop(logs, int(r["_row_id"]), f"NONNUMERIC_{col}", "value is not numeric where numeric data were required", col, r[col])
    df = df.loc[~bad].copy()
    df[col] = pd.to_numeric(df[col], errors="coerce")
    return df


def _typed_unique(values):
    out = []
    seen = set()
    for v in values:
        try:
            if pd.isna(v):
                key = ("missing", None)
            else:
                key = categorical_level_key(v)
        except Exception:
            key = categorical_level_key(v)
        if key not in seen:
            seen.add(key)
            out.append(v)
    return out


def _assert_no_grouping_identity_collisions(df, keys):
    """Reject group-by columns where pandas equality would merge typed levels."""
    for c in keys:
        typed = {categorical_level_key(v) for v in df[c].dropna().tolist()}
        pandas_unique = int(df[c].dropna().nunique())
        if len(typed) > pandas_unique:
            raise ValueError(
                f"technical replicate group_by column '{c}' contains equality-colliding categorical encodings "
                "(for example boolean/numeric aliases). Normalize the grouping key before aggregation."
            )


def _technical_replicate_aggregate(df, tech):
    keys = tech.get("group_by") or []
    value_cols = tech.get("value_columns") or []
    method = tech.get("method", "mean")
    _check_columns(df, keys + value_cols, "technical_replicates")
    _assert_no_grouping_identity_collisions(df, keys)

    for c in value_cols:
        vals = pd.to_numeric(df[c], errors="coerce")
        bad = df[c].notna() & vals.isna()
        if bad.any():
            examples = df.loc[bad, keys + [c]].head(5).to_dict("records")
            raise ValueError(f"technical replicate value column '{c}' contains nonnumeric values; examples={examples}")
        df[c] = vals

    carry = tech.get("carry_columns")
    if carry is None:
        carry = [c for c in df.columns if c not in set(keys) | set(value_cols) | {"_row_id"}]
    _check_columns(df, carry, "technical_replicates.carry_columns")

    # Metadata must be invariant within a technical-replicate group. Taking the
    # first value would silently hide group/condition conflicts.
    conflicts = []
    if carry:
        grouped = df.groupby(keys, dropna=False, sort=False)
        for c in carry:
            for group_key, frame in grouped:
                vals = _typed_unique(frame[c].tolist())
                if len(vals) <= 1:
                    continue
                if not isinstance(group_key, tuple):
                    group_key = (group_key,)
                conflicts.append({
                    "column": c,
                    "group": {k: jsonable_level(v) for k, v in zip(keys, group_key)},
                    "values": [None if pd.isna(v) else jsonable_level(v) for v in vals],
                })
                if len(conflicts) >= 10:
                    break
            if len(conflicts) >= 10:
                break
    if conflicts:
        raise ValueError(
            "Conflicting metadata inside technical-replicate groups. "
            "Resolve the scientific grouping or declare different group_by keys; "
            f"examples={conflicts[:10]}"
        )

    before = len(df)
    group_sizes = df.groupby(keys, dropna=False).size()
    groups_aggregated = int((group_sizes > 1).sum())
    rows_collapsed = int((group_sizes - 1).clip(lower=0).sum())
    named_aggs = {
        "_source_row_ids": ("_row_id", lambda x: ";".join(str(int(v)) for v in x)),
        "_technical_replicate_n": ("_row_id", "size"),
    }
    for c in value_cols:
        named_aggs[c] = (c, method)
    for c in carry:
        named_aggs[c] = (c, "first")
    out = df.groupby(keys, dropna=False, as_index=False, sort=False).agg(**named_aggs)
    out.insert(0, "_row_id", np.arange(1, len(out) + 1))
    return out, {
        "before_rows": before,
        "after_rows": int(len(out)),
        "groups_aggregated": groups_aggregated,
        "rows_collapsed": rows_collapsed,
        "group_by": keys,
        "value_columns": value_cols,
        "carry_columns": carry,
        "method": method,
        "metadata_conflict_policy": "error",
        "source_row_traceability_column": "_source_row_ids",
        "replicate_count_column": "_technical_replicate_n",
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True)
    ap.add_argument("--plan", required=True)
    ap.add_argument("--output", required=True)
    ap.add_argument("--log", required=True)
    ap.add_argument("--report", required=True)
    args = ap.parse_args()

    plan = read_json(args.plan)
    errors, warnings = validate(plan)
    if errors:
        raise ValueError("Invalid analysis plan: " + "; ".join(errors))
    for w in warnings:
        print(f"WARNING: {w}")

    cfg = plan.get("cleaning", {})
    expected_hash = (plan.get("input") or {}).get("sha256")
    actual_hash = sha256_file(args.input)
    if expected_hash and expected_hash.lower() != actual_hash.lower():
        raise ValueError(f"Input SHA-256 mismatch: plan={expected_hash} actual={actual_hash}")

    df = read_table(args.input).copy()
    reserved = {"_row_id", "_source_row_ids", "_technical_replicate_n"}
    collisions = sorted(reserved & set(df.columns))
    if collisions:
        raise ValueError(f"Raw input contains reserved provenance column(s) {collisions}; rename them before using this skill")
    df.insert(0, "_row_id", np.arange(1, len(df) + 1))
    start_n = len(df)
    logs = []

    tokens = cfg.get("missing_tokens", [])
    if tokens:
        # Apply missing-token replacement with the same typed scalar identity as
        # categorical selection. pandas.replace can silently downcast mixed
        # object columns (e.g. boolean/numeric identifiers) before later guards.
        for c in df.columns:
            if c == "_row_id":
                continue
            mask = categorical_levels_mask(df[c], tokens)
            if mask.any():
                df.loc[mask, c] = np.nan

    if cfg.get("drop_exact_duplicates", False):
        dup = typed_row_duplicate_mask(df.drop(columns=["_row_id"]), keep="first")
        for _, r in df.loc[dup, ["_row_id"]].iterrows():
            log_drop(logs, int(r["_row_id"]), "EXACT_DUPLICATE", "exact duplicate row")
        df = df.loc[~dup].copy()

    required = cfg.get("require_nonmissing", [])
    _check_columns(df, required, "require_nonmissing")
    for col in required:
        bad = df[col].isna()
        for _, r in df.loc[bad, ["_row_id"]].iterrows():
            log_drop(logs, int(r["_row_id"]), f"MISSING_{col}", "required value missing", col, None)
        df = df.loc[~bad].copy()

    numeric_cols = set(cfg.get("require_numeric", [])) | set(cfg.get("numeric_ranges", {}).keys())
    for col in sorted(numeric_cols):
        df = _coerce_numeric_with_audit(df, col, logs, "numeric requirement")

    for col, bounds in cfg.get("numeric_ranges", {}).items():
        vals = df[col]
        minv, maxv = bounds.get("min"), bounds.get("max")
        bad = pd.Series(False, index=df.index)
        if minv is not None:
            bad |= vals < float(minv)
        if maxv is not None:
            bad |= vals > float(maxv)
        for _, r in df.loc[bad, ["_row_id", col]].iterrows():
            log_drop(logs, int(r["_row_id"]), f"RANGE_{col}", "value outside declared valid range", col, r[col])
        df = df.loc[~bad].copy()

    for col, allowed in cfg.get("allowed_levels", {}).items():
        _check_columns(df, [col], "allowed_levels")
        bad = ~categorical_levels_mask(df[col], allowed) & df[col].notna()
        for _, r in df.loc[bad, ["_row_id", col]].iterrows():
            log_drop(logs, int(r["_row_id"]), f"LEVEL_{col}", "value not in declared allowed levels", col, r[col])
        df = df.loc[~bad].copy()

    aggregation = None
    tech = cfg.get("technical_replicates")
    if tech:
        df, aggregation = _technical_replicate_aggregate(df, tech)

    id_col = plan.get("variables", {}).get("id")
    id_dups = None
    duplicate_examples = []
    id_policy = cfg.get("id_duplicate_policy", "audit")
    if id_col:
        _check_columns(df, [id_col], "variables.id")
        dup_mask = df[id_col].notna() & typed_duplicate_mask(df[id_col], keep=False)
        id_dups = int(dup_mask.sum())
        if id_dups:
            duplicate_examples = df.loc[dup_mask, ["_row_id", id_col]].head(20).to_dict("records")
            if id_policy == "error":
                raise ValueError(
                    f"Duplicate independent-unit IDs remain after cleaning in '{id_col}' "
                    f"under id_duplicate_policy=error; examples={duplicate_examples}"
                )

    # Only columns whose scalar identity can change the scientific unit/group
    # selection need a strict round-trip identity guarantee. Numeric outcome/
    # predictor columns may safely round-trip between int/float representations.
    identity_columns = set()
    variables = plan.get("variables", {}) or {}
    for key in ["id", "group", "pair_id"]:
        if variables.get(key): identity_columns.add(variables[key])
    identity_columns.update((cfg.get("allowed_levels") or {}).keys())
    tech = cfg.get("technical_replicates") or {}
    identity_columns.update(tech.get("group_by") or [])
    identity_columns.update(tech.get("carry_columns") or [])
    for a in plan.get("analyses", []):
        for key in ["group", "pair_id", "condition", "row", "column", "outcome"]:
            if key in a and a.get(key):
                # outcome is categorical only for logistic; numeric outcomes are
                # harmless here because numeric int/float share typed identity.
                if key != "outcome" or a.get("type") == "logistic_regression":
                    identity_columns.add(a[key])
    for sitem in plan.get("sensitivity_analyses", []):
        filt = (sitem.get("data_filter") or {}).get("exclude_if") or []
        for rule in filt:
            if rule.get("operator") in {"eq", "ne", "in", "not_in"} and rule.get("column"):
                identity_columns.add(rule["column"])

    write_table(df, args.output)
    reloaded = read_table(args.output)
    mismatches = table_roundtrip_identity_mismatches(df, reloaded, sorted(identity_columns))
    if mismatches:
        try:
            Path(args.output).unlink()
        except OSError:
            pass
        raise ValueError(
            "Analysis-ready table serialization changed plan-relevant scalar identity. "
            "Use a .jsonl output path for type-preserving analysis-ready data or normalize the source encoding first. "
            f"examples={mismatches}"
        )
    log_df = pd.DataFrame(logs, columns=["_row_id", "rule_id", "reason", "column", "value"])
    Path(args.log).parent.mkdir(parents=True, exist_ok=True)
    log_df.to_csv(args.log, index=False)

    report = {
        "skill_version": SKILL_VERSION,
        "analysis_plan_schema_version": plan.get("analysis_plan_schema_version"),
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "input": str(args.input),
        "input_sha256": actual_hash,
        "plan": str(args.plan),
        "plan_sha256": sha256_file(args.plan),
        "rows_initial": start_n,
        "rows_final": int(len(df)),
        "rows_dropped_events": int(len(logs)),
        "id_column": id_col,
        "id_duplicate_policy": id_policy,
        "id_duplicate_rows_after_cleaning": id_dups,
        "id_typed_unique_nonmissing_after_cleaning": typed_nunique(df[id_col], dropna=True) if id_col else None,
        "id_duplicate_examples": duplicate_examples,
        "technical_replicate_aggregation": aggregation,
        "row_traceability": "aggregated_source_rows_preserved" if aggregation else "direct_raw_row_id",
        "output": str(args.output),
        "output_sha256": sha256_file(args.output),
        "cleaning_log": str(args.log),
        "cleaning_log_sha256": sha256_file(args.log),
    }
    write_json(report, args.report)
    print(f"Cleaned rows: {start_n} -> {len(df)}. Wrote {args.output}")


if __name__ == "__main__":
    main()
