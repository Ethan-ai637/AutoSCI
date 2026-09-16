#!/usr/bin/env python3
"""Deterministic workflow router/checkpoint manager for scientific-figure."""
import argparse, hashlib, json, re, subprocess, sys
from pathlib import Path
from datetime import datetime, timezone

MILESTONES=["semantic_contract","semantic_frozen","layout_selected","svg_candidate","qa_passed","critic_passed","released"]
SEMANTIC_KEYS=["message","source","claims","entities","relations","required_labels","invariants","panels","visual_encodings","forbidden_inferences","notation"]
PROFILE_ORDER={"draft":0,"standard":1,"release":2}

def installed_skill_version():
    p=Path(__file__).resolve().parents[1]/"VERSION"
    try:
        return p.read_text(encoding="utf-8").strip() or "unknown"
    except OSError:
        return "unknown"

def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))

def sha256_file(path):
    h=hashlib.sha256()
    with open(path,"rb") as f:
        for chunk in iter(lambda:f.read(1024*1024),b""): h.update(chunk)
    return "sha256:"+h.hexdigest()

def complexity(spec):
    ne=len(spec.get("entities",[]) or [])
    nr=len(spec.get("relations",[]) or [])
    np=len(spec.get("panels",[]) or [])
    core=sum(1 for c in (spec.get("claims",[]) or []) if isinstance(c,dict) and c.get("priority","core")=="core")
    feedback=sum(1 for r in (spec.get("relations",[]) or []) if isinstance(r,dict) and r.get("type") in ("feeds_back","contains","compares_with"))
    score=ne+nr*0.75+max(0,np-1)*2+max(0,core-2)*0.75+feedback*0.75
    return ({"level":"high" if score>=14 else "medium" if score>=8 else "low","score":round(score,2),
             "entities":ne,"relations":nr,"panels":np,"core_claims":core})

def resolve_profile(spec, override="auto"):
    if override!="auto": return override
    p=((spec.get("workflow") or {}).get("profile"))
    return p if p in PROFILE_ORDER else "standard"

def tournament_policy(spec, profile, level):
    mode=((spec.get("workflow") or {}).get("layout_tournament") or "auto")
    if mode=="on": return "required"
    if mode=="off": return "off"
    if profile=="draft": return "off"
    if profile=="release" and level in {"medium","high"}: return "required"
    if profile=="standard" and level=="high": return "recommended"
    return "off"

def now(): return datetime.now(timezone.utc).isoformat(timespec="seconds")

def semantic_digest(spec):
    payload={k:spec.get(k) for k in SEMANTIC_KEYS}
    raw=json.dumps(payload,ensure_ascii=False,sort_keys=True,separators=(",",":"))
    return "sha256:"+hashlib.sha256(raw.encode("utf-8")).hexdigest()

def run_quiet(cmd):
    p=subprocess.run(cmd,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True)
    if p.returncode!=0:
        print(p.stdout.rstrip())
    return p.returncode==0

def new_state(spec, profile):
    c=complexity(spec)
    return {"state_schema":"1.0","skill_version":installed_skill_version(),"profile":profile,"complexity":c,
            "layout_tournament":tournament_policy(spec,profile,c["level"]),"current_milestone":None,
            "semantic_lock":spec.get("semantic_lock"),"checkpoints":{}}

def load_state(path, spec, profile):
    p=Path(path)
    if not p.exists(): return new_state(spec,profile)
    state=read_json(p)
    state["skill_version"]=installed_skill_version()
    # Policy is derived from the current non-semantic workflow settings and complexity.
    c=complexity(spec); state["profile"]=profile; state["complexity"]=c
    state["layout_tournament"]=tournament_policy(spec,profile,c["level"])
    return state

