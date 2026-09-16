#!/usr/bin/env python3
import argparse, hashlib, json, sys
from pathlib import Path

def digest(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for chunk in iter(lambda:f.read(1024*1024),b''): h.update(chunk)
    return 'sha256:'+h.hexdigest()

def main():
    ap=argparse.ArgumentParser(description='Fingerprint an authoritative source file without copying it into the release')
    ap.add_argument('file'); ap.add_argument('--id',default='source-file'); ap.add_argument('--spec'); ap.add_argument('--locator',default=None)
    args=ap.parse_args(); p=Path(args.file)
    if not p.exists() or not p.is_file(): print(f'ERROR: source file not found: {p}'); return 1
    rec={'id':args.id,'name':p.name,'sha256':digest(p),'bytes':p.stat().st_size}
    if args.locator: rec['locator']=args.locator
    if not args.spec:
        print(json.dumps(rec,ensure_ascii=False,indent=2)); return 0
    sp=Path(args.spec)
    try: spec=json.loads(sp.read_text(encoding='utf-8'))
    except Exception as e: print(f'ERROR: cannot read spec: {e}'); return 2
    if spec.get('semantic_status')=='frozen': print('ERROR: spec is frozen; unlock before changing source fingerprints'); return 1
    src=spec.setdefault('source',{}); arts=src.setdefault('artifacts',[])
    arts=[x for x in arts if isinstance(x,dict) and x.get('id')!=args.id]; arts.append(rec); src['artifacts']=arts
    sp.write_text(json.dumps(spec,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(f'OK: source fingerprint added to {sp}: {rec["sha256"]}')
    return 0
if __name__=='__main__': raise SystemExit(main())
