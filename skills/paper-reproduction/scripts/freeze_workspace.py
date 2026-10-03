#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

from _util import iter_files, sha256_file


def main() -> int:
    ap = argparse.ArgumentParser(description="Write a sha256 manifest for a reproduction workspace.")
    ap.add_argument("workspace", type=Path)
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()

    ws = args.workspace.resolve()
    out = args.output.resolve()
    lines = []
    for p in iter_files(ws, exclude_names={out.name}):
        rel = p.relative_to(ws).as_posix()
        lines.append(f"{sha256_file(p)}  {rel}")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(lines) + ("\n" if lines else ""), encoding="utf-8")
    print(f"Wrote {len(lines)} hashes to {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
