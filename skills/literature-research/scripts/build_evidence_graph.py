#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
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


def main():
    ap = argparse.ArgumentParser(description="Build a machine-readable evidence graph without inventing relationships.")
    ap.add_argument("--records", required=True)
    ap.add_argument("--screening", required=True)
    ap.add_argument("--study-map", required=True)
    ap.add_argument("--evidence", required=True)
    ap.add_argument("--citation-trail", required=True)
    ap.add_argument("--synthesis-claims", required=True)
    ap.add_argument("--synthesis-evidence", required=True)
    ap.add_argument("--clusters")
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    records = read_csv(args.records)
    screening = read_csv(args.screening)
    study_map = read_csv(args.study_map)
    evidence = read_csv(args.evidence)
    trail = read_csv(args.citation_trail)
    synth = read_csv(args.synthesis_claims)
    links = read_csv(args.synthesis_evidence)
    clusters = read_csv(args.clusters) if args.clusters and Path(args.clusters).exists() else []

    errors, warnings = [], []
    record_by_id = {norm(r.get("record_id")): r for r in records if norm(r.get("record_id"))}
    screening_by_id = {norm(r.get("record_id")): r for r in screening if norm(r.get("record_id"))}
    study_by_record = {}
    study_nodes = {}
    for i, row in enumerate(study_map, 2):
        rid, sid = norm(row.get("record_id")), norm(row.get("study_id"))
        if not rid or not sid:
            errors.append(f"study_map row {i}: missing record_id/study_id")
            continue
        if rid not in record_by_id:
            errors.append(f"study_map row {i}: unknown record_id {rid}")
        study_by_record[rid] = sid
        study_nodes.setdefault(sid, {"id": sid, "type": "study", "report_ids": []})["report_ids"].append(rid)

    evidence_by_id = {}
    for i, row in enumerate(evidence, 2):
        cid, rid = norm(row.get("claim_id")), norm(row.get("source_id"))
        if not cid:
            errors.append(f"evidence row {i}: missing claim_id")
            continue
        if cid in evidence_by_id:
            errors.append(f"evidence row {i}: duplicate claim_id {cid}")
        evidence_by_id[cid] = row
        if rid not in record_by_id:
            errors.append(f"evidence row {i}: unknown source_id {rid}")

    synth_by_id = {}
    for i, row in enumerate(synth, 2):
        sid = norm(row.get("synthesis_id"))
        if not sid:
            errors.append(f"synthesis row {i}: missing synthesis_id")
            continue
        if sid in synth_by_id:
            errors.append(f"synthesis row {i}: duplicate synthesis_id {sid}")
        synth_by_id[sid] = row

    verification_counts_by_synth = defaultdict(Counter)
    for link in links:
        sid = norm(link.get("synthesis_id"))
        rel = norm(link.get("relation")).lower()
        if rel not in {"supports", "contradicts"}:
            continue
        erow = evidence_by_id.get(norm(link.get("claim_id")), {})
        support = norm(erow.get("support_level")).lower()
        verification = norm(erow.get("verification_status")).lower()
        if support in ELIGIBLE_SUPPORT_LEVELS and verification in ELIGIBLE_VERIFICATION:
            verification_counts_by_synth[sid][verification] += 1

    nodes = []
    def nid(kind: str, native: str) -> str:
        return f"{kind}:{native}"

    for rid, row in sorted(record_by_id.items()):
        scr = screening_by_id.get(rid, {})
        nodes.append({
            "id": nid("report", rid),
            "native_id": rid,
            "type": "report",
            "title": norm(row.get("title")),
            "year": norm(row.get("year")),
            "doi": norm(row.get("doi")),
            "url": norm(row.get("url")),
            "decision": norm(scr.get("decision")),
            "publication_type": norm(row.get("publication_type")),
        })
    for sid, node in sorted(study_nodes.items()):
        node["report_ids"] = sorted(set(node["report_ids"]))
        nodes.append({
            "id": nid("study", sid),
            "native_id": sid,
            "type": "study",
            "report_ids": node["report_ids"],
        })
    for cid, row in sorted(evidence_by_id.items()):
        nodes.append({
            "id": nid("evidence", cid),
            "native_id": cid,
            "type": "evidence_claim",
            "source_id": norm(row.get("source_id")),
            "study_id": norm(row.get("study_id")) or study_by_record.get(norm(row.get("source_id")), ""),
            "research_question_component": norm(row.get("research_question_component")),
            "reported_result": norm(row.get("reported_result")),
            "reviewer_interpretation": norm(row.get("reviewer_interpretation")),
            "limitations": norm(row.get("limitations")),
            "evidence_location": norm(row.get("evidence_location")),
            "support_level": norm(row.get("support_level")),
            "verification_status": norm(row.get("verification_status")),
        })
    for sid, row in sorted(synth_by_id.items()):
        nodes.append({
            "id": nid("synthesis", sid),
            "native_id": sid,
            "type": "synthesis_claim",
            "statement": norm(row.get("statement")),
            "research_question_component": norm(row.get("research_question_component")),
            "evidence_state": norm(row.get("evidence_state")),
            "scope": norm(row.get("scope")),
            "caveat": norm(row.get("caveat")),
            "verification_coverage": verification_coverage(verification_counts_by_synth.get(sid, Counter())),
            "verification_counts": dict(verification_counts_by_synth.get(sid, Counter())),
        })

    cluster_nodes = {}
    edges = []
    for rid, sid in sorted(study_by_record.items()):
        edges.append({"source": nid("report", rid), "target": nid("study", sid), "type": "report_of_study"})
    for cid, row in sorted(evidence_by_id.items()):
        rid = norm(row.get("source_id"))
        edges.append({"source": nid("evidence", cid), "target": nid("report", rid), "type": "evidence_from_report"})
        stid = norm(row.get("study_id")) or study_by_record.get(rid, "")
        if stid:
            edges.append({"source": nid("evidence", cid), "target": nid("study", stid), "type": "evidence_from_study"})
    for i, row in enumerate(links, 2):
        sid, cid, rel = norm(row.get("synthesis_id")), norm(row.get("claim_id")), norm(row.get("relation")).lower()
        if sid not in synth_by_id:
            errors.append(f"synthesis_evidence row {i}: unknown synthesis_id {sid}")
        if cid not in evidence_by_id:
            errors.append(f"synthesis_evidence row {i}: unknown claim_id {cid}")
        edges.append({"source": nid("evidence", cid), "target": nid("synthesis", sid), "type": f"synthesis_{rel or 'linked'}", "notes": norm(row.get("notes"))})
    for i, row in enumerate(trail, 2):
        src, dst = norm(row.get("source_id")), norm(row.get("target_id"))
        if src not in record_by_id or dst not in record_by_id:
            errors.append(f"citation_trail row {i}: unknown source/target {src}->{dst}")
        edges.append({
            "source": nid("report", src), "target": nid("report", dst), "type": f"citation_{norm(row.get('relation')).lower() or 'related'}",
            "verification_source": norm(row.get("verification_source")),
            "verification_url": norm(row.get("verification_url")),
        })
    for row in clusters:
        rid = norm(row.get("record_id"))
        cluster_id = norm(row.get("cluster_id")) or norm(row.get("cluster"))
        if not rid or not cluster_id:
            continue
        cid = nid("cluster", cluster_id)
        if cid not in cluster_nodes:
            cluster_nodes[cid] = {"id": cid, "native_id": cluster_id, "type": "topic_cluster", "label": norm(row.get("theme_name")) or norm(row.get("cluster_label")) or cluster_id}
        if rid not in record_by_id:
            warnings.append(f"cluster membership references unknown record_id {rid}")
        edges.append({"source": nid("report", rid), "target": cid, "type": "member_of_cluster"})
    nodes.extend(cluster_nodes.values())

    payload = {
        "schema": "autosci-literature-evidence-graph-v1",
        "counts": {
            "reports": len(record_by_id),
            "studies": len(study_nodes),
            "evidence_claims": len(evidence_by_id),
            "synthesis_claims": len(synth_by_id),
            "topic_clusters": len(cluster_nodes),
            "edges": len(edges),
        },
        "nodes": nodes,
        "edges": edges,
        "errors": errors,
        "warnings": warnings,
        "passed": not errors,
        "limitations": [
            "This graph serializes recorded relationships; it does not infer missing citation, study, or causal links.",
            "Topic-cluster membership is organizational and must not be interpreted as evidence of scientific agreement.",
        ],
    }
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"out": str(out), "counts": payload["counts"], "errors": errors, "warnings": warnings, "passed": not errors}, ensure_ascii=False, indent=2))
    raise SystemExit(1 if errors else 0)


if __name__ == "__main__":
    main()
