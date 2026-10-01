#!/usr/bin/env python3
"""Repository/package self-test for academic-manuscript-writing.

Uses only the Python standard library. It validates package hygiene and runs
release preflight against compatibility/current fixtures. Full mode also runs
small destructive mutations that must be rejected by release QA.
"""
from __future__ import annotations

from pathlib import Path
import argparse
import ast
import json
import os
import shutil
import subprocess
import sys
import tempfile
from typing import Dict, List, Optional, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed

ROOT = Path(__file__).resolve().parent.parent
MIN_PYTHON = (3, 8)
SCRIPTS = ROOT / "scripts"
EXAMPLES = ROOT / "examples"

QUICK_CASES = [
    "minimal",               # legacy v1.6 compatibility
    "revision-lifecycle",    # legacy v1.5 state-lineage compatibility
    "conflict-disposition",  # v1.7.x conflict governance
    "full-release-span",     # v1.8 full release
    "dynamic-writing-profile", # v2.0 dynamic discipline/venue profile
]

FULL_CASES = [
    "minimal",
    "full-release",
    "paragraph-composition",
    "revision-lifecycle",
    "conflict-disposition",
    "span-traceability",
    "full-release-span",
    "dynamic-writing-profile",
]


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def syntax_and_data_checks(errors: List[str]) -> None:
    if sys.version_info < MIN_PYTHON:
        errors.append(
            "python: academic-manuscript-writing requires Python %d.%d+; running %d.%d.%d"
            % (MIN_PYTHON[0], MIN_PYTHON[1], sys.version_info[0], sys.version_info[1], sys.version_info[2])
        )
        return

    # Parse source without writing __pycache__ files and enforce the declared
    # Python 3.8 syntax floor even when self-test runs on a newer interpreter.
    for path in sorted(SCRIPTS.glob("*.py")):
        try:
            source = path.read_text(encoding="utf-8")
            compile(source, str(path), "exec")
            ast.parse(source, filename=str(path), mode="exec", feature_version=(3, 8))
        except Exception as exc:
            errors.append(f"syntax: {path.relative_to(ROOT)}: {exc}")

    json_paths = sorted((ROOT / "schemas").glob("*.json")) + [ROOT / "templates" / "project.template.json", ROOT / "templates" / "section_plan.template.json", ROOT / "templates" / "writing_profile.template.json", ROOT / "templates" / "manuscript_contract.template.json"]
    json_paths += sorted(EXAMPLES.glob("*/project.json"))
    json_paths += sorted(EXAMPLES.glob("*/section_plan.json"))
    json_paths += sorted(EXAMPLES.glob("*/writing_profile.json"))
    json_paths += sorted(EXAMPLES.glob("*/manuscript_contract.json"))
    json_paths += sorted(EXAMPLES.glob("*/revision_diff.json"))
    json_paths += sorted(EXAMPLES.glob("*/workspace_state.previous.json"))
    for path in json_paths:
        if not path.exists():
            continue
        try:
            load_json(path)
        except Exception as exc:
            errors.append(f"json: {path.relative_to(ROOT)}: {exc}")

    for path in sorted(ROOT.glob("templates/*.jsonl")) + sorted(EXAMPLES.glob("*/*.jsonl")):
        try:
            for n, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
                if line.strip():
                    json.loads(line)
        except Exception as exc:
            errors.append(f"jsonl: {path.relative_to(ROOT)}:{n}: {exc}")


def version_checks(errors: List[str]) -> None:
    version = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
    template_version = str(load_json(ROOT / "templates" / "project.template.json").get("skill_version", ""))
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    changelog = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
    if version != template_version:
        errors.append(f"version: VERSION={version!r} but project.template.json={template_version!r}")
    if f"Current version: `{version}`" not in readme:
        errors.append(f"version: README.md does not declare Current version: `{version}`")
    if f"## {version} " not in changelog and f"## {version} —" not in changelog:
        errors.append(f"version: CHANGELOG.md has no {version} release entry")


def hygiene_checks(errors: List[str]) -> None:
    forbidden = []
    forbidden.extend(ROOT.rglob("*.pyc"))
    forbidden.extend(p for p in ROOT.rglob("__pycache__") if p.is_dir())
    forbidden.extend(ROOT.rglob("qa_report.json"))
    if forbidden:
        shown = ", ".join(str(p.relative_to(ROOT)) for p in sorted(set(forbidden))[:12])
        errors.append(f"hygiene: generated files/directories present: {shown}")


