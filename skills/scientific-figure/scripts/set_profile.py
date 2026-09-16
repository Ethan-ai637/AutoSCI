#!/usr/bin/env python3
import argparse, json, sys
from pathlib import Path

PROFILES={"draft","standard","release"}

def main():
    ap=argparse.ArgumentParser(description="Set scientific-figure execution profile; changes QA policy only, never scientific semantics")
    ap.add_argument("spec"); ap.add_argument("profile",choices=sorted(PROFILES)); args=ap.parse_args()
    p=Path(args.spec)
    try: spec=json.loads(p.read_text(encoding="utf-8"))
    except Exception as e: print(f"ERROR: cannot read spec: {e}"); return 2
    spec.setdefault("workflow",{})["profile"]=args.profile
    qa=spec.setdefault("qa",{})
    if args.profile=="draft":
        qa["geometry_audit"]="recommended"; qa["portability_audit"]="off"
    elif args.profile=="standard":
        qa["geometry_audit"]="required"; qa["portability_audit"]="recommended"
        qa.setdefault("allow_external_resources",False)
    else:
        qa["geometry_audit"]="required"; qa["portability_audit"]="required"
        qa["allow_external_resources"]=False; qa["require_generic_font_fallback"]=True
    p.write_text(json.dumps(spec,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(f"OK: workflow profile -> {args.profile} (semantic lock untouched)")
    return 0
if __name__=="__main__": raise SystemExit(main())
