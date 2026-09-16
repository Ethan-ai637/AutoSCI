#!/usr/bin/env python3
"""Optional benchmark harness for scientific-figure skill v1.8.

This script is intentionally outside the production figure workflow. It records
blind/referenced benchmark cases, immutable run artifacts, structured evaluations,
and comparison summaries without changing figure semantics.
"""
import argparse, datetime as dt, hashlib, json, re, shutil, sys
from pathlib import Path

FAILURE_CATEGORIES = {
    "source_grounding", "semantic", "notation", "visual_grammar", "layout",
    "geometry", "routing", "typography", "legibility", "style", "portability",
    "critic", "orchestration", "overconstraint", "efficiency", "other"
}
SCORE_KEYS = [
    "scientific_correctness", "claim_coverage", "structural_clarity",
    "visual_hierarchy", "reading_order", "final_size_legibility", "editability"
]

def now():
    return dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")

def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))

def write_json(path, obj):
    p=Path(path); p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(obj, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")

def digest(path):
    p=Path(path); h=hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda:f.read(1024*1024), b""): h.update(chunk)
    return "sha256:"+h.hexdigest()

def fingerprint(path, include_locator=True):
    p=Path(path)
    if not p.exists() or not p.is_file(): raise FileNotFoundError(path)
    out={"name":p.name,"sha256":digest(p),"bytes":p.stat().st_size}
    if include_locator: out["locator"]=str(p.resolve())
    return out

def slug(text):
    s=re.sub(r"[^a-zA-Z0-9._-]+","-",text.strip()).strip("-._").lower()
    return s or "run"

def skill_version():
    p=Path(__file__).resolve().parents[1]/"VERSION"
    return p.read_text(encoding="utf-8").strip() if p.exists() else "unknown"

def parse_time(s):
    if not s: return None
    try: return dt.datetime.fromisoformat(s.replace("Z","+00:00"))
    except Exception: return None

def state_summary(path):
    if not path: return None
    d=read_json(path); cps=d.get("checkpoints") or {}
    times=[]
    for cp in cps.values():
        t=parse_time(cp.get("at")) if isinstance(cp,dict) else None
        if t: times.append(t)
    elapsed=None
    if len(times)>=2: elapsed=round((max(times)-min(times)).total_seconds(),1)
    return {
        "profile":d.get("profile"), "complexity":d.get("complexity"),
        "layout_tournament":d.get("layout_tournament"),
        "current_milestone":d.get("current_milestone"),
        "checkpoint_count":len(cps), "checkpoint_elapsed_seconds":elapsed,
        "checkpoints":{k:(v.get("at") if isinstance(v,dict) else None) for k,v in cps.items()}
    }

def critic_summary(path):
    if not path: return None
    d=read_json(path)
    sem=((d.get("semantic_audit") or {}).get("scores") or {})
    vis=((d.get("visual_audit") or {}).get("scores") or {})
    blockers=[]
    blockers += list((d.get("semantic_audit") or {}).get("blockers") or [])
    blockers += list((d.get("visual_audit") or {}).get("blockers") or [])
    ground=((d.get("semantic_audit") or {}).get("source_grounding") or {})
    reg=(d.get("regression_check") or {})
    return {
        "status":d.get("status"), "semantic_scores":sem, "visual_scores":vis,
        "blocker_count":len(blockers),
        "unsupported_visible_claims":ground.get("unsupported_visible_claims") or [],
        "inferred_core_claims":ground.get("inferred_core_claims") or [],
        "new_regressions":reg.get("new_regressions") or []
    }

def cmd_init(a):
    src=Path(a.source)
    if not src.exists(): print(f"ERROR: source missing: {src}"); return 2
    out=Path(a.out); out.mkdir(parents=True, exist_ok=True); (out/"runs").mkdir(exist_ok=True)
    case_path=out/"case.json"
    if case_path.exists() and not a.overwrite:
        print(f"ERROR: {case_path} exists; use --overwrite intentionally"); return 1
    case={
        "benchmark_schema":"1.0", "case_id":a.case_id, "title":a.title or a.case_id,
        "created_utc":now(), "track":a.track, "figure_mode":a.figure_mode,
        "source":fingerprint(src),
        "protocol":{
            "author_reference_available":False,
            "author_reference":None,
            "reference_access_during_generation":"forbidden" if a.track=="blind" else "allowed",
            "reference_use_for_evaluation":"posthoc_only" if a.track=="blind" else "allowed",
            "target_width_in":a.target_width_in,
            "notes":a.notes or ""
        }
    }
    write_json(case_path,case)
    print(f"OK: benchmark case -> {case_path}")
    if a.track=="blind": print("BLIND TRACK: do not attach/show the author figure until at least one run is recorded.")
    return 0