def init_workspace_check(timeout: int, errors: List[str], notes: List[str]) -> None:
    env = dict(os.environ)
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    with tempfile.TemporaryDirectory(prefix="amw-init-") as td:
        workspace = Path(td) / "workspace"
        try:
            proc = subprocess.run(
                [sys.executable, str(SCRIPTS / "init_workspace.py"), str(workspace)],
                cwd=ROOT, env=env, text=True, capture_output=True, timeout=timeout
            )
        except subprocess.TimeoutExpired as exc:
            errors.append(f"init: timed out after {timeout}s: {exc}")
            return
        if proc.returncode != 0:
            errors.append(f"init: init_workspace.py failed: {(proc.stderr or proc.stdout)[-500:]}")
            return
        required = {
            "project.json", "sources.jsonl", "evidence.jsonl", "claims.jsonl",
            "revision_log.jsonl", "section_plan.json", "reporting_contracts.jsonl",
            "paragraph_contracts.jsonl", "revision_obligations.jsonl", "writing_sources.jsonl",
            "writing_profile.json", "manuscript_contract.json", "manuscript.md",
        }
        missing = sorted(name for name in required if not (workspace / name).exists())
        if missing:
            errors.append(f"init: missing initialized files: {missing}")
            return
        current = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
        initialized = str(load_json(workspace / "project.json").get("skill_version", ""))
        if initialized != current:
            errors.append(f"init: initialized project version {initialized!r} != package VERSION {current!r}")
            return
        notes.append(f"PASS init workspace: current version {current}")


def run_preflight(workspace: Path, report: Path, timeout: int) -> Tuple[int, Dict, str]:
    env = dict(os.environ)
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    cmd = [sys.executable, str(SCRIPTS / "preflight.py"), str(workspace), "--profile", "release", "--report", str(report)]
    try:
        proc = subprocess.run(cmd, cwd=ROOT, env=env, text=True, capture_output=True, timeout=timeout)
    except subprocess.TimeoutExpired as exc:
        return 124, {}, f"timed out after {timeout}s: {exc}"
    try:
        data = load_json(report) if report.exists() else json.loads(proc.stdout)
    except Exception:
        data = {}
    return proc.returncode, data, proc.stderr or proc.stdout


def run_audit(script: str, workspace: Path, timeout: int) -> Tuple[int, Dict, str]:
    env = dict(os.environ)
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    cmd = [sys.executable, str(SCRIPTS / script), str(workspace), "--profile", "release"]
    try:
        proc = subprocess.run(cmd, cwd=ROOT, env=env, text=True, capture_output=True, timeout=timeout)
    except subprocess.TimeoutExpired as exc:
        return 124, {}, f"timed out after {timeout}s: {exc}"
    try:
        data = json.loads(proc.stdout)
    except Exception:
        data = {}
    return proc.returncode, data, proc.stderr or proc.stdout


def positive_fixture_checks(case_names: List[str], timeout: int, errors: List[str], notes: List[str], workers: int = 1) -> None:
    with tempfile.TemporaryDirectory(prefix="amw-selftest-") as td_raw:
        td = Path(td_raw)

        def one(name: str):
            print(f"[self-test] release fixture: {name}", file=sys.stderr, flush=True)
            workspace = EXAMPLES / name
            report = td / f"{name}.json"
            result = run_preflight(workspace, report, timeout)
            print(f"[self-test] finished fixture: {name}", file=sys.stderr, flush=True)
            return name, *result

        # Fixtures are independent. Parallel execution keeps the smoke test practical
        # even though each preflight intentionally launches every deterministic audit.
        workers = min(max(1, workers), max(1, len(case_names)))
        with ThreadPoolExecutor(max_workers=workers) as pool:
            futures = [pool.submit(one, name) for name in case_names]
            results = [future.result() for future in as_completed(futures)]

        for name, code, data, output in sorted(results):
            if code != 0 or not data.get("ok") or data.get("warnings"):
                errors.append(
                    f"fixture: {name} expected release PASS/0 warnings; code={code}, "
                    f"errors={data.get('errors')}, warnings={data.get('warnings')}, output={output[-500:]}"
                )
            else:
                notes.append(f"PASS fixture {name}: {len(data.get('checks', []))} checks, 0 warnings")


