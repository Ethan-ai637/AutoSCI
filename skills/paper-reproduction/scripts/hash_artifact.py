#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

from _util import hash_path, utc_now, write_json


def main() -> int:
    ap = argparse.ArgumentParser(description="Hash a file or directory for reproduction provenance.")
    ap.add_argument("path", type=Path)
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()
    result = hash_path(args.path)
    result["captured_at"] = utc_now()
    write_json(args.output, result)
    print(args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
