#!/usr/bin/env python3
import argparse, json, math, re, sys, xml.etree.ElementTree as ET
from pathlib import Path

DIRECTED={"flow","causes","depends_on","maps_to","feeds_back","precedes"}
NUM_RE=re.compile(r"[-+]?(?:\d*\.\d+|\d+\.?)(?:[eE][-+]?\d+)?")
CMD_RE=re.compile(r"[AaCcHhLlMmQqSsTtVvZz]|[-+]?(?:\d*\.\d+|\d+\.?)(?:[eE][-+]?\d+)?")
ARITY={"M":2,"L":2,"H":1,"V":1,"C":6,"S":4,"Q":4,"T":2,"A":7,"Z":0}

def local(tag): return tag.split('}',1)[-1]
def fnum(x):
    try: return float(x)
    except: return None

def parse_vb(root):
    raw=root.get("viewBox")
    if not raw: return None
    vals=[fnum(x) for x in re.split(r"[ ,]+",raw.strip()) if x]
    return tuple(vals) if len(vals)==4 and all(v is not None for v in vals) else None

def parse_bounds(raw):
    vals=[fnum(x) for x in re.split(r"[ ,]+",raw.strip()) if x] if raw else []
    if len(vals)!=4 or any(v is None for v in vals) or vals[2] <= 0 or vals[3] <= 0: return None
    return tuple(vals)

def dist_point_rect(p,b):
    x,y=p; bx,by,bw,bh=b; rx=bx+bw; ry=by+bh
    dx=max(bx-x,0,x-rx); dy=max(by-y,0,y-ry)
    return math.hypot(dx,dy)

def overlap_ratio(a,b):
    ax,ay,aw,ah=a; bx,by,bw,bh=b
    iw=max(0,min(ax+aw,bx+bw)-max(ax,bx)); ih=max(0,min(ay+ah,by+bh)-max(ay,by))
    inter=iw*ih
    return inter/min(aw*ah,bw*bh) if min(aw*ah,bw*bh)>0 else 0

def route_line(el):
    vals=[fnum(el.get(k)) for k in ("x1","y1","x2","y2")]
    return ((vals[0],vals[1]),(vals[2],vals[3])) if all(v is not None for v in vals) else None

def route_poly(el):
    vals=[float(x) for x in NUM_RE.findall(el.get("points","") or "")]
    if len(vals)>=4 and len(vals)%2==0: return ((vals[0],vals[1]),(vals[-2],vals[-1]))
    return None

def route_path(el):
    toks=CMD_RE.findall(el.get("d","") or "")
    if not toks: return None
    i=0; cmd=None; cur=(0.0,0.0); start=None; end=None; sub_start=None
    def iscmd(t): return len(t)==1 and t.isalpha()
    try:
        while i<len(toks):
            if iscmd(toks[i]): cmd=toks[i]; i+=1
            if cmd is None: return None
            up=cmd.upper(); rel=cmd.islower(); n=ARITY.get(up)
            if n is None: return None
            if up=="Z":
                if sub_start is not None: cur=sub_start; end=cur
                cmd=None; continue
            if i+n>len(toks) or (i<len(toks) and iscmd(toks[i])): continue
            vals=[float(toks[i+j]) for j in range(n)]; i+=n
            x,y=cur
            if up in ("M","L","T"):
                nx,ny=vals[-2],vals[-1]
            elif up=="H": nx,ny=vals[-1],y
            elif up=="V": nx,ny=x,vals[-1]
            elif up in ("C","S","Q"): nx,ny=vals[-2],vals[-1]
            elif up=="A": nx,ny=vals[-2],vals[-1]
            else: return None
            if rel: nx,ny=nx+x,ny+y
            cur=(nx,ny)
            if start is None: start=cur
            if up=="M" and sub_start is None: sub_start=cur
            end=cur
            if up=="M": cmd="l" if rel else "L"
        return (start,end) if start is not None and end is not None else None
    except Exception:
        return None

def route_endpoints(group):
    preferred=[]; fallback=[]
    for el in group.iter():
        tag=local(el.tag)
        if tag not in ("path","line","polyline"): continue
        dest=preferred if str(el.get("data-route","")).lower() in ("1","true","yes") else fallback
        dest.append(el)
    for el in preferred+fallback:
        tag=local(el.tag)
        ep=route_line(el) if tag=="line" else route_poly(el) if tag=="polyline" else route_path(el)
        if ep: return ep
    return None

