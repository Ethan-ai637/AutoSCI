#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
from datetime import datetime, timezone
from pathlib import Path

from common import read_csv
from screening_rules import active_protocol_rules, matching_rules, norm

LOG_FIELDS = [
    "record_id", "title", "stage", "access_level", "reviewer", "decision", "reason_code",
    "criterion_id", "evidence_basis", "decided_at", "notes"
]


def utc_date():
    return datetime.now(timezone.utc).date().isoformat()


def write_csv(path: Path, rows: list[dict], fields: list[str]):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        w.writeheader(); w.writerows([{k: r.get(k, "") for k in fields} for r in rows])


def main():
    ap = argparse.ArgumentParser(description="Evaluate high-precision deterministic exclusion rules declared in protocol.json.")
    ap.add_argument("--protocol", required=True)
    ap.add_argument("--records", required=True)
    ap.add_argument("--output", required=True, help="CSV of matched exclusion candidates")
    ap.add_argument("--append-log", help="Optionally append deterministic exclusion events to screening_log.csv")
    ap.add_argument("--reviewer", default="deterministic-rule")
    ap.add_argument("--no-derived-safe-rules", action="store_true", help="Use only explicit deterministic_exclusion_rules; disable conservative publication-type derivation from exclusion_criteria")
    args = ap.parse_args()

    protocol = json.loads(Path(args.protocol).read_text(encoding="utf-8"))
    rules = active_protocol_rules(protocol, include_derived_safe=not args.no_derived_safe_rules)
    records = read_csv(args.records)
    candidates = []
    for rec in records:
        for rule in matching_rules(rec, rules):
            candidates.append({
                "record_id": norm(rec.get("record_id")),
                "title": norm(rec.get("title")),
                "rule_id": norm(rule.get("rule_id")),
                "field": norm(rule.get("field")),
                "operator": norm(rule.get("operator")),
                "reason_code": norm(rule.get("reason_code")),
                "criterion_id": norm(rule.get("criterion_id")) or norm(rule.get("rule_id")),
                "rule_source": norm(rule.get("rule_source")) or "explicit",
                "evidence_basis": f"Deterministic protocol rule {norm(rule.get('rule_id')) or '[unnamed]'} ({norm(rule.get('rule_source')) or 'explicit'}) matched {norm(rule.get('field'))}.",
            })
    out_fields = ["record_id", "title", "rule_id", "rule_source", "field", "operator", "reason_code", "criterion_id", "evidence_basis"]
    write_csv(Path(args.output), candidates, out_fields)

    appended = 0
    if args.append_log:
        p = Path(args.append_log)
        existing = read_csv(p) if p.exists() else []
        existing_keys = {(norm(x.get("record_id")), norm(x.get("criterion_id")), norm(x.get("stage"))) for x in existing}
        for c in candidates:
            key = (c["record_id"], c["criterion_id"], "adjudication")
            if key in existing_keys:
                continue
            existing.append({
                "record_id": c["record_id"], "title": c["title"], "stage": "adjudication",
                "access_level": "unknown", "reviewer": args.reviewer, "decision": "exclude",
                "reason_code": c["reason_code"], "criterion_id": c["criterion_id"],
                "evidence_basis": c["evidence_basis"], "decided_at": utc_date(),
                "notes": f"Auto-applied high-precision rule source={c.get('rule_source') or 'explicit'}. Recorded at adjudication stage so it overrides ordinary evidence-stage uncertainty but remains overridable by a deliberate final event after protocol/rule review.",
            })
            appended += 1
        write_csv(p, existing, LOG_FIELDS)

    print(json.dumps({"rules": len(rules), "records": len(records), "matches": len(candidates), "appended_events": appended}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
