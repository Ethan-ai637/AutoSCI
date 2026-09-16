#!/usr/bin/env python3
import argparse, hashlib, json, sys
from pathlib import Path

def digest(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for chunk in iter(lambda:f.read(1024*1024),b''): h.update(chunk)
    return 'sha256:'+h.hexdigest()

def main():
    ap=argparse.ArgumentParser(description='Verify a finalized scientific-figure release against manifest hashes')
    ap.add_argument('release_dir'); args=ap.parse_args(); root=Path(args.release_dir); mf=root/'manifest.json'
    try: m=json.loads(mf.read_text(encoding='utf-8'))
    except Exception as e: print(f'ERROR: cannot read manifest: {e}'); return 2
    errors=[]; checked=0
    for name,meta in (m.get('artifacts') or {}).items():
        p=root/name
        if not p.exists(): errors.append(f'missing artifact: {name}'); continue
        actual=digest(p); expected=meta.get('sha256')
        if actual!=expected: errors.append(f'hash mismatch: {name}\n  expected {expected}\n  actual   {actual}')
        if meta.get('bytes') is not None and p.stat().st_size!=meta.get('bytes'): errors.append(f'byte-size mismatch: {name}')
        checked+=1
    for e in errors: print('ERROR:',e)
    if errors: print('VERIFY RELEASE: FAIL'); return 1
    print(f'VERIFY RELEASE: PASS ({checked} artifacts, manifest_version={m.get("manifest_version","?")})')
    return 0
if __name__=='__main__': raise SystemExit(main())
