#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
import subprocess
from pathlib import Path

from _util import git_value, utc_now, write_json


def run(argv: list[str], cwd: Path | None = None, env: dict | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        argv,
        cwd=str(cwd) if cwd else None,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=False,
    )


def main() -> int:
    ap = argparse.ArgumentParser(description="Clone a selected research repository conservatively and optionally pin a ref.")
    ap.add_argument("--url", required=True, help="Selected repository URL. Do not embed credentials in this value.")
    ap.add_argument("--dest", required=True, type=Path)
    ap.add_argument("--ref", help="Exact commit/tag/branch to detach-checkout after clone.")
    ap.add_argument("--output", type=Path, help="Write acquisition provenance JSON.")
    args = ap.parse_args()

    if "@" in args.url.split("//")[-1].split("/")[0] and args.url.startswith(("http://", "https://")):
        raise SystemExit("Refusing URL that appears to contain embedded credentials. Use normal credential mechanisms outside the recorded URL.")

    dest = args.dest.resolve()
    if dest.exists() and any(dest.iterdir()):
        raise SystemExit(f"Destination is non-empty: {dest}")
    dest.parent.mkdir(parents=True, exist_ok=True)

    env = os.environ.copy()
    # Avoid unexpectedly downloading large LFS payloads during initial acquisition.
    env["GIT_LFS_SKIP_SMUDGE"] = "1"
    started = utc_now()
    clone = run(["git", "-c", "core.hooksPath=/dev/null", "clone", "--no-recurse-submodules", args.url, str(dest)], env=env)
    if clone.returncode != 0:
        if args.output:
            write_json(args.output, {
                "schema_version": "1.0", "started_at": started, "ended_at": utc_now(),
                "requested_url": args.url, "requested_ref": args.ref, "status": "clone_failed",
                "clone_stderr": clone.stderr[-8000:],
            })
        print(clone.stderr, end="", file=__import__("sys").stderr)
        return clone.returncode or 1

    checkout_status = "default_head"
    checkout_stderr = ""
    if args.ref:
        fetch = run(["git", "fetch", "--tags", "origin", args.ref], cwd=dest, env=env)
        # Some refs are already present and fetch by raw SHA can be denied; still try checkout.
        co = run(["git", "checkout", "--detach", args.ref], cwd=dest, env=env)
        checkout_stderr = (fetch.stderr + "\n" + co.stderr)[-8000:]
        if co.returncode != 0:
            status = "checkout_failed"
            if args.output:
                write_json(args.output, {
                    "schema_version": "1.0", "started_at": started, "ended_at": utc_now(),
                    "requested_url": args.url, "requested_ref": args.ref, "status": status,
                    "clone_stdout": clone.stdout[-4000:], "checkout_stderr": checkout_stderr,
                    "local_path": str(dest),
                })
            print(checkout_stderr, file=__import__("sys").stderr)
            return co.returncode or 1
        checkout_status = "detached_requested_ref"

    result = {
        "schema_version": "1.0",
        "started_at": started,
        "ended_at": utc_now(),
        "requested_url": args.url,
        "requested_ref": args.ref,
        "status": "ok",
        "checkout_status": checkout_status,
        "local_path": str(dest),
        "remote_url": git_value(dest, ["remote", "get-url", "origin"]),
        "commit": git_value(dest, ["rev-parse", "HEAD"]),
        "branch": git_value(dest, ["branch", "--show-current"]),
        "lfs_smudge_skipped": True,
        "submodules_initialized": False,
        "notes": "Clone acquisition does not verify paper identity. Submodules and LFS payloads were not initialized automatically.",
    }
    if args.output:
        write_json(args.output, result)
    print(f"Acquired {dest} @ {result['commit']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
