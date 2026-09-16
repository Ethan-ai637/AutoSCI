#!/usr/bin/env python3
import argparse, importlib.util, json, platform, shutil, subprocess, sys
from pathlib import Path

def cmd_version(exe, args):
    path=shutil.which(exe)
    if not path: return None
    try:
        p=subprocess.run([path,*args],stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,timeout=5)
        line=(p.stdout or '').strip().splitlines()
        return {"path":path,"version": line[0][:300] if line else "available"}
    except Exception as e:
        return {"path":path,"version":f"available (version probe failed: {e})"}

def py_pkg(name):
    if importlib.util.find_spec(name) is None: return None
    try:
        mod=__import__(name)
        return getattr(mod,'__version__','available')
    except Exception: return 'available'

def collect():
    cairosvg=py_pkg('cairosvg'); pillow=py_pkg('PIL')
    tools={
        'inkscape':cmd_version('inkscape',['--version']),
        'rsvg-convert':cmd_version('rsvg-convert',['--version']),
        'magick':cmd_version('magick',['-version']),
        'convert':cmd_version('convert',['-version']),
        'fontconfig':cmd_version('fc-list',['--version']),
    }
    renderers=[]
    if cairosvg: renderers.append('cairosvg')
    for x in ('inkscape','rsvg-convert','magick','convert'):
        if tools[x]: renderers.append(x)
    pdf=[]
    if cairosvg: pdf.append('cairosvg')
    for x in ('inkscape','rsvg-convert'):
        if tools[x]: pdf.append(x)
    grayscale=[]
    if pillow: grayscale.append('Pillow')
    for x in ('magick','convert'):
        if tools[x]: grayscale.append(x)
    return {
        'python':sys.version.split()[0],
        'platform':platform.system(),
        'packages':{'cairosvg':cairosvg,'Pillow':pillow},
        'tools':tools,
        'capabilities':{
            'svg_to_png':renderers,
            'svg_to_pdf':pdf,
            'grayscale_conversion':grayscale,
        }
    }

def main():
    ap=argparse.ArgumentParser(description='Check local capabilities needed by the scientific-figure skill')
    ap.add_argument('--json',action='store_true'); ap.add_argument('--strict',action='store_true')
    args=ap.parse_args(); d=collect()
    if args.json:
        print(json.dumps(d,ensure_ascii=False,indent=2))
    else:
        print(f"Python: {d['python']} ({d['platform']})")
        for cap,vals in d['capabilities'].items():
            print(f"{cap}: {', '.join(vals) if vals else 'MISSING'}")
        print(f"Pillow: {d['packages']['Pillow'] or 'missing'}")
        print(f"Fontconfig: {'available' if d['tools']['fontconfig'] else 'not detected'}")
        if not d['capabilities']['svg_to_png']:
            print('ACTION: install CairoSVG or Inkscape for deterministic SVG rendering.')
        if not d['capabilities']['svg_to_pdf']:
            print('ACTION: install CairoSVG or Inkscape if vector PDF export is required.')
        if not d['capabilities']['grayscale_conversion']:
            print('ACTION: install Pillow or ImageMagick when grayscale QA is required.')
    hard_missing=not bool(d['capabilities']['svg_to_png'])
    if args.strict and hard_missing: return 1
    return 0
if __name__=='__main__': raise SystemExit(main())
