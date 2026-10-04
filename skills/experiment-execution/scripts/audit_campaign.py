#!/usr/bin/env python3
"""Audit observed attempts against a preflighted campaign contract."""
from __future__ import annotations

import argparse
import json
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from preflight_campaign import check_scope_manifest, sha256, validate_campaign

STATUSES = {"completed", "failed", "interrupted", "oom", "cancelled"}


def _strict_equal(actual: Any, expected: Any) -> bool:
    """Compare JSON values without Python's bool/int equivalence (True == 1)."""
    if type(actual) is not type(expected):
        return False
    if isinstance(expected, dict):
        return set(actual) == set(expected) and all(
            _strict_equal(actual[key], value) for key, value in expected.items()
        )
    if isinstance(expected, list):
        return len(actual) == len(expected) and all(
            _strict_equal(left, right) for left, right in zip(actual, expected)
        )
    return actual == expected


def _counts_match(actual: Any, expected: dict[str, int]) -> bool:
    """Require exact integer counts; bool must not pass as int (e.g. True == 1)."""
    return (
        isinstance(actual, dict)
        and set(actual) == set(expected)
        and all(
            isinstance(actual[key], int)
            and not isinstance(actual[key], bool)
            and actual[key] == count
            for key, count in expected.items()
        )
    )


def _validate_observed_scope_manifests(
    root: Path, row: dict[str, Any], contract: dict[str, Any], label: str, errors: list[str]
) -> None:
    observed = row.get("observed_scope_manifests")
    expected_counts = contract["expected_counts"]
    official_populations = contract["official_scope_populations"]
    if not isinstance(observed, dict) or set(observed) != set(expected_counts):
        errors.append(f"{label}: observed_scope_manifests must contain exactly every official scope")
        return
    for scope_id, expected_population in official_populations.items():
        item = observed.get(scope_id)
        if not isinstance(item, dict):
            errors.append(f"{label}.observed_scope_manifests.{scope_id} must contain path and sha256")
            continue
        path_value, declared_hash = item.get("path"), item.get("sha256")
        if isinstance(path_value, str) and isinstance(row.get("run_id"), str) and isinstance(row.get("attempt_id"), str):
            results_root = (root / "results").resolve()
            attempt_root = (results_root / row["run_id"] / row["attempt_id"]).resolve()
            observed_path = (root / path_value).resolve()
            try:
                attempt_root.relative_to(results_root)
                observed_path.relative_to(attempt_root)
            except ValueError:
                errors.append(
                    f"{label}.observed_scope_manifests.{scope_id}: manifest must be stored under "
                    f"results/{row['run_id']}/{row['attempt_id']}/"
                )
                continue
        manifest_row = {
            "executed_manifest_path": path_value,
            "executed_manifest_sha256": declared_hash,
        }
        _, population = check_scope_manifest(
            root, manifest_row, "executed_manifest_path", scope_id, expected_counts[scope_id],
            f"{label}.observed_scope_manifests.{scope_id}", errors,
        )
        if population is not None and population != expected_population:
            errors.append(f"{label}.observed_scope_manifests.{scope_id}: actual run population differs from the complete official scope")


def _artifact(root: Path, value: Any, declared_hash: Any, label: str, errors: list[str], required: bool = True) -> bool:
    if value is None and not required:
        if declared_hash is not None:
            errors.append(f"{label}: hash must be null when no artifact path is recorded")
        return True
    if not isinstance(value, str) or not value.strip():
        errors.append(f"{label}: artifact path is required")
        return False
    path = Path(value)
    if path.is_absolute():
        errors.append(f"{label}: use a path relative to the campaign directory")
        return False
    resolved = (root / path).resolve()
    try:
        resolved.relative_to(root.resolve())
    except ValueError:
        errors.append(f"{label}: path escapes the campaign directory")
        return False
    if not resolved.is_file():
        errors.append(f"{label}: file does not exist: {value}")
        return False
    actual = sha256(resolved)
    if not isinstance(declared_hash, str) or declared_hash.lower() != actual:
        errors.append(f"{label}: declared SHA-256 does not match file ({actual})")
        return False
    return True


