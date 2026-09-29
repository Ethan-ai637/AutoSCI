#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from collections import defaultdict
from difflib import SequenceMatcher
from pathlib import Path

from common import CANONICAL_FIELDS, norm_doi, norm_id, norm_space, norm_title, read_csv, write_csv


def compatible_year(a, b):
    ya, yb = norm_space(a), norm_space(b)
    if not ya or not yb:
        return True
    try:
        return abs(int(ya[:4]) - int(yb[:4])) <= 1
    except ValueError:
        return ya == yb


def strong_identifier_conflict(a, b):
    pairs = [
        (norm_doi(a.get("doi")), norm_doi(b.get("doi"))),
        (norm_id(a.get("pmid")), norm_id(b.get("pmid"))),
        (norm_id(a.get("pmcid")), norm_id(b.get("pmcid"))),
        (norm_id(a.get("arxiv_id")), norm_id(b.get("arxiv_id"))),
    ]
    return any(x and y and x != y for x, y in pairs)


def exact_key(row):
    if norm_doi(row.get("doi")):
        return ("doi", norm_doi(row.get("doi")))
    if norm_id(row.get("pmid")):
        return ("pmid", norm_id(row.get("pmid")))
    if norm_id(row.get("pmcid")):
        return ("pmcid", norm_id(row.get("pmcid")))
    if norm_id(row.get("arxiv_id")):
        return ("arxiv", norm_id(row.get("arxiv_id")))
    t = norm_title(row.get("title"))
    if t:
        return ("title", t)
    return None


def richness(row):
    return sum(bool(norm_space(row.get(k))) for k in CANONICAL_FIELDS if k not in {"extra_json"}) + len(norm_space(row.get("abstract"))) / 10000


def merge_group(rows):
    canonical = max(rows, key=richness).copy()
    ids, sources, queries, urls = [], [], [], []
    for row in rows:
        ids.append(norm_space(row.get("record_id")))
        for value, bucket in [(row.get("source"), sources), (row.get("query_id"), queries), (row.get("url"), urls)]:
            v = norm_space(value)
            if v and v not in bucket:
                bucket.append(v)
        for field in CANONICAL_FIELDS:
            if not norm_space(canonical.get(field)) and norm_space(row.get(field)):
                canonical[field] = row[field]
    canonical["merged_from_ids"] = ";".join(x for x in ids if x)
    canonical["merged_sources"] = ";".join(sources)
    canonical["merged_query_ids"] = ";".join(queries)
    canonical["merged_urls"] = ";".join(urls)
    return canonical


def main():
    ap = argparse.ArgumentParser(description="Conservatively deduplicate normalized literature records.")
    ap.add_argument("input")
    ap.add_argument("-o", "--output", required=True)
    ap.add_argument("--report", required=True)
    ap.add_argument("--fuzzy-threshold", type=float, default=0.93)
    args = ap.parse_args()

    rows = read_csv(args.input)
    parent = list(range(len(rows)))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(a, b):
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[rb] = ra

    seen = {}
    exact_matches = []
    for i, row in enumerate(rows):
        key = exact_key(row)
        if key and key in seen:
            union(i, seen[key])
            exact_matches.append({"a": rows[seen[key]].get("record_id"), "b": row.get("record_id"), "rule": key[0]})
        elif key:
            seen[key] = i

    # Candidate fuzzy matching among records not already sharing a strong key.
    fuzzy_matches = []
    title_rows = [(i, norm_title(r.get("title"))) for i, r in enumerate(rows)]
    title_rows = [(i, t) for i, t in title_rows if len(t) >= 20]
    for pos, (i, ti) in enumerate(title_rows):
        for j, tj in title_rows[pos + 1:]:
            if find(i) == find(j):
                continue
            # Cheap blocking to avoid merging obviously different titles.
            if ti[:1] != tj[:1] or not compatible_year(rows[i].get("year"), rows[j].get("year")):
                continue
            if strong_identifier_conflict(rows[i], rows[j]):
                continue
            score = SequenceMatcher(None, ti, tj).ratio()
            if score >= args.fuzzy_threshold:
                union(i, j)
                fuzzy_matches.append({"a": rows[i].get("record_id"), "b": rows[j].get("record_id"), "score": round(score, 4)})

    groups = defaultdict(list)
    for i, row in enumerate(rows):
        groups[find(i)].append(row)

    merged = [merge_group(group) for _, group in sorted(groups.items(), key=lambda kv: min(rows.index(r) for r in kv[1]))]
    fields = CANONICAL_FIELDS + ["merged_from_ids", "merged_sources", "merged_query_ids", "merged_urls"]
    write_csv(args.output, merged, fields)

    report = {
        "input_records": len(rows),
        "output_records": len(merged),
        "duplicates_removed": len(rows) - len(merged),
        "fuzzy_threshold": args.fuzzy_threshold,
        "exact_matches": exact_matches,
        "fuzzy_matches": fuzzy_matches,
        "groups": [
            {"canonical_id": merge_group(group).get("record_id"), "member_ids": [r.get("record_id") for r in group]}
            for group in groups.values() if len(group) > 1
        ],
    }
    Path(args.report).parent.mkdir(parents=True, exist_ok=True)
    Path(args.report).write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"input={len(rows)} output={len(merged)} removed={len(rows)-len(merged)}")


if __name__ == "__main__":
    main()
