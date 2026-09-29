#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from common import read_csv

ALLOWED = {"backward_reference", "forward_citation", "same_study_version", "companion", "discovery_from"}


def main():
    ap = argparse.ArgumentParser(description="Audit citation-trail IDs, relation types, verification fields, and duplicates.")
    ap.add_argument("trail")
    ap.add_argument("--records", required=True)
    ap.add_argument("--report", required=True)
    ap.add_argument("--dot")
    args = ap.parse_args()

    records = read_csv(args.records)
    ids = {r.get("record_id", "") for r in records if r.get("record_id")}
    trail = read_csv(args.trail)
    errors, warnings = [], []
    seen = set()

    for idx, row in enumerate(trail, 2):
        s, t = (row.get("source_id") or "").strip(), (row.get("target_id") or "").strip()
        rel = (row.get("relation") or "").strip()
        if not s or not t:
            errors.append(f"row {idx}: missing source_id/target_id")
        if s and s not in ids:
            errors.append(f"row {idx}: unknown source_id {s}")
        if t and t not in ids:
            errors.append(f"row {idx}: unknown target_id {t}")
        if s and t and s == t:
            errors.append(f"row {idx}: self-edge {s}")
        if rel not in ALLOWED:
            errors.append(f"row {idx}: invalid relation {rel!r}")
        if not (row.get("verification_source") or "").strip():
            errors.append(f"row {idx}: missing verification_source")
        key = (s, t, rel)
        if key in seen:
            warnings.append(f"row {idx}: duplicate edge {key}")
        seen.add(key)

    report = {"edge_count": len(trail), "errors": errors, "warnings": warnings, "passed": not errors}
    Path(args.report).parent.mkdir(parents=True, exist_ok=True)
    Path(args.report).write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")

    if args.dot:
        lines = ["digraph citation_trail {", "  rankdir=LR;"]
        for row in trail:
            s, t, rel = row.get("source_id", ""), row.get("target_id", ""), row.get("relation", "")
            if s and t:
                safe_rel = rel.replace('"', '\\"')
                lines.append(f'  "{s}" -> "{t}" [label="{safe_rel}"];')
        lines.append("}")
        Path(args.dot).parent.mkdir(parents=True, exist_ok=True)
        Path(args.dot).write_text("\n".join(lines), encoding="utf-8")

    print(f"edges={len(trail)} errors={len(errors)} warnings={len(warnings)}")
    raise SystemExit(1 if errors else 0)


if __name__ == "__main__":
    main()
