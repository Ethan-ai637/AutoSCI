from __future__ import annotations

import json
import re
from typing import Any


SAFE_PUBLICATION_TYPE_TERMS = {
    "systematic review": "Systematic Review",
    "scoping review": "Scoping Review",
    "meta-analysis": "Meta-Analysis",
    "meta analysis": "Meta-Analysis",
    "review": "Review",
    "editorial": "Editorial",
    "commentary": "Commentary",
    "comment": "Comment",
}


def norm(v: Any) -> str:
    return str(v or "").strip()


def field_text(record: dict, field: str) -> str:
    if field == "title_or_abstract":
        return " ".join([norm(record.get("title")), norm(record.get("abstract"))]).strip()
    if field == "title_abstract_publication_type":
        return " ".join([norm(record.get("title")), norm(record.get("abstract")), norm(record.get("publication_type"))]).strip()
    value = record.get(field, "")
    if isinstance(value, (dict, list)):
        return json.dumps(value, ensure_ascii=False)
    return norm(value)


def rule_matches(record: dict, rule: dict) -> bool:
    if not isinstance(rule, dict) or rule.get("enabled", True) is False:
        return False
    field = norm(rule.get("field"))
    op = norm(rule.get("operator")).lower()
    value = field_text(record, field)
    folded = value.casefold()
    values = rule.get("values") or []
    if isinstance(values, str):
        values = [values]
    vals = [norm(x) for x in values if norm(x)]
    if op == "equals":
        return any(folded == x.casefold() for x in vals)
    if op == "contains_any":
        return any(x.casefold() in folded for x in vals)
    if op == "contains_all":
        return bool(vals) and all(x.casefold() in folded for x in vals)
    if op == "list_contains_any":
        # For structured delimited fields such as PubMed publication_type. Exact item matching avoids
        # false positives like Review matching "Peer-reviewed journal article".
        items = [x.strip().casefold() for x in re.split(r"[;|\n]", value) if x.strip()]
        wanted = {x.casefold() for x in vals}
        return bool(set(items) & wanted)
    if op == "regex":
        pattern = norm(rule.get("pattern")) or (vals[0] if vals else "")
        return bool(pattern and re.search(pattern, value, flags=re.IGNORECASE))
    if op == "exists":
        return bool(value)
    if op == "missing":
        return not bool(value)
    return False


def matching_rules(record: dict, rules: list[dict]) -> list[dict]:
    return [r for r in rules if isinstance(r, dict) and r.get("enabled", True) is not False and rule_matches(record, r)]


def _criterion_text(item: Any) -> str:
    if isinstance(item, str):
        return item
    if isinstance(item, dict):
        parts = [norm(item.get(k)) for k in ("criterion", "description", "text", "label", "name")]
        return " ".join(x for x in parts if x)
    return norm(item)


def derive_safe_rules(protocol: dict) -> list[dict]:
    """Derive only mechanically safe rules from literal publication types named in exclusion criteria.

    This deliberately does not infer semantic task exclusions such as imaging-only or patient-education-only.
    Those still require screening judgment unless the protocol contains an explicit deterministic rule.
    """
    found = []
    seen = set()
    for criterion in protocol.get("exclusion_criteria") or []:
        text = _criterion_text(criterion).casefold()
        if not text:
            continue
        # Longer terms first so "systematic review" is preserved while a generic Review rule can also be useful.
        for needle, canonical in SAFE_PUBLICATION_TYPE_TERMS.items():
            pattern = r"(?<![a-z])" + re.escape(needle) + r"s?(?![a-z])"
            if not re.search(pattern, text, flags=re.IGNORECASE):
                continue
            key = canonical.casefold()
            if key in seen:
                continue
            seen.add(key)
            found.append(canonical)
    if not found:
        return []
    return [{
        "rule_id": "auto_publication_type_exclusion",
        "field": "publication_type",
        "operator": "list_contains_any",
        "values": found,
        "reason_code": "WRONG_PUBLICATION_TYPE",
        "criterion_id": "auto_from_exclusion_criteria_publication_type",
        "enabled": True,
        "rule_source": "derived_safe",
        "note": "Conservatively derived only from publication-type names literally present in protocol.exclusion_criteria.",
    }]


def active_protocol_rules(protocol: dict, include_derived_safe: bool = True) -> list[dict]:
    explicit = []
    for r in protocol.get("deterministic_exclusion_rules") or []:
        if not isinstance(r, dict) or r.get("enabled", True) is False:
            continue
        item = dict(r)
        item.setdefault("rule_source", "explicit")
        explicit.append(item)
    if not include_derived_safe:
        return explicit

    derived = derive_safe_rules(protocol)
    # Avoid duplicate publication-type values already covered explicitly.
    explicitly_covered = set()
    for r in explicit:
        if norm(r.get("field")) == "publication_type" and norm(r.get("operator")).lower() in {"contains_any", "list_contains_any"}:
            vals = r.get("values") or []
            if isinstance(vals, str):
                vals = [vals]
            explicitly_covered.update(norm(v).casefold() for v in vals if norm(v))
    for r in derived:
        vals = [v for v in (r.get("values") or []) if norm(v).casefold() not in explicitly_covered]
        if vals:
            item = dict(r)
            item["values"] = vals
            explicit.append(item)
    return explicit
