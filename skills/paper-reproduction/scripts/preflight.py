#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
from pathlib import Path
from typing import Any

from _util import load_json, read_jsonl, sha256_file, utc_now, write_json

ALLOWED_STATES = {
    "exact_reproduction", "within_reported_variation", "numerically_different", "qualitatively_consistent",
    "partial_reproduction", "blocked_by_missing_data", "blocked_by_missing_artifact",
    "blocked_by_environment", "underspecified", "not_attempted"
}


def check(cond: bool, code: str, message: str, severity: str = "error") -> dict[str, Any] | None:
    if cond:
        return None
    return {"severity": severity, "code": code, "message": message}


def digest(path: Path) -> str | None:
    return sha256_file(path) if path.is_file() else None


def main() -> int:
    ap = argparse.ArgumentParser(description="Structural and semantic preflight for an AutoSCI paper-reproduction workspace.")
    ap.add_argument("workspace", type=Path)
    ap.add_argument("--output", type=Path)
    args = ap.parse_args()
    ws = args.workspace.resolve()
    findings: list[dict[str, Any]] = []

    contract_path = ws / "reproduction_contract.json"
    if not contract_path.exists():
        findings.append({"severity": "error", "code": "missing_contract", "message": "reproduction_contract.json is required"})
        contract = {}
    else:
        contract = load_json(contract_path)

    current_hashes = {
        "reproduction_contract_sha256": digest(contract_path),
        "run_plan_sha256": digest(ws / "run_plan.json"),
        "repository_manifest_sha256": digest(ws / "repository_manifest.json"),
        "data_manifest_sha256": digest(ws / "data_manifest.json"),
        "checkpoint_manifest_sha256": digest(ws / "checkpoint_manifest.jsonl"),
        "claim_code_map_sha256": digest(ws / "claim_code_map.jsonl"),
    }

    mode = contract.get("mode")
    profile = contract.get("profile")
    claims = contract.get("target_claims") or []
    claim_by_id = {c.get("claim_id"): c for c in claims if isinstance(c, dict) and c.get("claim_id")}
    claim_ids = set(claim_by_id)

    for f in [
        check(mode in {"REPO_REPRODUCE", "PAPER_ONLY", "REPO_AUDIT"}, "bad_mode", "contract mode is invalid"),
        check(profile in {"diagnostic", "standard", "release"}, "bad_profile", "contract profile is invalid"),
    ]:
        if f: findings.append(f)

    if contract.get("skill_version") not in {"1.2.0", None}:
        findings.append({"severity": "warning", "code": "skill_version_mismatch", "message": f"contract skill_version is {contract.get('skill_version')!r}, expected 1.2.0 for this package"})

    if mode != "REPO_AUDIT":
        f = check(bool(claim_ids), "no_target_claim", "at least one target claim is required outside REPO_AUDIT")
        if f: findings.append(f)

    for c in claims:
        cid = c.get("claim_id", "<missing>")
        cr = c.get("comparison_rule") or {}
        if c.get("type") in {"table_result", "figure_result", "benchmark", "runtime", "resource"} and cr.get("kind") == "unspecified":
            findings.append({"severity": "warning", "code": "comparison_unspecified", "message": f"{cid}: numeric/scoped claim has unspecified comparison rule"})
        if cr.get("kind") != "unspecified" and cr.get("predeclared") is not True:
            findings.append({"severity": "warning", "code": "comparison_not_predeclared", "message": f"{cid}: comparison rule is not marked predeclared"})

    if not (ws / "paper_manifest.json").exists() and mode != "REPO_AUDIT":
        findings.append({"severity": "error", "code": "missing_paper_manifest", "message": "paper_manifest.json is required"})
    elif mode != "REPO_AUDIT":
        paper = load_json(ws / "paper_manifest.json")
        if not paper.get("title"):
            findings.append({"severity": "warning", "code": "paper_title_missing", "message": "paper manifest has no title"})
        if not any([paper.get("doi"), paper.get("arxiv_id"), paper.get("canonical_url"), paper.get("source_used_for_reproduction")]):
            findings.append({"severity": "warning", "code": "paper_identity_weak", "message": "paper manifest has no DOI/arXiv/canonical/source locator"})

    plan_path = ws / "run_plan.json"
    if mode != "REPO_AUDIT" and profile in {"standard", "release"}:
        if not plan_path.exists():
            findings.append({"severity": "error", "code": "missing_run_plan", "message": "run_plan.json is required for standard/release reproduction"})
        else:
            plan = load_json(plan_path)
            items = plan.get("items") or []
            target_planned = set()
            smoke_present = False
            for item in items:
                if item.get("stage") == "smoke": smoke_present = True
                if item.get("scientific_target") is True or item.get("stage") == "target":
                    target_planned.update(item.get("claim_ids") or [])
            if mode == "REPO_REPRODUCE" and not smoke_present:
                findings.append({"severity": "warning", "code": "smoke_not_planned", "message": "no smoke-test step appears in run_plan.json"})
            for cid in claim_ids:
                if cid not in target_planned:
                    findings.append({"severity": "error", "code": "claim_not_planned", "message": f"{cid}: no scientific target step in run_plan.json"})

    repo = {}
    repo_commit = None
    if mode in {"REPO_REPRODUCE", "REPO_AUDIT"}:
        repo_path = ws / "repository_manifest.json"
        if not repo_path.exists():
            findings.append({"severity": "error", "code": "missing_repo_manifest", "message": "repository_manifest.json is required"})
        else:
            repo = load_json(repo_path)
            rev = repo.get("source_revision") or {}
            repo_commit = rev.get("commit")
            if not repo_commit:
                findings.append({"severity": "error", "code": "unpinned_revision", "message": "repository source revision has no commit SHA"})
            if rev.get("selection_basis") == "unknown":
                findings.append({"severity": "warning", "code": "unknown_revision_basis", "message": "revision selection basis is unknown"})
            if repo.get("official_status") == "unknown":
                findings.append({"severity": "warning", "code": "unknown_repo_identity", "message": "repository official status is unresolved"})
            elif not (repo.get("identity_evidence") or []):
                findings.append({"severity": "error" if profile == "release" else "warning", "code": "repo_identity_without_evidence", "message": "repository official status is set but identity_evidence is empty"})
            if rev.get("selection_basis") == "current_head_fallback":
                findings.append({"severity": "warning", "code": "current_head_fallback", "message": "current repository head is being used as a fallback rather than a paper-anchored revision"})
            if (repo.get("git") or {}).get("dirty"):
                findings.append({"severity": "warning", "code": "repo_manifest_dirty", "message": "repository manifest was captured from a dirty worktree"})

    mappings = read_jsonl(ws / "claim_code_map.jsonl")
    mapped_claims = {m.get("claim_id") for m in mappings if m.get("mapping_status") in {"verified", "partial", "inferred"}}
    if mode == "REPO_REPRODUCE":
        for cid in claim_ids:
            if cid not in mapped_claims:
                findings.append({"severity": "error", "code": "claim_unmapped", "message": f"{cid}: no mapped code artifact"})
    if repo_commit:
        for m in mappings:
            for art in m.get("repo_artifacts") or []:
                rev = art.get("revision")
                if rev and rev != repo_commit:
                    findings.append({"severity": "error" if profile == "release" else "warning", "code": "mapping_revision_mismatch", "message": f"{m.get('mapping_id')}: artifact {art.get('path')} revision {rev} != repository commit {repo_commit}"})

    data_ids = {d.get("dataset_id") for d in (load_json(ws / "data_manifest.json").get("datasets") or []) if d.get("dataset_id")} if (ws / "data_manifest.json").exists() else set()
    checkpoint_rows = read_jsonl(ws / "checkpoint_manifest.jsonl")
    checkpoint_ids = {r.get("checkpoint_id") for r in checkpoint_rows if r.get("checkpoint_id")}

    ledger = read_jsonl(ws / "run_ledger.jsonl")
    run_ids: set[str] = set()
    run_by_id: dict[str, dict] = {}
    for row in ledger:
        rid = row.get("run_id")
        if not rid:
            findings.append({"severity": "error", "code": "ledger_missing_run_id", "message": "run ledger entry lacks run_id"})
            continue
        if rid in run_ids:
            findings.append({"severity": "error", "code": "duplicate_run_id", "message": f"duplicate run_id: {rid}"})
        run_ids.add(rid); run_by_id[rid] = row
        for cid in row.get("claim_ids") or []:
            if claim_ids and cid not in claim_ids:
                findings.append({"severity": "error", "code": "unknown_run_claim", "message": f"{rid}: references unknown claim {cid}"})
        if row.get("git_dirty") and not row.get("patch_sha256"):
            findings.append({"severity": "error", "code": "dirty_without_patch_hash", "message": f"{rid}: dirty run has no patch fingerprint"})
        if repo_commit and row.get("source_commit") and row.get("source_commit") != repo_commit:
            findings.append({"severity": "error" if row.get("run_kind") == "target" else "warning", "code": "run_commit_mismatch", "message": f"{rid}: source_commit {row.get('source_commit')} != repository manifest commit {repo_commit}"})
        inputs = row.get("inputs") or {}
        if inputs.get("dataset_id") and inputs.get("dataset_id") not in data_ids:
            findings.append({"severity": "error", "code": "run_unknown_dataset", "message": f"{rid}: dataset_id {inputs.get('dataset_id')} not found in data_manifest.json"})
        if inputs.get("checkpoint_id") and inputs.get("checkpoint_id") not in checkpoint_ids:
            findings.append({"severity": "error", "code": "run_unknown_checkpoint", "message": f"{rid}: checkpoint_id {inputs.get('checkpoint_id')} not found in checkpoint_manifest.jsonl"})

        snap = row.get("provenance_snapshot") or {}
        if row.get("run_kind") == "target":
            if not snap.get("reproduction_contract_sha256"):
                findings.append({"severity": "error", "code": "target_run_unbound_contract", "message": f"{rid}: target run is not bound to a reproduction contract hash"})
            for key in ["reproduction_contract_sha256", "run_plan_sha256", "repository_manifest_sha256", "data_manifest_sha256", "checkpoint_manifest_sha256", "claim_code_map_sha256"]:
                recorded = snap.get(key)
                current = current_hashes.get(key)
                if not recorded:
                    findings.append({"severity": "error", "code": "target_run_incomplete_snapshot", "message": f"{rid}: target run lacks required {key} snapshot"})
                elif not current:
                    findings.append({"severity": "error", "code": "run_provenance_missing", "message": f"{rid}: {key[:-7]} is missing after the target run"})
                elif recorded != current:
                    findings.append({"severity": "error", "code": "run_provenance_stale", "message": f"{rid}: {key} changed after the run"})

    metric_rows: list[dict[str, str]] = []
    metrics_path = ws / "metrics.csv"
    if metrics_path.exists():
        with metrics_path.open("r", encoding="utf-8", newline="") as f:
            for i, row in enumerate(csv.DictReader(f), start=2):
                if not any((v or "").strip() for v in row.values()): continue
                metric_rows.append(row)
                if row.get("run_id") not in run_ids:
                    findings.append({"severity": "error", "code": "metric_unknown_run", "message": f"metrics.csv:{i}: unknown run_id {row.get('run_id')}"})
                if claim_ids and row.get("claim_id") not in claim_ids:
                    findings.append({"severity": "error", "code": "metric_unknown_claim", "message": f"metrics.csv:{i}: unknown claim_id {row.get('claim_id')}"})
                claim = claim_by_id.get(row.get("claim_id")) or {}
                expected_metric = claim.get("metric")
                actual_metric = row.get("metric")
                if expected_metric and (actual_metric or "").strip().casefold() != expected_metric.strip().casefold():
                    findings.append({"severity": "error", "code": "metric_name_mismatch", "message": f"metrics.csv:{i}: metric {actual_metric!r} does not match claim {row.get('claim_id')} metric {expected_metric!r}"})
                run = run_by_id.get(row.get("run_id"))
                if run and row.get("claim_id") not in (run.get("claim_ids") or []):
                    findings.append({"severity": "error", "code": "metric_run_claim_mismatch", "message": f"metrics.csv:{i}: claim {row.get('claim_id')} is not linked to run {row.get('run_id')}"})

    metric_pairs = {(r.get("run_id"), r.get("claim_id")) for r in metric_rows}
    assessment_path = ws / "reproduction_assessment.json"
    if assessment_path.exists():
        assessment = load_json(assessment_path)
        seen = set()
        for a in assessment.get("assessments") or []:
            cid = a.get("claim_id"); state = a.get("state"); support = a.get("supporting_run_ids") or []
            if cid: seen.add(cid)
            if cid not in claim_ids and claim_ids:
                findings.append({"severity": "error", "code": "assessment_unknown_claim", "message": f"assessment references unknown claim {cid}"})
                continue
            if state not in ALLOWED_STATES:
                findings.append({"severity": "error", "code": "assessment_bad_state", "message": f"{cid}: invalid state {state}"})
            supporting_runs = []
            for rid in support:
                if rid not in run_ids:
                    findings.append({"severity": "error", "code": "assessment_unknown_run", "message": f"{cid}: unknown supporting run {rid}"})
                else:
                    supporting_runs.append(run_by_id[rid])

            claim = claim_by_id.get(cid) or {}
            rule = claim.get("comparison_rule") or {}
            reported = claim.get("reported") or {}
            successful_target = [r for r in supporting_runs if r.get("run_kind") == "target" and r.get("exit_code") == 0 and not r.get("timed_out")]
            if state in {"exact_reproduction", "within_reported_variation", "numerically_different"}:
                if not successful_target:
                    findings.append({"severity": "error", "code": "assessment_without_successful_target", "message": f"{cid}: {state} requires at least one successful target run"})
                if not any((rid, cid) in metric_pairs for rid in support):
                    findings.append({"severity": "error", "code": "assessment_without_metric", "message": f"{cid}: {state} has no metrics.csv row linked to a supporting run"})
            if state == "exact_reproduction":
                if rule.get("kind") not in {"exact", "deterministic_equality"}:
                    findings.append({"severity": "error", "code": "exact_without_exact_rule", "message": f"{cid}: exact_reproduction requires exact/deterministic_equality comparison rule"})
                for r in successful_target:
                    if r.get("git_dirty"):
                        findings.append({"severity": "error", "code": "exact_from_dirty_run", "message": f"{cid}: exact_reproduction cannot be supported by dirty run {r.get('run_id')}"})
                    if repo_commit and r.get("source_commit") != repo_commit:
                        findings.append({"severity": "error", "code": "exact_commit_mismatch", "message": f"{cid}: exact_reproduction supporting run {r.get('run_id')} does not match repository commit"})
                if a.get("material_deviations"):
                    findings.append({"severity": "error", "code": "exact_with_material_deviation", "message": f"{cid}: exact_reproduction has material deviations"})
            elif state == "within_reported_variation":
                kind = rule.get("kind")
                params = rule.get("parameters") or {}
                variation = reported.get("variation") if isinstance(reported, dict) else None
                valid_basis = (kind == "reported_variation" and bool(variation)) or (kind in {"absolute_tolerance", "relative_tolerance"} and params.get("tolerance") is not None)
                if not valid_basis:
                    findings.append({"severity": "error", "code": "variation_without_basis", "message": f"{cid}: within_reported_variation lacks a declared variation/tolerance basis"})
            if state == "qualitatively_consistent" and not support:
                findings.append({"severity": "warning", "code": "qualitative_without_run", "message": f"{cid}: qualitatively_consistent has no supporting run"})
        if profile == "release" and mode != "REPO_AUDIT":
            for cid in claim_ids - seen:
                findings.append({"severity": "error", "code": "missing_assessment", "message": f"release claim {cid} has no assessment"})

    if mode == "PAPER_ONLY":
        underspecified = read_jsonl(ws / "underspecifications.jsonl")
        decisions = read_jsonl(ws / "implementation_decisions.jsonl")
        decision_claims = {cid for d in decisions for cid in (d.get("claim_ids") or [])}
        for u in underspecified:
            if u.get("status") in {"assumption_required", "resolved_by_assumption"}:
                for cid in u.get("claim_ids") or []:
                    if cid not in decision_claims:
                        findings.append({"severity": "error", "code": "assumption_without_decision", "message": f"{u.get('item_id')}: claim {cid} requires an implementation decision but none is linked"})

    if profile == "release":
        resolved = ws / "environment/resolved/system.json"
        if mode != "REPO_AUDIT" and not resolved.exists():
            findings.append({"severity": "error", "code": "missing_environment_capture", "message": "release profile requires environment/resolved/system.json after execution work"})

    errors = [f for f in findings if f["severity"] == "error"]
    warnings = [f for f in findings if f["severity"] == "warning"]
    report = {
        "schema_version": "1.1",
        "generated_at": utc_now(),
        "workspace": str(ws),
        "mode": mode,
        "profile": profile,
        "status": "pass" if not errors else "fail",
        "error_count": len(errors),
        "warning_count": len(warnings),
        "current_provenance_hashes": current_hashes,
        "findings": findings,
    }
    out = args.output.resolve() if args.output else ws / "preflight.json"
    write_json(out, report)
    print(f"{report['status']}: {len(errors)} error(s), {len(warnings)} warning(s) -> {out}")
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
