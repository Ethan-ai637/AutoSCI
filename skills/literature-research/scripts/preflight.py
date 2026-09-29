#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path

from common import norm_doi, norm_id, read_csv
from audit_search import as_number, effective_status, source_status
from screening_rules import active_protocol_rules, matching_rules

ALLOWED_DECISIONS = {"include", "exclude", "uncertain"}
ALLOWED_RELATIONS = {"backward_reference", "forward_citation", "same_study_version", "companion", "discovery_from"}
ALLOWED_SUPPORT_LEVELS = {"direct", "derived", "contextual", "unclear"}
ALLOWED_VERIFICATION = {"verified", "partial", "unverified"}
ALLOWED_STUDY_VERIFICATION = {"provisional", "verified", "partial", "unverified"}
ALLOWED_REPORT_ROLES = {
    "primary_or_only_report", "primary_report", "secondary_analysis", "follow_up",
    "protocol", "preprint_version", "conference_version", "journal_version",
    "supplement", "correction", "companion", "unknown"
}
ALLOWED_SYNTH_RELATIONS = {"supports", "contradicts", "qualifies", "context"}
ALLOWED_SYNTH_STATES = {"consistent", "mixed", "single_source", "single_study", "gap", "descriptive"}
ELIGIBLE_SYNTH_SUPPORT_LEVELS = {"direct", "derived"}
ELIGIBLE_SYNTH_VERIFICATION = {"verified", "partial"}
ALLOWED_SCREEN_STAGES = {"title_abstract", "full_text_attempted", "full_text_screened", "full_text", "adjudication", "final"}
ACCESS_LEVELS = {"", "unknown", "title_only", "abstract", "metadata_plus_abstract", "full_text"}
EVIDENCE_STAGE_RANK = {"title_abstract": 10, "full_text_attempted": 15, "full_text": 16, "full_text_screened": 20}


def norm(v):
    return str(v or "").strip()


def add_duplicate_errors(rows, field, normalizer, errors):
    vals = [normalizer(r.get(field)) for r in rows]
    dup = [v for v, c in Counter(v for v in vals if v).items() if c > 1]
    for value in dup:
        errors.append(f"duplicate canonical {field}: {value}")