def _register_attempt_artifact_path(
    root: Path, raw_path: Any, run_id: str, attempt_id: str, role: str,
    owners: dict[Path, tuple[str, str]], label: str, errors: list[str],
) -> None:
    if not isinstance(raw_path, str) or not raw_path.strip() or Path(raw_path).is_absolute():
        return
    resolved = (root / raw_path).resolve()
    try:
        resolved.relative_to(root.resolve())
    except ValueError:
        return
    owner = (f"{run_id}/{attempt_id}", role)
    previous = owners.get(resolved)
    if previous is not None:
        errors.append(
            f"{label}: artifact path is reused ({raw_path}); already assigned to "
            f"{previous[0]} as {previous[1]}"
        )
    else:
        owners[resolved] = owner


def _validate_metrics(
    root: Path, row: dict[str, Any], campaign: dict[str, Any], expected_counts: dict[str, int],
    artifact_paths: dict[Path, tuple[str, str]], label: str, errors: list[str],
) -> None:
    path_value = row.get("metrics_path")
    if not isinstance(path_value, str):
        return
    candidate = Path(path_value)
    if candidate.is_absolute():
        return
    path = (root / candidate).resolve()
    try:
        path.relative_to(root.resolve())
    except ValueError:
        return
    if not path.is_file():
        return
    try:
        metrics = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        errors.append(f"{label}.metrics: normalized metrics record is invalid JSON ({exc})")
        return
    except OSError as exc:
        errors.append(f"{label}.metrics: cannot read normalized metrics record ({exc})")
        return
    if not isinstance(metrics, dict):
        errors.append(f"{label}.metrics: normalized metrics record must be a JSON object")
        return
    for key in ["run_id", "attempt_id", "condition_id", "seed", "replicate_id"]:
        if not _strict_equal(metrics.get(key), row.get(key)):
            errors.append(f"{label}.metrics: {key} does not match the attempt record")
    if metrics.get("schema_version") != "1.1":
        errors.append(f"{label}.metrics: schema_version must be '1.1'")
    benchmark = metrics.get("benchmark")
    expected_benchmark = campaign.get("benchmark", {})
    if not isinstance(benchmark, dict) or benchmark.get("name") != expected_benchmark.get("name") or benchmark.get("version") != expected_benchmark.get("version") or benchmark.get("suite_id") != expected_benchmark.get("suite_id"):
        errors.append(f"{label}.metrics: benchmark name/version/suite_id do not match the campaign")
    if not _counts_match(metrics.get("scope_counts"), expected_counts):
        errors.append(f"{label}.metrics: scope_counts do not equal the full official scope counts")
    if not isinstance(metrics.get("metrics"), dict) or not metrics["metrics"]:
        errors.append(f"{label}.metrics: at least one named metric is required")
    elif any(not isinstance(value, (int, float)) or isinstance(value, bool) or not math.isfinite(value) for value in metrics["metrics"].values()):
        errors.append(f"{label}.metrics: metric values must be finite numbers")
    metadata = metrics.get("metric_metadata")
    if not isinstance(metadata, dict) or set(metadata) != set(metrics.get("metrics", {})):
        errors.append(f"{label}.metrics: metric_metadata must describe every named metric exactly once")
    elif any(not isinstance(spec, dict) or any(not isinstance(spec.get(key), str) or not spec[key].strip() for key in ["unit", "aggregation_level"]) for spec in metadata.values()):
        errors.append(f"{label}.metrics: each metric requires a unit and aggregation_level")
    raw_path, raw_hash = metrics.get("raw_evaluator_output_path"), metrics.get("raw_evaluator_output_sha256")
    run_id, attempt_id = row.get("run_id"), row.get("attempt_id")
    if isinstance(run_id, str) and isinstance(attempt_id, str):
        _register_attempt_artifact_path(
            root, raw_path, run_id, attempt_id, "raw evaluator output", artifact_paths,
            f"{label}.raw_evaluator_output", errors,
        )
        if isinstance(raw_path, str):
            results_root = (root / "results").resolve()
            attempt_root = (results_root / run_id / attempt_id).resolve()
            source_path = (root / raw_path).resolve()
            try:
                attempt_root.relative_to(results_root)
                source_path.relative_to(attempt_root)
            except ValueError:
                errors.append(
                    f"{label}.raw_evaluator_output must be stored under results/{run_id}/{attempt_id}/"
                )
    _artifact(root, raw_path, raw_hash, f"{label}.raw_evaluator_output", errors)


