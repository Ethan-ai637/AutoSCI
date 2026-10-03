#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path

from _util import run_cmd, utc_now, write_json

SAFE_ENV_KEYS = [
    "CUDA_VISIBLE_DEVICES", "OMP_NUM_THREADS", "MKL_NUM_THREADS", "OPENBLAS_NUM_THREADS",
    "PYTHONHASHSEED", "TOKENIZERS_PARALLELISM", "CUBLAS_WORKSPACE_CONFIG"
]


def command_version(argv: list[str]) -> dict | None:
    if shutil.which(argv[0]) is None:
        return None
    try:
        cp = run_cmd(argv, timeout=15.0)
    except subprocess.TimeoutExpired:
        return {"command": argv, "status": "timeout"}
    return {
        "command": argv,
        "returncode": cp.returncode,
        "stdout": cp.stdout.strip()[:8000],
        "stderr": cp.stderr.strip()[:4000],
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="Capture resolved runtime environment without dumping secrets.")
    ap.add_argument("--outdir", type=Path, required=True)
    args = ap.parse_args()
    out = args.outdir.resolve()
    out.mkdir(parents=True, exist_ok=True)

    system = {
        "schema_version": "1.0",
        "captured_at": utc_now(),
        "platform": platform.platform(),
        "system": platform.system(),
        "release": platform.release(),
        "machine": platform.machine(),
        "processor": platform.processor(),
        "python": {
            "version": sys.version,
            "executable": sys.executable,
            "implementation": platform.python_implementation(),
        },
        "safe_environment": {k: os.environ.get(k) for k in SAFE_ENV_KEYS if k in os.environ},
        "tools": {
            "nvidia_smi": command_version(["nvidia-smi", "--query-gpu=name,driver_version,memory.total", "--format=csv,noheader"]),
            "nvcc": command_version(["nvcc", "--version"]),
            "gcc": command_version(["gcc", "--version"]),
            "clang": command_version(["clang", "--version"]),
        },
    }
    write_json(out / "system.json", system)

    pip_freeze = ""
    try:
        cp = run_cmd([sys.executable, "-m", "pip", "freeze"], timeout=30.0)
        if cp.returncode == 0:
            pip_freeze = cp.stdout
    except Exception:
        pass
    (out / "pip_freeze.txt").write_text(pip_freeze, encoding="utf-8")

    packages = [line.strip() for line in pip_freeze.splitlines() if line.strip()]
    resolved = {
        "schema_version": "1.0",
        "captured_at": utc_now(),
        "python_executable": sys.executable,
        "package_count": len(packages),
        "package_snapshot": "pip_freeze.txt",
        "notes": "This is the environment observed by the capture script, not proof of the authors' original environment.",
    }
    write_json(out / "resolved_environment.json", resolved)
    print(out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
