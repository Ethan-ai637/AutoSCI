#!/usr/bin/env python3
import argparse, json, re, sys, xml.etree.ElementTree as ET
from pathlib import Path

def local(tag): return tag.split('}',1)[-1]
def norm(s): return re.sub(r"\s+"," ",s or "").strip()
def main():
    ap=argparse.ArgumentParser(description="Audit canonical mathematical/scientific notation against editable SVG text")
    ap.add_argument("spec"); ap.add_argument("svg"); args=ap.parse_args()
    try: spec=json.loads(Path(args.spec).read_text(encoding="utf-8"))
    except Exception as e: print(f"ERROR: cannot read spec: {e}"); return 2
    try: root=ET.fromstring(Path(args.svg).read_text(encoding="utf-8"))
    except Exception as e: print(f"ERROR: cannot parse SVG: {e}"); return 2
    texts=[norm("".join(el.itertext())) for el in root.iter() if local(el.tag)=="text"]
    hay=norm(" ".join(texts)); errors=[]; warnings=[]
    anchors={a.get("id") for a in (spec.get("source",{}) or {}).get("anchors",[]) if isinstance(a,dict)}
    for i,n in enumerate(spec.get("notation",[]) or []):
        if not isinstance(n,dict): errors.append(f"notation[{i}] must be object"); continue
        nid=n.get("id",f"notation[{i}]"); svg_text=n.get("required_svg_text","")
        refs=n.get("source_anchor_ids",[]) or []
        for aid in refs:
            if aid not in anchors: errors.append(f"{nid} references unknown source anchor {aid}")
        if n.get("required",True):
            if not svg_text: errors.append(f"{nid} required but required_svg_text is empty")
            elif norm(svg_text) not in hay: errors.append(f"{nid} canonical notation not found in editable SVG text: {svg_text!r}")
        if n.get("kind") in ("equation","symbol") and not refs:
            warnings.append(f"{nid} has no source anchor; exact notation provenance is weak")
    for w in warnings: print("WARN:",w)
    for e in errors: print("ERROR:",e)
    if errors: return 1
    print(f"OK: notation audit passed ({len(spec.get('notation',[]) or [])} canonical items)")
    return 0
if __name__=="__main__": sys.exit(main())