def main():
    ap=argparse.ArgumentParser(description="Audit semantic geometry: bounds, primary overlap, and relation endpoint proximity")
    ap.add_argument("spec"); ap.add_argument("svg"); args=ap.parse_args()
    try: spec=json.loads(Path(args.spec).read_text(encoding="utf-8"))
    except Exception as e: print(f"ERROR: cannot read spec: {e}"); return 2
    try: root=ET.fromstring(Path(args.svg).read_text(encoding="utf-8"))
    except Exception as e: print(f"ERROR: cannot parse SVG: {e}"); return 2
    qa=spec.get("qa",{}) or {}; policy=str(qa.get("geometry_audit","recommended"))
    hard=policy=="required"
    tol=float(qa.get("relation_endpoint_tolerance",28))
    max_overlap=float(qa.get("max_primary_overlap_ratio",0.15))
    vb=parse_vb(root)
    errors=[]; warnings=[]
    if not vb:
        (errors if hard else warnings).append("SVG viewBox required for geometry audit")
    entities={e.get("id"):e for e in spec.get("entities",[]) if isinstance(e,dict) and e.get("id")}
    relations={r.get("id"):r for r in spec.get("relations",[]) if isinstance(r,dict) and r.get("id")}
    egrp={}; rgrp={}
    for el in root.iter():
        if el.get("data-entity-id"): egrp[el.get("data-entity-id")]=el
        if el.get("data-relation-id"): rgrp[el.get("data-relation-id")]=el
    bounds={}
    for eid,e in entities.items():
        g=egrp.get(eid); b=parse_bounds(g.get("data-bounds")) if g is not None else None
        if not b:
            msg=f"entity {eid} lacks valid root-coordinate data-bounds='x y w h'"
            if hard and e.get("importance","primary")=="primary": errors.append(msg)
            else: warnings.append(msg)
            continue
        bounds[eid]=b
        if vb:
            vx,vy,vw,vh=vb; x,y,w,h=b
            if x < vx-1e-6 or y < vy-1e-6 or x+w > vx+vw+1e-6 or y+h > vy+vh+1e-6:
                errors.append(f"entity {eid} data-bounds extends outside viewBox: {b}")
    contained=set()
    for r in relations.values():
        if r.get("type")=="contains": contained.add(frozenset((r.get("source"),r.get("target"))))
    prim=[eid for eid,e in entities.items() if e.get("importance","primary")=="primary" and eid in bounds and e.get("type") not in ("group","annotation")]
    for i,a in enumerate(prim):
        for b in prim[i+1:]:
            if frozenset((a,b)) in contained: continue
            ratio=overlap_ratio(bounds[a],bounds[b])
            if ratio>max_overlap:
                errors.append(f"primary entities {a}/{b} overlap by {ratio:.1%} of smaller semantic bound (limit {max_overlap:.1%})")
    for rid,r in relations.items():
        g=rgrp.get(rid)
        if g is None: continue
        ep=route_endpoints(g)
        if not ep:
            (errors if hard else warnings).append(f"relation {rid} has no parseable path/line/polyline route; add data-route='true' to the visible connector")
            continue
        src=r.get("source"); tgt=r.get("target")
        if src not in bounds or tgt not in bounds:
            continue
        dss=dist_point_rect(ep[0],bounds[src]); dst=dist_point_rect(ep[1],bounds[tgt])
        if r.get("type") not in DIRECTED:
            alt=dist_point_rect(ep[0],bounds[tgt])+dist_point_rect(ep[1],bounds[src])
            cur=dss+dst
            if alt<cur: dss,dst=dist_point_rect(ep[1],bounds[src]),dist_point_rect(ep[0],bounds[tgt])
        if dss>tol: errors.append(f"relation {rid} route start is {dss:.1f} units from source {src} bounds (tolerance {tol:g})")
        if dst>tol: errors.append(f"relation {rid} route end is {dst:.1f} units from target {tgt} bounds (tolerance {tol:g})")
    for w in warnings: print("WARN:",w)
    for e in errors: print("ERROR:",e)
    if errors: return 1
    print(f"OK: geometry audit passed ({len(bounds)}/{len(entities)} entity bounds, {len(relations)} relations; policy={policy})")
    return 0
if __name__=="__main__": sys.exit(main())
