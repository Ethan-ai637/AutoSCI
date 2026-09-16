#!/usr/bin/env python3
import argparse, json, re, sys
from pathlib import Path

REQUIRED = ["message", "claims", "entities", "relations", "required_labels", "invariants", "forbidden_inferences", "target", "style_intent"]
REL_TYPES = {"flow","causes","depends_on","contains","maps_to","compares_with","feeds_back","precedes","shares"}
PRIORITIES = {"core","supporting","optional"}
SUPPORT = {"direct","inferred","user_provided"}

def load(path): return json.loads(Path(path).read_text(encoding="utf-8"))
def schema_at_least(data, major=1, minor=3):
    try:
        m=re.match(r"(\d+)\.(\d+)",str(data.get("schema_version","0.0")))
        return bool(m and (int(m.group(1)),int(m.group(2))) >= (major,minor))
    except: return False

def main():
    ap=argparse.ArgumentParser(description="Validate scientific figure semantic spec")
    ap.add_argument("spec"); args=ap.parse_args()
    try: data=load(args.spec)
    except Exception as e: print(f"ERROR: cannot read JSON: {e}"); return 2
    errors=[]; warnings=[]; strict=schema_at_least(data,1,3); v14=schema_at_least(data,1,4); v15=schema_at_least(data,1,5); v16=schema_at_least(data,1,6); v17=schema_at_least(data,1,7)
    for k in REQUIRED:
        if k not in data: errors.append(f"missing top-level field: {k}")
    if not str(data.get("message","")).strip(): errors.append("message must be non-empty")
    status=data.get("semantic_status")
    if status not in (None,"draft","frozen"): errors.append("semantic_status must be draft or frozen")
    if status=="frozen" and not data.get("semantic_lock"): errors.append("frozen spec must contain semantic_lock; run freeze_spec.py")
    if status!="frozen" and data.get("semantic_lock"): warnings.append("semantic_lock present while status is not frozen")

    source=data.get("source",{}) or {}; anchor_ids=[]
    for i,a in enumerate(source.get("anchors",[]) or []):
        if not isinstance(a,dict): errors.append(f"source.anchor[{i}] is not an object"); continue
        if not a.get("id"): errors.append(f"source.anchor[{i}] missing id")
        else: anchor_ids.append(a.get("id"))
        if not str(a.get("locator","")).strip(): errors.append(f"source.anchor[{i}] missing locator")
    if len(anchor_ids)!=len(set(anchor_ids)): errors.append("source anchor IDs must be unique")
    if strict and not anchor_ids: errors.append("schema >=1.3 requires at least one structured source anchor")
    known_anchors=set(anchor_ids)
    source_artifact_ids=[]
    for i,a in enumerate(source.get("artifacts",[]) or []):
        if not isinstance(a,dict): errors.append(f"source.artifacts[{i}] must be object"); continue
        if not a.get("id"): errors.append(f"source.artifacts[{i}] missing id")
        else: source_artifact_ids.append(a.get("id"))
        sha=str(a.get("sha256", ""))
        if sha and not re.fullmatch(r"sha256:[0-9a-fA-F]{64}",sha): errors.append(f"source.artifacts[{i}] invalid sha256 fingerprint")
        if a.get("bytes") is not None:
            try:
                if int(a.get("bytes")) < 0: errors.append(f"source.artifacts[{i}] bytes must be >= 0")
            except Exception: errors.append(f"source.artifacts[{i}] bytes must be integer")
    if len(source_artifact_ids)!=len(set(source_artifact_ids)): errors.append("source artifact IDs must be unique")

    entities=data.get("entities",[]); entity_ids=[]
    for i,x in enumerate(entities):
        if not isinstance(x,dict): errors.append(f"entity[{i}] is not an object"); continue
        if not x.get("id"): errors.append(f"entity[{i}] missing id")
        if not x.get("label"): warnings.append(f"entity[{i}] has empty label")
        entity_ids.append(x.get("id"))
    if len(entity_ids)!=len(set(entity_ids)): errors.append("entity IDs must be unique")
    known=set(entity_ids)

    relations=data.get("relations",[]); relation_ids=[]
    for i,r in enumerate(relations):
        if not isinstance(r,dict): errors.append(f"relation[{i}] is not an object"); continue
        for key in ("id","source","target","type"):
            if not r.get(key): errors.append(f"relation[{i}] missing {key}")
        relation_ids.append(r.get("id"))
        if r.get("source") not in known: errors.append(f"relation[{i}] unknown source {r.get('source')}")
        if r.get("target") not in known: errors.append(f"relation[{i}] unknown target {r.get('target')}")
        if r.get("type") not in REL_TYPES: warnings.append(f"relation[{i}] nonstandard type {r.get('type')}")
    if len(relation_ids)!=len(set(relation_ids)): errors.append("relation IDs must be unique")

    claims=data.get("claims",[]); claim_ids=[]
    for i,c in enumerate(claims):
        if not isinstance(c,dict): errors.append(f"claim[{i}] is not an object"); continue
        cid=c.get("id")
        if not cid: errors.append(f"claim[{i}] missing id")
        if not c.get("text"): errors.append(f"claim[{i}] missing text")
        if c.get("priority") and c.get("priority") not in PRIORITIES: warnings.append(f"claim[{i}] unknown priority {c.get('priority')}")
        if strict:
            if c.get("support") not in SUPPORT: errors.append(f"claim[{i}] support must be one of {sorted(SUPPORT)}")
            refs=c.get("source_anchor_ids")
            if not isinstance(refs,list): errors.append(f"claim[{i}] source_anchor_ids must be a list")
            else:
                for aid in refs:
                    if aid not in known_anchors: errors.append(f"claim[{i}] unknown source anchor {aid}")
        elif not c.get("source_anchor") and not c.get("source_anchor_ids"):
            warnings.append(f"claim[{i}] has no source anchor")
        claim_ids.append(cid)
    if len(claim_ids)!=len(set(claim_ids)): errors.append("claim IDs must be unique")
    if not claims: warnings.append("no claims recorded; confirm figure is intentionally non-claim-based")
    known_claims=set(claim_ids); covered=set()
    for kind, seq in (("entity",entities),("relation",relations)):
        for i,obj in enumerate(seq):
            if not isinstance(obj,dict): continue
            cids=obj.get("claim_ids",[]) or []
            for cid in cids:
                if cid not in known_claims: errors.append(f"{kind}[{i}] references unknown claim {cid}")
                else: covered.add(cid)
    for c in claims:
        if isinstance(c,dict) and c.get("priority","core")=="core" and c.get("id") not in covered:
            warnings.append(f"core claim {c.get('id')} is not mapped to any entity/relation")

    label_ids=[]
    for i,lbl in enumerate(data.get("required_labels",[])):
        if isinstance(lbl,str): warnings.append(f"required_labels[{i}] is a string; object form with id/text is preferred")
        elif isinstance(lbl,dict):
            if not lbl.get("text"): errors.append(f"required_labels[{i}] missing text")
            if lbl.get("id"): label_ids.append(lbl.get("id"))
        else: errors.append(f"required_labels[{i}] must be string or object")
    if len(label_ids)!=len(set(label_ids)): errors.append("required label IDs must be unique")

    panel_ids=[]
    for i,p in enumerate(data.get("panels",[]) or []):
        if not isinstance(p,dict): errors.append(f"panel[{i}] is not an object"); continue
        if not p.get("id"): errors.append(f"panel[{i}] missing id")
        panel_ids.append(p.get("id"))
        for eid in p.get("contains",[]) or []:
            if eid not in known: errors.append(f"panel[{i}] contains unknown entity {eid}")
    if len(panel_ids)!=len(set(panel_ids)): errors.append("panel IDs must be unique")

    for i,e in enumerate(data.get("visual_encodings",[]) or []):
        if not isinstance(e,dict): errors.append(f"visual_encodings[{i}] must be object"); continue
        if strict and (not isinstance(e.get("channels"),list) or not e.get("channels")):
            errors.append(f"visual_encodings[{i}] requires non-empty channels in schema >=1.3")


    notation_ids=[]
    for i,n in enumerate(data.get("notation",[]) or []):
        if not isinstance(n,dict): errors.append(f"notation[{i}] must be object"); continue
        if not n.get("id"): errors.append(f"notation[{i}] missing id")
        else: notation_ids.append(n.get("id"))
        if n.get("required",True) and not str(n.get("required_svg_text","")).strip(): errors.append(f"notation[{i}] required but required_svg_text is empty")
        refs=n.get("source_anchor_ids",[]) or []
        if not isinstance(refs,list): errors.append(f"notation[{i}] source_anchor_ids must be a list")
        else:
            for aid in refs:
                if aid not in known_anchors: errors.append(f"notation[{i}] unknown source anchor {aid}")
    if len(notation_ids)!=len(set(notation_ids)): errors.append("notation IDs must be unique")

    workflow=data.get("workflow",{}) or {}
    if v16:
        if workflow.get("profile") not in ("draft","standard","release"):
            errors.append("schema >=1.6 requires workflow.profile = draft|standard|release")
        if workflow.get("layout_tournament","auto") not in ("auto","on","off"):
            errors.append("workflow.layout_tournament must be auto|on|off")
        if workflow.get("max_refine_rounds") is not None:
            try:
                rounds=int(workflow.get("max_refine_rounds"))
                if not (1 <= rounds <= 5): errors.append("workflow.max_refine_rounds must be between 1 and 5")
            except Exception: errors.append("workflow.max_refine_rounds must be an integer")
    if v17 and workflow.get("orchestration") not in ("deterministic","manual"):
        errors.append("schema >=1.7 requires workflow.orchestration = deterministic|manual")

    qa=data.get("qa",{}) or {}
    if v14:
        if qa.get("geometry_audit") not in ("required","recommended","off"):
            errors.append("schema >=1.4 requires qa.geometry_audit = required|recommended|off")
        for key in ("max_primary_overlap_ratio","relation_endpoint_tolerance"):
            if key not in qa: warnings.append(f"qa.{key} missing; geometry audit will use its default")
    if v15:
        if qa.get("portability_audit") not in ("required","recommended","off"):
            errors.append("schema >=1.5 requires qa.portability_audit = required|recommended|off")
        for key in ("allow_external_resources","allow_embedded_raster","require_generic_font_fallback"):
            if key in qa and not isinstance(qa.get(key),bool): errors.append(f"qa.{key} must be boolean")
    if qa.get("max_primary_overlap_ratio") is not None:
        try:
            x=float(qa["max_primary_overlap_ratio"])
            if not (0 <= x <= 1): errors.append("qa.max_primary_overlap_ratio must be between 0 and 1")
        except Exception: errors.append("qa.max_primary_overlap_ratio must be numeric")
    if qa.get("relation_endpoint_tolerance") is not None:
        try:
            if float(qa["relation_endpoint_tolerance"]) < 0: errors.append("qa.relation_endpoint_tolerance must be >= 0")
        except Exception: errors.append("qa.relation_endpoint_tolerance must be numeric")

    target=data.get("target",{}) or {}; wpx=target.get("target_preview_width_px")
    if wpx is not None:
        try:
            if int(wpx)<200: warnings.append("target_preview_width_px is very small (<200)")
        except Exception: errors.append("target_preview_width_px must be an integer")
    width_in=target.get("width_in"); width_mm=target.get("width_mm")
    if width_in is None and width_mm is None: warnings.append("target physical width missing; target-size point-size audit will be skipped")
    for key,val in (("width_in",width_in),("width_mm",width_mm),("min_text_pt",target.get("min_text_pt"))):
        if val is not None:
            try:
                if float(val)<=0: errors.append(f"target.{key} must be positive")
            except Exception: errors.append(f"target.{key} must be numeric")
    exports=target.get("exports",[]) or []
    if not isinstance(exports,list): errors.append("target.exports must be a list")
    else:
        allowed_exports={"svg","pdf","png"}
        for x in exports:
            if x not in allowed_exports: warnings.append(f"target.exports contains nonstandard format {x!r}")

    for msg in warnings: print("WARN:",msg)
    for msg in errors: print("ERROR:",msg)
    if errors: return 1
    print(f"OK: {args.spec} ({len(entities)} entities, {len(relations)} relations, {len(claims)} claims, schema={data.get('schema_version','?')})")
    return 0
if __name__=="__main__": sys.exit(main())
