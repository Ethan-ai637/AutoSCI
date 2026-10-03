#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
import subprocess
import time
from pathlib import Path

from _util import append_jsonl, git_dirty, git_patch_fingerprint, git_value, sha256_file, utc_now

SAFE_ENV_KEYS = {
    "PATH", "HOME", "USERPROFILE", "TMP", "TEMP", "TMPDIR", "SYSTEMROOT", "WINDIR",
    "COMSPEC", "PATHEXT", "LANG", "LC_ALL", "LC_CTYPE", "TZ", "CUDA_VISIBLE_DEVICES",
    "CUDA_HOME", "CUDA_PATH", "VIRTUAL_ENV", "CONDA_PREFIX", "CONDA_DEFAULT_ENV",
    "OMP_NUM_THREADS", "MKL_NUM_THREADS", "OPENBLAS_NUM_THREADS", "NUMEXPR_NUM_THREADS",
    "PYTHONHASHSEED", "TOKENIZERS_PARALLELISM", "CUBLAS_WORKSPACE_CONFIG",
}
SENSITIVE_ENV_PARTS = ("SECRET", "TOKEN", "PASSWORD", "PASSWD", "API_KEY", "APIKEY", "PRIVATE_KEY", "CREDENTIAL", "AUTH", "COOKIE", "SSH", "ACCESS_KEY")


def _execution_environment(requested_keys: list[str]) -> dict[str, str]:
    """Pass a small runtime allowlist plus explicitly requested non-secret variables."""
    env = {key: value for key, value in os.environ.items() if key.upper() in SAFE_ENV_KEYS}
    for name in requested_keys:
        key = name.strip()
        normalized = key.upper()
        if not key:
            raise SystemExit("Environment variable name cannot be empty.")
        credential_like = normalized == "PAT" or normalized.endswith("_PAT") or any(part in normalized for part in SENSITIVE_ENV_PARTS)
        if normalized not in SAFE_ENV_KEYS and credential_like:
            raise SystemExit(f"Refusing to pass credential-like environment variable {key!r} to repository code.")
        if key not in os.environ:
            raise SystemExit(f"Requested environment variable is not set: {key}")
        env[key] = os.environ[key]
    return env


def _hash_if_file(path: Path) -> str | None:
    return sha256_file(path) if path.is_file() else None


