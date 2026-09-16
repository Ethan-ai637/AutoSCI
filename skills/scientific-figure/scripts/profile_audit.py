#!/usr/bin/env python3
import argparse, json, re, sys
from pathlib import Path

PROFILES={"draft","standard","release"}

def schema_tuple(v):
    m=re.match(r"(\d+)\.(\d+)",str(v or "0.0"))
    return (int(m.group(1)),int(m.group(2))) if m else (0,0)

def resolve(spec, override):
    if override and override != "auto": return override
    p=((spec.get("workflow") or {}).get("profile"))
    if p: return str(p)
    # Preserve v1.5-and-earlier behavior: the old preflight was effectively release-strict.
    return "release" if schema_tuple(spec.get("schema_version")) < (1,6) else "standard"

def main():
    ap=argparse.ArgumentParser(description="Audit workflow/profile requirements without changing scientific semantics")
    ap.add_argument("spec")
    ap.add_argument("--profile",choices=["auto",*sorted(PROFILES)],default="auto")
    args=ap.parse_args()
    try: spec=json.loads(Path(args.spec).read_text(encoding="utf-8"))
    except Exception as e: print(f"ERROR: cannot read spec: {e}"); return 2
    profile=resolve(spec,args.profile)
    errors=[]; warnings=[]
    qa=spec.get("qa",{}) or {}; target=spec.get("target",{}) or {}; source=spec.get("source",{}) or {}
    if profile in {"standard","release"}:
        if spec.get("semantic_status") != "frozen" or not spec.get("semantic_lock"):
            errors.append(f"{profile} profile requires frozen semantics with semantic_lock")
        if qa.get("geometry_audit") != "required":
            errors.append(f"{profile} profile requires qa.geometry_audit='required'")
        if target.get("width_in") is None and target.get("width_mm") is None:
            errors.append(f"{profile} profile requires target.width_in or target.width_mm for physical-size QA")
        if target.get("min_text_pt") is None:
            errors.append(f"{profile} profile requires target.min_text_pt")
    if profile == "release":
        if qa.get("portability_audit") != "required": errors.append("release profile requires qa.portability_audit='required'")
        if qa.get("allow_external_resources") is not False: errors.append("release profile requires qa.allow_external_resources=false")
        if qa.get("require_generic_font_fallback") is not True:
            warnings.append("release profile recommends qa.require_generic_font_fallback=true for cross-machine SVG portability")
        kind=str(source.get("kind","")).lower()
        if kind in {"paper","code","data"} and not (source.get("artifacts") or []):
            warnings.append("release profile: authoritative local source has no file fingerprint; add one when practical")
    print(f"PROFILE: {profile}")
    for w in warnings: print("WARN:",w)
    for e in errors: print("ERROR:",e)
    if errors: return 1
    print("OK: workflow profile requirements satisfied")
    return 0
if __name__=="__main__": raise SystemExit(main())
