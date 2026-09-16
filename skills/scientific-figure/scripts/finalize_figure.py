#!/usr/bin/env python3
import argparse, json, shutil, subprocess, sys
from pathlib import Path

def run(cmd,label):
    print(f"\n== {label} ==")
    p=subprocess.run(cmd)
    return p.returncode==0

def main():
    ap=argparse.ArgumentParser(description="Preflight, render, export, package, and hash a final scientific figure release")
    ap.add_argument("spec"); ap.add_argument("svg"); ap.add_argument("--outdir",default="release")
    ap.add_argument("--critic",default=None)
    ap.add_argument("--profile",choices=["standard","release"],default="release",help="Final delivery QA level; release is default")
    ap.add_argument("--pdf",action="store_true",help="Force vector PDF export even if target.exports omits pdf")
    ap.add_argument("--skip-pdf",action="store_true",help="Skip PDF export even if requested in target.exports")
    args=ap.parse_args(); here=Path(__file__).resolve().parent
    if not run([sys.executable,str(here/'preflight.py'),args.spec,args.svg,'--profile',args.profile],"PREFLIGHT"):
        print("FINALIZE: FAIL (preflight did not pass)"); return 1
    try: spec=json.loads(Path(args.spec).read_text(encoding='utf-8'))
    except Exception as e: print(f"ERROR: cannot read spec: {e}"); return 2
    out=Path(args.outdir); out.mkdir(parents=True,exist_ok=True)
    spec_out=out/'figure_spec.json'; svg_out=out/'figure.svg'
    shutil.copy2(args.spec,spec_out); shutil.copy2(args.svg,svg_out)
    if not run([sys.executable,str(here/'render_package.py'),str(spec_out),str(svg_out),'--outdir',str(out)],"RENDER PACKAGE"):
        print("FINALIZE: FAIL (render package)"); return 1
    files=[svg_out,spec_out,out/'figure.preview.png',out/'figure.target.png']
    gray=out/'figure.target.gray.png'
    if gray.exists(): files.append(gray)
    exports=((spec.get('target') or {}).get('exports') or [])
    want_pdf=(args.pdf or ('pdf' in exports)) and not args.skip_pdf
    if want_pdf:
        pdf_out=out/'figure.pdf'
        if not run([sys.executable,str(here/'export_vector.py'),str(svg_out),'--output',str(pdf_out)],"VECTOR PDF"):
            print("FINALIZE: FAIL (vector PDF requested but export failed)"); return 1
        files.append(pdf_out)
    if args.profile=="release" and not args.critic:
        print("ERROR: release finalization requires --critic critic.json so qualitative hard gates are auditable"); return 1
    if args.critic:
        c=Path(args.critic)
        if not c.exists(): print(f"ERROR: critic file not found: {c}"); return 1
        if not run([sys.executable,str(here/'critic_gate.py'),str(c),'--profile',args.profile,'--spec',args.spec],"CRITIC GATE"):
            print("FINALIZE: FAIL (critic hard gates did not pass)"); return 1
        c_out=out/'critic.json'; shutil.copy2(c,c_out); files.append(c_out)
    manifest=out/'manifest.json'
    cmd=[sys.executable,str(here/'artifact_manifest.py'),str(spec_out),*map(str,files),'--output',str(manifest),'--qa-profile',args.profile]
    if not run(cmd,"MANIFEST"): return 1
    if not run([sys.executable,str(here/'verify_release.py'),str(out)],"VERIFY RELEASE"): return 1
    print(f"\nFINALIZE ({args.profile}): PASS -> {out}")
    return 0
if __name__=='__main__': sys.exit(main())