def destructive_checks(timeout: int, errors: List[str], notes: List[str], enabled: bool = True) -> None:
    if not enabled:
        return
    base = EXAMPLES / "span-traceability"
    mutations = [
        (
            "missing_end_claim",
            lambda text: text.replace("<!-- END-CLAIM:C001 -->", "", 1),
            "claim span",
        ),
        (
            "claim_text_drift",
            lambda text: text.replace("12.4 units", "12.5 units", 1),
            "claim",
        ),
        (
            "uncovered_scientific_prose",
            lambda text: text.replace("<!-- END-CLAIM:C002 -->", "<!-- END-CLAIM:C002 --> A causes B.", 1),
            "outside exact claim spans",
        ),
    ]
    with tempfile.TemporaryDirectory(prefix="amw-negative-") as td_raw:
        td = Path(td_raw)

        def one(item):
            name, mutate, expected_hint = item
            print(f"[self-test] destructive span check: {name}", file=sys.stderr, flush=True)
            workspace = td / name
            shutil.copytree(base, workspace)
            manuscript = workspace / "manuscript.md"
            manuscript.write_text(mutate(manuscript.read_text(encoding="utf-8")), encoding="utf-8")
            return name, expected_hint, *run_audit("audit_claim_spans.py", workspace, timeout)

        with ThreadPoolExecutor(max_workers=3) as pool:
            results = [future.result() for future in as_completed([pool.submit(one, item) for item in mutations])]

        for name, expected_hint, code, data, output in sorted(results):
            if code == 0 or data.get("ok"):
                errors.append(f"negative fixture: {name} unexpectedly passed release")
                continue
            joined = " ".join(str(x) for x in data.get("errors", [])).lower()
            if expected_hint and expected_hint.lower() not in joined:
                errors.append(
                    f"negative fixture: {name} failed, but expected diagnostic hint {expected_hint!r} was absent; "
                    f"errors={data.get('errors')}, output={output[-500:]}"
                )
            else:
                notes.append(f"PASS negative {name}: release correctly rejected mutation")



def writing_profile_destructive_checks(timeout: int, errors: List[str], notes: List[str], enabled: bool = True) -> None:
    if not enabled:
        return
    base = EXAMPLES / "dynamic-writing-profile"

    def mutate_nonofficial(workspace: Path) -> None:
        path=workspace / "writing_sources.jsonl"
        row=json.loads(path.read_text(encoding="utf-8").strip())
        row["authority_level"]="secondary"
        path.write_text(json.dumps(row)+"\n", encoding="utf-8")

    def mutate_stale_contract(workspace: Path) -> None:
        path=workspace / "writing_profile.json"
        data=load_json(path)
        data["constraints"][0]["requirement"] += " Updated after contract generation."
        path.write_text(json.dumps(data, indent=2)+"\n", encoding="utf-8")

    def mutate_stage_mismatch(workspace: Path) -> None:
        path=workspace / "project.json"
        data=load_json(path)
        data["writing_context"]["submission_stage"]="camera_ready"
        path.write_text(json.dumps(data, indent=2)+"\n", encoding="utf-8")

    def mutate_article_type_mismatch(workspace: Path) -> None:
        path=workspace / "project.json"
        data=load_json(path)
        data["writing_context"]["article_type"]="journal_article"
        path.write_text(json.dumps(data, indent=2)+"\n", encoding="utf-8")

    def mutate_track_mismatch(workspace: Path) -> None:
        path=workspace / "project.json"
        data=load_json(path)
        data["writing_context"]["track"]="industry"
        path.write_text(json.dumps(data, indent=2)+"\n", encoding="utf-8")

    def mutate_missing_section(workspace: Path) -> None:
        path=workspace / "manuscript.md"
        text=path.read_text(encoding="utf-8")
        text=text.replace("# Methods\n\n<!-- CLAIM:CM1 -->\nThe primary outcome was compared between conditions A and B using the prespecified analysis.<!-- END-CLAIM:CM1 -->\n\n", "", 1)
        path.write_text(text, encoding="utf-8")


    def mutate_manual_pending(workspace: Path) -> None:
        path=workspace / "manuscript_contract.json"
        data=load_json(path)
        data["manual_checks"][0]["status"]="pending"
        path.write_text(json.dumps(data, indent=2)+"\n", encoding="utf-8")
    mutations = [
        ("venue_without_official_source", mutate_nonofficial, "official"),
        ("stale_manuscript_contract", mutate_stale_contract, "stale"),
        ("submission_stage_mismatch", mutate_stage_mismatch, "context"),
        ("article_type_mismatch", mutate_article_type_mismatch, "context"),
        ("track_mismatch", mutate_track_mismatch, "context"),
        ("missing_required_venue_section", mutate_missing_section, "missing required contract section"),
        ("pending_manual_venue_check", mutate_manual_pending, "manual check status"),
    ]
    with tempfile.TemporaryDirectory(prefix="amw-writing-negative-") as td_raw:
        td=Path(td_raw)
        for name, mutate, expected_hint in mutations:
            workspace=td/name
            shutil.copytree(base, workspace)
            mutate(workspace)
            code, data, output=run_audit("audit_writing_profile.py", workspace, timeout)
            if code == 0 or data.get("ok"):
                errors.append(f"negative writing-profile fixture: {name} unexpectedly passed release")
                continue
            joined=" ".join(str(x) for x in data.get("errors", [])).lower()
            if expected_hint.lower() not in joined:
                errors.append(
                    f"negative writing-profile fixture: {name} failed, but expected diagnostic hint {expected_hint!r} was absent; "
                    f"errors={data.get('errors')}, output={output[-500:]}"
                )
            else:
                notes.append(f"PASS negative writing-profile {name}: release correctly rejected mutation")

