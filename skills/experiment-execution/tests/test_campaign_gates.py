from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
import shutil
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

from audit_campaign import _counts_match


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_source_snapshot(ws: Path, base_commit: str) -> Path:
    file_path = "src/changed.py"
    content = b"print('snapshot')\n"
    manifest = {
        "schema_version": "1.0", "base_commit": base_commit,
        "files": [{"path": file_path, "sha256": hashlib.sha256(content).hexdigest()}],
    }
    archive_path = ws / "source.snapshot.zip"
    with zipfile.ZipFile(archive_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        archive.writestr(file_path, content)
        archive.writestr("source-manifest.json", json.dumps(manifest))
    return archive_path


def run_script(name: str, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run([sys.executable, str(SCRIPTS / name), *args], text=True, capture_output=True, check=False)


def prepare_campaign(root: Path, stage: str = "pilot", seeds: list[int] | None = None) -> Path:
    ws = root / "campaign"
    ws.mkdir(parents=True)
    (ws / "manifests").mkdir()
    (ws / "configs").mkdir()
    (ws / "results").mkdir()
    (ws / "protocol.md").write_text("Predeclared test protocol.\n", encoding="utf-8")
    (ws / "configs" / "baseline.json").write_text('{"batch_size": 8}\n', encoding="utf-8")
    scopes = []
    for scope_id, count in [("train", 100), ("test", 25)]:
        content = json.dumps({"scope_id": scope_id, "unit_ids": [f"{scope_id}_{i}" for i in range(count)]}, sort_keys=True) + "\n"
        official = ws / "manifests" / f"{scope_id}.official.json"
        executed = ws / "manifests" / f"{scope_id}.executed.json"
        official.write_text(content, encoding="utf-8")
        executed.write_text(content, encoding="utf-8")
        scopes.append({
            "scope_id": scope_id,
            "role": scope_id,
            "official_source": {"url": "https://example.invalid/bench/tasks", "revision": "b" * 40, "locator": "tasks.py:1-100"},
            "official_manifest_path": official.relative_to(ws).as_posix(),
            "official_manifest_sha256": digest(official),
            "executed_manifest_path": executed.relative_to(ws).as_posix(),
            "executed_manifest_sha256": digest(executed),
            "expected_unit_count": count,
        })
    seed_list = seeds if seeds is not None else [13]
    campaign = {
        "schema_version": "1.1",
        "campaign_id": "campaign_test",
        "experiment_id": "exp_test",
        "stage": stage,
        "protocol_path": "protocol.md",
        "protocol_sha256": digest(ws / "protocol.md"),
        "source_commit": "a" * 40,
        "source_state": {"dirty": False, "patch_path": None, "patch_sha256": None,
                         "source_snapshot_path": None, "source_snapshot_sha256": None},
        "research_question": "Does the method improve the benchmark metric?",
        "decision_rule": "Continue only if the predeclared margin is met.",
        "benchmark": {
            "name": "OfficialBench", "version": "1.0", "canonical_url": "https://example.invalid/bench",
            "official_code_url": "https://example.invalid/code", "official_code_revision": "b" * 40,
            "official_code_artifact_path": None, "official_code_artifact_sha256": None,
            "suite_id": "full", "scope_policy": "full_official_benchmark", "expected_unit_name": "unit",
            "required_scopes": ["train", "test"], "scope_manifests": scopes,
            "loader_entrypoint": "official.load", "evaluator_entrypoint": "official.evaluate", "metric_entrypoint": "official.metric",
        },
        "data_policy": {"source": "official_benchmark", "full_official_scope": True, "subset": False,
                        "generated_scientific_data": False, "custom_task_data": False, "official_loader": True, "official_evaluator": True},
        "seed_policy": {"seeds": seed_list, "replicate_ids": [], "rationale": "Predeclared pilot/confirmation seed policy.",
                        "confirmatory_basis": "Prior variance and precision target." if stage == "confirmatory" else None},
        "conditions": [{"condition_id": "baseline", "description": "baseline", "randomness_mode": "seeded_stochastic", "config_path": "configs/baseline.json",
                        "config_sha256": digest(ws / "configs" / "baseline.json"), "checkpoint_policy": "none", "checkpoint_selection_rule": None}],
        "runs": [{"run_id": f"baseline_seed{seed}", "condition_id": "baseline", "seed": seed, "replicate_id": None,
                  "config_path": "configs/baseline.json", "config_sha256": digest(ws / "configs" / "baseline.json")} for seed in seed_list],
        "resource_plan": {"accelerator": "CPU test", "memory_gb": 1, "storage_gb": 1, "expected_runtime_hours": 1, "estimate_basis": "test fixture"},
    }
    path = ws / "campaign.json"
    path.write_text(json.dumps(campaign, indent=2) + "\n", encoding="utf-8")
    return path


def make_attempt(ws: Path, campaign: dict, status: str = "completed", observed_test_count: int = 25, attempt_id: str = "baseline_seed13_attempt01") -> dict:
    run = campaign["runs"][0]
    log = ws / "results" / f"{attempt_id}.log"
    log.write_text("attempt output\n", encoding="utf-8")
    observed_manifests = {}
    for scope in campaign["benchmark"]["scope_manifests"]:
        source = ws / scope["executed_manifest_path"]
        target = ws / "results" / run["run_id"] / attempt_id / "scope-manifests" / f"{scope['scope_id']}.json"
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)
        observed_manifests[scope["scope_id"]] = {
            "path": target.relative_to(ws).as_posix(), "sha256": digest(target),
        }
    environment_path = ws / "results" / run["run_id"] / attempt_id / "environment.json"
    environment_path.parent.mkdir(parents=True, exist_ok=True)
    hardware = {
        "cpu_model": "test CPU", "logical_cpu_count": 1,
        "system_memory_bytes": 1024, "accelerators": [],
    }
    hardware_probe = ws / "results" / run["run_id"] / attempt_id / "hardware" / "probe-output.json"
    hardware_probe.parent.mkdir(parents=True, exist_ok=True)
    hardware_probe.write_text(json.dumps(hardware) + "\n", encoding="utf-8")
    environment_path.write_text(json.dumps({
        "schema_version": "1.1", "run_id": run["run_id"], "attempt_id": attempt_id,
        "platform": {"operating_system": "test", "architecture": "test"},
        "hardware": hardware,
        "hardware_evidence": [{
            "command": ["hardware-probe", "--json"],
            "path": hardware_probe.relative_to(ws).as_posix(),
            "sha256": digest(hardware_probe),
        }],
        "software_versions": {"python": "test"},
    }) + "\n", encoding="utf-8")
    row = {
        "schema_version": "1.0",
        "run_id": run["run_id"], "attempt_id": attempt_id, "condition_id": run["condition_id"], "seed": run["seed"],
        "replicate_id": run["replicate_id"],
        "status": status, "source_commit": campaign["source_commit"], "source_state": campaign["source_state"], "command": ["python", "evaluate.py"],
        "config_path": run["config_path"], "config_sha256": run["config_sha256"],
        "official_scope_manifest_sha256": {s["scope_id"]: s["official_manifest_sha256"] for s in campaign["benchmark"]["scope_manifests"]},
        "executed_scope_manifest_sha256": {s["scope_id"]: s["executed_manifest_sha256"] for s in campaign["benchmark"]["scope_manifests"]},
        "observed_scope_manifests": observed_manifests,
        "observed_scope_counts": {"train": 100, "test": observed_test_count},
        "started_at": "2026-01-01T00:00:00Z", "finished_at": "2026-01-01T00:01:00Z", "runtime_seconds": 60,
        "hardware": hardware, "environment": {
            "manifest_path": environment_path.relative_to(ws).as_posix(), "manifest_sha256": digest(environment_path),
        },
        "log_path": log.relative_to(ws).as_posix(), "log_sha256": digest(log),
        "metrics_path": None, "metrics_sha256": None, "checkpoint_path": None, "checkpoint_sha256": None, "checkpoint_metadata": None,
        "failure_reason": "test failure" if status != "completed" else None, "retry_reason": None,
        "exit_code": 0 if status == "completed" else 1,
    }
    if status == "completed":
        metrics = ws / "results" / f"{attempt_id}.metrics.json"
        raw_output = ws / "results" / run["run_id"] / attempt_id / "raw-evaluator-output.json"
        raw_output.parent.mkdir(parents=True, exist_ok=True)
        raw_output.write_text(json.dumps({"accuracy": 0.5, "evaluated_examples": observed_test_count}) + "\n", encoding="utf-8")
        metrics.write_text(json.dumps({
            "schema_version": "1.1", "run_id": run["run_id"], "attempt_id": attempt_id,
            "condition_id": run["condition_id"], "seed": run["seed"], "replicate_id": run["replicate_id"],
            "benchmark": {"name": campaign["benchmark"]["name"], "version": campaign["benchmark"]["version"], "suite_id": campaign["benchmark"]["suite_id"]},
            "scope_counts": {"train": 100, "test": observed_test_count}, "metrics": {"accuracy": 0.5},
            "metric_metadata": {"accuracy": {"unit": "fraction", "aggregation_level": "mean_over_official_test_examples"}},
            "raw_evaluator_output_path": raw_output.relative_to(ws).as_posix(),
            "raw_evaluator_output_sha256": digest(raw_output),
        }) + "\n", encoding="utf-8")
        row["metrics_path"] = metrics.relative_to(ws).as_posix()
        row["metrics_sha256"] = digest(metrics)
        if campaign["conditions"][0]["checkpoint_policy"] == "required":
            checkpoint = ws / "results" / f"{attempt_id}.ckpt"
            checkpoint.write_bytes(b"test checkpoint")
            row["checkpoint_path"] = checkpoint.relative_to(ws).as_posix()
            row["checkpoint_sha256"] = digest(checkpoint)
            row["checkpoint_metadata"] = {
                "run_id": run["run_id"], "source_commit": campaign["source_commit"],
                "config_sha256": run["config_sha256"], "seed": run["seed"],
                "replicate_id": run["replicate_id"], "training_step_or_epoch": 20,
                "selection_rule": campaign["conditions"][0]["checkpoint_selection_rule"],
            }
    return row


class CampaignGateTests(unittest.TestCase):
    def test_scope_counts_require_exact_non_boolean_integers(self):
        self.assertTrue(_counts_match({"test": 1}, {"test": 1}))
        self.assertFalse(_counts_match({"test": True}, {"test": 1}))
        self.assertFalse(_counts_match({"test": 1.0}, {"test": 1}))
        self.assertFalse(_counts_match({"test": 1, "extra": 0}, {"test": 1}))

    def test_full_scope_single_seed_pilot_passes(self):
        with tempfile.TemporaryDirectory() as td:
            campaign = prepare_campaign(Path(td))
            cp = run_script("preflight_campaign.py", str(campaign))
            self.assertEqual(cp.returncode, 0, cp.stdout + cp.stderr)

    def test_malformed_ids_fail_closed_without_traceback(self):
        with tempfile.TemporaryDirectory() as td:
            campaign_path = prepare_campaign(Path(td))
            campaign = json.loads(campaign_path.read_text(encoding="utf-8"))
            campaign["runs"][0]["condition_id"] = []
            campaign_path.write_text(json.dumps(campaign), encoding="utf-8")
            cp = run_script("preflight_campaign.py", str(campaign_path))
            self.assertNotEqual(cp.returncode, 0)
            self.assertNotIn("Traceback", cp.stdout + cp.stderr)
        with tempfile.TemporaryDirectory() as td:
            campaign_path = prepare_campaign(Path(td))
            campaign = json.loads(campaign_path.read_text(encoding="utf-8"))
            ledger = campaign_path.parent / "run_ledger.jsonl"
            ledger.write_text(json.dumps({"run_id": ["bad"], "attempt_id": "attempt01"}) + "\n", encoding="utf-8")
            cp = run_script("audit_campaign.py", str(campaign_path), "--ledger", str(ledger), "--output", str(campaign_path.parent / "audit.json"))
            self.assertNotEqual(cp.returncode, 0)
            self.assertNotIn("Traceback", cp.stdout + cp.stderr)

    def test_confirmatory_campaign_requires_and_accepts_preregistered_multiple_seeds(self):
        with tempfile.TemporaryDirectory() as td:
            campaign = prepare_campaign(Path(td), stage="confirmatory", seeds=[13, 29])
            cp = run_script("preflight_campaign.py", str(campaign))
            self.assertEqual(cp.returncode, 0, cp.stdout + cp.stderr)

    def test_uncontrolled_and_deterministic_randomness_modes_are_representable(self):
        with tempfile.TemporaryDirectory() as td:
            campaign_path = prepare_campaign(Path(td))
            campaign = json.loads(campaign_path.read_text(encoding="utf-8"))
            campaign["seed_policy"].update({"seeds": [], "replicate_ids": ["rep01"]})
            campaign["conditions"][0]["randomness_mode"] = "uncontrolled_stochastic"
            campaign["runs"][0].update({"seed": None, "replicate_id": "rep01", "run_id": "baseline_rep01"})
            campaign_path.write_text(json.dumps(campaign), encoding="utf-8")
            cp = run_script("preflight_campaign.py", str(campaign_path))
            self.assertEqual(cp.returncode, 0, cp.stdout + cp.stderr)
        with tempfile.TemporaryDirectory() as td:
            campaign_path = prepare_campaign(Path(td), stage="confirmatory")
            campaign = json.loads(campaign_path.read_text(encoding="utf-8"))
            campaign["seed_policy"].update({"seeds": [], "replicate_ids": ["rep01", "rep02"],
                                             "confirmatory_basis": "Two preregistered API replicates for a precision estimate."})
            campaign["conditions"][0]["randomness_mode"] = "uncontrolled_stochastic"
            planned = campaign["runs"][0]
            campaign["runs"] = [{**planned, "run_id": f"baseline_{rid}", "seed": None, "replicate_id": rid}
                                for rid in campaign["seed_policy"]["replicate_ids"]]
            campaign_path.write_text(json.dumps(campaign), encoding="utf-8")
            cp = run_script("preflight_campaign.py", str(campaign_path))
            self.assertEqual(cp.returncode, 0, cp.stdout + cp.stderr)
        with tempfile.TemporaryDirectory() as td:
            campaign_path = prepare_campaign(Path(td))
            campaign = json.loads(campaign_path.read_text(encoding="utf-8"))
            campaign["seed_policy"].update({"seeds": [], "replicate_ids": []})
            campaign["conditions"][0]["randomness_mode"] = "deterministic"
            campaign["runs"][0].update({"seed": None, "replicate_id": None, "run_id": "baseline_deterministic"})
            campaign_path.write_text(json.dumps(campaign), encoding="utf-8")
            cp = run_script("preflight_campaign.py", str(campaign_path))
            self.assertEqual(cp.returncode, 0, cp.stdout + cp.stderr)

    def test_manifest_count_mismatch_and_duplicate_ids_are_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            campaign_path = prepare_campaign(Path(td))
            campaign = json.loads(campaign_path.read_text(encoding="utf-8"))
            campaign["benchmark"]["scope_manifests"][0]["expected_unit_count"] = 99
            campaign_path.write_text(json.dumps(campaign), encoding="utf-8")
            cp = run_script("preflight_campaign.py", str(campaign_path))
            self.assertNotEqual(cp.returncode, 0)
            self.assertIn("does not match", cp.stdout)
        with tempfile.TemporaryDirectory() as td:
            campaign_path = prepare_campaign(Path(td))
            campaign = json.loads(campaign_path.read_text(encoding="utf-8"))
            manifest_path = campaign_path.parent / campaign["benchmark"]["scope_manifests"][0]["official_manifest_path"]
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            manifest["unit_ids"][1] = manifest["unit_ids"][0]
            manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
            row = campaign["benchmark"]["scope_manifests"][0]
            row["official_manifest_sha256"] = digest(manifest_path)
            executed_path = campaign_path.parent / row["executed_manifest_path"]
            executed_path.write_text(json.dumps(manifest), encoding="utf-8")
            row["executed_manifest_sha256"] = digest(executed_path)
            campaign_path.write_text(json.dumps(campaign), encoding="utf-8")
            cp = run_script("preflight_campaign.py", str(campaign_path))
            self.assertNotEqual(cp.returncode, 0)
            self.assertIn("duplicate unit_ids", cp.stdout)

    def test_dirty_source_requires_a_hash_bound_patch_and_complete_snapshot(self):
        with tempfile.TemporaryDirectory() as td:
            campaign_path = prepare_campaign(Path(td))
            campaign = json.loads(campaign_path.read_text(encoding="utf-8"))
            patch = campaign_path.parent / "source.patch"
            patch.write_text("diff --git a/code.py b/code.py\n", encoding="utf-8")
            snapshot = write_source_snapshot(campaign_path.parent, campaign["source_commit"])
            campaign["source_state"] = {
                "dirty": True, "patch_path": "source.patch", "patch_sha256": digest(patch),
                "source_snapshot_path": snapshot.name, "source_snapshot_sha256": digest(snapshot),
            }
            campaign_path.write_text(json.dumps(campaign), encoding="utf-8")
            cp = run_script("preflight_campaign.py", str(campaign_path))
            self.assertEqual(cp.returncode, 0, cp.stdout + cp.stderr)
            campaign["source_state"]["patch_sha256"] = "0" * 64
            campaign_path.write_text(json.dumps(campaign), encoding="utf-8")
            cp = run_script("preflight_campaign.py", str(campaign_path))
            self.assertNotEqual(cp.returncode, 0)

    def test_moving_code_refs_need_a_hash_bound_source_archive(self):
        with tempfile.TemporaryDirectory() as td:
            campaign_path = prepare_campaign(Path(td))
            campaign = json.loads(campaign_path.read_text(encoding="utf-8"))
            benchmark = campaign["benchmark"]
            campaign["source_commit"] = "main"
            campaign_path.write_text(json.dumps(campaign), encoding="utf-8")
            cp = run_script("preflight_campaign.py", str(campaign_path))
            self.assertNotEqual(cp.returncode, 0)
            self.assertIn("full immutable", cp.stdout)
            campaign["source_commit"] = "a" * 40
            benchmark["official_code_revision"] = "main"
            campaign_path.write_text(json.dumps(campaign), encoding="utf-8")
            cp = run_script("preflight_campaign.py", str(campaign_path))
            self.assertNotEqual(cp.returncode, 0)
            self.assertIn("full commit SHA", cp.stdout)

            source_archive = campaign_path.parent / "official-source.tar.gz"
            source_archive.write_bytes(b"pinned official source archive")
            benchmark["official_code_revision"] = "release-1.0"
            benchmark["official_code_artifact_path"] = source_archive.name
            benchmark["official_code_artifact_sha256"] = digest(source_archive)
            campaign_path.write_text(json.dumps(campaign), encoding="utf-8")
            cp = run_script("preflight_campaign.py", str(campaign_path))
            self.assertEqual(cp.returncode, 0, cp.stdout + cp.stderr)

    def test_complete_attempt_for_full_official_scope_passes_audit(self):
        with tempfile.TemporaryDirectory() as td:
            campaign_path = prepare_campaign(Path(td))
            campaign = json.loads(campaign_path.read_text(encoding="utf-8"))
            row = make_attempt(campaign_path.parent, campaign)
            ledger = campaign_path.parent / "run_ledger.jsonl"
            ledger.write_text(json.dumps(row) + "\n", encoding="utf-8")
            cp = run_script("audit_campaign.py", str(campaign_path), "--ledger", str(ledger), "--output", str(campaign_path.parent / "audit.json"))
            self.assertEqual(cp.returncode, 0, cp.stdout + cp.stderr)

    def test_metrics_identity_and_required_checkpoint_metadata_are_audited(self):
        with tempfile.TemporaryDirectory() as td:
            campaign_path = prepare_campaign(Path(td))
            campaign = json.loads(campaign_path.read_text(encoding="utf-8"))
            campaign["conditions"][0].update({"checkpoint_policy": "required", "checkpoint_selection_rule": "best validation accuracy"})
            campaign_path.write_text(json.dumps(campaign), encoding="utf-8")
            row = make_attempt(campaign_path.parent, campaign)
            row["checkpoint_metadata"]["selection_rule"] = "best test accuracy"
            ledger = campaign_path.parent / "run_ledger.jsonl"
            ledger.write_text(json.dumps(row) + "\n", encoding="utf-8")
            cp = run_script("audit_campaign.py", str(campaign_path), "--ledger", str(ledger), "--output", str(campaign_path.parent / "audit.json"))
            self.assertNotEqual(cp.returncode, 0)
            self.assertIn("checkpoint_metadata.selection_rule", cp.stdout)

        with tempfile.TemporaryDirectory() as td:
            campaign_path = prepare_campaign(Path(td))
            campaign = json.loads(campaign_path.read_text(encoding="utf-8"))
            row = make_attempt(campaign_path.parent, campaign)
            metrics_path = campaign_path.parent / row["metrics_path"]
            metrics = json.loads(metrics_path.read_text(encoding="utf-8"))
            metrics["attempt_id"] = "wrong_attempt"
            metrics_path.write_text(json.dumps(metrics), encoding="utf-8")
            row["metrics_sha256"] = digest(metrics_path)
            ledger = campaign_path.parent / "run_ledger.jsonl"
            ledger.write_text(json.dumps(row) + "\n", encoding="utf-8")
            cp = run_script("audit_campaign.py", str(campaign_path), "--ledger", str(ledger), "--output", str(campaign_path.parent / "audit.json"))
            self.assertNotEqual(cp.returncode, 0)
            self.assertIn("attempt_id does not match", cp.stdout)

    def test_audit_rejects_naive_timestamps_boolean_counts_and_nonfinite_checkpoint_steps(self):
        with tempfile.TemporaryDirectory() as td:
            campaign_path = prepare_campaign(Path(td))
            campaign = json.loads(campaign_path.read_text(encoding="utf-8"))
            campaign["conditions"][0].update({"checkpoint_policy": "required", "checkpoint_selection_rule": "last step"})
            campaign_path.write_text(json.dumps(campaign), encoding="utf-8")
            row = make_attempt(campaign_path.parent, campaign)
            row["started_at"] = "2026-01-01T00:00:00"
            row["observed_scope_counts"]["test"] = True
            row["checkpoint_metadata"]["training_step_or_epoch"] = float("nan")
            ledger = campaign_path.parent / "run_ledger.jsonl"
            ledger.write_text(json.dumps(row) + "\n", encoding="utf-8")
            cp = run_script("audit_campaign.py", str(campaign_path), "--ledger", str(ledger), "--output", str(campaign_path.parent / "audit.json"))
            self.assertNotEqual(cp.returncode, 0)
            self.assertIn("started_at must include a timezone", cp.stdout)
            self.assertIn("observed scope counts", cp.stdout)
            self.assertIn("training_step_or_epoch", cp.stdout)

    def test_pilot_rejects_multiple_seeds_and_confirmatory_rejects_one(self):
        with tempfile.TemporaryDirectory() as td:
            pilot = prepare_campaign(Path(td) / "pilot", seeds=[1, 2])
            cp = run_script("preflight_campaign.py", str(pilot))
            self.assertNotEqual(cp.returncode, 0)
            self.assertIn("exactly one seed", cp.stdout)
        with tempfile.TemporaryDirectory() as td:
            confirmatory = prepare_campaign(Path(td) / "confirmatory", stage="confirmatory", seeds=[1])
            cp = run_script("preflight_campaign.py", str(confirmatory))
            self.assertNotEqual(cp.returncode, 0)
            self.assertIn("at least two", cp.stdout)

    def test_subset_and_changed_execution_manifest_are_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            campaign_path = prepare_campaign(Path(td))
            campaign = json.loads(campaign_path.read_text(encoding="utf-8"))
            campaign["data_policy"]["subset"] = True
            campaign_path.write_text(json.dumps(campaign), encoding="utf-8")
            cp = run_script("preflight_campaign.py", str(campaign_path))
            self.assertNotEqual(cp.returncode, 0)
            self.assertIn("data_policy.subset", cp.stdout)
        with tempfile.TemporaryDirectory() as td:
            campaign_path = prepare_campaign(Path(td))
            campaign = json.loads(campaign_path.read_text(encoding="utf-8"))
            executed = campaign_path.parent / campaign["benchmark"]["scope_manifests"][0]["executed_manifest_path"]
            executed.write_text('{"unit_ids":["one"]}\n', encoding="utf-8")
            cp = run_script("preflight_campaign.py", str(campaign_path))
            self.assertNotEqual(cp.returncode, 0)
            self.assertIn("does not match file", cp.stdout)

    def test_same_official_scope_with_reordered_manifest_ids_is_accepted(self):
        with tempfile.TemporaryDirectory() as td:
            campaign_path = prepare_campaign(Path(td))
            campaign = json.loads(campaign_path.read_text(encoding="utf-8"))
            row = campaign["benchmark"]["scope_manifests"][0]
            executed = campaign_path.parent / row["executed_manifest_path"]
            manifest = json.loads(executed.read_text(encoding="utf-8"))
            manifest["unit_ids"].reverse()
            executed.write_text(json.dumps(manifest), encoding="utf-8")
            row["executed_manifest_sha256"] = digest(executed)
            campaign_path.write_text(json.dumps(campaign), encoding="utf-8")
            cp = run_script("preflight_campaign.py", str(campaign_path))
            self.assertEqual(cp.returncode, 0, cp.stdout + cp.stderr)

    def test_large_scope_can_use_hash_bound_artifact_manifests(self):
        with tempfile.TemporaryDirectory() as td:
            campaign_path = prepare_campaign(Path(td))
            campaign = json.loads(campaign_path.read_text(encoding="utf-8"))
            row = campaign["benchmark"]["scope_manifests"][0]
            official_path = campaign_path.parent / row["official_manifest_path"]
            executed_path = campaign_path.parent / row["executed_manifest_path"]
            manifest = {"scope_id": row["scope_id"], "artifacts": [{"artifact_id": "train-shard-000", "sha256": "c" * 64, "unit_count": row["expected_unit_count"]}]}
            official_path.write_text(json.dumps(manifest), encoding="utf-8")
            executed_path.write_text(json.dumps(manifest), encoding="utf-8")
            row["official_manifest_sha256"] = digest(official_path)
            row["executed_manifest_sha256"] = digest(executed_path)
            campaign_path.write_text(json.dumps(campaign), encoding="utf-8")
            cp = run_script("preflight_campaign.py", str(campaign_path))
            self.assertEqual(cp.returncode, 0, cp.stdout + cp.stderr)

    def test_audit_rejects_partial_scope_count(self):
        with tempfile.TemporaryDirectory() as td:
            campaign_path = prepare_campaign(Path(td))
            campaign = json.loads(campaign_path.read_text(encoding="utf-8"))
            row = make_attempt(campaign_path.parent, campaign, observed_test_count=5)
            ledger = campaign_path.parent / "run_ledger.jsonl"
            ledger.write_text(json.dumps(row) + "\n", encoding="utf-8")
            cp = run_script("audit_campaign.py", str(campaign_path), "--ledger", str(ledger), "--output", str(campaign_path.parent / "audit.json"))
            self.assertNotEqual(cp.returncode, 0)
            self.assertIn("observed scope counts", cp.stdout)

    def test_failed_attempt_is_preserved_when_retry_completes(self):
        with tempfile.TemporaryDirectory() as td:
            campaign_path = prepare_campaign(Path(td))
            campaign = json.loads(campaign_path.read_text(encoding="utf-8"))
            failed = make_attempt(campaign_path.parent, campaign, status="oom", attempt_id="baseline_seed13_attempt01")
            completed = make_attempt(campaign_path.parent, campaign, status="completed", attempt_id="baseline_seed13_attempt02")
            completed["retry_reason"] = "Retry after preserving the original OOM attempt."
            completed["started_at"] = "2026-01-01T00:02:00Z"
            completed["finished_at"] = "2026-01-01T00:03:00Z"
            ledger = campaign_path.parent / "run_ledger.jsonl"
            ledger.write_text(json.dumps(failed) + "\n" + json.dumps(completed) + "\n", encoding="utf-8")
            cp = run_script("audit_campaign.py", str(campaign_path), "--ledger", str(ledger), "--output", str(campaign_path.parent / "audit.json"))
            self.assertEqual(cp.returncode, 0, cp.stdout + cp.stderr)
            report = json.loads((campaign_path.parent / "audit.json").read_text(encoding="utf-8"))
            self.assertEqual(report["attempt_count"], 2)
            self.assertEqual(report["completed_attempt_count"], 1)

    def test_audit_refuses_report_paths_outside_campaign(self):
        with tempfile.TemporaryDirectory() as td:
            campaign_path = prepare_campaign(Path(td))
            campaign = json.loads(campaign_path.read_text(encoding="utf-8"))
            row = make_attempt(campaign_path.parent, campaign)
            ledger = campaign_path.parent / "run_ledger.jsonl"
            ledger.write_text(json.dumps(row) + "\n", encoding="utf-8")
            outside = campaign_path.parent.parent / "audit-outside.json"
            cp = run_script("audit_campaign.py", str(campaign_path), "--ledger", str(ledger), "--output", str(outside))
            self.assertEqual(cp.returncode, 2)
            self.assertFalse(outside.exists())


if __name__ == "__main__":
    unittest.main()
