#!/usr/bin/env python3
"""Validate manuscript-reviewer for skill upload and public GitHub release."""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MAX_SKILL_DESCRIPTION = 1024
MAX_SKILL_FILE = 256 * 1024
MAX_SUPPORT_FILE = 25 * 1024 * 1024
MAX_FILE_COUNT = 500

def fail(msg: str) -> None:
    print(f"FAIL: {msg}")
    raise SystemExit(1)

def ok(msg: str) -> None:
    print(f"PASS: {msg}")

def load_yaml(path: Path):
    try:
        import yaml
    except Exception as e:
        fail(f"PyYAML unavailable: {e}")
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def load_yaml_from_text(text: str):
    try:
        import yaml
    except Exception as e:
        fail(f"PyYAML unavailable: {e}")
    return yaml.safe_load(text)

def skill_frontmatter_check() -> None:
    skill_files = [p for p in ROOT.rglob("*") if p.is_file() and p.name.lower() == "skill.md"]
    if len(skill_files) != 1 or skill_files[0] != ROOT / "SKILL.md":
        fail(f"expected exactly one root SKILL.md; found {[str(p.relative_to(ROOT)) for p in skill_files]}")
    text = (ROOT / "SKILL.md").read_text(encoding="utf-8")
    m = re.match(r"\A---\n(.*?)\n---\n(.*)\Z", text, flags=re.S)
    if not m:
        fail("SKILL.md front matter missing or malformed")
    fm = load_yaml_from_text(m.group(1))
    if not isinstance(fm, dict):
        fail("SKILL.md front matter must be a mapping")
    name = fm.get("name")
    desc = fm.get("description")
    if name != "manuscript-reviewer":
        fail(f"unexpected skill name: {name!r}")
    if not isinstance(desc, str) or not desc.strip():
        fail("skill description missing")
    if len(desc) > MAX_SKILL_DESCRIPTION:
        fail(f"skill description exceeds {MAX_SKILL_DESCRIPTION} characters")
    if not m.group(2).strip():
        fail("SKILL.md body is empty")
    if (ROOT / "SKILL.md").stat().st_size > MAX_SKILL_FILE:
        fail("SKILL.md exceeds conservative 256 KiB portability bound")
    ok(f"SKILL.md front matter valid; description={len(desc)} chars")

def public_repo_check() -> None:
    required = ["README.md","LICENSE","CONTRIBUTING.md","SECURITY.md","CODE_OF_CONDUCT.md","CITATION.cff","requirements-dev.txt","Makefile",".gitignore",".github/workflows/validate.yml","agents/openai.yaml","docs/ARCHITECTURE.md","docs/EVALUATION.md","scripts/build_release.py"]
    missing = [x for x in required if not (ROOT / x).exists()]
    if missing:
        fail(f"public-repository files missing: {missing}")
    workflow = (ROOT / ".github/workflows/validate.yml").read_text(encoding="utf-8")
    if "scripts/validate_release.py" not in workflow:
        fail("GitHub validation workflow does not run release validator")
    ok("public-repository scaffolding present")

def github_metadata_check() -> None:
    workflow = load_yaml(ROOT / ".github/workflows/validate.yml")
    if not isinstance(workflow, dict) or "jobs" not in workflow:
        fail("GitHub Actions workflow is not a valid workflow mapping")
    for issue in sorted((ROOT / ".github/ISSUE_TEMPLATE").glob("*.yml")):
        data = load_yaml(issue)
        if not isinstance(data, dict):
            fail(f"invalid GitHub issue form: {issue.name}")
        for key in ["name", "description", "body"]:
            if key not in data:
                fail(f"GitHub issue form {issue.name} missing {key}")
    ok("GitHub workflow and issue forms parse")

def version_check() -> None:
    version = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
    if not re.fullmatch(r"\d+\.\d+\.\d+", version):
        fail(f"invalid VERSION: {version!r}")
    for name in ["RELEASE_NOTES.md","CHANGELOG.md","SKILL.md","CITATION.cff"]:
        text = (ROOT / name).read_text(encoding="utf-8")
        if version not in text:
            fail(f"{name} does not mention VERSION {version}")
    cff = load_yaml(ROOT / "CITATION.cff")
    if not isinstance(cff, dict) or str(cff.get("version")) != version:
        fail("CITATION.cff version does not match VERSION")
    if cff.get("license") != "MIT":
        fail("CITATION.cff license must match bundled MIT LICENSE")
    ok(f"version {version} is consistent")

def agent_metadata_check() -> None:
    data = load_yaml(ROOT / "agents/openai.yaml")
    if not isinstance(data, dict) or not isinstance(data.get("interface"), dict):
        fail("agents/openai.yaml must contain interface mapping")
    interface = data["interface"]
    for key in ["display_name","short_description"]:
        if not isinstance(interface.get(key), str) or not interface[key].strip():
            fail(f"agents/openai.yaml missing {key}")
    default = interface.get("default_prompt")
    if default is not None and (not isinstance(default, str) or not default.strip()):
        fail("agents/openai.yaml default_prompt must be non-empty string")
    policy = data.get("policy", {})
    if policy:
        products = policy.get("products")
        if not isinstance(products, list) or not products or any(p not in {"CHAT","CODEX"} for p in products):
            fail("agents/openai.yaml policy.products must be CHAT/CODEX list")
        if not isinstance(policy.get("allow_implicit_invocation"), bool):
            fail("agents/openai.yaml policy.allow_implicit_invocation must be boolean")
    ok("OpenAI agent metadata valid")

