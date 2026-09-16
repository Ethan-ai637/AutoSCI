#!/usr/bin/env python3
import argparse, json, sys
from pathlib import Path

COLOR_ONLY={"color","hue","fill-color","stroke-color","fill","stroke"}

def main():
    ap=argparse.ArgumentParser(description="Audit publication-robust semantic encodings")
    ap.add_argument("spec"); args=ap.parse_args()
    try: spec=json.loads(Path(args.spec).read_text(encoding="utf-8"))
    except Exception as e: print(f"ERROR: cannot read spec: {e}"); return 2
    target=spec.get("target",{}) or {}
    require_gray=bool(target.get("grayscale_safe",False))
    encs=spec.get("visual_encodings",[]) or []
    errors=[]; warnings=[]
    for i,e in enumerate(encs):
        if not isinstance(e,dict): warnings.append(f"visual_encodings[{i}] is not an object"); continue
        meaning=e.get("meaning") or f"encoding[{i}]"
        channels=e.get("channels")
        if channels is None:
            warnings.append(f"{meaning!r} has no channels metadata; robustness cannot be audited")
            continue
        if not isinstance(channels,list) or not channels:
            errors.append(f"{meaning!r} channels must be a non-empty list")
            continue
        normalized={str(x).strip().lower() for x in channels}
        noncolor=normalized-COLOR_ONLY
        if require_gray and not noncolor:
            errors.append(f"{meaning!r} is encoded only by color; add label/position/shape/pattern/line-style redundancy for grayscale safety")
        if "color" in normalized and not noncolor:
            warnings.append(f"{meaning!r} depends entirely on color and may fail color-vision/print conditions")
    for w in warnings: print("WARN:",w)
    for e in errors: print("ERROR:",e)
    if errors: return 1
    print(f"OK: publication robustness audit passed ({len(encs)} semantic encodings; grayscale_safe={require_gray})")
    return 0

if __name__=="__main__": sys.exit(main())
