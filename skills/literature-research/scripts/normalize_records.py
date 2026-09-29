#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from common import CANONICAL_FIELDS, norm_doi, norm_space, read_records_any, stable_record_id, write_csv

ALIASES = {
    "record_id": ["record_id", "id", "paper_id"],
    "title": ["title", "paper_title", "name"],
    "authors": ["authors", "author", "creators"],
    "year": ["year", "publication_year", "published_year"],
    "venue": ["venue", "journal", "container_title", "conference"],
    "doi": ["doi", "DOI"],
    "pmid": ["pmid", "PMID"],
    "pmcid": ["pmcid", "PMCID"],
    "arxiv_id": ["arxiv_id", "arxiv", "arXiv"],
    "url": ["url", "URL", "link"],
    "abstract": ["abstract", "summary"],
    "source": ["source", "database", "provider"],
    "query_id": ["query_id", "search_id"],
    "retrieved_at": ["retrieved_at", "retrieval_date", "searched_at"],
    "publication_type": ["publication_type", "type", "document_type"],
}


def first_value(row, names):
    for name in names:
        if name in row and row[name] not in (None, "", []):
            value = row[name]
            if isinstance(value, list):
                return "; ".join(norm_space(v) for v in value)
            if isinstance(value, dict):
                return json.dumps(value, ensure_ascii=False, sort_keys=True)
            return norm_space(value)
    return ""


def normalize(row):
    out = {k: first_value(row, aliases) for k, aliases in ALIASES.items()}
    out["doi"] = norm_doi(out.get("doi"))
    extras = {k: v for k, v in row.items() if not any(k in aliases for aliases in ALIASES.values())}
    out["extra_json"] = json.dumps(extras, ensure_ascii=False, sort_keys=True) if extras else ""
    if not out.get("record_id"):
        out["record_id"] = stable_record_id(out)
    return out


def main():
    ap = argparse.ArgumentParser(description="Normalize bibliographic exports into the AutoSCI canonical record schema.")
    ap.add_argument("inputs", nargs="+", help="CSV, JSON, or JSONL inputs")
    ap.add_argument("-o", "--output", required=True)
    args = ap.parse_args()

    rows = []
    for path in args.inputs:
        for raw in read_records_any(path):
            rows.append(normalize(raw))
    write_csv(args.output, rows, CANONICAL_FIELDS)
    print(f"normalized_records={len(rows)} output={Path(args.output)}")


if __name__ == "__main__":
    main()
