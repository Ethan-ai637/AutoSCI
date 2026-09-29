#!/usr/bin/env python3
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from pathlib import Path

from common import read_csv

ELIGIBLE_SUPPORT_LEVELS = {"direct", "derived"}
ELIGIBLE_VERIFICATION = {"verified", "partial"}


def verification_coverage(counts):
    total = counts.get("verified", 0) + counts.get("partial", 0)
    if total == 0:
        return "not_applicable"
    if counts.get("partial", 0) == 0:
        return "complete"
    if counts.get("verified", 0) == 0:
        return "partial_only"
    return "mixed"


def norm(v):
    return str(v or "").strip()


def short(text: str, n: int = 220) -> str:
    text = norm(text)
    return text if len(text) <= n else text[: n - 1].rstrip() + "…"


def main():
    ap = argparse.ArgumentParser(description="Render audited synthesis tables into a deterministic human-readable claim brief.")
    ap.add_argument("--evidence", required=True)
    ap.add_argument("--claims", required=True)
    ap.add_argument("--links", required=True)
    ap.add_argument("--records")
    ap.add_argument("--study-map")
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    evidence = read_csv(args.evidence)
    claims = read_csv(args.claims)
    links = read_csv(args.links)
    records = read_csv(args.records) if args.records else []
    study_map = read_csv(args.study_map) if args.study_map else []

    evidence_by_id = {norm(r.get("claim_id")): r for r in evidence if norm(r.get("claim_id"))}
    title_by_record = {norm(r.get("record_id")): norm(r.get("title")) for r in records if norm(r.get("record_id"))}
    study_by_record = {norm(r.get("record_id")): norm(r.get("study_id")) for r in study_map if norm(r.get("record_id"))}
    links_by_synth = defaultdict(list)
    for row in links:
        links_by_synth[norm(row.get("synthesis_id"))].append(row)

    lines = [
        "# Synthesis brief",
        "",
        "> Deterministic rendering of existing synthesis/evidence tables. It introduces no new scientific claims.",
        "",
    ]
    grouped = defaultdict(list)
    for row in claims:
        grouped[norm(row.get("research_question_component")) or "Unspecified"].append(row)

    for component in sorted(grouped):
        lines += [f"## {component}", ""]
        for claim in grouped[component]:
            sid = norm(claim.get("synthesis_id"))
            lines += [f"### {sid} — {norm(claim.get('statement'))}", ""]
            meta = []
            if norm(claim.get("evidence_state")):
                meta.append(f"**Evidence state:** {norm(claim.get('evidence_state'))}")
            if norm(claim.get("scope")):
                meta.append(f"**Scope:** {norm(claim.get('scope'))}")
            if meta:
                lines += ["  ·  ".join(meta), ""]
            if norm(claim.get("caveat")):
                lines += [f"**Caveat:** {norm(claim.get('caveat'))}", ""]

            slinks = links_by_synth.get(sid, [])
            verification_counts = Counter()
            for _link in slinks:
                if norm(_link.get("relation")).lower() not in {"supports", "contradicts"}:
                    continue
                _erow = evidence_by_id.get(norm(_link.get("claim_id")), {})
                _support = norm(_erow.get("support_level")).lower()
                _verification = norm(_erow.get("verification_status")).lower()
                if _support in ELIGIBLE_SUPPORT_LEVELS and _verification in ELIGIBLE_VERIFICATION:
                    verification_counts[_verification] += 1
            coverage = verification_coverage(verification_counts)
            lines += [f"**Verification coverage:** {coverage} (verified={verification_counts.get('verified', 0)}, partial={verification_counts.get('partial', 0)})", ""]
            relation_order = ["supports", "contradicts", "qualifies", "context"]
            for rel in relation_order:
                rows = [x for x in slinks if norm(x.get("relation")).lower() == rel]
                if not rows:
                    continue
                lines += [f"**{rel.capitalize()}**", ""]
                for link in rows:
                    cid = norm(link.get("claim_id"))
                    erow = evidence_by_id.get(cid, {})
                    rid = norm(erow.get("source_id"))
                    stid = norm(erow.get("study_id")) or study_by_record.get(rid, "")
                    support = norm(erow.get("support_level")).lower()
                    verification = norm(erow.get("verification_status")).lower()
                    eligible = support in ELIGIBLE_SUPPORT_LEVELS and verification in ELIGIBLE_VERIFICATION
                    title = title_by_record.get(rid, "")
                    result = short(erow.get("reported_result")) or short(erow.get("reviewer_interpretation")) or "[no result text recorded]"
                    locator = norm(erow.get("evidence_location")) or "locator not recorded"
                    status = "eligible" if eligible else "provenance-only"
                    source_label = rid + (f" · {short(title, 100)}" if title else "")
                    study_label = f" · study {stid}" if stid else ""
                    lines.append(f"- `{cid}` ({status}; {support or 'support n/a'}; {verification or 'verification n/a'}) — {source_label}{study_label}")
                    lines.append(f"  - Evidence: {result}")
                    lines.append(f"  - Location: {locator}")
                lines.append("")
            if not slinks:
                lines += ["**Evidence links:** none recorded", ""]
    lines += [
        "## Interpretation boundary",
        "",
        "This brief is a routing artifact. Re-check the evidence table and source material before quoting exact values, causal language, or source wording.",
        "",
    ]
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(lines), encoding="utf-8")
    print(f"wrote={out} synthesis_claims={len(claims)} evidence_claims={len(evidence_by_id)}")


if __name__ == "__main__":
    main()
