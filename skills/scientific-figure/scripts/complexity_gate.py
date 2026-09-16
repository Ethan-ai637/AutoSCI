#!/usr/bin/env python3
import argparse, json, sys
from pathlib import Path

def main():
    ap=argparse.ArgumentParser(description="Estimate figure composition complexity and recommend layout tournament when useful")
    ap.add_argument("spec"); ap.add_argument("--profile",choices=["auto","draft","standard","release"],default="auto"); args=ap.parse_args()
    try: spec=json.loads(Path(args.spec).read_text(encoding="utf-8"))
    except Exception as e: print(f"ERROR: cannot read spec: {e}"); return 2
    profile=args.profile if args.profile!="auto" else ((spec.get("workflow") or {}).get("profile") or "standard")
    ne=len(spec.get("entities",[]) or [])
    nr=len(spec.get("relations",[]) or [])
    np=len(spec.get("panels",[]) or [])
    core=sum(1 for c in (spec.get("claims",[]) or []) if isinstance(c,dict) and c.get("priority","core")=="core")
    feedback=sum(1 for r in (spec.get("relations",[]) or []) if isinstance(r,dict) and r.get("type") in ("feeds_back","contains","compares_with"))
    score=ne + nr*0.75 + max(0,np-1)*2 + max(0,core-2)*0.75 + feedback*0.75
    if score >= 14:
        level="high"
    elif score >= 8:
        level="medium"
    else:
        level="low"
    mode=((spec.get("workflow") or {}).get("layout_tournament") or "auto")
    if mode=="off": rec="Layout tournament disabled by workflow; use one deliberate macro-layout and document the reason."
    elif mode=="on": rec="Generate 2–3 low-fidelity candidates before detailed SVG work."
    elif profile=="draft": rec="Draft profile: use one layout unless the first macro-structure is clearly ambiguous."
    elif profile=="release" and level in {"medium","high"}: rec="Release profile: compare 2 candidates for medium complexity and 3 for high complexity."
    elif level=="high": rec="Generate 2–3 low-fidelity candidates before detailed SVG work."
    elif level=="medium": rec="Tournament is optional; compare 2 candidates only when competing scientific grammars are plausible."
    else: rec="A single planned layout is sufficient; do not create variants without a reason."
    print(f"COMPLEXITY: {level} (score={score:.2f}; entities={ne}, relations={nr}, panels={np}, core_claims={core}; profile={profile})")
    print("RECOMMENDATION:",rec)
    return 0
if __name__=="__main__": sys.exit(main())
