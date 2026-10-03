#!/usr/bin/env python3
from __future__ import annotations

import argparse
import fnmatch
from pathlib import Path

from _util import git_dirty, git_lines, git_value, utc_now, write_json

ENV_PATTERNS = [
    "requirements*.txt", "environment*.yml", "environment*.yaml", "pyproject.toml",
    "setup.py", "setup.cfg", "Pipfile", "Pipfile.lock", "poetry.lock", "uv.lock",
    "conda*.yml", "conda*.yaml", "package.json", "package-lock.json", "yarn.lock"
]
CONTAINER_PATTERNS = ["Dockerfile", "Dockerfile.*", "docker-compose*.yml", "docker-compose*.yaml", "compose*.yml", "compose*.yaml"]
LICENSE_PATTERNS = ["LICENSE", "LICENSE.*", "COPYING", "COPYING.*"]
CONFIG_SUFFIXES = {".yaml", ".yml", ".json", ".toml", ".ini", ".cfg"}
ENTRY_NAMES = {"train.py", "evaluate.py", "eval.py", "test.py", "main.py", "run.py", "inference.py", "predict.py"}


def matches_any(name: str, patterns: list[str]) -> bool:
    return any(fnmatch.fnmatch(name, p) for p in patterns)


def detect_files(repo: Path) -> dict:
    env, container, entry, configs, licenses = [], [], [], [], []
    for p in repo.rglob("*"):
        if not p.is_file() or ".git" in p.parts:
            continue
        try:
            rel = p.relative_to(repo).as_posix()
        except ValueError:
            continue
        name = p.name
        depth = len(Path(rel).parts)
        if depth <= 3 and matches_any(name, ENV_PATTERNS):
            env.append(rel)
        if depth <= 3 and matches_any(name, CONTAINER_PATTERNS):
            container.append(rel)
        if depth <= 4 and (name in ENTRY_NAMES or rel.startswith("scripts/") and p.suffix in {".py", ".sh"}):
            entry.append(rel)
        if depth <= 5 and p.suffix.lower() in CONFIG_SUFFIXES and any(part.lower() in {"config", "configs", "conf", "experiments"} for part in p.parts):
            configs.append(rel)
        if depth <= 2 and matches_any(name, LICENSE_PATTERNS):
            licenses.append(rel)
    limit = lambda xs: sorted(dict.fromkeys(xs))[:500]
    return {
        "environment_files": limit(env),
        "container_files": limit(container),
        "entrypoint_candidates": limit(entry),
        "config_candidates": limit(configs),
        "license_files": limit(licenses),
    }


def parse_submodules(lines: list[str]) -> list[dict]:
    out = []
    for line in lines:
        if not line.strip():
            continue
        marker = line[0]
        rest = line[1:].strip().split()
        out.append({
            "state": {" ": "initialized", "-": "not_initialized", "+": "different_commit", "U": "merge_conflict"}.get(marker, "unknown"),
            "commit": rest[0] if rest else None,
            "path": rest[1] if len(rest) > 1 else None,
            "raw": line,
        })
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description="Inspect observable Git/repository state for paper reproduction.")
    ap.add_argument("--repo", required=True, type=Path)
    ap.add_argument("--output", required=True, type=Path)
    ap.add_argument("--repository-id", default="repo_001")
    args = ap.parse_args()

    repo = args.repo.resolve()
    if not (repo / ".git").exists() and git_value(repo, ["rev-parse", "--is-inside-work-tree"]) != "true":
        raise SystemExit(f"Not a Git worktree: {repo}")

    remote = git_value(repo, ["remote", "get-url", "origin"])
    commit = git_value(repo, ["rev-parse", "HEAD"])
    branch = git_value(repo, ["branch", "--show-current"])
    tags = git_lines(repo, ["tag", "--points-at", "HEAD"])
    dirty = git_dirty(repo)
    submodules = parse_submodules(git_lines(repo, ["submodule", "status", "--recursive"]))
    attrs = (repo / ".gitattributes")
    lfs = False
    if attrs.exists():
        try:
            lfs = "filter=lfs" in attrs.read_text(encoding="utf-8", errors="replace")
        except OSError:
            pass

    manifest = {
        "schema_version": "1.0",
        "repository_id": args.repository_id,
        "inspected_at": utc_now(),
        "local_path": str(repo),
        "remote_url": remote,
        "official_status": "unknown",
        "identity_evidence": [],
        "source_revision": {
            "commit": commit,
            "branch": branch,
            "tags_at_head": tags,
            "release": None,
            "selection_basis": "unknown",
            "selection_evidence": [],
        },
        "git": {
            "dirty": dirty,
            "submodules": submodules,
            "lfs_detected": lfs,
        },
        "detected": detect_files(repo),
        "notes": "Observable repository facts were collected mechanically. Fill identity and revision-selection evidence separately.",
    }
    write_json(args.output, manifest)
    print(args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
