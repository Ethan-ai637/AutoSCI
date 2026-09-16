#!/usr/bin/env python3
import argparse, re, sys, xml.etree.ElementTree as ET
from pathlib import Path

BAD_TEXT_RE = re.compile(r"\b(lorem ipsum|todo|placeholder|replace:)\b", re.I)
URL_RE = re.compile(r"^(?:https?:)?//", re.I)

def local(tag): return tag.split('}',1)[-1]

def parse_font_size(el):
    raw=el.get("font-size")
    if raw:
        m=re.match(r"\s*([0-9.]+)", raw)
        if m:
            try: return float(m.group(1))
            except: pass
    style=el.get("style","")
    m=re.search(r"font-size\s*:\s*([0-9.]+)",style)
    if m:
        try: return float(m.group(1))
        except: pass
    return None

def main():
    ap=argparse.ArgumentParser(description="Lightweight structural lint for scientific SVG figures")
    ap.add_argument("svg")
    args=ap.parse_args(); p=Path(args.svg)
    try: root=ET.fromstring(p.read_text(encoding="utf-8"))
    except Exception as e: print(f"ERROR: invalid XML/SVG: {e}"); return 2
    errors=[]; warnings=[]
    if local(root.tag)!="svg": errors.append("root element is not <svg>")
    if not root.get("viewBox"): warnings.append("missing viewBox; responsive/vector scaling may be fragile")
    text_nodes=[]; rects=0; filters=0; images=0; foreign=0; external_images=0
    ids=set(); dup=set(); marker_ends=0
    for el in root.iter():
        tag=local(el.tag); eid=el.get("id")
        if eid:
            if eid in ids: dup.add(eid)
            ids.add(eid)
        if tag=="text":
            txt="".join(el.itertext()).strip(); text_nodes.append(txt)
            if BAD_TEXT_RE.search(txt): warnings.append(f"placeholder-like text found: {txt[:60]!r}")
            fs=parse_font_size(el)
            if fs is not None and fs < 9: warnings.append(f"very small text ({fs}px): {txt[:50]!r}")
        elif tag=="rect": rects+=1
        elif tag=="filter": filters+=1
        elif tag=="image":
            images+=1
            href=el.get("href") or el.get("{http://www.w3.org/1999/xlink}href") or ""
            if URL_RE.match(href): external_images+=1
        elif tag=="foreignObject": foreign+=1
        if el.get("marker-end"): marker_ends+=1
    if dup: errors.append("duplicate element IDs: "+", ".join(sorted(dup)))
    if not text_nodes: warnings.append("no SVG text nodes found; ordinary labels may be non-editable paths")
    if rects > max(12, len(text_nodes)*0.8): warnings.append(f"box-soup risk: {rects} rectangles for {len(text_nodes)} text nodes")
    if filters>3: warnings.append(f"decorative filter risk: {filters} filters")
    if images>0: warnings.append(f"contains {images} raster image element(s); verify resolution and provenance")
    if external_images>0: errors.append(f"contains {external_images} externally linked image(s); embed/localize assets for reliable export")
    if foreign>0: warnings.append(f"contains {foreign} foreignObject element(s); portability across renderers may be fragile")
    for w in warnings: print("WARN:",w)
    for e in errors: print("ERROR:",e)
    if errors: return 1
    print(f"OK: parsed SVG; text={len(text_nodes)}, rects={rects}, raster_images={images}, filters={filters}, arrow_markers={marker_ends}")
    return 0

if __name__=="__main__": sys.exit(main())
