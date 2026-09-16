#!/usr/bin/env python3
import argparse, json, re, sys, xml.etree.ElementTree as ET
from pathlib import Path

NUM=re.compile(r"^\s*([0-9]*\.?[0-9]+)")

def local(tag): return tag.split('}',1)[-1]

def number(raw):
    if raw is None: return None
    m=NUM.match(str(raw))
    return float(m.group(1)) if m else None

def style_font(style):
    m=re.search(r"(?:^|;)\s*font-size\s*:\s*([0-9]*\.?[0-9]+)", style or "")
    return float(m.group(1)) if m else None

def root_width_units(root):
    vb=root.get("viewBox")
    if vb:
        parts=re.split(r"[ ,]+",vb.strip())
        if len(parts)==4:
            try: return float(parts[2])
            except: pass
    return number(root.get("width"))

def collect_text(root):
    rows=[]
    def walk(el, inherited=None):
        fs=number(el.get("font-size"))
        if fs is None: fs=style_font(el.get("style",""))
        if fs is None: fs=inherited
        if local(el.tag)=="text":
            txt=re.sub(r"\s+"," ","".join(el.itertext())).strip()
            rows.append((txt,fs))
        for c in list(el): walk(c,fs)
    walk(root,None)
    return rows

def main():
    ap=argparse.ArgumentParser(description="Estimate final physical text sizes after an SVG is scaled to its intended width")
    ap.add_argument("spec"); ap.add_argument("svg")
    args=ap.parse_args()
    try: spec=json.loads(Path(args.spec).read_text(encoding="utf-8"))
    except Exception as e: print(f"ERROR: cannot read spec: {e}"); return 2
    try: root=ET.fromstring(Path(args.svg).read_text(encoding="utf-8"))
    except Exception as e: print(f"ERROR: cannot parse SVG: {e}"); return 2
    target=spec.get("target",{}) or {}
    width_in=target.get("width_in")
    if width_in is None and target.get("width_mm") is not None:
        try: width_in=float(target["width_mm"])/25.4
        except: pass
    try: width_in=float(width_in)
    except Exception:
        print("WARN: target.width_in/width_mm missing; physical-size legibility audit skipped")
        return 0
    min_pt=float(target.get("min_text_pt",7.5))
    vw=root_width_units(root)
    if not vw or vw<=0:
        print("ERROR: SVG needs a numeric viewBox width or width for physical legibility audit"); return 1
    rows=collect_text(root)
    warnings=[]; errors=[]; measured=[]; unknown=[]
    for txt,fs in rows:
        if fs is None:
            unknown.append(txt[:60]); continue
        pt=fs/vw*width_in*72.0
        measured.append((pt,txt))
        if pt < min_pt:
            errors.append((pt,txt))
    for txt in unknown[:8]: warnings.append(f"font size unresolved (possibly stylesheet/class): {txt!r}")
    if len(unknown)>8: warnings.append(f"font size unresolved for {len(unknown)} text nodes total")
    for w in warnings: print("WARN:",w)
    for pt,txt in sorted(errors)[:20]: print(f"ERROR: target text {pt:.2f} pt < {min_pt:.2f} pt: {txt[:70]!r}")
    if errors:
        print(f"FAIL: {len(errors)}/{len(rows)} text nodes below minimum at {width_in:g} in target width")
        return 1
    if measured:
        smallest=min(measured,key=lambda x:x[0])
        print(f"OK: physical legibility passed; min estimated text={smallest[0]:.2f} pt at {width_in:g} in width ({len(measured)} measured)")
    else:
        print("WARN: no text sizes could be measured; inspect target render manually")
    return 0

if __name__=="__main__": sys.exit(main())
