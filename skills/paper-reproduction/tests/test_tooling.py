from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"


def run_script(name: str, *args: str, cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPTS / name), *args],
        cwd=str(cwd) if cwd else None,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=False,
    )


class ToolingTests(unittest.TestCase):
    def test_init_workspace_has_no_fake_claim_rows(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            ws = Path(td) / "repro"
            cp = run_script("init_workspace.py", str(ws), "--mode", "REPO_REPRODUCE", "--profile", "standard")
            self.assertEqual(cp.returncode, 0, cp.stderr)
            contract = json.loads((ws / "reproduction_contract.json").read_text())
            assessment = json.loads((ws / "reproduction_assessment.json").read_text())
            self.assertEqual(contract["skill_version"], "1.2.0")
            self.assertEqual(contract["target_claims"], [])
            self.assertEqual(assessment["assessments"], [])
            self.assertEqual((ws / "claim_code_map.jsonl").read_text(), "")
            self.assertEqual((ws / "run_ledger.jsonl").read_text(), "")

    def test_repo_inspection_and_run_ledger(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            repo = root / "repo"
            repo.mkdir()
            subprocess.run(["git", "init", "-q"], cwd=repo, check=True)
            subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=repo, check=True)
            subprocess.run(["git", "config", "user.name", "test"], cwd=repo, check=True)
            (repo / "evaluate.py").write_text('print("ok")\n')
            (repo / "config.yaml").write_text("x: 1\n")
            subprocess.run(["git", "add", "."], cwd=repo, check=True)
            subprocess.run(["git", "commit", "-qm", "init"], cwd=repo, check=True)

            manifest = root / "repo.json"
            cp = run_script("inspect_repo.py", "--repo", str(repo), "--output", str(manifest))
            self.assertEqual(cp.returncode, 0, cp.stderr)
            obj = json.loads(manifest.read_text())
            self.assertTrue(obj["source_revision"]["commit"])
            self.assertFalse(obj["git"]["dirty"])

            ledger = root / "ledger.jsonl"
            logs = root / "logs"
            cp = run_script(
                "run_with_ledger.py",
                "--ledger", str(ledger),
                "--run-id", "smoke_1",
                "--claim-id", "claim_1",
                "--run-kind", "smoke",
                "--cwd", str(repo),
                "--config", "config.yaml",
                "--logs-dir", str(logs),
                "--", sys.executable, "evaluate.py",
            )
            self.assertEqual(cp.returncode, 0, cp.stderr)
            row = json.loads(ledger.read_text().strip())
            self.assertEqual(row["run_id"], "smoke_1")
            self.assertEqual(row["exit_code"], 0)
            self.assertFalse(row["git_dirty"])
            self.assertTrue(row["config"]["sha256"])

    def test_dirty_repo_requires_explicit_override(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            repo = root / "repo"
            repo.mkdir()
            subprocess.run(["git", "init", "-q"], cwd=repo, check=True)
            subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=repo, check=True)
            subprocess.run(["git", "config", "user.name", "test"], cwd=repo, check=True)
            (repo / "run.py").write_text('print("clean")\n')
            subprocess.run(["git", "add", "."], cwd=repo, check=True)
            subprocess.run(["git", "commit", "-qm", "init"], cwd=repo, check=True)
            (repo / "run.py").write_text('print("dirty")\n')

            ledger = root / "ledger.jsonl"
            logs = root / "logs"
            cp = run_script(
                "run_with_ledger.py",
                "--ledger", str(ledger),
                "--run-id", "dirty_1",
                "--claim-id", "claim_1",
                "--run-kind", "diagnostic",
                "--cwd", str(repo),
                "--logs-dir", str(logs),
                "--", sys.executable, "run.py",
            )
            self.assertNotEqual(cp.returncode, 0)
            self.assertIn("dirty Git worktree", cp.stderr)

            cp = run_script(
                "run_with_ledger.py",
                "--ledger", str(ledger),
                "--run-id", "dirty_2",
                "--claim-id", "claim_1",
                "--run-kind", "diagnostic",
                "--cwd", str(repo),
                "--logs-dir", str(logs),
                "--allow-dirty",
                "--", sys.executable, "run.py",
            )
            self.assertEqual(cp.returncode, 0, cp.stderr)
            row = json.loads(ledger.read_text().strip())
            self.assertTrue(row["git_dirty"])
            self.assertTrue(row["patch_sha256"])


if __name__ == "__main__":
    unittest.main()