def schema_check() -> None:
    try:
        import jsonschema
    except Exception as e:
        fail(f"jsonschema unavailable: {e}")
    finding_schema = json.loads((ROOT / "schemas/finding_record.schema.json").read_text(encoding="utf-8"))
    revision_schema = json.loads((ROOT / "schemas/revision_delta.schema.json").read_text(encoding="utf-8"))
    jsonschema.Draft202012Validator.check_schema(finding_schema)
    jsonschema.Draft202012Validator.check_schema(revision_schema)
    def json_blocks(path: Path):
        text = path.read_text(encoding="utf-8")
        return re.findall(r"```json\s*(.*?)\s*```", text, flags=re.S)
    fblocks = json_blocks(ROOT / "examples/example_finding.md")
    if not fblocks: fail("no JSON example in examples/example_finding.md")
    for block in fblocks: jsonschema.validate(json.loads(block), finding_schema)
    rblocks = json_blocks(ROOT / "examples/example_revision_delta.md")
    if not rblocks: fail("no JSON example in examples/example_revision_delta.md")
    for block in rblocks: jsonschema.validate(json.loads(block), revision_schema)
    ok("schemas and bundled JSON examples validate")

def yaml_check() -> None:
    files = sorted((ROOT / "regressions").glob("*.yaml")) + [ROOT / "templates/regression_case.yaml"]
    for p in files:
        obj = load_yaml(p)
        if not isinstance(obj, dict): fail(f"YAML fixture/template is not a mapping: {p.relative_to(ROOT)}")
    if not (ROOT / "regressions/security_embedded_prompt_injection.yaml").exists():
        fail("security regression fixture missing")
    ok(f"parsed {len(files)} regression YAML files")

def local_reference_check() -> None:
    prefixes=("checks/","schemas/","templates/","examples/","regressions/","maintenance/","scripts/","docs/","agents/")
    missing=set()
    for p in ROOT.rglob("*.md"):
        text=p.read_text(encoding="utf-8")
        for token in re.findall(r"`([^`]+)`", text):
            token=token.rstrip(".,;:")
            if token.startswith(prefixes) and not (ROOT / token).exists():
                missing.add(token)
    if missing: fail(f"missing local references: {sorted(missing)}")
    ok("local markdown references resolve")

def state_schema_check() -> None:
    fs=json.loads((ROOT/"schemas/finding_record.schema.json").read_text(encoding="utf-8"))
    rs=json.loads((ROOT/"schemas/revision_delta.schema.json").read_text(encoding="utf-8"))
    state_text=(ROOT/"checks/state_model.md").read_text(encoding="utf-8")
    required_tokens=["verified_support","partial_support","contradicted","missing_required_evidence","ambiguous_mapping","unavailable_to_verify","not_applicable","finding","author_query","coverage_gap","Critical","Major","Moderate","Minor","resolved","partially_resolved","persistent","reclassified","not_reassessable","no_longer_material"]
    for tok in required_tokens:
        if f"`{tok}`" not in state_text and tok not in {"Critical","Major","Moderate","Minor"}:
            fail(f"state model missing token {tok}")
    serialized=json.dumps(fs)+json.dumps(rs)
    for tok in ["finding","author_query","coverage_gap","Critical","Major","Moderate","Minor","resolved","partially_resolved","persistent","reclassified","not_reassessable","no_longer_material"]:
        if tok not in serialized: fail(f"schema registry missing state {tok}")
    ok("core state vocabulary is represented in schemas/state model")

def package_safety_check() -> None:
    files=[p for p in ROOT.rglob("*") if p.is_file()]
    if len(files)>MAX_FILE_COUNT: fail(f"file count {len(files)} exceeds {MAX_FILE_COUNT}")
    symlinks=[str(p.relative_to(ROOT)) for p in ROOT.rglob("*") if p.is_symlink()]
    if symlinks: fail(f"symlinks not allowed in release bundle: {symlinks}")
    too_large=[str(p.relative_to(ROOT)) for p in files if p.stat().st_size>MAX_SUPPORT_FILE]
    if too_large: fail(f"supporting files exceed 25 MiB: {too_large}")
    ok(f"package limits safe: {len(files)} files, no symlinks")

def manifest_check() -> None:
    manifest=ROOT/"manifest.txt"
    if not manifest.exists(): fail("manifest.txt missing")
    listed=[x.strip() for x in manifest.read_text(encoding="utf-8").splitlines() if x.strip()]
    actual=sorted(str(p.relative_to(ROOT)).replace("\\","/") for p in ROOT.rglob("*") if p.is_file() and "__pycache__" not in p.parts)
    if sorted(listed)!=actual:
        missing=sorted(set(actual)-set(listed)); extra=sorted(set(listed)-set(actual))
        fail(f"manifest mismatch; unlisted={missing}; missing_files={extra}")
    if len(listed)!=len(set(listed)): fail("manifest contains duplicate entries")
    ok(f"manifest covers {len(actual)} files")

def main() -> None:
    skill_frontmatter_check(); public_repo_check(); github_metadata_check(); version_check(); agent_metadata_check(); schema_check(); yaml_check(); local_reference_check(); state_schema_check(); package_safety_check(); manifest_check()
    print("ALL RELEASE VALIDATIONS PASSED")

if __name__=="__main__":
    main()