def parse_shard(value: Optional[str], total_items: int) -> Optional[Tuple[int, int]]:
    if not value:
        return None
    try:
        left, right = value.split("/", 1)
        index, total = int(left), int(right)
    except Exception as exc:
        raise ValueError("shard must use INDEX/TOTAL, e.g. 1/3") from exc
    if total < 1 or index < 1 or index > total:
        raise ValueError("shard requires 1 <= INDEX <= TOTAL")
    if total_items and total > total_items:
        raise ValueError(f"shard TOTAL={total} exceeds available positive fixtures={total_items}")
    return index, total


def shard_items(items: List[str], shard: Optional[Tuple[int, int]]) -> List[str]:
    if not shard:
        return list(items)
    index, total = shard
    return [item for pos, item in enumerate(items) if pos % total == index - 1]


def main() -> None:
    ap = argparse.ArgumentParser(description="Self-test the academic-manuscript-writing package.")
    mode = ap.add_mutually_exclusive_group()
    mode.add_argument("--quick", action="store_true", help="Run package checks plus five representative release fixtures (default).")
    mode.add_argument("--full", action="store_true", help="Run all positive fixtures plus destructive span tests.")
    ap.add_argument("--timeout", type=int, default=60, help="Per-preflight timeout in seconds (default: 60).")
    ap.add_argument("--shard", help="Full-mode CI shard as INDEX/TOTAL, e.g. 1/3. Destructive tests run in shard 1.")
    ap.add_argument("--json-report", help="Optional path for a machine-readable self-test report.")
    args = ap.parse_args()

    errors: List[str] = []
    notes: List[str] = []
    syntax_and_data_checks(errors)
    version_checks(errors)
    hygiene_checks(errors)
    init_workspace_check(args.timeout, errors, notes)

    full = bool(args.full)
    if args.shard and not full:
        errors.append("shard: --shard is supported only with --full")
        shard = None
    else:
        try:
            shard = parse_shard(args.shard, len(FULL_CASES))
        except ValueError as exc:
            errors.append(f"shard: {exc}")
            shard = None

    selected = shard_items(FULL_CASES, shard) if full else QUICK_CASES
    positive_fixture_checks(selected, args.timeout, errors, notes, workers=(min(5, len(selected)) if not full else 1))
    if full:
        destructive_checks(args.timeout, errors, notes, enabled=(shard is None or shard[0] == 1))
        writing_profile_destructive_checks(args.timeout, errors, notes, enabled=(shard is None or shard[0] == 1))

    report = {
        "ok": not errors,
        "version": (ROOT / "VERSION").read_text(encoding="utf-8").strip(),
        "mode": "full" if full else "quick",
        "shard": args.shard if full else None,
        "errors": errors,
        "checks": notes,
    }
    if args.json_report:
        Path(args.json_report).write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    print(json.dumps(report, indent=2, ensure_ascii=False))
    raise SystemExit(0 if report["ok"] else 1)


if __name__ == "__main__":
    main()