def _workspace_snapshot(workspace: Path) -> dict:
    files = {
        "reproduction_contract": workspace / "reproduction_contract.json",
        "run_plan": workspace / "run_plan.json",
        "repository_manifest": workspace / "repository_manifest.json",
        "data_manifest": workspace / "data_manifest.json",
        "checkpoint_manifest": workspace / "checkpoint_manifest.jsonl",
        "claim_code_map": workspace / "claim_code_map.jsonl",
    }
    return {
        "captured_at": utc_now(),
        **{f"{name}_sha256": _hash_if_file(path) for name, path in files.items()},
    }


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Execute an argv command and append immutable-style provenance to a JSONL run ledger.",
        epilog="Pass the command after --. This wrapper executes code; inspect untrusted repositories first.",
    )
    ap.add_argument("--ledger", type=Path, required=True)
    ap.add_argument("--workspace", type=Path, help="Reproduction workspace. Defaults to the ledger parent directory.")
    ap.add_argument("--run-id", required=True)
    ap.add_argument("--claim-id", action="append", dest="claim_ids", default=[])
    ap.add_argument("--run-kind", choices=["setup", "smoke", "target", "diagnostic", "exploratory"], required=True)
    ap.add_argument("--cwd", type=Path, required=True)
    ap.add_argument("--config", type=Path)
    ap.add_argument("--seed")
    ap.add_argument("--dataset-id")
    ap.add_argument("--checkpoint-id")
    ap.add_argument("--logs-dir", type=Path, required=True)
    ap.add_argument("--timeout", type=float, default=None, help="Timeout in seconds.")
    ap.add_argument("--allow-dirty", action="store_true")
    ap.add_argument("--env", action="append", default=[], metavar="NAME", help="Pass one explicitly reviewed, non-secret environment variable to the command. May be repeated.")
    ap.add_argument("--notes")
    ap.add_argument("command", nargs=argparse.REMAINDER)
    args = ap.parse_args()

    command = list(args.command)
    if command and command[0] == "--":
        command = command[1:]
    if not command:
        raise SystemExit("No command supplied after --")

    ledger = args.ledger.resolve()
    workspace = args.workspace.resolve() if args.workspace else ledger.parent.resolve()
    cwd = args.cwd.resolve()
    dirty = git_dirty(cwd)
    commit = git_value(cwd, ["rev-parse", "HEAD"])
    patch = git_patch_fingerprint(cwd) if dirty else None
    if dirty and not args.allow_dirty:
        raise SystemExit("Refusing to execute with a dirty Git worktree. Document the patch and use --allow-dirty intentionally.")

    logs = args.logs_dir.resolve()
    logs.mkdir(parents=True, exist_ok=True)
    stdout_path = logs / f"{args.run_id}.stdout.log"
    stderr_path = logs / f"{args.run_id}.stderr.log"

    config_obj = None
    if args.config:
        cfg = args.config if args.config.is_absolute() else cwd / args.config
        config_obj = {"path": str(cfg), "sha256": sha256_file(cfg) if cfg.is_file() else None}

    snapshot = _workspace_snapshot(workspace)
    if args.run_kind == "target" and not snapshot.get("reproduction_contract_sha256"):
        raise SystemExit("Target runs require a reproduction_contract.json in the workspace so the run can be bound to a contract hash.")
    execution_env = _execution_environment(args.env)

    started = utc_now()
    t0 = time.monotonic()
    timed_out = False
    returncode = None
    stdout_text = ""
    stderr_text = ""
    try:
        cp = subprocess.run(
            command,
            cwd=str(cwd),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False,
            timeout=args.timeout,
            env=execution_env,
        )
        returncode = cp.returncode
        stdout_text = cp.stdout
        stderr_text = cp.stderr
    except subprocess.TimeoutExpired as e:
        timed_out = True
        returncode = None
        stdout_text = e.stdout.decode() if isinstance(e.stdout, bytes) else (e.stdout or "")
        stderr_text = e.stderr.decode() if isinstance(e.stderr, bytes) else (e.stderr or "")
        stderr_text += "\n[AutoSCI wrapper] command timed out.\n"
    except FileNotFoundError as e:
        returncode = 127
        stderr_text = f"[AutoSCI wrapper] executable not found: {e}\n"
    ended = utc_now()
    duration = time.monotonic() - t0

    stdout_path.write_text(stdout_text, encoding="utf-8", errors="replace")
    stderr_path.write_text(stderr_text, encoding="utf-8", errors="replace")

    entry = {
        "run_id": args.run_id,
        "run_kind": args.run_kind,
        "claim_ids": args.claim_ids,
        "command": command,
        "cwd": str(cwd),
        "started_at": started,
        "ended_at": ended,
        "duration_seconds": round(duration, 6),
        "exit_code": returncode,
        "timed_out": timed_out,
        "source_commit": commit,
        "git_dirty": dirty,
        "patch_sha256": patch,
        "config": config_obj,
        "seed": args.seed,
        "inputs": {
            "dataset_id": args.dataset_id,
            "checkpoint_id": args.checkpoint_id,
        },
        "provenance_snapshot": snapshot,
        "environment_variable_names": sorted(execution_env),
        "stdout_path": str(stdout_path),
        "stderr_path": str(stderr_path),
        "outputs": [],
        "notes": args.notes,
    }
    append_jsonl(ledger, entry)
    print(f"run_id={args.run_id} exit_code={returncode} ledger={ledger}")
    if timed_out:
        return 124
    return int(returncode or 0)


if __name__ == "__main__":
    raise SystemExit(main())