def _validate_environment_snapshot(
    root: Path, row: dict[str, Any], artifact_paths: dict[Path, tuple[str, str]], label: str, errors: list[str]
) -> None:
    environment = row.get("environment")
    if not isinstance(environment, dict):
        errors.append(f"{label}.environment must contain a hash-bound snapshot")
        return
    path_value, declared_hash = environment.get("manifest_path"), environment.get("manifest_sha256")
    if not _artifact(root, path_value, declared_hash, f"{label}.environment_snapshot", errors):
        return
    if not isinstance(path_value, str):
        return
    results_root = (root / "results").resolve()
    attempt_root = (results_root / str(row.get("run_id")) / str(row.get("attempt_id"))).resolve()
    snapshot_path = (root / path_value).resolve()
    try:
        attempt_root.relative_to(results_root)
        snapshot_path.relative_to(attempt_root)
    except ValueError:
        errors.append(f"{label}.environment_snapshot must be stored under results/{row.get('run_id')}/{row.get('attempt_id')}/")
        return
    try:
        snapshot = json.loads(snapshot_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        errors.append(f"{label}.environment_snapshot must be valid JSON ({exc})")
        return
    if not isinstance(snapshot, dict):
        errors.append(f"{label}.environment_snapshot must be a JSON object")
        return
    if snapshot.get("schema_version") != "1.1":
        errors.append(f"{label}.environment_snapshot.schema_version must be '1.1'")
    for key in ["run_id", "attempt_id"]:
        if snapshot.get(key) != row.get(key):
            errors.append(f"{label}.environment_snapshot.{key} does not match the attempt")
    platform = snapshot.get("platform")
    if not isinstance(platform, dict) or any(not isinstance(platform.get(key), str) or not platform[key].strip() for key in ["operating_system", "architecture"]):
        errors.append(f"{label}.environment_snapshot.platform requires operating_system and architecture")
    hardware = snapshot.get("hardware")
    hardware_valid = (
        isinstance(hardware, dict)
        and isinstance(hardware.get("cpu_model"), str) and bool(hardware["cpu_model"].strip())
        and isinstance(hardware.get("logical_cpu_count"), int) and not isinstance(hardware.get("logical_cpu_count"), bool) and hardware["logical_cpu_count"] > 0
        and isinstance(hardware.get("system_memory_bytes"), int) and not isinstance(hardware.get("system_memory_bytes"), bool) and hardware["system_memory_bytes"] > 0
        and isinstance(hardware.get("accelerators"), list)
        and set(hardware) == {"cpu_model", "logical_cpu_count", "system_memory_bytes", "accelerators"}
    )
    if hardware_valid:
        for index, accelerator in enumerate(hardware["accelerators"]):
            if (
                not isinstance(accelerator, dict)
                or not isinstance(accelerator.get("kind"), str) or not accelerator["kind"].strip()
                or not isinstance(accelerator.get("model"), str) or not accelerator["model"].strip()
                or not isinstance(accelerator.get("device_count"), int) or isinstance(accelerator.get("device_count"), bool) or accelerator["device_count"] < 1
                or (accelerator.get("memory_bytes_per_device") is not None and (
                    not isinstance(accelerator.get("memory_bytes_per_device"), int)
                    or isinstance(accelerator.get("memory_bytes_per_device"), bool)
                    or accelerator["memory_bytes_per_device"] < 1
                ))
                or set(accelerator) != {"kind", "model", "device_count", "memory_bytes_per_device"}
            ):
                errors.append(f"{label}.environment_snapshot.hardware.accelerators[{index}] is invalid")
    else:
        errors.append(f"{label}.environment_snapshot.hardware requires CPU model/count, system memory bytes, and an accelerator list")
    if hardware_valid and not _strict_equal(row.get("hardware"), hardware):
        errors.append(f"{label}.hardware does not match the hash-bound environment snapshot")
    hardware_evidence = snapshot.get("hardware_evidence")
    if not isinstance(hardware_evidence, list) or not hardware_evidence:
        errors.append(f"{label}.environment_snapshot.hardware_evidence must contain hash-bound probe output(s)")
    else:
        for index, evidence in enumerate(hardware_evidence):
            evidence_label = f"{label}.environment_snapshot.hardware_evidence[{index}]"
            if not isinstance(evidence, dict):
                errors.append(f"{evidence_label} must contain command, path, and sha256")
                continue
            command, evidence_path, evidence_hash = evidence.get("command"), evidence.get("path"), evidence.get("sha256")
            if not isinstance(command, list) or not command or any(not isinstance(arg, str) or not arg for arg in command):
                errors.append(f"{evidence_label}.command must be a non-empty argv list")
            if set(evidence) != {"command", "path", "sha256"}:
                errors.append(f"{evidence_label} contains missing or unknown fields")
            if isinstance(evidence_path, str):
                evidence_file = (root / evidence_path).resolve()
                try:
                    evidence_file.relative_to(attempt_root)
                except ValueError:
                    errors.append(f"{evidence_label}.path must be stored under results/{row.get('run_id')}/{row.get('attempt_id')}/")
                if isinstance(row.get("run_id"), str) and isinstance(row.get("attempt_id"), str):
                    _register_attempt_artifact_path(
                        root, evidence_path, row["run_id"], row["attempt_id"], "hardware probe output",
                        artifact_paths, evidence_label, errors,
                    )
            _artifact(root, evidence_path, evidence_hash, evidence_label, errors)
    software = snapshot.get("software_versions")
    if not isinstance(software, dict) or not software or any(not isinstance(key, str) or not key.strip() or not isinstance(value, str) or not value.strip() for key, value in software.items()):
        errors.append(f"{label}.environment_snapshot.software_versions must map software names to exact versions")
    lock = snapshot.get("dependency_lock")
    if lock is not None:
        if not isinstance(lock, dict):
            errors.append(f"{label}.environment_snapshot.dependency_lock must be null or contain path and sha256")
        else:
            _artifact(root, lock.get("path"), lock.get("sha256"), f"{label}.environment_dependency_lock", errors)


def _validate_checkpoint_metadata(row: dict[str, Any], campaign: dict[str, Any], condition: dict[str, Any], label: str, errors: list[str]) -> None:
    path = row.get("checkpoint_path")
    metadata = row.get("checkpoint_metadata")
    if path is None:
        if metadata is not None:
            errors.append(f"{label}: checkpoint_metadata must be null when no checkpoint path is recorded")
        return
    if not isinstance(metadata, dict):
        errors.append(f"{label}: checkpoint_metadata is required when a checkpoint is recorded")
        return
    expected = {
        "run_id": row.get("run_id"),
        "source_commit": campaign.get("source_commit"),
        "config_sha256": row.get("config_sha256"),
        "seed": row.get("seed"),
        "replicate_id": row.get("replicate_id"),
        "selection_rule": condition.get("checkpoint_selection_rule"),
    }
    for key, value in expected.items():
        if not _strict_equal(metadata.get(key), value):
            errors.append(f"{label}.checkpoint_metadata.{key} does not match the frozen run/condition")
    step = metadata.get("training_step_or_epoch")
    invalid_numeric_step = isinstance(step, (int, float)) and (not math.isfinite(step) or step < 0)
    if not isinstance(step, (str, int, float)) or isinstance(step, bool) or (isinstance(step, str) and not step.strip()) or invalid_numeric_step:
        errors.append(f"{label}.checkpoint_metadata.training_step_or_epoch is required")


def audit_ledger(campaign_path: Path, ledger_path: Path) -> tuple[dict[str, Any], list[str]]:
    contract, errors, root = validate_campaign(campaign_path)
    if errors:
        return {"status": "fail", "error_count": len(errors), "findings": errors}, errors
    ledger_resolved = ledger_path.resolve()
    try:
        ledger_resolved.relative_to(root.resolve())
    except ValueError:
        errors.append("ledger path must stay inside the campaign directory")
        return {"status": "fail", "error_count": len(errors), "findings": errors}, errors
    if not ledger_resolved.is_file():
        errors.append(f"ledger does not exist: {ledger_path}")
        return {"status": "fail", "error_count": len(errors), "findings": errors}, errors

    attempts: list[dict[str, Any]] = []
    for lineno, line in enumerate(ledger_resolved.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError as exc:
            errors.append(f"ledger line {lineno}: invalid JSON: {exc}")
            continue
        if not isinstance(row, dict):
            errors.append(f"ledger line {lineno}: record must be a JSON object")
            continue
        attempts.append(row)

    campaign = contract["campaign"]
    expected_runs = contract["run_by_id"]
    conditions = contract["condition_by_id"]
    official_scope_hashes = contract["official_scope_hashes"]
    executed_scope_hashes = contract["executed_scope_hashes"]
    expected_counts = contract["expected_counts"]
    attempt_ids: set[str] = set()
    attempts_by_run: dict[str, list[dict[str, Any]]] = {}
    attempt_artifact_paths: dict[Path, tuple[str, str]] = {}

    for i, row in enumerate(attempts, start=1):
        label = f"ledger attempt {i}"
        if row.get("schema_version") != "1.0":
            errors.append(f"{label}: schema_version must be '1.0'; migrate the attempt record before audit")
        aid, rid = row.get("attempt_id"), row.get("run_id")
        if not isinstance(aid, str) or not aid.strip():
            errors.append(f"{label}: attempt_id is required")
        elif aid in attempt_ids:
            errors.append(f"duplicate attempt_id: {aid}")
        else:
            attempt_ids.add(aid)
        planned = expected_runs.get(rid) if isinstance(rid, str) else None
        if not isinstance(rid, str):
            errors.append(f"{label}: run_id must be a string")
        if planned is None:
            errors.append(f"{label}: run_id {rid!r} is not in the campaign")
            continue
        attempts_by_run.setdefault(rid, []).append(row)
        if isinstance(aid, str) and aid.strip():
            for key in ["log_path", "metrics_path", "checkpoint_path"]:
                _register_attempt_artifact_path(
                    root, row.get(key), rid, aid, key, attempt_artifact_paths,
                    f"ledger attempt {i}.{key}", errors,
                )
            environment = row.get("environment")
            if isinstance(environment, dict):
                _register_attempt_artifact_path(
                    root, environment.get("manifest_path"), rid, aid, "environment snapshot",
                    attempt_artifact_paths, f"ledger attempt {i}.environment_snapshot", errors,
                )
            observed_paths = row.get("observed_scope_manifests")
            if isinstance(observed_paths, dict):
                for scope_id, artifact in observed_paths.items():
                    if isinstance(artifact, dict):
                        _register_attempt_artifact_path(
                            root, artifact.get("path"), rid, aid, f"scope manifest {scope_id}",
                            attempt_artifact_paths, f"ledger attempt {i}.observed_scope_manifests.{scope_id}", errors,
                        )
        condition_id = planned.get("condition_id")
        condition = conditions.get(condition_id) or {}
        for key in ["condition_id", "seed", "replicate_id", "config_path", "config_sha256"]:
            expected = planned.get(key)
            if key in {"config_path", "config_sha256"}:
                expected = condition.get(key)
            if not _strict_equal(row.get(key), expected):
                errors.append(f"{label}: {key} {row.get(key)!r} does not match planned value {expected!r}")
        if row.get("source_commit") != campaign.get("source_commit"):
            errors.append(f"{label}: source_commit does not match the frozen campaign commit")
        if not _strict_equal(row.get("source_state"), campaign.get("source_state")):
            errors.append(f"{label}: source_state does not match the frozen campaign state/patch")
        if not isinstance(row.get("status"), str) or row.get("status") not in STATUSES:
            errors.append(f"{label}: invalid status {row.get('status')!r}")
            continue
        if not isinstance(row.get("command"), list) or not row.get("command") or any(not isinstance(arg, str) or not arg for arg in row.get("command", [])):
            errors.append(f"{label}: exact command argv must be a non-empty list of strings")
        for key in ["started_at", "finished_at"]:
            if not isinstance(row.get(key), str) or not row[key].strip():
                errors.append(f"{label}: {key} is required")
        parsed_times: dict[str, datetime] = {}
        for key in ["started_at", "finished_at"]:
            value = row.get(key)
            if isinstance(value, str) and value.strip():
                try:
                    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
                    if parsed.utcoffset() is None:
                        errors.append(f"{label}: {key} must include a timezone")
                    else:
                        parsed_times[key] = parsed
                except ValueError:
                    errors.append(f"{label}: {key} must be an ISO-8601 timestamp")
        if len(parsed_times) == 2 and parsed_times["finished_at"] < parsed_times["started_at"]:
            errors.append(f"{label}: finished_at precedes started_at")
        runtime = row.get("runtime_seconds")
        if not isinstance(runtime, (int, float)) or isinstance(runtime, bool) or not math.isfinite(runtime) or runtime < 0:
            errors.append(f"{label}: runtime_seconds must be a finite non-negative number")
        elif len(parsed_times) == 2 and parsed_times["finished_at"] >= parsed_times["started_at"]:
            elapsed_seconds = (parsed_times["finished_at"] - parsed_times["started_at"]).total_seconds()
            tolerance_seconds = max(5.0, elapsed_seconds * 0.02)
            if abs(runtime - elapsed_seconds) > tolerance_seconds:
                errors.append(
                    f"{label}: runtime_seconds differs from the started_at/finished_at interval "
                    f"by more than {tolerance_seconds:g} seconds"
                )
        for key in ["hardware", "environment"]:
            if not isinstance(row.get(key), dict) or not row[key]:
                errors.append(f"{label}: non-empty {key} metadata is required")
        if not _strict_equal(row.get("official_scope_manifest_sha256"), official_scope_hashes):
            errors.append(f"{label}: official scope manifest hashes do not match the frozen campaign")
        if not _strict_equal(row.get("executed_scope_manifest_sha256"), executed_scope_hashes):
            errors.append(f"{label}: executed scope manifest hashes do not match the loader manifest")

        status = row["status"]
        if "exit_code" not in row or (row.get("exit_code") is not None and (not isinstance(row.get("exit_code"), int) or isinstance(row.get("exit_code"), bool))):
            errors.append(f"{label}: exit_code must be an integer or null")
        if status == "completed":
            if row.get("exit_code") != 0:
                errors.append(f"{label}: completed status requires exit_code 0")
            counts = row.get("observed_scope_counts")
            if not _counts_match(counts, expected_counts):
                errors.append(f"{label}: observed scope counts do not equal every full official scope count")
            _validate_observed_scope_manifests(root, row, contract, label, errors)
            if row.get("failure_reason") is not None:
                errors.append(f"{label}: completed attempts must have failure_reason=null")
            _validate_environment_snapshot(root, row, attempt_artifact_paths, label, errors)
            _artifact(root, row.get("log_path"), row.get("log_sha256"), f"{label}.log", errors)
            _artifact(root, row.get("metrics_path"), row.get("metrics_sha256"), f"{label}.metrics", errors)
            _validate_metrics(root, row, campaign, expected_counts, attempt_artifact_paths, label, errors)
            checkpoint_policy = condition.get("checkpoint_policy")
            checkpoint_required = checkpoint_policy == "required"
            if checkpoint_policy == "none" and row.get("checkpoint_path") is not None:
                errors.append(f"{label}: checkpoint is forbidden by the condition policy")
            _artifact(root, row.get("checkpoint_path"), row.get("checkpoint_sha256"), f"{label}.checkpoint", errors, required=checkpoint_required)
            _validate_checkpoint_metadata(row, campaign, condition, label, errors)
        else:
            if not isinstance(row.get("failure_reason"), str) or not row["failure_reason"].strip():
                errors.append(f"{label}: failed/interrupted attempts require failure_reason")
            _artifact(root, row.get("log_path"), row.get("log_sha256"), f"{label}.log", errors)
            _artifact(root, row.get("metrics_path"), row.get("metrics_sha256"), f"{label}.partial_metrics", errors, required=False)
            _artifact(root, row.get("checkpoint_path"), row.get("checkpoint_sha256"), f"{label}.partial_checkpoint", errors, required=False)
            environment = row.get("environment")
            if isinstance(environment, dict) and (environment.get("manifest_path") is not None or environment.get("manifest_sha256") is not None):
                _artifact(root, environment.get("manifest_path"), environment.get("manifest_sha256"), f"{label}.partial_environment_snapshot", errors)
            _validate_checkpoint_metadata(row, campaign, condition, label, errors)
            if row.get("checkpoint_path") is None and row.get("checkpoint_metadata") is not None:
                errors.append(f"{label}: checkpoint_metadata must be null when no partial checkpoint is recorded")

    missing = sorted(set(expected_runs) - set(attempts_by_run))
    for rid in missing:
        errors.append(f"planned run {rid} has no ledger attempt")
    for rid, rows in attempts_by_run.items():
        previous_finished: datetime | None = None
        successful_attempt_seen = False
        for index, retry in enumerate(rows):
            if successful_attempt_seen:
                errors.append(f"run {rid}: no attempt may follow a completed attempt; start a new campaign if a rerun is needed")
            if index > 0:
                if not isinstance(retry.get("retry_reason"), str) or not retry["retry_reason"].strip():
                    errors.append(f"run {rid}: every retry after the first attempt requires retry_reason")
            started_at, finished_at = retry.get("started_at"), retry.get("finished_at")
            parsed_start = parsed_finish = None
            try:
                if isinstance(started_at, str):
                    parsed_start = datetime.fromisoformat(started_at.replace("Z", "+00:00"))
                if isinstance(finished_at, str):
                    parsed_finish = datetime.fromisoformat(finished_at.replace("Z", "+00:00"))
            except ValueError:
                pass  # The per-attempt timestamp validation above reports malformed values.
            if parsed_start is not None and parsed_start.utcoffset() is not None and previous_finished is not None and parsed_start < previous_finished:
                errors.append(f"run {rid}: retry started before the prior attempt finished")
            if parsed_finish is not None and parsed_finish.utcoffset() is not None:
                previous_finished = parsed_finish
            if retry.get("status") == "completed":
                successful_attempt_seen = True
        completed = [row for row in rows if row.get("status") == "completed"]
        if not completed:
            errors.append(f"planned run {rid} has no successful full-scope attempt")
        elif len(completed) > 1:
            errors.append(f"planned run {rid} has multiple completed attempts; resolve under the preregistered retry rule")

    report = {
        "schema_version": "1.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "campaign_id": campaign.get("campaign_id"),
        "status": "pass" if not errors else "fail",
        "planned_run_count": len(expected_runs),
        "attempt_count": len(attempts),
        "completed_attempt_count": sum(row.get("status") == "completed" for row in attempts),
        "error_count": len(errors),
        "findings": errors,
    }
    return report, errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit run attempts, benchmark coverage, hashes, and artifacts against a campaign.")
    parser.add_argument("campaign", type=Path)
    parser.add_argument("--ledger", type=Path, required=True)
    parser.add_argument("--output", type=Path, help="Optional report path; by default use a timestamped file beside the campaign.")
    args = parser.parse_args()
    campaign_root = args.campaign.resolve().parent
    report, errors = audit_ledger(args.campaign, args.ledger)
    out = args.output or campaign_root / f"campaign-audit-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}.json"
    out = out.resolve()
    try:
        out.relative_to(campaign_root.resolve())
    except ValueError:
        print("FAIL: audit report path must stay inside the campaign directory")
        return 2
    if out.exists():
        print(f"FAIL: refusing to overwrite existing audit report: {out}")
        return 2
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(f"{report['status'].upper()}: {report['error_count']} issue(s); {report.get('completed_attempt_count', 0)}/{report.get('planned_run_count', 0)} planned runs complete; report={out}")
    for error in errors:
        print(f"- {error}")
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
