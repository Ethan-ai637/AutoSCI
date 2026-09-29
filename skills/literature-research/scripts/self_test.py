#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import subprocess
import sys
import tempfile
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PY = sys.executable


def run(*args):
    return subprocess.run(
        [PY, "-S", *map(str, args)], cwd=ROOT, check=True,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
    )


def run_expect_fail(*args):
    proc = subprocess.run(
        [PY, "-S", *map(str, args)], cwd=ROOT, check=False,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
    )
    assert proc.returncode != 0, f"expected failure but command passed: {args}"
    return proc


def write_csv(path, fields, rows):
    with Path(path).open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader(); w.writerows(rows)


def main():
    with tempfile.TemporaryDirectory(prefix="literature-research-") as td:
        t = Path(td)
        normalized = t / "records.normalized.csv"
        deduped = t / "records.deduped.csv"
        report = t / "dedup_report.json"
        review = t / "review"
        protocol = t / "protocol.json"
        search_log = t / "search_log.csv"

        run("scripts/normalize_records.py", "examples/minimal/raw_records.csv", "-o", normalized)
        run("scripts/deduplicate_records.py", normalized, "-o", deduped, "--report", report)
        data = json.loads(report.read_text())
        assert data["input_records"] == 4 and data["output_records"] == 3
        run("scripts/init_review_artifacts.py", deduped, "--outdir", review)
        workspace_meta = json.loads((review / "workspace_meta.json").read_text(encoding="utf-8"))
        assert workspace_meta["workspace_schema"] == "autosci-literature-research-workspace-v2"
        assert workspace_meta["created_by_skill_version"] == "1.6.1"

        records = list(csv.DictReader(deduped.open(encoding="utf-8")))
        record_ids = [r["record_id"] for r in records]

        protocol.write_text(json.dumps({
            "protocol_id": "SELFTEST-001",
            "protocol_version": "1.0",
            "created_at": "2026-09-29",
            "profile": "standard",
            "research_question": "Which methods are evaluated for widget detection or classification?",
            "concepts": [
                {"name": "widgets", "terms": ["widget"]},
                {"name": "methods", "terms": ["deep learning", "transformer", "baseline"]}
            ],
            "inclusion_criteria": ["evaluates a widget method"],
            "exclusion_criteria": ["not about widgets"],
            "target_sources": ["ExampleDB", "OtherDB"],
            "stopping_rule": "Complete the two planned example searches.",
            "synthesis_unit": "study",
            "screening_plan": {"stages": ["title_abstract"], "reviewers_per_record": 1, "conflict_resolution": "adjudication"},
            "deterministic_exclusion_rules": [],
            "protocol_changes": []
        }, indent=2), encoding="utf-8")

        write_csv(search_log,
            ["query_id", "search_stage", "source", "interface", "query", "searched_at", "filters", "concept_blocks", "search_status", "result_count", "imported_count", "new_unique_count", "new_screened_count", "new_included_count", "stopping_evidence", "coverage_note", "notes"],
            [
                {"query_id": "Q1", "search_stage": "structured", "source": "ExampleDB", "interface": "example", "query": "widget AND methods", "searched_at": "2026-09-29", "filters": "", "concept_blocks": "widgets;methods", "search_status": "succeeded", "result_count": "3", "imported_count": "3", "new_unique_count": "3", "new_screened_count": "3", "new_included_count": "3", "stopping_evidence": "", "coverage_note": "complete fixture", "notes": ""},
                {"query_id": "Q2", "search_stage": "seed", "source": "OtherDB", "interface": "example", "query": "deep learning widget", "searched_at": "2026-09-29", "filters": "", "concept_blocks": "widgets;methods", "search_status": "succeeded", "result_count": "1", "imported_count": "1", "new_unique_count": "0", "new_screened_count": "0", "new_included_count": "0", "stopping_evidence": "yes", "coverage_note": "complete fixture", "notes": "duplicate DOI"},
            ]
        )
        run("scripts/audit_search.py", "--protocol", protocol, "--search-log", search_log, "--report", review / "search_audit.json")

        screening_log = review / "screening_log.csv"
        events = list(csv.DictReader(screening_log.open(encoding="utf-8")))
        for row in events:
            row["reviewer"] = "reviewer-1"
            row["access_level"] = "abstract"
            row["decision"] = "include"
            row["decided_at"] = "2026-09-29"
            row["evidence_basis"] = "title/abstract"
        write_csv(screening_log, list(events[0].keys()), events)
        run("scripts/reconcile_screening.py", screening_log, "--records", deduped, "-o", review / "screening.csv", "--conflicts", review / "screening_conflicts.json")

        # Exercise the report-vs-study layer: first two reports belong to one verified study.
        study_map_path = review / "study_map.csv"
        study_map = list(csv.DictReader(study_map_path.open(encoding="utf-8")))
        shared_study = study_map[0]["study_id"]
        study_map[0].update({
            "study_id": shared_study,
            "report_role": "preprint_version",
            "linkage_basis": "self-test explicit version-family fixture",
            "verification_status": "verified",
        })
        study_map[1].update({
            "study_id": shared_study,
            "report_role": "journal_version",
            "linkage_basis": "self-test explicit version-family fixture",
            "verification_status": "verified",
        })
        write_csv(study_map_path, list(study_map[0].keys()), study_map)
        study_by_record = {r["record_id"]: r["study_id"] for r in study_map}

        run("scripts/cluster_records.py", review / "screening.csv", "--records", deduped, "-o", review / "clusters.csv", "--summary", review / "cluster_summary.md")

        evidence_fields = [
            "source_id", "study_id", "source_version", "claim_id", "research_question_component", "study_design_or_method",
            "population_dataset_context", "intervention_or_method", "comparator_or_baseline", "outcome_metric",
            "reported_result", "uncertainty_or_variance", "authors_interpretation", "reviewer_interpretation",
            "limitations", "evidence_location", "support_level", "verification_status", "evidence_strength_note"
        ]
        evidence_rows = []
        for i, rid in enumerate(record_ids, 1):
            evidence_rows.append({
                "source_id": rid, "study_id": study_by_record[rid], "source_version": "record", "claim_id": f"E{i:03d}",
                "research_question_component": "methods", "study_design_or_method": "evaluation",
                "population_dataset_context": "widget datasets", "intervention_or_method": records[i-1]["title"],
                "comparator_or_baseline": "", "outcome_metric": "", "reported_result": records[i-1]["abstract"],
                "uncertainty_or_variance": "", "authors_interpretation": "", "reviewer_interpretation": "",
                "limitations": "minimal example", "evidence_location": "abstract", "support_level": "direct",
                "verification_status": "verified", "evidence_strength_note": "example metadata only"
            })
        write_csv(review / "evidence_table.csv", evidence_fields, evidence_rows)

        trail_fields = ["source_id", "target_id", "relation", "verification_source", "verification_url", "verified_at", "notes"]
        write_csv(review / "citation_trail.csv", trail_fields, [
            {
                "source_id": record_ids[0], "target_id": record_ids[1], "relation": "same_study_version",
                "verification_source": "self-test fixture", "verification_url": "", "verified_at": "2026-09-29", "notes": "version-family test"
            },
            {
                "source_id": record_ids[1], "target_id": record_ids[2], "relation": "discovery_from",
                "verification_source": "self-test fixture", "verification_url": "", "verified_at": "2026-09-29", "notes": "example discovery"
            }
        ])
        run("scripts/audit_citation_trail.py", review / "citation_trail.csv", "--records", deduped, "--report", review / "citation_trail_audit.json")
        run(
            "scripts/audit_studies.py",
            "--records", deduped,
            "--study-map", study_map_path,
            "--screening", review / "screening.csv",
            "--citation-trail", review / "citation_trail.csv",
            "--evidence", review / "evidence_table.csv",
            "--profile", "standard",
            "--summary", review / "study_summary.csv",
            "--report", review / "study_audit.json",
        )
        study_audit = json.loads((review / "study_audit.json").read_text(encoding="utf-8"))
        assert study_audit["studies"] == 2 and study_audit["included_reports"] == 3 and study_audit["included_studies"] == 2

        synth_fields = [
            "synthesis_id", "statement", "research_question_component", "evidence_state",
            "verification_coverage", "verified_evidence_count", "partial_evidence_count",
            "eligible_support_unit_count", "eligible_contradict_unit_count",
            "scope", "caveat", "notes"
        ]
        write_csv(review / "synthesis_claims.csv", synth_fields,
            [{"synthesis_id": "S001", "statement": "Multiple independent studies evaluate method families for widget tasks.", "research_question_component": "methods", "evidence_state": "consistent", "verification_coverage": "", "verified_evidence_count": "", "partial_evidence_count": "", "eligible_support_unit_count": "", "eligible_contradict_unit_count": "", "scope": "minimal fixture", "caveat": "synthetic example", "notes": ""}]
        )
        # Link one report from the shared study plus the third report from a second study.
        write_csv(review / "synthesis_evidence.csv", ["synthesis_id", "claim_id", "relation", "notes"], [
            {"synthesis_id": "S001", "claim_id": "E001", "relation": "supports", "notes": ""},
            {"synthesis_id": "S001", "claim_id": "E003", "relation": "supports", "notes": ""},
        ])
        run(
            "scripts/audit_synthesis.py",
            "--evidence", review / "evidence_table.csv",
            "--claims", review / "synthesis_claims.csv",
            "--links", review / "synthesis_evidence.csv",
            "--study-map", study_map_path,
            "--report", review / "synthesis_audit.json",
            "--update-claims",
        )
        synth_audit = json.loads((review / "synthesis_audit.json").read_text(encoding="utf-8"))
        assert synth_audit["claim_metrics"]["S001"]["studies"] == 2
        assert synth_audit["claim_metrics"]["S001"]["verification_coverage"] == "complete"
        persisted_claim = next(csv.DictReader((review / "synthesis_claims.csv").open(encoding="utf-8")))
        assert persisted_claim["verification_coverage"] == "complete"
        assert persisted_claim["verified_evidence_count"] == "2"
        assert persisted_claim["partial_evidence_count"] == "0"
        assert persisted_claim["eligible_support_unit_count"] == "2"
        assert persisted_claim["eligible_contradict_unit_count"] == "0"

        # Guard against false replication: two reports from the same study cannot satisfy `consistent`.
        false_links = review / "synthesis_evidence.false_independence.csv"
        write_csv(false_links, ["synthesis_id", "claim_id", "relation", "notes"], [
            {"synthesis_id": "S001", "claim_id": "E001", "relation": "supports", "notes": ""},
            {"synthesis_id": "S001", "claim_id": "E002", "relation": "supports", "notes": ""},
        ])
        failed = run_expect_fail(
            "scripts/audit_synthesis.py",
            "--evidence", review / "evidence_table.csv",
            "--claims", review / "synthesis_claims.csv",
            "--links", false_links,
            "--study-map", study_map_path,
        )
        assert "requires >=2 distinct eligible supporting studies" in failed.stdout

        # Context-only/unverified evidence must not satisfy a `consistent` claim.
        weak_evidence = review / "evidence_table.context_only.csv"
        weak_rows = [dict(r) for r in evidence_rows]
        weak_rows[0]["support_level"] = "contextual"
        weak_rows[0]["verification_status"] = "unverified"
        write_csv(weak_evidence, evidence_fields, weak_rows)
        weak_failed = run_expect_fail(
            "scripts/audit_synthesis.py",
            "--evidence", weak_evidence,
            "--claims", review / "synthesis_claims.csv",
            "--links", review / "synthesis_evidence.csv",
            "--study-map", study_map_path,
        )
        assert "requires >=2 distinct eligible supporting studies" in weak_failed.stdout

        # v1.6: attempted/failed source coverage must not count as successful coverage.
        failed_search = t / "search_log.failed.csv"
        failed_rows = list(csv.DictReader(search_log.open(encoding="utf-8")))
        failed_rows[1]["search_status"] = "failed"
        failed_rows[1]["imported_count"] = "0"
        failed_rows[1]["notes"] = "HTTP 503"
        write_csv(failed_search, list(failed_rows[0].keys()), failed_rows)
        failed_search_report = review / "search_audit.failed.json"
        run("scripts/audit_search.py", "--protocol", protocol, "--search-log", failed_search, "--report", failed_search_report)
        failed_search_audit = json.loads(failed_search_report.read_text(encoding="utf-8"))
        assert failed_search_audit["source_coverage"]["OtherDB"] == "failed"
        assert "OtherDB" in failed_search_audit["failed_target_sources"]

        # v1.6: a stopping rule without complete tagged marginal-yield evidence is not mechanically verifiable.
        no_yield = t / "search_log.no_yield.csv"
        no_yield_rows = list(csv.DictReader(search_log.open(encoding="utf-8")))
        no_yield_rows[1]["new_screened_count"] = ""
        write_csv(no_yield, list(no_yield_rows[0].keys()), no_yield_rows)
        no_yield_report = review / "search_audit.no_yield.json"
        run("scripts/audit_search.py", "--protocol", protocol, "--search-log", no_yield, "--report", no_yield_report)
        no_yield_audit = json.loads(no_yield_report.read_text(encoding="utf-8"))
        assert no_yield_audit["stopping_rule_status"] == "not_assessable"

        # v1.6: strict full-text protocols cannot be satisfied by title/abstract screening or legacy pseudo-full-text.
        strict_protocol = t / "protocol.strict_fulltext.json"
        strict_data = json.loads(protocol.read_text(encoding="utf-8"))
        strict_data["screening_plan"]["stages"] = ["title_abstract", "full_text"]
        strict_protocol.write_text(json.dumps(strict_data, indent=2), encoding="utf-8")
        strict_fail = run_expect_fail(
            "scripts/preflight.py", "--protocol", strict_protocol, "--records", deduped,
            "--screening", review / "screening.csv", "--screening-log", review / "screening_log.csv",
            "--study-map", study_map_path, "--evidence", review / "evidence_table.csv",
            "--citation-trail", review / "citation_trail.csv", "--search-log", search_log,
            "--synthesis-claims", review / "synthesis_claims.csv", "--synthesis-evidence", review / "synthesis_evidence.csv"
        )
        assert "has not completed true full-text screening" in strict_fail.stdout

        # v1.6: an explicit deterministic exclusion rule outranks uncertain.
        rule_protocol = t / "protocol.rule.json"
        rule_data = json.loads(protocol.read_text(encoding="utf-8"))
        rule_data["deterministic_exclusion_rules"] = [{
            "rule_id": "exclude_classical_title", "field": "title", "operator": "contains_any",
            "values": ["Classical baselines"], "reason_code": "explicit_test_exclusion",
            "criterion_id": "explicit_test_exclusion", "enabled": True
        }]
        rule_protocol.write_text(json.dumps(rule_data, indent=2), encoding="utf-8")
        rule_candidates = review / "obvious_exclusions.csv"
        run("scripts/apply_screening_rules.py", "--protocol", rule_protocol, "--records", deduped, "--output", rule_candidates)
        candidates = list(csv.DictReader(rule_candidates.open(encoding="utf-8")))
        assert len(candidates) == 1 and candidates[0]["reason_code"] == "explicit_test_exclusion"
        rule_screening = t / "screening.rule.csv"
        rule_rows = list(csv.DictReader((review / "screening.csv").open(encoding="utf-8")))
        target = next(r for r in rule_rows if "Classical baselines" in r["title"])
        target["decision"] = "uncertain"
        target["reason_code"] = "insufficient_accessible_evidence"
        write_csv(rule_screening, list(rule_rows[0].keys()), rule_rows)
        rule_fail = run_expect_fail(
            "scripts/preflight.py", "--protocol", rule_protocol, "--records", deduped,
            "--screening", rule_screening, "--screening-log", review / "screening_log.csv",
            "--study-map", study_map_path, "--evidence", review / "evidence_table.csv",
            "--citation-trail", review / "citation_trail.csv", "--search-log", search_log,
            "--synthesis-claims", review / "synthesis_claims.csv", "--synthesis-evidence", review / "synthesis_evidence.csv"
        )
        assert "matches high-precision deterministic exclusion rule" in rule_fail.stdout

        # v1.6.1: publication types literally excluded by protocol criteria are derived safely even when explicit rules are empty.
        derived_protocol = t / "protocol.derived_rule.json"
        derived_data = json.loads(protocol.read_text(encoding="utf-8"))
        derived_data["exclusion_criteria"] = ["Exclude reviews, systematic reviews, scoping reviews, editorials, and commentaries."]
        derived_data["deterministic_exclusion_rules"] = []
        derived_protocol.write_text(json.dumps(derived_data, indent=2), encoding="utf-8")
        derived_records = t / "records.derived_rule.csv"
        derived_rows = [dict(r) for r in records]
        derived_rows[0]["publication_type"] = "Journal Article; Review; English Abstract"
        write_csv(derived_records, list(derived_rows[0].keys()), derived_rows)
        derived_candidates = review / "obvious_exclusions.derived.csv"
        run("scripts/apply_screening_rules.py", "--protocol", derived_protocol, "--records", derived_records, "--output", derived_candidates)
        derived_matches = list(csv.DictReader(derived_candidates.open(encoding="utf-8")))
        assert len(derived_matches) == 1
        assert derived_matches[0]["rule_source"] == "derived_safe"
        assert derived_matches[0]["reason_code"] == "WRONG_PUBLICATION_TYPE"

        # Disabled explicit rules must not leak into preview or preflight.
        disabled_protocol = t / "protocol.disabled_rule.json"
        disabled_data = json.loads(protocol.read_text(encoding="utf-8"))
        disabled_data["deterministic_exclusion_rules"] = [{
            "rule_id": "disabled_test", "field": "title", "operator": "contains_any",
            "values": ["Classical baselines"], "reason_code": "disabled", "enabled": False
        }]
        disabled_protocol.write_text(json.dumps(disabled_data, indent=2), encoding="utf-8")
        disabled_candidates = review / "obvious_exclusions.disabled.csv"
        run("scripts/apply_screening_rules.py", "--protocol", disabled_protocol, "--records", deduped, "--output", disabled_candidates)
        assert list(csv.DictReader(disabled_candidates.open(encoding="utf-8"))) == []

        run(
            "scripts/preflight.py",
            "--protocol", protocol,
            "--records", deduped,
            "--screening", review / "screening.csv",
            "--screening-log", review / "screening_log.csv",
            "--study-map", study_map_path,
            "--evidence", review / "evidence_table.csv",
            "--citation-trail", review / "citation_trail.csv",
            "--search-log", search_log,
            "--synthesis-claims", review / "synthesis_claims.csv",
            "--synthesis-evidence", review / "synthesis_evidence.csv",
            "--report", review / "preflight.json",
        )
        preflight = json.loads((review / "preflight.json").read_text(encoding="utf-8"))
        assert preflight["passed"] is True
        assert preflight["counts"]["included_reports"] == 3
        assert preflight["counts"]["included_studies"] == 2

        run(
            "scripts/validate_workspace.py",
            "--root", t,
            "--require-final",
            "--report", "review/schema_audit.json",
        )
        schema_audit = json.loads((review / "schema_audit.json").read_text(encoding="utf-8"))
        assert schema_audit["passed"] is True
        assert schema_audit["workspace_schema"] == "autosci-literature-research-workspace-v2"

        run(
            "scripts/build_flow_report.py",
            "--search-log", search_log,
            "--records", deduped,
            "--dedup-report", report,
            "--screening", review / "screening.csv",
            "--screening-log", review / "screening_log.csv",
            "--study-map", study_map_path,
            "--evidence", review / "evidence_table.csv",
            "--synthesis-claims", review / "synthesis_claims.csv",
            "--synthesis-evidence", review / "synthesis_evidence.csv",
            "--out", review / "flow_report.json",
        )
        flow = json.loads((review / "flow_report.json").read_text(encoding="utf-8"))
        assert flow["flow"]["deduplication"]["canonical_records"] == 3
        assert flow["flow"]["study_identity"]["included_studies"] == 2

        run(
            "scripts/build_evidence_graph.py",
            "--records", deduped,
            "--screening", review / "screening.csv",
            "--study-map", study_map_path,
            "--evidence", review / "evidence_table.csv",
            "--citation-trail", review / "citation_trail.csv",
            "--synthesis-claims", review / "synthesis_claims.csv",
            "--synthesis-evidence", review / "synthesis_evidence.csv",
            "--clusters", review / "clusters.csv",
            "--out", review / "evidence_graph.json",
        )
        graph = json.loads((review / "evidence_graph.json").read_text(encoding="utf-8"))
        assert graph["passed"] is True
        assert graph["counts"]["reports"] == 3
        assert graph["counts"]["studies"] == 2
        assert graph["counts"]["synthesis_claims"] == 1
        assert any(e["type"] == "synthesis_supports" for e in graph["edges"])
        synth_node = next(n for n in graph["nodes"] if n.get("type") == "synthesis_claim")
        assert synth_node["verification_coverage"] == "complete"

        run(
            "scripts/build_synthesis_brief.py",
            "--evidence", review / "evidence_table.csv",
            "--claims", review / "synthesis_claims.csv",
            "--links", review / "synthesis_evidence.csv",
            "--records", deduped,
            "--study-map", study_map_path,
            "--out", review / "synthesis_brief.md",
        )
        brief = (review / "synthesis_brief.md").read_text(encoding="utf-8")
        assert "S001" in brief and "eligible" in brief and "Verification coverage:** complete" in brief and "introduces no new scientific claims" in brief

        run("scripts/snapshot_review.py", "--root", t, "--manifest", "review/review_manifest.json", "--require-preflight")
        run("scripts/verify_snapshot.py", review / "review_manifest.json", "--root", t)
        manifest = json.loads((review / "review_manifest.json").read_text(encoding="utf-8"))
        frozen_paths = {x["path"] for x in manifest["artifacts"]}
        assert "review/evidence_graph.json" in frozen_paths
        assert "review/synthesis_brief.md" in frozen_paths
        assert "review/workspace_meta.json" in frozen_paths
        assert "review/schema_audit.json" in frozen_paths
        assert manifest["workspace_schema"] == "autosci-literature-research-workspace-v2"

        handoff = t / "handoff"
        run(
            "scripts/build_handoff_bundle.py",
            "--root", t,
            "--outdir", handoff,
            "--target", "scientific-figure",
        )
        handoff_manifest = json.loads((handoff / "handoff_manifest.json").read_text(encoding="utf-8"))
        assert handoff_manifest["target"] == "scientific-figure"
        assert handoff_manifest["frozen"] is True
        assert handoff_manifest["workspace_schema"] == "autosci-literature-research-workspace-v2"
        assert (handoff / "review/evidence_graph.json").exists()
        assert "quantitative plots" in " ".join(handoff_manifest["routing_notes"])

        # Frozen snapshots must detect later workspace edits.
        original_search = search_log.read_text(encoding="utf-8")
        search_log.write_text(original_search + "\n", encoding="utf-8")
        changed = run_expect_fail("scripts/verify_snapshot.py", review / "review_manifest.json", "--root", t)
        assert "changed artifact: search_log.csv" in changed.stdout
        stale_handoff = run_expect_fail(
            "scripts/build_handoff_bundle.py",
            "--root", t,
            "--outdir", t / "handoff-stale",
            "--target", "generic",
        )
        assert "frozen snapshot verification failed before handoff" in (stale_handoff.stdout + stale_handoff.stderr)
        search_log.write_text(original_search, encoding="utf-8")

        # Legacy migration is preview-first and must not invent scientific content.
        legacy = t / "legacy"
        legacy_review = legacy / "review"
        legacy_review.mkdir(parents=True)
        shutil.copy2(protocol, legacy / "protocol.json")
        shutil.copy2(search_log, legacy / "search_log.csv")
        shutil.copy2(deduped, legacy / "records.deduped.csv")
        shutil.copy2(review / "screening.csv", legacy_review / "screening.csv")
        shutil.copy2(review / "study_map.csv", legacy_review / "study_map.csv")
        shutil.copy2(review / "evidence_table.csv", legacy_review / "evidence_table.csv")
        shutil.copy2(review / "citation_trail.csv", legacy_review / "citation_trail.csv")
        shutil.copy2(review / "synthesis_claims.csv", legacy_review / "synthesis_claims.csv")
        shutil.copy2(review / "synthesis_evidence.csv", legacy_review / "synthesis_evidence.csv")
        shutil.copy2(review / "preflight.json", legacy_review / "preflight.json")
        legacy_preserved = {
            p.relative_to(legacy).as_posix(): p.read_bytes()
            for p in legacy.rglob("*") if p.is_file()
        }
        legacy_preview = run("scripts/migrate_workspace.py", "--root", legacy)
        assert not (legacy_review / "workspace_meta.json").exists()
        assert "create_workspace_meta" in legacy_preview.stdout
        run("scripts/migrate_workspace.py", "--root", legacy, "--apply")
        migrated_meta = json.loads((legacy_review / "workspace_meta.json").read_text(encoding="utf-8"))
        assert migrated_meta["workspace_schema"] == "autosci-literature-research-workspace-v2"
        assert migrated_meta["migration_history"]
        for rel, before in legacy_preserved.items():
            assert (legacy / rel).read_bytes() == before, f"migration unexpectedly changed compatible legacy file: {rel}"
        run("scripts/validate_workspace.py", "--root", legacy, "--require-final")

        # Structural drift must be rejected deterministically.
        broken = t / "broken-evidence.csv"
        broken_fields = [x for x in evidence_fields if x != "claim_id"]
        write_csv(broken, broken_fields, [{k: v for k, v in evidence_rows[0].items() if k != "claim_id"}])
        shutil.copy2(broken, legacy_review / "evidence_table.csv")
        structural_fail = run_expect_fail("scripts/validate_workspace.py", "--root", legacy, "--require-final")
        assert "missing required columns" in structural_fail.stdout and "claim_id" in structural_fail.stdout
        run("scripts/migrate_workspace.py", "--root", legacy, "--apply")
        run("scripts/validate_workspace.py", "--root", legacy, "--require-final")
        migrated_evidence = list(csv.DictReader((legacy_review / "evidence_table.csv").open(encoding="utf-8")))
        assert "claim_id" in migrated_evidence[0] and migrated_evidence[0]["claim_id"] == ""
        semantic_after_migration = run_expect_fail(
            "scripts/preflight.py",
            "--protocol", legacy / "protocol.json",
            "--records", legacy / "records.deduped.csv",
            "--screening", legacy_review / "screening.csv",
            "--study-map", legacy_review / "study_map.csv",
            "--evidence", legacy_review / "evidence_table.csv",
            "--citation-trail", legacy_review / "citation_trail.csv",
            "--search-log", legacy / "search_log.csv",
            "--synthesis-claims", legacy_review / "synthesis_claims.csv",
            "--synthesis-evidence", legacy_review / "synthesis_evidence.csv",
        )
        assert "missing claim_id" in semantic_after_migration.stdout

        print("literature-research self-test: PASS")


if __name__ == "__main__":
    main()
