#!/usr/bin/env python3
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import importlib
import platform
import sys
from pathlib import Path
from _common import read_json, write_json, sha256_file, SKILL_VERSION


def ver(name):
    try:
        m=importlib.import_module(name); return getattr(m,"__version__","installed")
    except Exception: return None


def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--plan",required=True); ap.add_argument("--inputs",nargs="+",required=True); ap.add_argument("--out",required=True); args=ap.parse_args()
    plan=read_json(args.plan)
    files=[]
    for f in args.inputs:
        p=Path(f); files.append({"path":str(p),"size_bytes":p.stat().st_size,"sha256":sha256_file(p)})
    manifest={
        "skill":"scientific-data-analysis","skill_version":SKILL_VERSION,
        "created_at_utc":datetime.now(timezone.utc).isoformat(),
        "analysis_id":plan.get("analysis_id"),"analysis_plan_schema_version":plan.get("analysis_plan_schema_version"),
        "planning_id":plan.get("planning_id"),"power_plan_schema_version":plan.get("power_plan_schema_version"),
        "plan_version":plan.get("plan_version"),"plan_sha256":sha256_file(args.plan),"random_seed":plan.get("random_seed"),
        "missing_data":plan.get("missing_data"),"resampling":plan.get("resampling"),
        "python":sys.version,"platform":platform.platform(),
        "packages":{n:ver(n) for n in ["numpy","pandas","scipy","statsmodels","matplotlib","openpyxl"]},
        "files":files
    }
    write_json(manifest,args.out); print(f"Wrote {args.out}")

if __name__=="__main__": main()