def cmd_verify_source(a):
    case=read_json(a.case); src=case.get("source") or {}; loc=src.get("locator")
    if not loc:
        print("ERROR: case has no local source locator"); return 2
    p=Path(loc)
    if not p.exists(): print(f"ERROR: source locator missing: {p}"); return 1
    actual=digest(p)
    if actual!=src.get("sha256"):
        print("VERIFY SOURCE: FAIL"); print("expected:",src.get("sha256")); print("actual:  ",actual); return 1
    print("VERIFY SOURCE: PASS"); return 0

def cmd_attach_reference(a):
    cp=Path(a.case); case=read_json(cp)
    runs=list((cp.parent/"runs").glob("*/run.json"))
    if case.get("track")=="blind" and not runs:
        print("ERROR: blind case has no recorded run; attach the author reference only after generation is recorded"); return 1
    try:
        ref=fingerprint(a.reference)
    except FileNotFoundError:
        print(f"ERROR: reference missing: {a.reference}"); return 2
    case.setdefault("protocol",{})["author_reference_available"]=True
    case["protocol"]["author_reference"]={**ref,"attached_utc":now(),"generation_use_forbidden":case.get("track")=="blind"}
    write_json(cp,case)
    print("OK: author reference attached for post-hoc evaluation")
    return 0

def collect_artifacts(paths):
    out=[]
    seen=set()
    for raw in paths:
        p=Path(raw)
        if not p.exists() or not p.is_file(): raise FileNotFoundError(raw)
        key=str(p.resolve())
        if key in seen: continue
        seen.add(key)
        out.append({"name":p.name,"locator":key,"sha256":digest(p),"bytes":p.stat().st_size})
    return out

def cmd_record(a):
    cp=Path(a.case); case=read_json(cp)
    # Bind every run to the exact source snapshot recorded by the case.
    src=case.get("source") or {}; loc=src.get("locator")
    if loc and Path(loc).exists() and digest(loc)!=src.get("sha256"):
        print("ERROR: benchmark source changed since case initialization; create a new case or restore the original snapshot"); return 1
    if case.get("track")=="blind" and (case.get("protocol") or {}).get("author_reference_available"):
        print("ERROR: author reference has already been attached; no additional blind-generation runs may be recorded in this case")
        print("ACTION: create a new blind case for additional uncontaminated runs, or use a separate reference-assisted track")
        return 1
    rid=slug(a.run_id or a.variant); rd=cp.parent/"runs"/rid
    if rd.exists() and any(rd.iterdir()) and not a.overwrite:
        print(f"ERROR: run directory exists: {rd}; choose --run-id or use --overwrite"); return 1
    rd.mkdir(parents=True,exist_ok=True)
    artifacts=list(a.artifact or [])
    for x in (a.spec,a.svg,a.critic,a.state):
        if x: artifacts.append(x)
    if a.release_dir:
        rp=Path(a.release_dir)
        if not rp.exists(): print(f"ERROR: release dir missing: {rp}"); return 2
        artifacts += [str(x) for x in sorted(rp.iterdir()) if x.is_file()]
    try: arts=collect_artifacts(artifacts)
    except FileNotFoundError as e: print(f"ERROR: artifact missing: {e}"); return 2
    spec_info=None
    if a.spec:
        spec=read_json(a.spec)
        spec_info={"schema_version":spec.get("schema_version"),"profile":((spec.get("workflow") or {}).get("profile")),"semantic_lock":spec.get("semantic_lock"),"message":spec.get("message")}
    run={
        "run_schema":"1.0", "case_id":case.get("case_id"), "run_id":rid,
        "variant":a.variant, "recorded_utc":now(), "skill_version":skill_version() if a.uses_skill else None,
        "uses_scientific_figure_skill":bool(a.uses_skill), "generation_reference_access":a.reference_access,
        "prompt_condition":a.prompt_condition or "", "spec":spec_info,
        "workflow":state_summary(a.state) if a.state else None,
        "critic":critic_summary(a.critic) if a.critic else None,
        "artifacts":arts,
        "notes":a.notes or ""
    }
    if case.get("track")=="blind" and a.reference_access!="withheld":
        print("ERROR: blind benchmark run must declare --reference-access withheld"); return 1
    if a.copy_artifacts:
        ad=rd/"artifacts"; ad.mkdir(exist_ok=True)
        for rec in arts:
            src=Path(rec["locator"]); dst=ad/src.name
            if dst.exists() and digest(dst)!=rec["sha256"]:
                dst=ad/(src.stem+"-"+rec["sha256"][7:15]+src.suffix)
            shutil.copy2(src,dst)
    write_json(rd/"run.json",run)
    print(f"OK: benchmark run -> {rd/'run.json'}")
    return 0

