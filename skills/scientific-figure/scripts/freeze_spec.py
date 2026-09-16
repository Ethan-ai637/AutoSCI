#!/usr/bin/env python3
import argparse, copy, hashlib, json, sys
from pathlib import Path

SEMANTIC_KEYS = [
    "message", "source", "claims", "entities", "relations", "required_labels",
    "invariants", "panels", "visual_encodings", "forbidden_inferences", "notation"
]

def semantic_payload(spec):
    return {k: copy.deepcopy(spec.get(k)) for k in SEMANTIC_KEYS}

def semantic_digest(spec):
    raw = json.dumps(semantic_payload(spec), ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return "sha256:" + hashlib.sha256(raw.encode("utf-8")).hexdigest()

def main():
    ap=argparse.ArgumentParser(description="Freeze or verify the semantic portion of a scientific figure spec")
    ap.add_argument("spec")
    ap.add_argument("--check", action="store_true", help="Verify an existing semantic lock without modifying the file")
    ap.add_argument("--unlock", action="store_true", help="Return spec to draft and clear the lock intentionally")
    args=ap.parse_args(); p=Path(args.spec)
    try: spec=json.loads(p.read_text(encoding="utf-8"))
    except Exception as e: print(f"ERROR: cannot read spec: {e}"); return 2

    if args.unlock:
        spec["semantic_status"]="draft"; spec["semantic_lock"]=None
        p.write_text(json.dumps(spec,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
        print("OK: semantic lock cleared; spec is draft")
        return 0

    digest=semantic_digest(spec)
    if args.check:
        lock=spec.get("semantic_lock")
        if spec.get("semantic_status")!="frozen":
            print("ERROR: semantic_status is not frozen"); return 1
        if not lock:
            print("ERROR: frozen spec has no semantic_lock; run freeze_spec.py without --check"); return 1
        if lock != digest:
            print("ERROR: semantic lock mismatch; scientific content changed after freeze")
            print(f"EXPECTED: {lock}\nACTUAL:   {digest}")
            print("ACTION: verify the change, run --unlock, edit the spec, then freeze again")
            return 1
        print(f"OK: semantic lock verified ({digest})"); return 0

    spec["semantic_status"]="frozen"; spec["semantic_lock"]=digest
    p.write_text(json.dumps(spec,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(f"OK: semantic spec frozen ({digest})")
    return 0

if __name__=="__main__": sys.exit(main())
