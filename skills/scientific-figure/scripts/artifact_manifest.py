#!/usr/bin/env python3
import argparse, datetime, hashlib, json, sys
from pathlib import Path

def digest(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for chunk in iter(lambda:f.read(1024*1024),b''): h.update(chunk)
    return "sha256:"+h.hexdigest()

def main():
    ap=argparse.ArgumentParser(description="Build a reproducibility manifest for a finalized scientific figure package")
    ap.add_argument("spec"); ap.add_argument("files",nargs="+")
    ap.add_argument("--output",default="manifest.json")
    ap.add_argument("--skill-root",default=None)
    ap.add_argument("--qa-profile",default=None,choices=["draft","standard","release"])
    args=ap.parse_args()
    try: spec=json.loads(Path(args.spec).read_text(encoding='utf-8'))
    except Exception as e: print(f"ERROR: cannot read spec: {e}"); return 2
    root=Path(args.skill_root) if args.skill_root else Path(__file__).resolve().parents[1]
    version=(root/'VERSION').read_text(encoding='utf-8').strip() if (root/'VERSION').exists() else 'unknown'
    entries={}
    for raw in args.files:
        p=Path(raw)
        if not p.exists() or not p.is_file(): print(f"ERROR: missing artifact {p}"); return 1
        entries[p.name]={"sha256":digest(p),"bytes":p.stat().st_size}
    try:
        from doctor import collect as collect_toolchain
        toolchain=collect_toolchain()
    except Exception as e:
        toolchain={"probe_error":str(e)}
    source_fingerprints=[]
    for rec in ((spec.get("source") or {}).get("artifacts") or []):
        if isinstance(rec,dict):
            source_fingerprints.append({k:rec.get(k) for k in ("id","name","sha256","bytes","locator") if rec.get(k) is not None})
    out={
        "manifest_version":"1.2",
        "generated_utc":datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "skill":"scientific-figure",
        "skill_version":version,
        "spec_schema_version":spec.get("schema_version"),
        "semantic_lock":spec.get("semantic_lock"),
        "semantic_status":spec.get("semantic_status"),
        "qa_profile":args.qa_profile or ((spec.get("workflow") or {}).get("profile")),
        "source_fingerprints":source_fingerprints,
        "toolchain":toolchain,
        "artifacts":entries
    }
    Path(args.output).write_text(json.dumps(out,ensure_ascii=False,indent=2)+"\n",encoding='utf-8')
    print(f"OK: manifest -> {args.output} ({len(entries)} artifacts)")
    return 0
if __name__=='__main__': sys.exit(main())
