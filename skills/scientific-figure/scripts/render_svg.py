#!/usr/bin/env python3
import argparse, shutil, subprocess, sys
from pathlib import Path

def run(cmd):
    try:
        subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return True
    except Exception:
        return False

def main():
    ap=argparse.ArgumentParser(description="Render SVG to PNG using the first available local renderer")
    ap.add_argument("svg")
    ap.add_argument("--output", required=True)
    g=ap.add_mutually_exclusive_group()
    g.add_argument("--scale", type=float, default=None, help="Raster scale multiplier (default 2 if --width is omitted)")
    g.add_argument("--width", type=int, help="Target output width in pixels; useful for final-size sanity renders")
    args=ap.parse_args()
    src=Path(args.svg); out=Path(args.output); out.parent.mkdir(parents=True, exist_ok=True)
    scale=args.scale if args.scale is not None else 2.0

    try:
        import cairosvg
        kw={"url":str(src),"write_to":str(out)}
        if args.width: kw["output_width"]=args.width
        else: kw["scale"]=scale
        cairosvg.svg2png(**kw)
        print(f"OK: rendered with CairoSVG -> {out}"); return 0
    except Exception:
        pass

    if shutil.which("inkscape"):
        cmd=["inkscape",str(src),"--export-type=png",f"--export-filename={out}"]
        if args.width: cmd.append(f"--export-width={args.width}")
        else: cmd.append(f"--export-dpi={96*scale}")
        if run(cmd): print(f"OK: rendered with Inkscape -> {out}"); return 0

    if shutil.which("rsvg-convert"):
        cmd=["rsvg-convert","-o",str(out)]
        if args.width: cmd += ["-w",str(args.width)]
        else: cmd += ["-z",str(scale)]
        cmd.append(str(src))
        if run(cmd): print(f"OK: rendered with rsvg-convert -> {out}"); return 0

    for exe in ("magick","convert"):
        if shutil.which(exe):
            density=str(int(96*scale))
            cmd=[exe,"-density",density,str(src)]
            if args.width: cmd += ["-resize",f"{args.width}x"]
            cmd.append(str(out))
            if run(cmd): print(f"OK: rendered with {exe} -> {out}"); return 0

    print("ERROR: no working SVG renderer found. Install cairosvg or Inkscape, or render in a browser.")
    return 1

if __name__=="__main__": sys.exit(main())
