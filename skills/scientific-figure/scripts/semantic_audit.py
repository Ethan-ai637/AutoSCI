#!/usr/bin/env python3
import argparse, json, re, sys, xml.etree.ElementTree as ET
from pathlib import Path

DIRECTED={"flow","causes","depends_on","maps_to","feeds_back","precedes"}
def local(tag): return tag.split('}',1)[-1]
def norm(s): return re.sub(r"\s+", " ", s or "").strip()
def load_spec(path): return json.loads(Path(path).read_text(encoding="utf-8"))

def descendants(el): return list(el.iter())

def main():
    ap=argparse.ArgumentParser(description="Audit spec-to-SVG semantic traceability and required labels")
    ap.add_argument("spec"); ap.add_argument("svg"); args=ap.parse_args()
    try: spec=load_spec(args.spec)
    except Exception as e: print(f"ERROR: cannot read spec: {e}"); return 2
    try: root=ET.fromstring(Path(args.svg).read_text(encoding="utf-8"))
    except Exception as e: print(f"ERROR: cannot parse SVG: {e}"); return 2

    errors=[]; warnings=[]
    elements=list(root.iter()); svg_ids={el.get("id") for el in elements if el.get("id")}
    entity_el={}; relation_el={}; panel_el={}
    for el in elements:
        if el.get("data-entity-id"): entity_el[el.get("data-entity-id")]=el
        if el.get("data-relation-id"): relation_el[el.get("data-relation-id")]=el
        if el.get("data-panel-id"): panel_el[el.get("data-panel-id")]=el
    for el in elements:
        eid=el.get("id","")
        if eid.startswith("entity-") and eid[7:] not in entity_el: entity_el[eid[7:]]=el
        if eid.startswith("relation-") and eid[9:] not in relation_el: relation_el[eid[9:]]=el
        if eid.startswith("panel-") and eid[6:] not in panel_el: panel_el[eid[6:]]=el

    text=" ".join(norm("".join(el.itertext())) for el in elements if local(el.tag)=="text")
    text_norm=norm(text)

    for e in spec.get("entities",[]):
        eid=e.get("id")
        if eid and eid not in entity_el: errors.append(f"missing traceable SVG group for entity {eid}")

    for r in spec.get("relations",[]):
        rid=r.get("id"); el=relation_el.get(rid)
        if el is None:
            errors.append(f"missing traceable SVG group for relation {rid}"); continue
        svg_type=el.get("data-relation-type")
        if svg_type and svg_type!=r.get("type"): errors.append(f"relation {rid} SVG type {svg_type!r} != spec type {r.get('type')!r}")
        src=el.get("data-source-id"); tgt=el.get("data-target-id")
        if src is None: warnings.append(f"relation {rid} lacks data-source-id; endpoint traceability is weaker")
        elif src!=r.get("source"): errors.append(f"relation {rid} SVG source {src!r} != spec source {r.get('source')!r}")
        if tgt is None: warnings.append(f"relation {rid} lacks data-target-id; endpoint traceability is weaker")
        elif tgt!=r.get("target"): errors.append(f"relation {rid} SVG target {tgt!r} != spec target {r.get('target')!r}")
        if r.get("type") in DIRECTED:
            has_arrow=any(x.get("marker-end") or x.get("marker-start") for x in descendants(el))
            if not has_arrow: warnings.append(f"directed relation {rid} has no SVG marker arrowhead; visually verify direction")

    for p in spec.get("panels",[]) or []:
        pid=p.get("id")
        if pid and pid not in panel_el: warnings.append(f"panel {pid} has no traceable SVG group")

    for i,lbl in enumerate(spec.get("required_labels",[])):
        if isinstance(lbl,str): label=lbl; case=True
        else: label=lbl.get("text",""); case=lbl.get("case_sensitive",True)
        if not label: continue
        hay=text_norm if case else text_norm.lower(); needle=norm(label) if case else norm(label).lower()
        if needle not in hay: errors.append(f"required label not found in SVG text: {label!r}")

    for w in warnings: print("WARN:",w)
    for e in errors: print("ERROR:",e)
    if errors: return 1
    print(f"OK: semantic audit passed ({len(spec.get('entities',[]))} entities, {len(spec.get('relations',[]))} relations)")
    return 0
if __name__=="__main__": sys.exit(main())
