#!/usr/bin/env python3
import argparse, shutil, subprocess, sys
from pathlib import Path

def run(cmd):
    try:
        subprocess.run(cmd,check=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        return True
    except Exception: return False

def main():
    ap=argparse.ArgumentParser(description='Export an SVG master to vector PDF using an available local renderer')
    ap.add_argument('svg'); ap.add_argument('--output',required=True); args=ap.parse_args()
    src=Path(args.svg); out=Path(args.output); out.parent.mkdir(parents=True,exist_ok=True)
    try:
        import cairosvg
        cairosvg.svg2pdf(url=str(src),write_to=str(out)); print(f'OK: vector PDF with CairoSVG -> {out}'); return 0
    except Exception: pass
    if shutil.which('inkscape'):
        if run(['inkscape',str(src),'--export-type=pdf',f'--export-filename={out}']): print(f'OK: vector PDF with Inkscape -> {out}'); return 0
    if shutil.which('rsvg-convert'):
        if run(['rsvg-convert','-f','pdf','-o',str(out),str(src)]): print(f'OK: vector PDF with rsvg-convert -> {out}'); return 0
    print('ERROR: no working vector-PDF renderer found. Install CairoSVG or Inkscape.')
    return 1
if __name__=='__main__': raise SystemExit(main())