def save_state(path,state):
    Path(path).write_text(json.dumps(state,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")

def required_milestones(profile):
    if profile=="draft": return ["semantic_contract","layout_selected","svg_candidate","qa_passed","critic_passed"]
    if profile=="standard": return ["semantic_contract","semantic_frozen","layout_selected","svg_candidate","qa_passed","critic_passed"]
    return MILESTONES[:]

def stale_checkpoints(state, spec):
    stale=[]
    current_lock=spec.get("semantic_lock")
    for milestone,cp in (state.get("checkpoints") or {}).items():
        reasons=[]
        cp_lock=cp.get("semantic_lock")
        if cp_lock and cp_lock != current_lock: reasons.append("semantic_lock changed")
        cp_sem=cp.get("semantic_digest")
        if cp_sem and cp_sem != semantic_digest(spec): reasons.append("scientific semantic payload changed")
        if milestone in {"qa_passed","critic_passed","released"}:
            cp_profile=cp.get("profile")
            current_profile=state.get("profile")
            if cp_profile in PROFILE_ORDER and current_profile in PROFILE_ORDER and PROFILE_ORDER[current_profile] > PROFILE_ORDER[cp_profile]:
                reasons.append(f"QA profile upgraded {cp_profile}->{current_profile}")
        for item in cp.get("files",[]):
            p=Path(item.get("path",""))
            if not p.exists(): reasons.append(f"missing {p}")
            else:
                actual=sha256_file(p)
                if actual!=item.get("sha256"): reasons.append(f"hash changed {p}")
        if reasons: stale.append((milestone,reasons))
    return stale

def earliest_valid_index(state, spec, profile):
    req=required_milestones(profile); stale={x[0] for x in stale_checkpoints(state,spec)}
    idx=-1
    for i,m in enumerate(req):
        if m in stale: break
        if m not in (state.get("checkpoints") or {}): break
        idx=i
    return idx,req

def next_action(state,spec,profile,state_path="workflow_state.json"):
    idx,req=earliest_valid_index(state,spec,profile)
    next_m=req[idx+1] if idx+1<len(req) else None
    tournament=state.get("layout_tournament")
    if next_m is None:
        return {"milestone":None,"kind":"done","instruction":"Workflow is complete for this profile.","command":None}
    actions={
      "semantic_contract":("model","Build and scientifically verify the source-grounded figure_spec.json. Then run the checkpoint command; it validates spec + grounding before advancing.","python scripts/orchestrate.py checkpoint figure_spec.json semantic_contract --state {STATE}"),
      "semantic_frozen":("command","Freeze the scientifically verified semantic contract and checkpoint the verified lock.","python scripts/freeze_spec.py figure_spec.json && python scripts/orchestrate.py checkpoint figure_spec.json semantic_frozen --state {STATE}"),
      "layout_selected":("model",("Run the required layout tournament, select the winning macro-layout, save layout_plan.md (and layout_tournament.json), then checkpoint it." if tournament=="required" else "Select a deliberate macro-layout and save layout_plan.md. A tournament is recommended but not blocking; then checkpoint it." if tournament=="recommended" else "Select one deliberate macro-layout, save layout_plan.md, then checkpoint it."),"python scripts/orchestrate.py checkpoint figure_spec.json layout_selected --state {STATE} --file layout_plan.md" + (" --file layout_tournament.json" if tournament=="required" else "")),
      "svg_candidate":("model","Generate or revise the editable traceable SVG from the frozen/verified spec and selected layout, then checkpoint it; lint + semantic traceability are rerun automatically.","python scripts/orchestrate.py checkpoint figure_spec.json svg_candidate --state {STATE} --file figure.svg"),
      "qa_passed":("command",f"Checkpoint deterministic {profile} QA for the exact spec/SVG pair; preflight is rerun automatically.","python scripts/orchestrate.py checkpoint figure_spec.json qa_passed --state {STATE} --file figure.svg"),
      "critic_passed":("model","Render, perform separate semantic and visual critique, fix hard defects, rerun QA after edits, then checkpoint the completed critic record.","python scripts/orchestrate.py checkpoint figure_spec.json critic_passed --state {STATE} --file critic.json --file figure.svg"),
      "released":("command","Finalize and verify the publication release package, then checkpoint its verified manifest.","python scripts/finalize_figure.py figure_spec.json figure.svg --critic critic.json --outdir release && python scripts/orchestrate.py checkpoint figure_spec.json released --state {STATE} --file release/manifest.json")
    }
    kind,instruction,command=actions[next_m]
    if command: command=command.replace("{STATE}",str(state_path))
    return {"milestone":next_m,"kind":kind,"instruction":instruction,"command":command}

def cmd_init(args):
    spec=read_json(args.spec); profile=resolve_profile(spec,args.profile); state=new_state(spec,profile); save_state(args.state,state)
    print(f"OK: workflow initialized -> {args.state}")
    print(f"PROFILE: {profile}; COMPLEXITY: {state['complexity']['level']} ({state['complexity']['score']}); TOURNAMENT: {state['layout_tournament']}")
    return 0

def cmd_status(args):
    spec=read_json(args.spec); profile=resolve_profile(spec,args.profile); state=load_state(args.state,spec,profile)
    idx,req=earliest_valid_index(state,spec,profile); stale=stale_checkpoints(state,spec)
    print(f"PROFILE: {profile}")
    c=state['complexity']; print(f"COMPLEXITY: {c['level']} (score={c['score']})")
    print(f"LAYOUT TOURNAMENT: {state['layout_tournament']}")
    for i,m in enumerate(req):
        mark="DONE" if i<=idx else "PENDING"
        if any(s[0]==m for s in stale): mark="STALE"
        print(f"- {m}: {mark}")
    a=next_action(state,spec,profile,args.state)
    print("NEXT:", a["milestone"] or "complete")
    print(a["instruction"])
    if a.get("command"): print("COMMAND:",a["command"])
    return 1 if stale else 0

def cmd_next(args):
    spec=read_json(args.spec); profile=resolve_profile(spec,args.profile); state=load_state(args.state,spec,profile)
    stale=stale_checkpoints(state,spec)
    if stale:
        print("STATE: STALE")
        for m,reasons in stale:
            print(f"- {m}: " + "; ".join(reasons))
        print("ACTION: resume from the earliest stale milestone and re-checkpoint it.")
        return 1
    a=next_action(state,spec,profile,args.state)
    print(f"NEXT: {a['milestone'] or 'complete'} [{a['kind']}]")
    print(a['instruction'])
    if a.get('command'): print("COMMAND:",a['command'])
    return 0

def cmd_checkpoint(args):
    spec=read_json(args.spec); profile=resolve_profile(spec,args.profile); state=load_state(args.state,spec,profile)
    req=required_milestones(profile)
    if args.milestone not in req:
        print(f"ERROR: milestone {args.milestone!r} is not used by profile {profile}"); return 2
    pos=req.index(args.milestone)
    # Never allow a later milestone to be asserted before all earlier required milestones are valid.
    stale_map={m:reasons for m,reasons in stale_checkpoints(state,spec)}
    missing_prev=[m for m in req[:pos] if m not in (state.get("checkpoints") or {})]
    stale_prev=[m for m in req[:pos] if m in stale_map]
    if missing_prev or stale_prev:
        if missing_prev: print("ERROR: prior milestones not checkpointed: " + ", ".join(missing_prev))
        if stale_prev: print("ERROR: prior milestones are stale: " + ", ".join(stale_prev))
        print("ACTION: resume from the earliest missing/stale milestone before advancing")
        return 1
    here=Path(__file__).resolve().parent
    files=[]
    spec_path=Path(args.spec).resolve()
    for name in args.file or []:
        p=Path(name)
        if not p.exists(): print(f"ERROR: checkpoint file missing: {p}"); return 2
        # semantic milestones track semantic content, not non-semantic JSON formatting/status fields
        if args.milestone in {"semantic_contract","semantic_frozen"} and p.resolve()==spec_path:
            continue
        files.append({"path":str(p),"sha256":sha256_file(p),"bytes":p.stat().st_size})
    if args.milestone=="semantic_contract":
        if not run_quiet([sys.executable,str(here/"validate_spec.py"),args.spec]) or not run_quiet([sys.executable,str(here/"source_audit.py"),args.spec]):
            print("ERROR: semantic_contract checkpoint requires spec/source validation to pass"); return 1
    if args.milestone=="semantic_frozen":
        if spec.get("semantic_status")!="frozen" or not spec.get("semantic_lock"):
            print("ERROR: cannot checkpoint semantic_frozen without a frozen spec and semantic_lock"); return 1
        if not run_quiet([sys.executable,str(here/"freeze_spec.py"),args.spec,"--check"]):
            print("ERROR: semantic lock verification failed"); return 1
    if args.milestone=="layout_selected" and state.get("layout_tournament")=="required":
        tournament_files=[Path(x) for x in (args.file or []) if "tournament" in Path(x).name.lower()]
        default=Path("layout_tournament.json")
        if not tournament_files and not default.exists():
            print("ERROR: this profile/complexity requires a layout tournament; checkpoint its scorecard (e.g. layout_tournament.json)"); return 1
    if args.milestone=="svg_candidate":
        svgs=[Path(x) for x in (args.file or []) if Path(x).suffix.lower()==".svg"]
        if not svgs:
            print("ERROR: svg_candidate checkpoint requires --file <candidate.svg>"); return 1
        if not run_quiet([sys.executable,str(here/"svg_lint.py"),str(svgs[0])]) or not run_quiet([sys.executable,str(here/"semantic_audit.py"),args.spec,str(svgs[0])]):
            print("ERROR: SVG candidate must pass lint + semantic traceability before checkpoint"); return 1
    if args.milestone=="qa_passed":
        svgs=[Path(x) for x in (args.file or []) if Path(x).suffix.lower()==".svg"]
        if not svgs:
            print("ERROR: qa_passed checkpoint requires --file <figure.svg>"); return 1
        if not run_quiet([sys.executable,str(here/"preflight.py"),args.spec,str(svgs[0]),"--profile",profile]):
            print("ERROR: cannot checkpoint qa_passed because preflight failed"); return 1
    if args.milestone=="critic_passed":
        critics=[Path(x) for x in (args.file or []) if "critic" in Path(x).name.lower() and Path(x).suffix.lower()==".json"]
        if not critics:
            print("ERROR: critic_passed checkpoint requires --file critic.json"); return 1
        if not run_quiet([sys.executable,str(here/"critic_gate.py"),str(critics[0]),"--profile",profile,"--spec",args.spec]):
            print("ERROR: critic hard gates did not pass"); return 1
    if args.milestone=="released":
        if profile!="release": print("ERROR: released milestone requires release profile"); return 1
        manifests=[Path(x) for x in (args.file or []) if Path(x).name=="manifest.json"]
        if not manifests:
            print("ERROR: released checkpoint requires --file release/manifest.json"); return 1
        if not run_quiet([sys.executable,str(here/"verify_release.py"),str(manifests[0].parent)]):
            print("ERROR: release verification failed"); return 1
    # Re-checkpointing an earlier milestone invalidates everything after it.
    for m in list((state.get("checkpoints") or {}).keys()):
        if m in req and req.index(m)>pos: state["checkpoints"].pop(m,None)
    state.setdefault("checkpoints",{})[args.milestone]={"at":now(),"profile":profile,"semantic_lock":spec.get("semantic_lock"),"semantic_digest":semantic_digest(spec),"files":files}
    state["current_milestone"]=args.milestone; state["semantic_lock"]=spec.get("semantic_lock")
    save_state(args.state,state)
    print(f"OK: checkpoint -> {args.milestone}; invalidated later milestones if present")
    return 0

def cmd_verify(args):
    spec=read_json(args.spec); profile=resolve_profile(spec,args.profile); state=load_state(args.state,spec,profile)
    stale=stale_checkpoints(state,spec)
    if stale:
        print("VERIFY: STALE")
        for m,reasons in stale: print(f"- {m}: " + "; ".join(reasons))
        return 1
    print("VERIFY: PASS")
    return 0

def parser():
    ap=argparse.ArgumentParser(description="Deterministic orchestration/checkpointing for scientific figures")
    sub=ap.add_subparsers(dest="cmd",required=True)
    for name in ("init","status","next","verify"):
        p=sub.add_parser(name); p.add_argument("spec"); p.add_argument("--state",default="workflow_state.json"); p.add_argument("--profile",choices=["auto","draft","standard","release"],default="auto")
    p=sub.add_parser("checkpoint"); p.add_argument("spec"); p.add_argument("milestone",choices=MILESTONES); p.add_argument("--state",default="workflow_state.json"); p.add_argument("--profile",choices=["auto","draft","standard","release"],default="auto"); p.add_argument("--file",action="append",default=[])
    return ap

def main():
    args=parser().parse_args()
    return {"init":cmd_init,"status":cmd_status,"next":cmd_next,"checkpoint":cmd_checkpoint,"verify":cmd_verify}[args.cmd](args)
if __name__=="__main__": raise SystemExit(main())
