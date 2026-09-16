#!/usr/bin/env python3
import argparse, json, subprocess, sys, shutil
from pathlib import Path

def make_gray(src,dst):
    try:
        from PIL import Image
        with Image.open(src) as im:
            if im.mode in ("RGBA","LA"):
                alpha=im.getchannel("A")
                gray=im.convert("L").convert("RGBA")
                gray.putalpha(alpha)
            else:
                gray=im.convert("L")
            gray.save(dst)
        print(f"OK: grayscale preview with Pillow -> {dst}")
        return True
    except ImportError:
        pass
    except Exception as e:
        print(f"WARN: Pillow grayscale failed: {e}")
    for exe in ("magick","convert"):
        if shutil.which(exe):
            cmd=[exe,str(src),"-colorspace","Gray",str(dst)]
            try:
                subprocess.run(cmd,check=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
                print(f"OK: grayscale preview with {exe} -> {dst}")
                return True
            except Exception as e:
                print(f"WARN: {exe} grayscale failed: {e}")
    print("ERROR: grayscale QA requested but no working Pillow/ImageMagick conversion is available")
    return False

def main():
    ap=argparse.ArgumentParser(description="Render working-size, final-use, and grayscale scientific figure previews")
    ap.add_argument("spec"); ap.add_argument("svg"); ap.add_argument("--outdir",default=".")
    args=ap.parse_args(); here=Path(__file__).resolve().parent; out=Path(args.outdir); out.mkdir(parents=True,exist_ok=True)
    try: spec=json.loads(Path(args.spec).read_text(encoding="utf-8"))
    except Exception as e: print(f"ERROR: cannot read spec: {e}"); return 2
    target=spec.get("target",{}) or {}
    width_px=target.get("target_preview_width_px")
    if not width_px:
        width_in=target.get("width_in")
        dpi=target.get("target_render_dpi",150)
        try: width_px=round(float(width_in)*float(dpi))
        except: width_px=700
    stem=Path(args.svg).stem
    preview=out/f"{stem}.preview.png"; target_png=out/f"{stem}.target.png"
    cmds=[
        [sys.executable,str(here/"render_svg.py"),args.svg,"--output",str(preview),"--scale","2"],
        [sys.executable,str(here/"render_svg.py"),args.svg,"--output",str(target_png),"--width",str(int(width_px))],
    ]
    for cmd in cmds:
        if subprocess.run(cmd).returncode!=0: return 1
    if target.get("grayscale_safe",False):
        if not make_gray(target_png,out/f"{stem}.target.gray.png"):
            return 1
    print(f"OK: render package -> {out}")
    return 0
if __name__=="__main__": sys.exit(main())
