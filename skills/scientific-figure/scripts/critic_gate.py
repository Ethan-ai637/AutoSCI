#!/usr/bin/env python3
import argparse, json, sys
from pathlib import Path

def num(d,*keys):
    cur=d
    for k in keys:
        if not isinstance(cur,dict): return None
        cur=cur.get(k)
    try: return float(cur)
    except Exception: return None

def main():
    ap=argparse.ArgumentParser(description="Deterministically gate a completed scientific-figure critic record")
    ap.add_argument("critic"); ap.add_argument("--profile",choices=["draft","standard","release"],default="standard"); ap.add_argument("--spec",default=None)
    a=ap.parse_args()
    try: c=json.loads(Path(a.critic).read_text(encoding="utf-8"))
    except Exception as e: print(f"ERROR: cannot read critic: {e}"); return 2
    errors=[]
    if c.get("status") != "complete": errors.append("critic.status must be 'complete' before it can pass")
    sa=c.get("semantic_audit") or {}; va=c.get("visual_audit") or {}
    for section,name in ((sa,"semantic_audit"),(va,"visual_audit")):
        blockers=section.get("blockers")
        if not isinstance(blockers,list): errors.append(f"{name}.blockers must be a list")
        elif blockers: errors.append(f"{name}.blockers is not empty")
    unsupported=((sa.get("source_grounding") or {}).get("unsupported_visible_claims") or [])
    inferred=((sa.get("source_grounding") or {}).get("inferred_core_claims") or [])
    regress=((c.get("regression_check") or {}).get("new_regressions") or [])
    if unsupported: errors.append("unsupported visible claims remain")
    if inferred: errors.append("inferred core claims remain")
    if regress: errors.append("new regressions remain")
    sc=num(c,"semantic_audit","scores","semantic_correctness")
    co=num(c,"semantic_audit","scores","completeness")
    le=num(c,"visual_audit","scores","legibility")
    pr=num(c,"visual_audit","scores","publication_readiness")
    required=[("semantic_correctness",sc,9.0)]
    if a.profile in {"standard","release"}: required += [("completeness",co,8.0),("legibility",le,7.0 if a.profile=="standard" else 8.0)]
    if a.profile=="release": required += [("publication_readiness",pr,8.0)]
    for name,val,thr in required:
        if val is None: errors.append(f"missing numeric score: {name}")
        elif val < thr: errors.append(f"{name}={val:g} < required {thr:g}")
    if a.spec:
        try: spec=json.loads(Path(a.spec).read_text(encoding="utf-8"))
        except Exception as e: print(f"ERROR: cannot read spec: {e}"); return 2
        if a.profile=="release" and (spec.get("target") or {}).get("grayscale_safe") is True:
            if (va.get("robustness") or {}).get("grayscale_checked") is not True:
                errors.append("release target is grayscale_safe but critic did not record grayscale_checked=true")
    for e in errors: print("ERROR:",e)
    if errors: return 1
    print(f"OK: critic hard gates passed ({a.profile})")
    return 0
if __name__=="__main__": raise SystemExit(main())
