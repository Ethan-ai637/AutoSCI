#!/usr/bin/env python3
from __future__ import annotations

import argparse
import math
import re
from collections import Counter, defaultdict
from pathlib import Path

from common import read_csv, write_csv

STOP = set("a an and are as at be been by can could for from has have in into is it its may method methods model models of on or our paper result results study studies system systems that the their this to using via was we were with".split())


def tokenize(text):
    return [t for t in re.findall(r"[a-zA-Z][a-zA-Z0-9_-]{2,}", (text or "").lower()) if t not in STOP]


def build_vectors(rows):
    docs = [Counter(tokenize((r.get("title") or "") + " " + (r.get("abstract") or ""))) for r in rows]
    df = Counter()
    for d in docs:
        df.update(d.keys())
    n = max(1, len(docs))
    vecs = []
    for d in docs:
        v = {}
        for term, tf in d.items():
            idf = math.log((1 + n) / (1 + df[term])) + 1
            v[term] = (1 + math.log(tf)) * idf
        norm = math.sqrt(sum(x*x for x in v.values())) or 1.0
        vecs.append({k: x / norm for k, x in v.items()})
    return vecs


def cosine(a, b):
    if len(a) > len(b):
        a, b = b, a
    return sum(v * b.get(k, 0.0) for k, v in a.items())


def main():
    ap = argparse.ArgumentParser(description="Create deterministic candidate topic clusters from screened literature records.")
    ap.add_argument("input", help="screening.csv or a record CSV containing title/abstract")
    ap.add_argument("-o", "--output", required=True)
    ap.add_argument("--summary", required=True)
    ap.add_argument("--records", help="Optional deduplicated records CSV when input is screening.csv")
    ap.add_argument("--threshold", type=float, default=0.23)
    args = ap.parse_args()

    rows = read_csv(args.input)
    if args.records:
        meta = {r.get("record_id"): r for r in read_csv(args.records)}
        rows = [{**meta.get(r.get("record_id"), {}), **r} for r in rows]
    # If screening decisions exist, cluster include/uncertain only; blank decisions are retained for exploratory use.
    if rows and "decision" in rows[0]:
        rows = [r for r in rows if (r.get("decision") or "").strip().lower() in {"", "include", "uncertain"}]

    vecs = build_vectors(rows)
    n = len(rows)
    parent = list(range(n))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(a, b):
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[rb] = ra

    for i in range(n):
        for j in range(i + 1, n):
            if cosine(vecs[i], vecs[j]) >= args.threshold:
                union(i, j)

    groups = defaultdict(list)
    for i in range(n):
        groups[find(i)].append(i)
    ordered = sorted(groups.values(), key=lambda g: (-len(g), min(g)))
    out = []
    summary_lines = ["# Candidate topic clusters", "", f"Similarity threshold: `{args.threshold}`", ""]
    for cidx, members in enumerate(ordered, 1):
        cid = f"C{cidx:03d}"
        terms = Counter()
        for i in members:
            terms.update(tokenize((rows[i].get("title") or "") + " " + (rows[i].get("abstract") or "")))
        top_terms = [t for t, _ in terms.most_common(8)]
        summary_lines += [f"## {cid}", "", f"Top terms: {', '.join(top_terms) if top_terms else '(none)'}", ""]
        for i in members:
            r = rows[i]
            out.append({"cluster_id": cid, "record_id": r.get("record_id", ""), "title": r.get("title", ""), "candidate_terms": ";".join(top_terms), "theme_name": "", "notes": ""})
            summary_lines.append(f"- {r.get('record_id','')}: {r.get('title','')}")
        summary_lines.append("")

    write_csv(args.output, out, ["cluster_id", "record_id", "title", "candidate_terms", "theme_name", "notes"])
    Path(args.summary).parent.mkdir(parents=True, exist_ok=True)
    Path(args.summary).write_text("\n".join(summary_lines), encoding="utf-8")
    print(f"records={n} clusters={len(ordered)} threshold={args.threshold}")


if __name__ == "__main__":
    main()