def cmd_new_eval(a):
    run=read_json(a.run)
    out=Path(a.out) if a.out else Path(a.run).with_name("evaluation.json")
    ev={
        "evaluation_schema":"1.0", "case_id":run.get("case_id"), "run_id":run.get("run_id"),
        "status":"in_progress", "evaluator":{"kind":"human","name":""},
        "posthoc_author_reference_used":False,
        "scores":{k:None for k in SCORE_KEYS},
        "failures":[],
        "reference_comparison":{
            "semantic_elements_missed":[], "useful_layout_insights":[],
            "acceptable_differences":[], "notes":""
        },
        "verdict":None, "notes":""
    }
    write_json(out,ev); print(f"OK: evaluation template -> {out}"); return 0

def validate_eval_obj(ev):
    errors=[]
    if ev.get("status") not in {"in_progress","complete"}: errors.append("status must be in_progress|complete")
    scores=ev.get("scores") or {}
    for k in SCORE_KEYS:
        v=scores.get(k)
        if ev.get("status")=="complete" and v is None: errors.append(f"complete evaluation missing score {k}")
        if v is not None and (not isinstance(v,(int,float)) or isinstance(v,bool) or v<0 or v>10): errors.append(f"score {k} must be 0..10 or null")
    for i,f in enumerate(ev.get("failures") or []):
        if not isinstance(f,dict): errors.append(f"failure[{i}] must be object"); continue
        if f.get("category") not in FAILURE_CATEGORIES: errors.append(f"failure[{i}] invalid category {f.get('category')!r}")
        if f.get("severity") not in {"minor","major","critical"}: errors.append(f"failure[{i}] severity must be minor|major|critical")
        if not str(f.get("description") or "").strip(): errors.append(f"failure[{i}] missing description")
    if ev.get("status")=="complete" and ev.get("verdict") not in {"pass","partial","fail"}: errors.append("complete evaluation verdict must be pass|partial|fail")
    return errors

def cmd_validate_eval(a):
    ev=read_json(a.evaluation); errors=validate_eval_obj(ev)
    for e in errors: print("ERROR:",e)
    if errors: return 1
    print("EVALUATION: PASS"); return 0

def fmt(v):
    if v is None: return "—"
    if isinstance(v,float): return f"{v:.1f}"
    return str(v)

