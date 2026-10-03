from __future__ import annotations

import hashlib
import json
import os
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def write_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2, ensure_ascii=False)
        f.write("\n")


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    out: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as f:
        for lineno, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                value = json.loads(line)
            except json.JSONDecodeError as e:
                raise ValueError(f"{path}:{lineno}: invalid JSON: {e}") from e
            if not isinstance(value, dict):
                raise ValueError(f"{path}:{lineno}: JSONL row must be an object")
            out.append(value)
    return out


def append_jsonl(path: Path, obj: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(obj, ensure_ascii=False, sort_keys=True) + "\n")


def sha256_file(path: Path, chunk_size: int = 1024 * 1024) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        while True:
            chunk = f.read(chunk_size)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def iter_files(root: Path, exclude_names: Iterable[str] = ()) -> list[Path]:
    excludes = set(exclude_names)
    if root.is_file():
        return [root]
    files: list[Path] = []
    for p in root.rglob("*"):
        if p.is_symlink() or not p.is_file():
            continue
        if p.name in excludes:
            continue
        files.append(p)
    return sorted(files, key=lambda p: p.as_posix())


def hash_path(root: Path) -> dict[str, Any]:
    root = root.resolve()
    if root.is_file():
        return {
            "kind": "file",
            "path": str(root),
            "size": root.stat().st_size,
            "sha256": sha256_file(root),
        }
    if not root.is_dir():
        raise FileNotFoundError(root)
    entries = []
    aggregate = hashlib.sha256()
    total_size = 0
    for p in iter_files(root):
        rel = p.relative_to(root).as_posix()
        digest = sha256_file(p)
        size = p.stat().st_size
        total_size += size
        entries.append({"path": rel, "size": size, "sha256": digest})
        aggregate.update(rel.encode("utf-8"))
        aggregate.update(b"\0")
        aggregate.update(digest.encode("ascii"))
        aggregate.update(b"\n")
    return {
        "kind": "directory",
        "path": str(root),
        "file_count": len(entries),
        "total_size": total_size,
        "sha256_manifest": aggregate.hexdigest(),
        "files": entries,
    }


def run_cmd(argv: list[str], cwd: Path | None = None, timeout: float | None = 20.0) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        argv,
        cwd=str(cwd) if cwd else None,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=False,
        timeout=timeout,
    )


def git_value(repo: Path, args: list[str]) -> str | None:
    try:
        cp = run_cmd(["git", *args], cwd=repo, timeout=15.0)
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return None
    if cp.returncode != 0:
        return None
    return cp.stdout.strip() or None


def git_lines(repo: Path, args: list[str]) -> list[str]:
    value = git_value(repo, args)
    return value.splitlines() if value else []


def git_dirty(repo: Path) -> bool | None:
    try:
        cp = run_cmd(["git", "status", "--porcelain=v1", "--untracked-files=all"], cwd=repo, timeout=15.0)
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return None
    if cp.returncode != 0:
        return None
    return bool(cp.stdout.strip())


def git_patch_fingerprint(repo: Path) -> str | None:
    try:
        tracked = run_cmd(["git", "diff", "--binary", "HEAD"], cwd=repo, timeout=20.0)
        untracked = git_lines(repo, ["ls-files", "--others", "--exclude-standard"])
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return None
    if tracked.returncode != 0:
        return None
    payload = bytearray(tracked.stdout.encode("utf-8", errors="replace"))
    for rel in sorted(untracked):
        p = repo / rel
        if p.is_file():
            payload.extend(b"\nUNTRACKED\0")
            payload.extend(rel.encode("utf-8", errors="replace"))
            payload.extend(b"\0")
            try:
                payload.extend(sha256_file(p).encode("ascii"))
            except OSError:
                payload.extend(b"UNREADABLE")
    return sha256_bytes(bytes(payload)) if payload else None
