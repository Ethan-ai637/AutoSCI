from __future__ import annotations

import csv
import hashlib
import json
import re
import unicodedata
from pathlib import Path
from typing import Dict, Iterable, List

CANONICAL_FIELDS = [
    "record_id", "title", "authors", "year", "venue", "doi", "pmid", "pmcid",
    "arxiv_id", "url", "abstract", "source", "query_id", "retrieved_at",
    "publication_type", "extra_json"
]


def norm_space(value: object) -> str:
    return re.sub(r"\s+", " ", str(value or "")).strip()


def norm_title(value: object) -> str:
    text = unicodedata.normalize("NFKD", norm_space(value)).casefold()
    text = re.sub(r"[^\w\s]", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def norm_doi(value: object) -> str:
    doi = norm_space(value).lower()
    doi = re.sub(r"^https?://(?:dx\.)?doi\.org/", "", doi)
    doi = re.sub(r"^doi:\s*", "", doi)
    return doi.strip().rstrip(".,;)")


def norm_id(value: object) -> str:
    return norm_space(value).lower()


def stable_record_id(row: Dict[str, str]) -> str:
    basis = norm_doi(row.get("doi")) or norm_id(row.get("pmid")) or norm_id(row.get("arxiv_id"))
    if not basis:
        basis = f"{norm_title(row.get('title'))}|{norm_space(row.get('year'))}|{norm_space(row.get('authors'))[:80]}"
    return "R" + hashlib.sha1(basis.encode("utf-8")).hexdigest()[:12]



def stable_study_id(record_id: object) -> str:
    basis = norm_space(record_id) or "unassigned"
    return "S" + hashlib.sha1(basis.encode("utf-8")).hexdigest()[:12]


def read_csv(path: str | Path) -> List[Dict[str, str]]:
    with open(path, "r", encoding="utf-8-sig", newline="") as f:
        return [dict(r) for r in csv.DictReader(f)]


def write_csv(path: str | Path, rows: Iterable[Dict[str, object]], fields: List[str]) -> None:
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        for row in rows:
            w.writerow({k: row.get(k, "") for k in fields})


def read_records_any(path: str | Path) -> List[Dict[str, object]]:
    p = Path(path)
    suffix = p.suffix.lower()
    if suffix == ".csv":
        return read_csv(p)
    if suffix in {".jsonl", ".ndjson"}:
        out = []
        with open(p, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    out.append(json.loads(line))
        return out
    if suffix == ".json":
        data = json.loads(p.read_text(encoding="utf-8"))
        if isinstance(data, list):
            return data
        if isinstance(data, dict):
            for key in ("records", "items", "results", "data"):
                if isinstance(data.get(key), list):
                    return data[key]
            return [data]
    raise ValueError(f"Unsupported input format: {p}")