def main():
    ap = argparse.ArgumentParser(description="Cross-artifact QA for literature-research workflows.")
    ap.add_argument("--protocol", required=True)
    ap.add_argument("--records", required=True)
    ap.add_argument("--screening", required=True)
    ap.add_argument("--screening-log")
    ap.add_argument("--study-map")
    ap.add_argument("--evidence", required=True)
    ap.add_argument("--citation-trail", required=True)
    ap.add_argument("--search-log", required=True)
    ap.add_argument("--synthesis-claims")
    ap.add_argument("--synthesis-evidence")
    ap.add_argument("--report")
    args = ap.parse_args()

    errors, warnings = [], []
    protocol = json.loads(Path(args.protocol).read_text(encoding="utf-8"))
    profile = norm(protocol.get("profile", "standard")).lower()
    if profile not in {"exploratory", "standard", "systematic"}:
        errors.append(f"invalid protocol profile: {profile}")
    synthesis_unit = norm(protocol.get("synthesis_unit", "study")).lower() or "study"
    if synthesis_unit not in {"study", "report"}:
        errors.append(f"invalid protocol synthesis_unit: {synthesis_unit}")
    if not norm(protocol.get("research_question")):
        errors.append("protocol missing research_question")
    if profile in {"standard", "systematic"}:
        for field in ("inclusion_criteria", "exclusion_criteria", "target_sources", "stopping_rule"):
            if not protocol.get(field):
                errors.append(f"protocol missing/empty {field}")
        for field in ("protocol_id", "protocol_version", "created_at"):
            if not norm(protocol.get(field)):
                msg = f"protocol missing {field}; reproducible handoff is weaker without protocol identity/version metadata"
                (errors if profile == "systematic" else warnings).append(msg)
    changes = protocol.get("protocol_changes") or []
    if not isinstance(changes, list):
        errors.append("protocol_changes must be a list")
        changes = []
    for i, change in enumerate(changes, 1):
        if not isinstance(change, dict):
            errors.append(f"protocol_changes[{i}] must be an object")
            continue
        missing = [k for k in ("changed_at", "field", "rationale") if not norm(change.get(k))]
        if missing:
            msg = f"protocol_changes[{i}] missing {missing}"
            (errors if profile == "systematic" else warnings).append(msg)

    records = read_csv(args.records)
    record_by_id = {norm(r.get("record_id")): r for r in records if norm(r.get("record_id"))}
    ids = set(record_by_id)
    if len(ids) != len(records):
        errors.append("records contain missing or duplicate record_id values")
    add_duplicate_errors(records, "doi", norm_doi, errors)
    add_duplicate_errors(records, "pmid", norm_id, errors)
    add_duplicate_errors(records, "pmcid", norm_id, errors)
    add_duplicate_errors(records, "arxiv_id", norm_id, errors)

    screening = read_csv(args.screening)
    screened_ids = set()
    decision_by_id = {}
    for idx, row in enumerate(screening, 2):
        rid = norm(row.get("record_id"))
        dec = norm(row.get("decision")).lower()
        if rid not in ids:
            errors.append(f"screening row {idx}: unknown record_id {rid}")
        if rid in screened_ids:
            errors.append(f"screening row {idx}: repeated final record_id {rid}")
        screened_ids.add(rid)
        decision_by_id[rid] = dec
        if profile != "exploratory" and dec not in ALLOWED_DECISIONS:
            errors.append(f"screening row {idx}: invalid/blank decision {dec!r}")
        elif dec and dec not in ALLOWED_DECISIONS:
            warnings.append(f"screening row {idx}: unrecognized decision {dec!r}")
        if dec == "exclude" and not norm(row.get("reason_code")):
            errors.append(f"screening row {idx}: exclusion missing reason_code")
        conflict = norm(row.get("conflict_status")).lower()
        if conflict == "unresolved":
            msg = f"screening row {idx}: unresolved reviewer conflict for {rid}"
            (errors if profile == "systematic" else warnings).append(msg)
        if dec and not norm(row.get("screening_stage")):
            warnings.append(f"screening row {idx}: decision has no screening_stage")
    if profile in {"standard", "systematic"} and ids - screened_ids:
        errors.append(f"screening missing {len(ids-screened_ids)} record(s)")

    screening_plan = protocol.get("screening_plan") or {}
    required_stages = [norm(x).lower() for x in screening_plan.get("stages", []) if norm(x)]
    strict_full_text_required = any(x == "full_text" for x in required_stages)
    flexible_full_text_required = any(x in {"full_text_or_most_complete_accessible_record", "full_text_or_best_available"} for x in required_stages)
    if profile in {"standard", "systematic"} and (strict_full_text_required or flexible_full_text_required):
        for idx, row in enumerate(screening, 2):
            if norm(row.get("decision")).lower() != "include":
                continue
            evidence_stage = norm(row.get("evidence_stage")).lower()
            access_level = norm(row.get("access_level")).lower()
            rid = norm(row.get("record_id"))
            if strict_full_text_required:
                if evidence_stage != "full_text_screened" or access_level != "full_text":
                    errors.append(
                        f"screening row {idx}: included record {rid} has not completed true full-text screening "
                        f"(evidence_stage={evidence_stage!r}, access_level={access_level!r})"
                    )
            elif flexible_full_text_required:
                if evidence_stage not in {"full_text_attempted", "full_text_screened"}:
                    errors.append(
                        f"screening row {idx}: included record {rid} must at least record full_text_attempted when protocol allows most-complete-accessible screening "
                        f"(evidence_stage={evidence_stage!r})"
                    )
                if evidence_stage == "full_text_screened" and access_level != "full_text":
                    errors.append(f"screening row {idx}: full_text_screened requires access_level=full_text")
                if evidence_stage == "full_text_attempted" and access_level == "full_text":
                    warnings.append(f"screening row {idx}: full text appears available but evidence_stage remains full_text_attempted")
            if evidence_stage == "full_text":
                errors.append(f"screening row {idx}: legacy ambiguous evidence_stage='full_text' cannot satisfy v1.6 full-text requirements")

    # High-precision deterministic exclusions declared in the protocol take precedence over uncertain.
    deterministic_rules = active_protocol_rules(protocol, include_derived_safe=True)
    for idx, row in enumerate(screening, 2):
        rid = norm(row.get("record_id"))
        if norm(row.get("decision")).lower() != "uncertain" or rid not in record_by_id:
            continue
        matches = matching_rules(record_by_id[rid], deterministic_rules)
        if matches:
            rule_ids = [norm(x.get("rule_id")) or "[unnamed]" for x in matches]
            errors.append(f"screening row {idx}: uncertain record {rid} matches high-precision deterministic exclusion rule(s) {rule_ids}; exclude it or revise the protocol criteria/rule")

    declared_reviewers = screening_plan.get("reviewers_per_record", 1)
    try:
        declared_reviewers = int(declared_reviewers)
    except (TypeError, ValueError):
        declared_reviewers = 1
    if declared_reviewers > 1 and not args.screening_log:
        msg = "protocol declares multiple reviewers_per_record but --screening-log was not supplied"
        (errors if profile == "systematic" else warnings).append(msg)

    screening_log = []
    if args.screening_log:
        screening_log = read_csv(args.screening_log)
        seen_events = set()
        events_by_record = defaultdict(list)
        for idx, row in enumerate(screening_log, 2):
            rid = norm(row.get("record_id"))
            dec = norm(row.get("decision")).lower()
            reviewer = norm(row.get("reviewer"))
            stage = norm(row.get("stage")).lower()
            access = norm(row.get("access_level")).lower()
            if rid not in ids:
                errors.append(f"screening_log row {idx}: unknown record_id {rid}")
            else:
                events_by_record[rid].append(row)
            if stage and stage not in ALLOWED_SCREEN_STAGES:
                errors.append(f"screening_log row {idx}: invalid stage {stage!r}")
            if access not in ACCESS_LEVELS:
                errors.append(f"screening_log row {idx}: invalid access_level {access!r}")
            if dec and dec not in ALLOWED_DECISIONS:
                errors.append(f"screening_log row {idx}: invalid decision {dec!r}")
            if dec == "exclude" and not norm(row.get("reason_code")):
                errors.append(f"screening_log row {idx}: exclusion missing reason_code")
            if profile == "systematic" and dec and not reviewer:
                errors.append(f"screening_log row {idx}: systematic decision missing reviewer")
            if stage == "full_text_screened":
                if access != "full_text":
                    errors.append(f"screening_log row {idx}: full_text_screened requires access_level=full_text")
                if dec and not norm(row.get("evidence_basis")):
                    errors.append(f"screening_log row {idx}: full_text_screened decision missing evidence_basis")
            if stage == "full_text_attempted" and access == "full_text":
                warnings.append(f"screening_log row {idx}: full_text_attempted has access_level=full_text; use full_text_screened if review was completed")
            if stage == "full_text":
                warnings.append(f"screening_log row {idx}: legacy ambiguous stage='full_text'; relabel as full_text_attempted or full_text_screened")
            key = (rid, stage, reviewer, norm(row.get("decided_at")))
            if dec and key in seen_events:
                warnings.append(f"screening_log row {idx}: possible duplicate event {key}")
            seen_events.add(key)

        # Detect copied pseudo-full-text events that add no access/evidence beyond title/abstract.
        for rid, events in events_by_record.items():
            ta = [x for x in events if norm(x.get("stage")).lower() == "title_abstract"]
            later = [x for x in events if norm(x.get("stage")).lower() in {"full_text", "full_text_attempted", "full_text_screened"}]
            for lrow in later:
                if not ta:
                    continue
                same_basis = any(norm(x.get("evidence_basis")) == norm(lrow.get("evidence_basis")) and norm(x.get("decision")).lower() == norm(lrow.get("decision")).lower() for x in ta)
                if same_basis and norm(lrow.get("access_level")).lower() not in {"full_text"}:
                    warnings.append(f"{rid}: later screening event duplicates title/abstract decision/evidence without documenting higher access; do not represent this as completed full-text screening")

    # Report-to-study mapping. A bibliographic report is not necessarily an independent study.
    study_rows = read_csv(args.study_map) if args.study_map else []
    study_by_record = {}
    reports_by_study = defaultdict(list)
    if profile in {"standard", "systematic"} and not args.study_map:
        errors.append("standard/systematic workflow requires --study-map")
    for idx, row in enumerate(study_rows, 2):
        rid = norm(row.get("record_id"))
        sid = norm(row.get("study_id"))
        role = norm(row.get("report_role")).lower()
        status = norm(row.get("verification_status")).lower()
        if rid not in ids:
            errors.append(f"study_map row {idx}: unknown record_id {rid}")
        if rid in study_by_record:
            errors.append(f"study_map row {idx}: duplicate mapping for record_id {rid}")
        study_by_record[rid] = sid
        if not sid:
            errors.append(f"study_map row {idx}: missing study_id")
        else:
            reports_by_study[sid].append(row)
        if role and role not in ALLOWED_REPORT_ROLES:
            errors.append(f"study_map row {idx}: invalid report_role {role!r}")
        if status and status not in ALLOWED_STUDY_VERIFICATION:
            errors.append(f"study_map row {idx}: invalid verification_status {status!r}")
    if args.study_map and profile in {"standard", "systematic"} and ids - set(study_by_record):
        errors.append(f"study_map missing {len(ids-set(study_by_record))} record(s)")
    for sid, rows in reports_by_study.items():
        if len(rows) <= 1:
            continue
        for row in rows:
            rid = norm(row.get("record_id"))
            basis = norm(row.get("linkage_basis"))
            status = norm(row.get("verification_status")).lower()
            if not basis:
                msg = f"study {sid}: multi-report grouping lacks linkage_basis for {rid}"
                (errors if profile == "systematic" else warnings).append(msg)
            if status in {"provisional", "unverified", ""}:
                msg = f"study {sid}: multi-report grouping is not sufficiently verified for {rid} ({status or 'blank'})"
                (errors if profile == "systematic" else warnings).append(msg)

    evidence = read_csv(args.evidence)
    claim_ids = set()
    evidence_source_ids = set()
    evidence_by_claim = {}
    for idx, row in enumerate(evidence, 2):
        sid = norm(row.get("source_id"))
        study_id = norm(row.get("study_id"))
        cid = norm(row.get("claim_id"))
        if sid not in ids:
            errors.append(f"evidence row {idx}: unknown source_id {sid}")
        else:
            evidence_source_ids.add(sid)
            if decision_by_id.get(sid) == "exclude":
                warnings.append(f"evidence row {idx}: source {sid} is excluded in final screening")
            mapped = study_by_record.get(sid, "")
            if args.study_map and profile in {"standard", "systematic"} and not study_id:
                errors.append(f"evidence row {idx}: missing study_id for source {sid}")
            elif study_id and mapped and study_id != mapped:
                errors.append(f"evidence row {idx}: study_id {study_id} disagrees with study_map {mapped} for source {sid}")
        if profile in {"standard", "systematic"} and not cid:
            errors.append(f"evidence row {idx}: missing claim_id")
        if cid:
            if cid in claim_ids:
                errors.append(f"evidence row {idx}: duplicate claim_id {cid}")
            claim_ids.add(cid)
            evidence_by_claim[cid] = row
        if not norm(row.get("reported_result")) and not norm(row.get("reviewer_interpretation")):
            warnings.append(f"evidence row {idx}: no reported_result or reviewer_interpretation")
        level = norm(row.get("support_level")).lower()
        if level and level not in ALLOWED_SUPPORT_LEVELS:
            errors.append(f"evidence row {idx}: invalid support_level {level!r}")
        status = norm(row.get("verification_status")).lower()
        if status and status not in ALLOWED_VERIFICATION:
            errors.append(f"evidence row {idx}: invalid verification_status {status!r}")
        if profile in {"standard", "systematic"} and cid and not norm(row.get("evidence_location")):
            warnings.append(f"evidence row {idx}: claim {cid} has no evidence_location")

    included_ids = {rid for rid, dec in decision_by_id.items() if dec == "include"}
    missing_evidence = sorted(included_ids - evidence_source_ids)
    if missing_evidence:
        warnings.append(f"{len(missing_evidence)} included record(s) have no evidence row")

    trail = read_csv(args.citation_trail)
    for idx, row in enumerate(trail, 2):
        s, t = norm(row.get("source_id")), norm(row.get("target_id"))
        rel = norm(row.get("relation")).lower()
        if s not in ids or t not in ids:
            errors.append(f"citation row {idx}: unknown source/target id")
        if s and s == t:
            errors.append(f"citation row {idx}: self-edge")
        if rel not in ALLOWED_RELATIONS:
            errors.append(f"citation row {idx}: invalid relation {rel!r}")
        if not norm(row.get("verification_source")):
            errors.append(f"citation row {idx}: missing verification_source")
        if rel == "same_study_version" and s in study_by_record and t in study_by_record:
            ss, ts = study_by_record.get(s), study_by_record.get(t)
            if ss and ts and ss != ts:
                errors.append(f"citation row {idx}: same_study_version conflicts with study_map ({ss} != {ts})")

    search = read_csv(args.search_log)
    if profile in {"standard", "systematic"} and not search:
        errors.append("search_log is empty")
    qids = set()
    source_rows = defaultdict(list)
    marginal_missing = []
    stopping_rows = []
    for idx, row in enumerate(search, 2):
        qid = norm(row.get("query_id"))
        source = norm(row.get("source"))
        stage = norm(row.get("search_stage")).lower()
        declared_status = norm(row.get("search_status")).lower()
        eff_status = effective_status(row)
        if not source or not norm(row.get("query")):
            errors.append(f"search row {idx}: missing source/query")
        if qid:
            if qid in qids:
                errors.append(f"search row {idx}: duplicate query_id {qid}")
            qids.add(qid)
        else:
            warnings.append(f"search row {idx}: missing query_id")
        if source:
            source_rows[source.casefold()].append(row)
        if profile in {"standard", "systematic"} and not declared_status:
            msg = f"search row {idx}: missing search_status; attempted and successful coverage must be distinguished"
            (errors if profile == "systematic" else warnings).append(msg)
        if profile == "systematic" and not norm(row.get("searched_at")):
            errors.append(f"search row {idx}: systematic profile requires searched_at")
        imported = as_number(row.get("imported_count"))
        if stage in {"structured", "backward", "forward", "gap", "update"} and eff_status != "failed" and imported is not None and imported > 0:
            missing = [f for f in ("new_unique_count", "new_screened_count", "new_included_count") if as_number(row.get(f)) is None]
            if missing:
                marginal_missing.append((idx, qid, missing))
        if norm(row.get("stopping_evidence")).lower() in {"1", "true", "yes", "y"}:
            stopping_rows.append((idx, row))

    target_sources = [norm(x) for x in protocol.get("target_sources", []) if norm(x)]
    source_coverage = {src: source_status(source_rows.get(src.casefold(), [])) for src in target_sources}
    not_attempted = [s for s, st in source_coverage.items() if st == "not_attempted"]
    failed_sources = [s for s, st in source_coverage.items() if st == "failed"]
    partial_sources = [s for s, st in source_coverage.items() if st in {"partial", "unknown"}]
    if not_attempted:
        msg = f"protocol target_sources not attempted: {not_attempted}"
        (errors if profile == "systematic" else warnings).append(msg)
    if failed_sources:
        msg = f"protocol target_sources attempted but failed: {failed_sources}"
        (errors if profile == "systematic" else warnings).append(msg)
    if partial_sources:
        warnings.append(f"protocol target_sources only partially/unclearly covered: {partial_sources}")
    if marginal_missing:
        msg = f"{len(marginal_missing)} iterative search row(s) imported records without complete new_unique/new_screened/new_included counts"
        (errors if profile == "systematic" else warnings).append(msg)
    stopping_verifiable = False
    if stopping_rows:
        stopping_verifiable = all(
            effective_status(r) in {"succeeded", "partial"}
            and all(as_number(r.get(f)) is not None for f in ("new_unique_count", "new_screened_count", "new_included_count"))
            for _, r in stopping_rows
        )
    if protocol.get("stopping_rule") and not stopping_verifiable:
        msg = "stopping rule cannot be mechanically verified from explicit stopping_evidence rows with complete marginal-yield counts"
        (errors if profile == "systematic" else warnings).append(msg)

    synthesis_counts = {"claims": 0, "links": 0}
    if bool(args.synthesis_claims) != bool(args.synthesis_evidence):
        errors.append("provide both --synthesis-claims and --synthesis-evidence, or neither")
    elif args.synthesis_claims and args.synthesis_evidence:
        synth_claims = read_csv(args.synthesis_claims)
        synth_links = read_csv(args.synthesis_evidence)
        synthesis_counts = {"claims": len(synth_claims), "links": len(synth_links)}
        synth_ids = set()
        synth_by_id = {}
        links_by_synth = defaultdict(list)
        for idx, row in enumerate(synth_claims, 2):
            synth_id = norm(row.get("synthesis_id"))
            state = norm(row.get("evidence_state")).lower()
            if not synth_id:
                errors.append(f"synthesis claim row {idx}: missing synthesis_id")
            elif synth_id in synth_ids:
                errors.append(f"synthesis claim row {idx}: duplicate synthesis_id {synth_id}")
            synth_ids.add(synth_id)
            synth_by_id[synth_id] = row
            if not norm(row.get("statement")):
                errors.append(f"synthesis claim row {idx}: missing statement")
            if state and state not in ALLOWED_SYNTH_STATES:
                errors.append(f"synthesis claim row {idx}: invalid evidence_state {state!r}")
        for idx, row in enumerate(synth_links, 2):
            synth_id = norm(row.get("synthesis_id"))
            cid = norm(row.get("claim_id"))
            rel = norm(row.get("relation")).lower()
            if synth_id not in synth_ids:
                errors.append(f"synthesis link row {idx}: unknown synthesis_id {synth_id}")
            if cid not in claim_ids:
                errors.append(f"synthesis link row {idx}: unknown evidence claim_id {cid}")
            if rel not in ALLOWED_SYNTH_RELATIONS:
                errors.append(f"synthesis link row {idx}: invalid relation {rel!r}")
            links_by_synth[synth_id].append(row)
        for synth_id in synth_ids:
            row = synth_by_id.get(synth_id, {})
            state = norm(row.get("evidence_state")).lower()
            slinks = links_by_synth.get(synth_id, [])
            if not slinks and state != "gap":
                errors.append(f"synthesis claim {synth_id} has no evidence links")
                continue
            if state == "gap":
                continue
            sources, studies = set(), set()
            support_sources, support_studies = set(), set()
            contradict_sources, contradict_studies = set(), set()
            verification_counts = Counter()
            for link in slinks:
                erow = evidence_by_claim.get(norm(link.get("claim_id")), {})
                rid = norm(erow.get("source_id"))
                stid = norm(erow.get("study_id")) or study_by_record.get(rid, "")
                rel = norm(link.get("relation")).lower()
                level = norm(erow.get("support_level")).lower()
                ver = norm(erow.get("verification_status")).lower()
                eligible = level in ELIGIBLE_SYNTH_SUPPORT_LEVELS and ver in ELIGIBLE_SYNTH_VERIFICATION
                if rid:
                    sources.add(rid)
                if stid:
                    studies.add(stid)
                if not eligible:
                    continue
                if rel in {"supports", "contradicts"}:
                    verification_counts[ver] += 1
                if rel == "supports":
                    if rid: support_sources.add(rid)
                    if stid: support_studies.add(stid)
                elif rel == "contradicts":
                    if rid: contradict_sources.add(rid)
                    if stid: contradict_studies.add(stid)
            if synthesis_unit == "study":
                support_units, contradict_units, label = support_studies, contradict_studies, "studies"
            else:
                support_units, contradict_units, label = support_sources, contradict_sources, "source records"
            substantive = verification_counts.get("verified", 0) + verification_counts.get("partial", 0)
            if substantive == 0:
                derived_coverage = "not_applicable"
            elif verification_counts.get("partial", 0) == 0:
                derived_coverage = "complete"
            elif verification_counts.get("verified", 0) == 0:
                derived_coverage = "partial_only"
            else:
                derived_coverage = "mixed"
            persisted_coverage = norm(row.get("verification_coverage")).lower()
            if persisted_coverage and persisted_coverage != derived_coverage:
                errors.append(f"synthesis claim {synth_id}: persisted verification_coverage={persisted_coverage!r} disagrees with derived {derived_coverage!r}; rerun audit_synthesis.py --update-claims")
            elif not persisted_coverage:
                warnings.append(f"synthesis claim {synth_id}: verification_coverage is not persisted; run audit_synthesis.py --update-claims")
            persisted_counts = {
                "verified_evidence_count": verification_counts.get("verified", 0),
                "partial_evidence_count": verification_counts.get("partial", 0),
                "eligible_support_unit_count": len(support_units),
                "eligible_contradict_unit_count": len(contradict_units),
            }
            for field, expected in persisted_counts.items():
                raw = norm(row.get(field))
                if raw:
                    try:
                        actual = int(raw)
                    except ValueError:
                        errors.append(f"synthesis claim {synth_id}: {field} must be an integer, got {raw!r}")
                    else:
                        if actual != expected:
                            errors.append(f"synthesis claim {synth_id}: persisted {field}={actual} disagrees with derived {expected}; rerun audit_synthesis.py --update-claims")
            if state == "consistent":
                if len(support_units) < 2:
                    errors.append(f"synthesis claim {synth_id}: consistent evidence requires >=2 distinct eligible supporting {label}")
                if contradict_units:
                    errors.append(f"synthesis claim {synth_id}: consistent evidence has eligible contradicting {label}")
            if state == "mixed" and (not support_units or not contradict_units):
                errors.append(f"synthesis claim {synth_id}: mixed evidence requires eligible supports and contradicts evidence")
            if state == "gap" and (support_units or contradict_units):
                errors.append(f"synthesis claim {synth_id}: gap claim has substantive supporting/contradicting evidence")
            if state == "single_study" and len(support_studies | contradict_studies) != 1:
                errors.append(f"synthesis claim {synth_id}: single_study requires substantive evidence from exactly 1 study")
            if state == "single_source" and len(support_sources | contradict_sources) != 1:
                errors.append(f"synthesis claim {synth_id}: single_source requires substantive evidence from exactly 1 source record")
            if state == "single_source" and studies:
                warnings.append(f"synthesis claim {synth_id}: prefer single_study when study_map is available")

    included_studies = {
        study_by_record[rid] for rid in included_ids
        if rid in study_by_record and study_by_record[rid]
    }
    result = {
        "profile": profile,
        "synthesis_unit": synthesis_unit,
        "counts": {
            "records": len(records),
            "studies": len(set(v for v in study_by_record.values() if v)),
            "screening_rows": len(screening),
            "screening_events": len(screening_log),
            "included_reports": sum(norm(r.get("decision")).lower() == "include" for r in screening),
            "included_studies": len(included_studies),
            "excluded": sum(norm(r.get("decision")).lower() == "exclude" for r in screening),
            "uncertain": sum(norm(r.get("decision")).lower() == "uncertain" for r in screening),
            "evidence_rows": len(evidence),
            "citation_edges": len(trail),
            "search_rows": len(search),
            "synthesis_claims": synthesis_counts["claims"],
            "synthesis_links": synthesis_counts["links"],
            "full_text_screened": sum(norm(r.get("evidence_stage")).lower() == "full_text_screened" for r in screening),
            "full_text_attempted": sum(norm(r.get("evidence_stage")).lower() == "full_text_attempted" for r in screening),
        },
        "search_coverage": source_coverage,
        "stopping_rule_verifiable": stopping_verifiable,
        "marginal_yield_missing_rows": [
            {"row": i, "query_id": q, "missing": m} for i, q, m in marginal_missing
        ],
        "errors": errors,
        "warnings": warnings,
        "passed": not errors,
    }
    if args.report:
        Path(args.report).parent.mkdir(parents=True, exist_ok=True)
        Path(args.report).write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(result, indent=2, ensure_ascii=False))
    raise SystemExit(1 if errors else 0)


if __name__ == "__main__":
    main()
