#!/usr/bin/env python3
import argparse, json, re, sys
from pathlib import Path

SUPPORT={"direct","inferred","user_provided"}
PRIORITIES={"core","supporting","optional"}

def version_num(v):
    try:
        parts=str(v).split(".")
        return tuple(int(re.match(r"\d+",p).group()) if re.match(r"\d+",p) else 0 for p in parts[:2])
    except Exception:
        return (0,0)

def main():
    ap=argparse.ArgumentParser(description="Audit claim-to-source grounding in a scientific figure spec")
    ap.add_argument("spec"); args=ap.parse_args()
    try: spec=json.loads(Path(args.spec).read_text(encoding="utf-8"))
    except Exception as e: print(f"ERROR: cannot read spec: {e}"); return 2

    strict=version_num(spec.get("schema_version","0")) >= (1,3)
    errors=[]; warnings=[]
    source=spec.get("source",{}) or {}
    anchors=source.get("anchors",[]) or []
    anchor_ids=[]
    for i,a in enumerate(anchors):
        if not isinstance(a,dict): errors.append(f"source.anchor[{i}] is not an object"); continue
        aid=a.get("id")
        if not aid: errors.append(f"source.anchor[{i}] missing id")
        else: anchor_ids.append(aid)
        if not str(a.get("locator","")).strip(): errors.append(f"source.anchor[{i}] missing locator")
        if not str(a.get("evidence_summary","")).strip(): warnings.append(f"source.anchor[{i}] has no evidence_summary")
    if len(anchor_ids)!=len(set(anchor_ids)): errors.append("source anchor IDs must be unique")
    known=set(anchor_ids)
    if strict and not anchors: errors.append("schema >=1.3 requires structured source.anchors")

    claims=spec.get("claims",[]) or []
    used=set()
    for i,c in enumerate(claims):
        if not isinstance(c,dict): continue
        cid=c.get("id") or f"claim[{i}]"
        support=c.get("support")
        if strict and support not in SUPPORT: errors.append(f"{cid} support must be one of {sorted(SUPPORT)}")
        elif support and support not in SUPPORT: warnings.append(f"{cid} has unknown support={support!r}")
        refs=c.get("source_anchor_ids")
        # Backward compatibility with v1.2 free-text anchor.
        if refs is None:
            if c.get("source_anchor"):
                warnings.append(f"{cid} uses legacy free-text source_anchor; migrate to source_anchor_ids")
                refs=[]
            else:
                refs=[]
        if not isinstance(refs,list): errors.append(f"{cid} source_anchor_ids must be a list"); refs=[]
        for aid in refs:
            if aid not in known: errors.append(f"{cid} references unknown source anchor {aid!r}")
            else: used.add(aid)

        priority=c.get("priority","core")
        if priority not in PRIORITIES: warnings.append(f"{cid} unknown priority {priority!r}")
        if support in ("direct","user_provided") and strict and not refs:
            errors.append(f"{cid} is {support} but has no source_anchor_ids")
        if support=="inferred":
            if priority=="core": errors.append(f"{cid} is a core claim but marked inferred; obtain direct support or demote/remove it")
            if not refs: warnings.append(f"{cid} is inferred without nearby source anchors; verify inference explicitly")

    # Notation/equation entries can legitimately consume a source anchor without a separate claim.
    for n in spec.get("notation",[]) or []:
        if not isinstance(n,dict): continue
        for aid in n.get("source_anchor_ids",[]) or []:
            if aid in known: used.add(aid)
    for aid in sorted(known-used): warnings.append(f"source anchor {aid} is currently unused by claims/notation")
    for w in warnings: print("WARN:",w)
    for e in errors: print("ERROR:",e)
    if errors: return 1
    print(f"OK: source grounding audit passed ({len(claims)} claims, {len(anchors)} anchors)")
    return 0

if __name__=="__main__": sys.exit(main())