def cmd_compare(a):
    cp=Path(a.case); case=read_json(cp); rows=[]
    for rp in sorted((cp.parent/"runs").glob("*/run.json")):
        run=read_json(rp); ep=rp.with_name("evaluation.json"); ev=read_json(ep) if ep.exists() else None
        if ev:
            errs=validate_eval_obj(ev)
            if errs:
                print(f"ERROR: invalid evaluation {ep}: " + "; ".join(errs)); return 1
        rows.append((run,ev))
    if not rows: print("ERROR: no recorded runs"); return 1
    lines=[f"# Benchmark comparison — {case.get('title') or case.get('case_id')}","",f"Track: `{case.get('track')}`  ",f"Source SHA-256: `{(case.get('source') or {}).get('sha256','')}`  ",""]
    lines += ["## Outcome matrix","", "| Variant | Skill | Profile | Sci. | Coverage | Structure | Hierarchy | Legibility | Editability | Verdict |", "|---|---:|---|---:|---:|---:|---:|---:|---:|---|"]
    for run,ev in rows:
        sc=(ev or {}).get("scores") or {}; verdict=(ev or {}).get("verdict") or "—"
        profile=((run.get("spec") or {}).get("profile") or (run.get("workflow") or {}).get("profile") or "—")
        lines.append("| " + " | ".join([
            str(run.get("variant")), "yes" if run.get("uses_scientific_figure_skill") else "no", str(profile),
            fmt(sc.get("scientific_correctness")),fmt(sc.get("claim_coverage")),fmt(sc.get("structural_clarity")),
            fmt(sc.get("visual_hierarchy")),fmt(sc.get("final_size_legibility")),fmt(sc.get("editability")),str(verdict)
        ]) + " |")
    lines += ["","## Failure counts","", "| Variant | Critical | Major | Minor | Categories |", "|---|---:|---:|---:|---|"]
    for run,ev in rows:
        fs=(ev or {}).get("failures") or []; cats=sorted({f.get("category") for f in fs if isinstance(f,dict) and f.get("category")})
        counts={s:sum(1 for f in fs if isinstance(f,dict) and f.get("severity")==s) for s in ("critical","major","minor")}
        lines.append(f"| {run.get('variant')} | {counts['critical']} | {counts['major']} | {counts['minor']} | {', '.join(cats) or '—'} |")
    lines += ["","## Interpretation rule","","Do not rank runs by similarity to the author figure or by a single composite score. Prioritize scientific correctness and claim coverage first; treat different but valid visual grammars as acceptable. Use failure categories to decide the next skill change.",""]
    text="\n".join(lines)
    if a.out: Path(a.out).write_text(text,encoding="utf-8"); print(f"OK: comparison -> {a.out}")
    else: print(text)
    return 0

def parser():
    ap=argparse.ArgumentParser(description="Optional benchmark/failure-analysis harness for scientific-figure")
    sub=ap.add_subparsers(dest="cmd",required=True)
    p=sub.add_parser("init"); p.add_argument("--case-id",required=True); p.add_argument("--source",required=True); p.add_argument("--out",required=True); p.add_argument("--track",choices=["blind","reference-assisted"],default="blind"); p.add_argument("--title"); p.add_argument("--figure-mode",default="method-overview"); p.add_argument("--target-width-in",type=float,default=7.0); p.add_argument("--notes"); p.add_argument("--overwrite",action="store_true")
    p=sub.add_parser("verify-source"); p.add_argument("--case",required=True)
    p=sub.add_parser("attach-reference"); p.add_argument("--case",required=True); p.add_argument("--reference",required=True)
    p=sub.add_parser("record"); p.add_argument("--case",required=True); p.add_argument("--variant",required=True); p.add_argument("--run-id"); p.add_argument("--uses-skill",action="store_true"); p.add_argument("--reference-access",choices=["withheld","provided"],default="withheld"); p.add_argument("--prompt-condition"); p.add_argument("--spec"); p.add_argument("--svg"); p.add_argument("--critic"); p.add_argument("--state"); p.add_argument("--release-dir"); p.add_argument("--artifact",action="append",default=[]); p.add_argument("--copy-artifacts",action="store_true"); p.add_argument("--notes"); p.add_argument("--overwrite",action="store_true")
    p=sub.add_parser("new-eval"); p.add_argument("--run",required=True); p.add_argument("--out")
    p=sub.add_parser("validate-eval"); p.add_argument("evaluation")
    p=sub.add_parser("compare"); p.add_argument("--case",required=True); p.add_argument("--out")
    return ap

def main():
    a=parser().parse_args()
    return {"init":cmd_init,"verify-source":cmd_verify_source,"attach-reference":cmd_attach_reference,"record":cmd_record,"new-eval":cmd_new_eval,"validate-eval":cmd_validate_eval,"compare":cmd_compare}[a.cmd](a)

if __name__=="__main__": raise SystemExit(main())
