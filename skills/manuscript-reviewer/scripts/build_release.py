#!/usr/bin/env python3
"""Build a deterministic manuscript-reviewer skill ZIP from manifest.txt."""
from __future__ import annotations

import argparse
import subprocess
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOP = "manuscript-reviewer"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=None)
    parser.add_argument("--skip-validate", action="store_true")
    args = parser.parse_args()

    if not args.skip_validate:
        subprocess.run([sys.executable, str(ROOT / "scripts" / "validate_release.py")], check=True)

    version = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
    output = args.output or (ROOT.parent / "dist" / f"manuscript-reviewer-v{version}.zip")
    output.parent.mkdir(parents=True, exist_ok=True)

    entries = [x.strip() for x in (ROOT / "manifest.txt").read_text(encoding="utf-8").splitlines() if x.strip()]
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
        for rel in sorted(entries):
            src = ROOT / rel
            arc = f"{TOP}/{rel}"
            info = zipfile.ZipInfo(arc)
            info.date_time = (2026, 1, 1, 0, 0, 0)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o644 << 16
            zf.writestr(info, src.read_bytes())

    with zipfile.ZipFile(output) as zf:
        bad = zf.testzip()
        if bad:
            raise SystemExit(f"archive integrity failure: {bad}")
        names = zf.namelist()
        if not names or any(not n.startswith(TOP + "/") for n in names):
            raise SystemExit("archive must contain exactly one manuscript-reviewer/ top-level folder")
    print(output)


if __name__ == "__main__":
    main()
