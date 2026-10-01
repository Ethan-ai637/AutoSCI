#!/usr/bin/env python3
from __future__ import annotations

import argparse
import compileall
import json
import subprocess
import sys
from pathlib import Path

from _common import ANALYSIS_PLAN_SCHEMA_VERSION, POWER_PLAN_SCHEMA_VERSION, SKILL_VERSION

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"


def fail(message: str) -> None:
    raise RuntimeError(message)


def require(condition: bool, message: str) -> None:
    if not condition:
        fail(message)


def read_json(path: Path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def run(label: str, *args: str) -> None:
    print(f"release-check: {label}", flush=True)
    completed = subprocess.run([sys.executable, *args], cwd=ROOT)
    if completed.returncode != 0:
        fail(f"{label} failed with exit code {completed.returncode}")


def remove_python_caches() -> None:
    caches = sorted((p for p in ROOT.rglob("__pycache__") if p.is_dir()), key=lambda p: len(p.parts), reverse=True)
    for cache in caches:
        for child in cache.iterdir():
            if child.is_file() or child.is_symlink():
                child.unlink()
        try:
            cache.rmdir()
        except OSError:
            pass


def assert_no_python_caches() -> None:
    generated = [p for p in ROOT.rglob("*") if p.is_file() and p.suffix == ".pyc"]
    require(not generated, "generated Python bytecode files remain in the release tree")


def check_static_contract() -> None:
    print("release-check: static contract", flush=True)
    version = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
    require(version == SKILL_VERSION, f"VERSION={version!r} != code skill version {SKILL_VERSION!r}")

    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
    changelog = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
    require(readme.startswith(f"# scientific-data-analysis v{SKILL_VERSION}"), "README title version mismatch")
    require(f"# Scientific Data Analysis — v{SKILL_VERSION}" in skill[:2000], "SKILL title version mismatch")
    require(f"## {SKILL_VERSION} —" in changelog[:1000], "CHANGELOG current release entry missing near top")

    analysis_example = read_json(ROOT / "examples" / "analysis_plan.json")
    contrast_example = read_json(ROOT / "examples" / "planned_contrast_plan.json")
    analysis_template = read_json(ROOT / "templates" / "analysis_plan.template.json")
    power_example = read_json(ROOT / "examples" / "power_plan.json")
    power_template = read_json(ROOT / "templates" / "power_plan.template.json")

    for name, obj in [
        ("analysis example", analysis_example),
        ("contrast example", contrast_example),
        ("analysis template", analysis_template),
    ]:
        require(obj.get("analysis_plan_schema_version") == ANALYSIS_PLAN_SCHEMA_VERSION, f"{name} schema mismatch")
    for name, obj in [("power example", power_example), ("power template", power_template)]:
        require(obj.get("power_plan_schema_version") == POWER_PLAN_SCHEMA_VERSION, f"{name} schema mismatch")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate the scientific-data-analysis release tree.")
    parser.add_argument(
        "--full",
        action="store_true",
        help="also run the complete post-data and power self-test suites (recommended for CI/releases)",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        check_static_contract()
        print("release-check: compile scripts", flush=True)
        ok = compileall.compile_dir(str(SCRIPTS), quiet=1, force=True)
        require(ok, "Python source compilation failed")
        remove_python_caches()

        run("doctor", "scripts/doctor.py")
        run("analysis plan", "scripts/validate_plan.py", "examples/analysis_plan.json")
        run("planned contrast plan", "scripts/validate_plan.py", "examples/planned_contrast_plan.json")
        run("power plan", "scripts/validate_power_plan.py", "examples/power_plan.json")
        if args.full:
            run("power self-test", "scripts/power_self_test.py")
            run("post-data self-test", "scripts/self_test.py")
        check_static_contract()
        remove_python_caches()
        assert_no_python_caches()
    except Exception as exc:
        print(f"scientific-data-analysis release check: FAIL — {exc}", file=sys.stderr)
        return 1
    mode = "FULL" if args.full else "QUICK"
    print(f"scientific-data-analysis release check: PASS ({mode})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
