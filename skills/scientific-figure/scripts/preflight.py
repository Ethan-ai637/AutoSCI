#!/usr/bin/env python3
import argparse, json, re, subprocess, sys
from pathlib import Path

def schema_tuple(v):
    m=re.match(r"(\d+)\.(\d+)",str(v or "0.0")); return (int(m.group(1)),int(m.group(2))) if m else (0,0)

def resolve_profile(spec, override):
    if override != "auto": return override
    p=((spec.get("workflow") or {}).get("profile"))
    if p: return str(p)
    return "release" if schema_tuple(spec.get("schema_version")) < (1,6) else "standard"

def run(label, cmd):
    print(f"\n== {label} ==")
    return subprocess.run(cmd).returncode

def main():
    ap=argparse.ArgumentParser(description="Run profile-aware deterministic scientific-figure preflight checks")
    ap.add_argument("spec"); ap.add_argument("svg")
    ap.add_argument("--profile",choices=["auto","draft","standard","release"],default="auto")
    args=ap.parse_args(); here=Path(__file__).resolve().parent
    try: spec=json.loads(Path(args.spec).read_text(encoding="utf-8"))
    except Exception: spec={}
    profile=resolve_profile(spec,args.profile)
    print(f"PREFLIGHT PROFILE: {profile}")
    checks=[
        ("PROFILE POLICY",[sys.executable,str(here/"profile_audit.py"),args.spec,"--profile",profile]),
        ("SPEC VALIDATION",[sys.executable,str(here/"validate_spec.py"),args.spec]),
        ("SOURCE GROUNDING",[sys.executable,str(here/"source_audit.py"),args.spec]),
    ]
    if spec.get("semantic_status")=="frozen":
        checks.append(("SEMANTIC LOCK",[sys.executable,str(here/"freeze_spec.py"),args.spec,"--check"]))
    checks += [("SVG LINT",[sys.executable,str(here/"svg_lint.py"),args.svg]),
               ("SEMANTIC TRACEABILITY",[sys.executable,str(here/"semantic_audit.py"),args.spec,args.svg])]
    if spec.get("notation"):
        checks.append(("NOTATION FIDELITY",[sys.executable,str(here/"notation_audit.py"),args.spec,args.svg]))
    if profile in {"standard","release"}:
        checks += [("GEOMETRY AUDIT",[sys.executable,str(here/"geometry_audit.py"),args.spec,args.svg]),
                   ("TARGET LEGIBILITY",[sys.executable,str(here/"target_legibility.py"),args.spec,args.svg])]
    if profile=="release":
        checks += [("PUBLICATION ROBUSTNESS",[sys.executable,str(here/"robustness_audit.py"),args.spec]),
                   ("PORTABILITY AUDIT",[sys.executable,str(here/"portability_audit.py"),args.spec,args.svg])]
    failed=[]
    for label,cmd in checks:
        code=run(label,cmd)
        if code!=0: failed.append((label,code))
    if failed:
        print(f"\nPREFLIGHT ({profile}): FAIL")
        for label,code in failed: print(f"- {label}: exit {code}")
        return 1
    print(f"\nPREFLIGHT ({profile}): PASS")
    return 0
if __name__=="__main__": raise SystemExit(main())
