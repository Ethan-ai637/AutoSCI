#!/usr/bin/env python3
"""Validate a preregistered experiment campaign before any scientific run."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import sys
import zipfile
from pathlib import PurePosixPath
from pathlib import Path
from typing import Any


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def is_full_sha(value: Any) -> bool:
    return isinstance(value, str) and re.fullmatch(r"(?:[a-fA-F0-9]{40}|[a-fA-F0-9]{64})", value) is not None


def inside(root: Path, raw: Any, label: str, errors: list[str]) -> Path | None:
    if not isinstance(raw, str) or not raw.strip():
        errors.append(f"{label}: path is required")
        return None
    candidate = Path(raw)
    if candidate.is_absolute():
        errors.append(f"{label}: use a path relative to the campaign directory")
        return None
    resolved = (root / candidate).resolve()
    try:
        resolved.relative_to(root.resolve())
    except ValueError:
        errors.append(f"{label}: path escapes the campaign directory")
        return None
    if not resolved.is_file():
        errors.append(f"{label}: file does not exist: {raw}")
        return None
    return resolved


def check_hashed_file(root: Path, raw_path: Any, declared_hash: Any, label: str, errors: list[str]) -> str | None:
    path = inside(root, raw_path, label, errors)
    if path is None:
        return None
    actual = sha256(path)
    if not isinstance(declared_hash, str) or declared_hash.lower() != actual:
        errors.append(f"{label}: declared SHA-256 does not match file ({actual})")
    return actual


def check_source_snapshot(root: Path, raw_path: Any, declared_hash: Any, base_commit: str, errors: list[str]) -> None:
    archive_path = inside(root, raw_path, "source_state.source_snapshot", errors)
    if archive_path is None:
        return
    actual_hash = sha256(archive_path)
    if not isinstance(declared_hash, str) or declared_hash.lower() != actual_hash:
        errors.append(f"source_state.source_snapshot: declared SHA-256 does not match archive ({actual_hash})")
    try:
        with zipfile.ZipFile(archive_path) as archive:
            infos = archive.infolist()
            names = [info.filename for info in infos if not info.is_dir()]
            if len(names) != len(set(names)):
                errors.append("source_state.source_snapshot: archive contains duplicate file paths")
                return
            if "source-manifest.json" not in names:
                errors.append("source_state.source_snapshot: archive must contain source-manifest.json")
                return
            raw_manifest = archive.read("source-manifest.json")
            manifest = json.loads(raw_manifest.decode("utf-8"))
            if not isinstance(manifest, dict) or manifest.get("schema_version") != "1.0":
                errors.append("source_state.source_snapshot: source-manifest.json must be schema version 1.0")
                return
            if manifest.get("base_commit") != base_commit:
                errors.append("source_state.source_snapshot: manifest base_commit does not match source_commit")
                return
            files = manifest.get("files")
            if not isinstance(files, list) or not files:
                errors.append("source_state.source_snapshot: manifest must list every snapshotted source file")
                return
            declared_files: dict[str, str] = {}
            for index, item in enumerate(files):
                if not isinstance(item, dict):
                    errors.append(f"source_state.source_snapshot.files[{index}] must be an object")
                    continue
                file_path, file_hash = item.get("path"), item.get("sha256")
                relative = PurePosixPath(file_path) if isinstance(file_path, str) else None
                if (relative is None or not file_path or "\\" in file_path or relative.is_absolute()
                        or relative.as_posix() != file_path
                        or any(part in {"", ".", ".."} for part in relative.parts)
                        or not isinstance(file_hash, str) or re.fullmatch(r"[a-fA-F0-9]{64}", file_hash) is None):
                    errors.append(f"source_state.source_snapshot.files[{index}] requires a safe relative path and SHA-256")
                    continue
                if file_path in declared_files:
                    errors.append(f"source_state.source_snapshot: duplicate manifest path {file_path!r}")
                    continue
                declared_files[file_path] = file_hash.lower()
            archive_files = set(names) - {"source-manifest.json"}
            if set(declared_files) != archive_files:
                errors.append("source_state.source_snapshot: archive file set does not exactly match source-manifest.json")
            for file_path, file_hash in declared_files.items():
                if file_path in archive_files:
                    with archive.open(file_path) as handle:
                        digest = hashlib.sha256()
                        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                            digest.update(chunk)
                    if digest.hexdigest() != file_hash:
                        errors.append(f"source_state.source_snapshot: content hash mismatch for {file_path}")
    except (OSError, RuntimeError, KeyError, zipfile.BadZipFile, UnicodeDecodeError, json.JSONDecodeError) as exc:
        errors.append(f"source_state.source_snapshot: invalid ZIP archive or manifest ({exc})")


def check_scope_manifest(root: Path, row: dict[str, Any], path_key: str, scope_id: str, expected_count: Any,
                         label: str, errors: list[str]) -> tuple[str | None, dict[str, int] | None]:
    hash_key = path_key.removesuffix("_path") + "_sha256"
    actual = check_hashed_file(root, row.get(path_key), row.get(hash_key), label, errors)
    raw_path = row.get(path_key)
    if actual is None or not isinstance(raw_path, str):
        return actual, None
    manifest_path = (root / raw_path).resolve()
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        errors.append(f"{label}: scope manifest must be valid JSON ({exc})")
        return actual, None
    if not isinstance(manifest, dict) or manifest.get("scope_id") != scope_id:
        errors.append(f"{label}: manifest scope_id must match {scope_id!r}")
        return actual, None
    unit_ids = manifest.get("unit_ids")
    artifacts = manifest.get("artifacts")
    population: dict[str, int] | None = None
    if isinstance(unit_ids, list) and unit_ids and all(isinstance(unit, str) and unit.strip() for unit in unit_ids):
        population = {unit: 1 for unit in unit_ids}
        if len(population) != len(unit_ids):
            errors.append(f"{label}: manifest contains duplicate unit_ids")
    elif isinstance(artifacts, list) and artifacts and all(isinstance(item, dict) for item in artifacts):
        population = {}
        artifact_ids: set[str] = set()
        for index, artifact in enumerate(artifacts):
            artifact_id, artifact_hash, unit_count = artifact.get("artifact_id"), artifact.get("sha256"), artifact.get("unit_count")
            if not isinstance(artifact_id, str) or not artifact_id.strip() or not isinstance(artifact_hash, str) or len(artifact_hash) != 64 or not isinstance(unit_count, int) or isinstance(unit_count, bool) or unit_count < 1:
                errors.append(f"{label}.artifacts[{index}] requires artifact_id, SHA-256, and positive unit_count")
                continue
            try:
                int(artifact_hash, 16)
            except ValueError:
                errors.append(f"{label}.artifacts[{index}].sha256 must be hexadecimal")
                continue
            if artifact_id in artifact_ids:
                errors.append(f"{label}: duplicate artifact_id {artifact_id!r}")
            artifact_ids.add(artifact_id)
            population[f"{artifact_id}@{artifact_hash.lower()}"] = unit_count
        if len(artifact_ids) != len(artifacts):
            errors.append(f"{label}: artifact_id values must be unique and all artifact rows valid")
    else:
        errors.append(f"{label}: normalized manifest must contain unique unit_ids or immutable artifact rows")
        return actual, None
    observed_count = sum(population.values())
    if isinstance(expected_count, int) and not isinstance(expected_count, bool) and observed_count != expected_count:
        errors.append(f"{label}: expected_unit_count {expected_count} does not match manifest population count {observed_count}")
    source = row.get("official_source")
    if path_key.startswith("official_") and (not isinstance(source, dict) or any(not isinstance(source.get(key), str) or not source[key].strip() for key in ["url", "revision", "locator"])):
        errors.append(f"{label}: official_source must include a reviewable url, revision, and locator")
    return actual, population


def validate_campaign(campaign_path: Path) -> tuple[dict[str, Any], list[str], Path]:
    errors: list[str] = []
    path = campaign_path.resolve()
    root = path.parent
    try:
        campaign = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return {}, [f"cannot read campaign JSON: {exc}"], root
    if not isinstance(campaign, dict):
        return {}, ["campaign root must be a JSON object"], root
    if campaign.get("schema_version") != "1.2":
        errors.append("schema_version must be '1.2'; migrate the campaign before preflight")

    for key in ["campaign_id", "experiment_id", "research_question", "decision_rule"]:
        if not isinstance(campaign.get(key), str) or not campaign[key].strip():
            errors.append(f"{key}: non-empty value is required")
    thresholds = campaign.get("decision_thresholds")
    if not isinstance(thresholds, list):
        errors.append("decision_thresholds must be a list; use [] when no numeric pass/fail/continue/stop threshold is planned")
        thresholds = []
    threshold_ids: set[str] = set()
    threshold_basis_types = {
        "official_benchmark_protocol", "domain_standard", "peer_reviewed_source",
        "statistical_design", "local_empirical_evidence", "resource_constraint",
        "repository_policy", "mathematical_derivation",
    }
    threshold_operators = {"<", "<=", ">", ">=", "=="}
    for index, threshold in enumerate(thresholds):
        label = f"decision_thresholds[{index}]"
        if not isinstance(threshold, dict):
            errors.append(f"{label} must be an object")
            continue
        allowed_threshold_keys = {
            "threshold_id", "decision", "operator", "value", "unit", "basis_type",
            "basis_reference", "source_locator", "applicability", "derivation",
        }
        extra_threshold_keys = set(threshold) - allowed_threshold_keys
        if extra_threshold_keys:
            errors.append(f"{label} contains unsupported field(s): {sorted(extra_threshold_keys)}")
        threshold_id = threshold.get("threshold_id")
        if not isinstance(threshold_id, str) or not threshold_id.strip():
            errors.append(f"{label}.threshold_id must be a non-empty string")
        elif threshold_id in threshold_ids:
            errors.append(f"duplicate decision threshold id: {threshold_id}")
        else:
            threshold_ids.add(threshold_id)
        for key in ["decision", "unit", "basis_reference", "source_locator", "applicability", "derivation"]:
            if not isinstance(threshold.get(key), str) or not threshold[key].strip():
                errors.append(f"{label}.{key} must explain the threshold and its evidence basis")
        operator = threshold.get("operator")
        if not isinstance(operator, str) or operator not in threshold_operators:
            errors.append(f"{label}.operator must be one of {sorted(threshold_operators)}")
        value = threshold.get("value")
        if not isinstance(value, (int, float)) or isinstance(value, bool) or not math.isfinite(value):
            errors.append(f"{label}.value must be a finite number")
        basis_type = threshold.get("basis_type")
        if not isinstance(basis_type, str) or basis_type not in threshold_basis_types:
            errors.append(f"{label}.basis_type must identify a recognized evidence or policy source")
    if not is_full_sha(campaign.get("source_commit")):
        errors.append("source_commit must be a full immutable 40- or 64-character commit SHA")
    resource_plan = campaign.get("resource_plan")
    if not isinstance(resource_plan, dict):
        errors.append("resource_plan must declare hardware and resource estimates before launch")
    else:
        for key in ["accelerator", "estimate_basis"]:
            if not isinstance(resource_plan.get(key), str) or not resource_plan[key].strip():
                errors.append(f"resource_plan.{key} must be a non-empty string")
        for key in ["memory_gb", "storage_gb", "expected_runtime_hours"]:
            value = resource_plan.get(key)
            if not isinstance(value, (int, float)) or isinstance(value, bool) or not math.isfinite(value) or value <= 0:
                errors.append(f"resource_plan.{key} must be a finite positive number")
    if not isinstance(campaign.get("stage"), str) or campaign.get("stage") not in {"pilot", "confirmatory"}:
        errors.append("stage must be 'pilot' or 'confirmatory'")
    source_state = campaign.get("source_state")
    if (not isinstance(source_state, dict) or not isinstance(source_state.get("dirty"), bool)
            or any(key not in source_state for key in ["patch_path", "patch_sha256", "source_snapshot_path", "source_snapshot_sha256"])):
        errors.append("source_state must record whether the source tree was dirty")
    elif source_state["dirty"]:
        check_hashed_file(root, source_state.get("patch_path"), source_state.get("patch_sha256"), "source_state.patch", errors)
        check_source_snapshot(root, source_state.get("source_snapshot_path"), source_state.get("source_snapshot_sha256"), campaign.get("source_commit"), errors)
    elif any(source_state.get(key) is not None for key in ["patch_path", "patch_sha256", "source_snapshot_path", "source_snapshot_sha256"]):
        errors.append("clean source_state must use null patch and source snapshot fields")

    protocol_hash = check_hashed_file(root, campaign.get("protocol_path"), campaign.get("protocol_sha256"), "protocol", errors)
    _ = protocol_hash

    benchmark = campaign.get("benchmark")
    if not isinstance(benchmark, dict):
        benchmark = {}
        errors.append("benchmark: object is required")
    for key in ["name", "version", "canonical_url", "official_code_url", "official_code_revision", "suite_id", "loader_entrypoint", "evaluator_entrypoint", "metric_entrypoint"]:
        if not isinstance(benchmark.get(key), str) or not benchmark[key].strip():
            errors.append(f"benchmark.{key}: non-empty value is required")
    revision = benchmark.get("official_code_revision")
    if not is_full_sha(revision):
        artifact_hash = benchmark.get("official_code_artifact_sha256")
        if not isinstance(artifact_hash, str) or re.fullmatch(r"[a-fA-F0-9]{64}", artifact_hash) is None:
            errors.append("benchmark.official_code_revision must be a full commit SHA or bind a versioned source archive by SHA-256")
        else:
            check_hashed_file(root, benchmark.get("official_code_artifact_path"), artifact_hash, "benchmark.official_code_artifact", errors)
    elif benchmark.get("official_code_artifact_path") is not None or benchmark.get("official_code_artifact_sha256") is not None:
        check_hashed_file(root, benchmark.get("official_code_artifact_path"), benchmark.get("official_code_artifact_sha256"), "benchmark.official_code_artifact", errors)
    if benchmark.get("scope_policy") != "full_official_benchmark":
        errors.append("benchmark.scope_policy must be 'full_official_benchmark'; benchmark subsets are not allowed")

    required_scopes = benchmark.get("required_scopes")
    scope_rows = benchmark.get("scope_manifests")
    if not isinstance(required_scopes, list) or not required_scopes or any(not isinstance(x, str) or not x for x in required_scopes):
        errors.append("benchmark.required_scopes must list every official scope used by the protocol")
        required_scopes = []
    elif len(required_scopes) != len(set(required_scopes)):
        errors.append("benchmark.required_scopes contains duplicate values")
    if not isinstance(scope_rows, list) or not scope_rows:
        errors.append("benchmark.scope_manifests must include official and executed manifests for every required scope")
        scope_rows = []
    scope_ids: list[str] = []
    official_scope_hashes: dict[str, str] = {}
    executed_scope_hashes: dict[str, str] = {}
    official_scope_populations: dict[str, dict[str, int]] = {}
    expected_counts: dict[str, int] = {}
    for i, row in enumerate(scope_rows):
        label = f"benchmark.scope_manifests[{i}]"
        if not isinstance(row, dict):
            errors.append(f"{label}: must be an object")
            continue
        scope_id = row.get("scope_id")
        if not isinstance(scope_id, str) or not scope_id.strip():
            errors.append(f"{label}.scope_id: non-empty value is required")
            continue
        scope_ids.append(scope_id)
        count = row.get("expected_unit_count")
        official_hash, official_ids = check_scope_manifest(root, row, "official_manifest_path", scope_id, count, f"{label}.official_manifest", errors)
        executed_hash, executed_ids = check_scope_manifest(root, row, "executed_manifest_path", scope_id, count, f"{label}.executed_manifest", errors)
        if official_ids is not None and executed_ids is not None and official_ids != executed_ids:
            errors.append(f"{label}: executed unit/artifact population differs from the complete official scope")
        if official_hash:
            official_scope_hashes[scope_id] = official_hash
        if official_ids is not None:
            official_scope_populations[scope_id] = official_ids
        if executed_hash:
            executed_scope_hashes[scope_id] = executed_hash
        if not isinstance(count, int) or isinstance(count, bool) or count < 1:
            errors.append(f"{label}.expected_unit_count must be a positive integer")
        else:
            expected_counts[scope_id] = count
    if len(scope_ids) != len(set(scope_ids)):
        errors.append("benchmark.scope_manifests contains duplicate scope_id values")
    if set(scope_ids) != set(required_scopes):
        errors.append("benchmark.scope_manifests must match required_scopes exactly")

    data_policy = campaign.get("data_policy")
    if not isinstance(data_policy, dict):
        data_policy = {}
        errors.append("data_policy: object is required")
    required_policy = {
        "source": "official_benchmark",
        "full_official_scope": True,
        "subset": False,
        "generated_scientific_data": False,
        "custom_task_data": False,
        "official_loader": True,
        "official_evaluator": True,
    }
    for key, expected in required_policy.items():
        if data_policy.get(key) != expected:
            errors.append(f"data_policy.{key} must be {expected!r}")

    seed_policy = campaign.get("seed_policy")
    if not isinstance(seed_policy, dict):
        seed_policy = {}
        errors.append("seed_policy: object is required")
    seeds = seed_policy.get("seeds")
    if not isinstance(seeds, list) or any(not isinstance(s, int) or isinstance(s, bool) for s in seeds):
        errors.append("seed_policy.seeds must be a list of distinct integer seeds (empty only when no condition uses controlled randomness)")
        seeds = []
    if len(seeds) != len(set(seeds)):
        errors.append("seed_policy.seeds contains duplicate values")
    replicate_ids = seed_policy.get("replicate_ids")
    if not isinstance(replicate_ids, list) or any(not isinstance(r, str) or not r.strip() for r in replicate_ids):
        errors.append("seed_policy.replicate_ids must be a list of non-empty replicate IDs")
        replicate_ids = []
    if len(replicate_ids) != len(set(replicate_ids)):
        errors.append("seed_policy.replicate_ids contains duplicates")
    if not isinstance(seed_policy.get("rationale"), str) or not seed_policy["rationale"].strip():
        errors.append("seed_policy.rationale is required")

    conditions = campaign.get("conditions")
    if not isinstance(conditions, list) or not conditions:
        errors.append("conditions must contain at least one preregistered condition")
        conditions = []
    condition_by_id: dict[str, dict[str, Any]] = {}
    for i, condition in enumerate(conditions):
        label = f"conditions[{i}]"
        if not isinstance(condition, dict):
            errors.append(f"{label}: must be an object")
            continue
        cid = condition.get("condition_id")
        if not isinstance(cid, str) or not cid.strip():
            errors.append(f"{label}.condition_id: non-empty value is required")
            continue
        if cid in condition_by_id:
            errors.append(f"duplicate condition_id: {cid}")
        condition_by_id[cid] = condition
        if not isinstance(condition.get("randomness_mode"), str) or condition.get("randomness_mode") not in {"seeded_stochastic", "uncontrolled_stochastic", "deterministic"}:
            errors.append(f"{label}.randomness_mode must be seeded_stochastic, uncontrolled_stochastic, or deterministic")
        if not isinstance(condition.get("checkpoint_policy"), str) or condition.get("checkpoint_policy") not in {"none", "optional", "required"}:
            errors.append(f"{label}.checkpoint_policy must be none, optional, or required")
        checkpoint_policy = condition.get("checkpoint_policy")
        if isinstance(checkpoint_policy, str) and checkpoint_policy in {"optional", "required"} and (not isinstance(condition.get("checkpoint_selection_rule"), str) or not condition["checkpoint_selection_rule"].strip()):
            errors.append(f"{label}.checkpoint_selection_rule is required when a checkpoint may be recorded")
        check_hashed_file(root, condition.get("config_path"), condition.get("config_sha256"), f"{label}.config", errors)
    modes = {c.get("randomness_mode") for c in condition_by_id.values() if isinstance(c.get("randomness_mode"), str)}
    if "seeded_stochastic" not in modes and seeds:
        errors.append("seed_policy.seeds must be empty when no condition uses controlled randomness")
    if "uncontrolled_stochastic" not in modes and replicate_ids:
        errors.append("seed_policy.replicate_ids must be empty when no condition uses uncontrolled randomness")

    runs = campaign.get("runs")
    if not isinstance(runs, list) or not runs:
        errors.append("runs must enumerate every condition × planned seed before launch")
        runs = []
    run_ids: set[str] = set()
    run_pairs: set[tuple[str, str, int | str | None]] = set()
    for i, run in enumerate(runs):
        label = f"runs[{i}]"
        if not isinstance(run, dict):
            errors.append(f"{label}: must be an object")
            continue
        rid, cid, seed, replicate_id = run.get("run_id"), run.get("condition_id"), run.get("seed"), run.get("replicate_id")
        if not isinstance(rid, str) or not rid.strip():
            errors.append(f"{label}.run_id: non-empty value is required")
        elif rid in run_ids:
            errors.append(f"duplicate run_id: {rid}")
        else:
            run_ids.add(rid)
        condition = condition_by_id.get(cid) if isinstance(cid, str) else None
        if not isinstance(cid, str):
            errors.append(f"{label}.condition_id must be a string")
        if condition is None:
            errors.append(f"{label}: condition_id {cid!r} is not declared")
        if condition:
            mode = condition.get("randomness_mode")
            if mode == "seeded_stochastic":
                if not isinstance(seed, int) or isinstance(seed, bool) or seed not in seeds or replicate_id is not None:
                    errors.append(f"{label}: seeded_stochastic runs require a declared integer seed and null replicate_id")
                else:
                    pair = (cid, mode, seed)
                    if pair in run_pairs:
                        errors.append(f"{label}: duplicate condition/seed run for {cid} / {seed}")
                    run_pairs.add(pair)
            elif mode == "uncontrolled_stochastic":
                if seed is not None or not isinstance(replicate_id, str) or replicate_id not in replicate_ids:
                    errors.append(f"{label}: uncontrolled_stochastic runs require null seed and a declared replicate_id")
                else:
                    pair = (cid, mode, replicate_id)
                    if pair in run_pairs:
                        errors.append(f"{label}: duplicate replicate run for {cid} / {replicate_id}")
                    run_pairs.add(pair)
            elif mode == "deterministic":
                if seed is not None or replicate_id is not None:
                    errors.append(f"{label}: deterministic runs require null seed and null replicate_id")
                else:
                    pair = (cid, mode, None)
                    if pair in run_pairs:
                        errors.append(f"{label}: deterministic condition {cid} may be run only once per campaign")
                    run_pairs.add(pair)
        if condition:
            for key in ["config_path", "config_sha256"]:
                if run.get(key) != condition.get(key):
                    errors.append(f"{label}.{key} does not match condition {cid!r}")
    expected_pairs: set[tuple[str, str, int | str | None]] = set()
    for cid, condition in condition_by_id.items():
        mode = condition.get("randomness_mode")
        if mode == "seeded_stochastic":
            if campaign.get("stage") == "pilot" and len(seeds) != 1:
                errors.append(f"pilot campaigns require exactly one seed for seeded condition {cid}")
            expected_pairs.update((cid, mode, seed) for seed in seeds)
        elif mode == "uncontrolled_stochastic":
            if campaign.get("stage") == "pilot" and len(replicate_ids) != 1:
                errors.append(f"pilot campaigns require exactly one replicate for uncontrolled condition {cid}")
            expected_pairs.update((cid, mode, replicate_id) for replicate_id in replicate_ids)
        elif mode == "deterministic":
            expected_pairs.add((cid, mode, None))
    if run_pairs != expected_pairs:
        errors.append("runs must enumerate exactly one run per declared seed/replicate and exactly one per deterministic condition")
    has_multiple_stochastic_runs = len(seeds) > 1 or len(replicate_ids) > 1
    if campaign.get("stage") == "confirmatory" and has_multiple_stochastic_runs:
        if not isinstance(seed_policy.get("additional_runs_basis"), str) or not seed_policy["additional_runs_basis"].strip():
            errors.append("campaigns with multiple seeds/replicates require a predeclared basis for adding repeats")

    return {
        "campaign": campaign,
        "root": root,
        "run_by_id": {r.get("run_id"): r for r in runs if isinstance(r, dict) and isinstance(r.get("run_id"), str)},
        "condition_by_id": condition_by_id,
        "official_scope_hashes": official_scope_hashes,
        "executed_scope_hashes": executed_scope_hashes,
        "official_scope_populations": official_scope_populations,
        "expected_counts": expected_counts,
    }, errors, root


def main() -> int:
    parser = argparse.ArgumentParser(description="Fail-closed preflight for a benchmark-complete experiment campaign.")
    parser.add_argument("campaign", type=Path)
    args = parser.parse_args()
    result, errors, _ = validate_campaign(args.campaign)
    if errors:
        print(f"FAIL: {len(errors)} campaign issue(s)")
        for error in errors:
            print(f"- {error}")
        return 1
    campaign = result["campaign"]
    print(f"PASS: {campaign['campaign_id']} ({campaign['stage']}); {len(campaign['runs'])} planned full-scope run(s); {len(result['official_scope_hashes'])} official scope(s) hash-bound")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
