#!/usr/bin/env python3
"""Suite-level paired benchmark analysis for scientific-figure.

This is optional evaluation infrastructure. It never changes the production
figure workflow or figure_spec schema. A suite binds multiple benchmark cases to
stable source fingerprints and compares named variants pairwise, metric by
metric, without a composite score.
"""
import argparse, datetime as dt, json, hashlib, sys, statistics
from collections import Counter, defaultdict
from pathlib import Path

SCORE_KEYS = [
    "scientific_correctness", "claim_coverage", "structural_clarity",
    "visual_hierarchy", "reading_order", "final_size_legibility", "editability"
]
HIGH_PRIORITY = {"scientific_correctness", "claim_coverage"}
SEVERITIES = ("critical", "major", "minor")


def now():
    return dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")


def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def write_json(path, obj):
    p = Path(path); p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(obj, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")


def digest(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as f:
        for chunk in iter(lambda: f.read(1024*1024), b""):
            h.update(chunk)
    return "sha256:" + h.hexdigest()


def mean(xs):
    return sum(xs)/len(xs) if xs else None


def fmt(v):
    return "—" if v is None else f"{v:.2f}"


def resolve(base, locator):
    p = Path(locator)
    return p if p.is_absolute() else (base / p).resolve()


def case_record(case_path):
    cp = Path(case_path).resolve(); case = read_json(cp)
    src = case.get("source") or {}
    return {
        "case_id": case.get("case_id"), "title": case.get("title") or case.get("case_id"),
        "case_locator": str(cp), "case_sha256": digest(cp),
        "source_sha256": src.get("sha256"), "track": case.get("track"),
        "figure_mode": case.get("figure_mode")
    }


def cmd_init(a):
    out = Path(a.out); out.parent.mkdir(parents=True, exist_ok=True)
    if out.exists() and not a.overwrite:
        print(f"ERROR: suite exists: {out}; use --overwrite intentionally"); return 1
    suite = {
        "benchmark_suite_schema": "1.0", "suite_id": a.suite_id,
        "title": a.title or a.suite_id, "created_utc": now(),
        "cases": [], "variants": [], "notes": a.notes or ""
    }
    write_json(out, suite); print(f"OK: benchmark suite -> {out}"); return 0


def cmd_add_case(a):
    sp = Path(a.suite); suite = read_json(sp)
    try: rec = case_record(a.case)
    except Exception as e: print(f"ERROR: cannot load case: {e}"); return 2
    if any(x.get("case_id") == rec["case_id"] for x in suite.get("cases") or []):
        print(f"ERROR: duplicate case_id {rec['case_id']!r}"); return 1
    suite.setdefault("cases", []).append(rec); write_json(sp, suite)
    print(f"OK: added case {rec['case_id']}"); return 0


def cmd_add_variant(a):
    sp = Path(a.suite); suite = read_json(sp)
    if any(x.get("id") == a.variant for x in suite.get("variants") or []):
        print(f"ERROR: duplicate variant {a.variant!r}"); return 1
    if a.role == "ablation" and not a.parent:
        print("ERROR: ablation variant requires --parent"); return 1
    rec = {"id": a.variant, "role": a.role, "description": a.description or ""}
    if a.parent: rec["parent"] = a.parent
    if a.change: rec["change"] = a.change
    suite.setdefault("variants", []).append(rec); write_json(sp, suite)
    print(f"OK: added variant {a.variant}"); return 0


def find_run(case_path, variant):
    cp = Path(case_path); matches=[]
    for rp in sorted((cp.parent/"runs").glob("*/run.json")):
        try: run = read_json(rp)
        except Exception: continue
        if run.get("variant") == variant: matches.append((rp,run))
    if len(matches) != 1:
        return None, f"expected exactly one run for variant {variant!r}, found {len(matches)}"
    rp, run = matches[0]; ep = rp.with_name("evaluation.json")
    if not ep.exists(): return None, f"missing evaluation for variant {variant!r}"
    ev = read_json(ep)
    if ev.get("status") != "complete": return None, f"evaluation incomplete for variant {variant!r}"
    scores = ev.get("scores") or {}
    missing = [k for k in SCORE_KEYS if not isinstance(scores.get(k),(int,float)) or isinstance(scores.get(k),bool)]
    if missing: return None, f"evaluation missing numeric scores for {variant!r}: {', '.join(missing)}"
    return {"run_path":str(rp),"run":run,"evaluation_path":str(ep),"evaluation":ev}, None


def verify_suite(suite_path, require_variants=None):
    sp = Path(suite_path); suite = read_json(sp); errors=[]; infos=[]
    cases = suite.get("cases") or []
    seen=set()
    for rec in cases:
        cid=rec.get("case_id")
        if not cid or cid in seen: errors.append(f"duplicate/missing case_id {cid!r}"); continue
        seen.add(cid)
        cp = Path(rec.get("case_locator") or "")
        if not cp.exists(): errors.append(f"case {cid}: missing case file {cp}"); continue
        case = read_json(cp)
        if case.get("case_id") != cid: errors.append(f"case {cid}: case_id changed")
        if (case.get("source") or {}).get("sha256") != rec.get("source_sha256"):
            errors.append(f"case {cid}: source fingerprint changed")
        if require_variants:
            for v in require_variants:
                _, err = find_run(cp,v)
                if err: errors.append(f"case {cid}: {err}")
        infos.append(cid)
    variants=suite.get("variants") or []
    varids=[v.get("id") for v in variants]
    if any(not v for v in varids): errors.append("variant id missing")
    if len(varids)!=len(set(varids)): errors.append("duplicate variant ids in suite")
    known=set(varids)
    for v in variants:
        if v.get("role") not in {"baseline","candidate","ablation"}: errors.append(f"variant {v.get('id')!r}: invalid role")
        if v.get("role")=="ablation":
            parent=v.get("parent")
            if not parent: errors.append(f"ablation {v.get('id')!r}: missing parent")
            elif parent not in known: errors.append(f"ablation {v.get('id')!r}: unknown parent {parent!r}")
    if require_variants:
        for rv in require_variants:
            if rv not in known: errors.append(f"required variant {rv!r} is not registered in suite")
    return suite, errors, infos


def cmd_verify(a):
    suite, errors, infos = verify_suite(a.suite, a.require_variant or None)
    for e in errors: print("ERROR:",e)
    if errors: print("SUITE VERIFY: FAIL"); return 1
    print(f"SUITE VERIFY: PASS ({len(infos)} cases)"); return 0


def failure_counts(ev):
    bysev=Counter(); bycat=Counter(); bycat_sev=Counter()
    for f in ev.get("failures") or []:
        if not isinstance(f,dict): continue
        sev=f.get("severity"); cat=f.get("category")
        if sev: bysev[sev]+=1
        if cat: bycat[cat]+=1
        if cat and sev: bycat_sev[(cat,sev)]+=1
    return bysev,bycat,bycat_sev


def cmd_compare(a):
    suite, errors, _ = verify_suite(a.suite, [a.baseline,a.candidate])
    if errors:
        for e in errors: print("ERROR:",e)
        return 1
    rows=[]
    for rec in suite.get("cases") or []:
        b,_=find_run(rec["case_locator"],a.baseline); c,_=find_run(rec["case_locator"],a.candidate)
        rows.append((rec,b,c))

    metric_stats={}
    for k in SCORE_KEYS:
        pairs=[(float(b["evaluation"]["scores"][k]),float(c["evaluation"]["scores"][k])) for _,b,c in rows]
        deltas=[y-x for x,y in pairs]
        metric_stats[k]={
            "baseline_mean":mean([x for x,_ in pairs]), "candidate_mean":mean([y for _,y in pairs]),
            "mean_delta":mean(deltas), "median_delta":statistics.median(deltas),
            "wins":sum(d>0 for d in deltas), "ties":sum(d==0 for d in deltas), "losses":sum(d<0 for d in deltas)
        }

    bsev=Counter(); csev=Counter(); bcatsev=Counter(); ccatsev=Counter()
    regressions=[]
    for rec,b,c in rows:
        bev,cev=b["evaluation"],c["evaluation"]
        bs,_,bcs=failure_counts(bev); cs,_,ccs=failure_counts(cev)
        bsev.update(bs); csev.update(cs); bcatsev.update(bcs); ccatsev.update(ccs)
        scd=float(cev["scores"]["scientific_correctness"])-float(bev["scores"]["scientific_correctness"])
        covd=float(cev["scores"]["claim_coverage"])-float(bev["scores"]["claim_coverage"])
        newcrit=max(0,cs["critical"]-bs["critical"])
        if scd<0 or covd<0 or newcrit>0:
            regressions.append((rec["case_id"],scd,covd,newcrit))

    lines=[f"# Benchmark suite comparison — {suite.get('title') or suite.get('suite_id')}","",
           f"Baseline: `{a.baseline}`  ",f"Candidate: `{a.candidate}`  ",f"Paired cases: **{len(rows)}**  ",""]
    lines += ["## Paired metric results","","| Metric | Baseline mean | Candidate mean | Mean Δ | Median Δ | W / T / L |","|---|---:|---:|---:|---:|---:|"]
    labels={k:k.replace("_"," ") for k in SCORE_KEYS}
    for k in SCORE_KEYS:
        s=metric_stats[k]; lines.append(f"| {labels[k]} | {fmt(s['baseline_mean'])} | {fmt(s['candidate_mean'])} | {s['mean_delta']:+.2f} | {s['median_delta']:+.2f} | {s['wins']} / {s['ties']} / {s['losses']} |")
    lines += ["","No composite score is computed. Scientific correctness and claim coverage have priority over visual dimensions.",""]

    lines += ["## Case-level high-priority regressions",""]
    if regressions:
        lines += ["| Case | Δ scientific correctness | Δ claim coverage | New critical failures |","|---|---:|---:|---:|"]
        for cid,sd,cd,nc in regressions: lines.append(f"| {cid} | {sd:+.1f} | {cd:+.1f} | {nc} |")
    else: lines.append("None detected on paired cases.")

    lines += ["","## Failure severity totals","","| Severity | Baseline | Candidate | Δ |","|---|---:|---:|---:|"]
    for sev in SEVERITIES: lines.append(f"| {sev} | {bsev[sev]} | {csev[sev]} | {csev[sev]-bsev[sev]:+d} |")

    cats=sorted({k[0] for k in set(bcatsev)|set(ccatsev)})
    lines += ["","## Major + critical failures by category","","| Category | Baseline | Candidate | Δ |","|---|---:|---:|---:|"]
    if cats:
        for cat in cats:
            bv=sum(bcatsev[(cat,s)] for s in ("critical","major")); cv=sum(ccatsev[(cat,s)] for s in ("critical","major"))
            lines.append(f"| {cat} | {bv} | {cv} | {cv-bv:+d} |")
    else: lines.append("| — | 0 | 0 | 0 |")

    lines += ["","## Per-case paired deltas","","| Case | Sci. Δ | Coverage Δ | Structure Δ | Hierarchy Δ | Reading Δ | Legibility Δ | Editability Δ |","|---|---:|---:|---:|---:|---:|---:|---:|"]
    for rec,b,c in rows:
        bs=b["evaluation"]["scores"]; cs=c["evaluation"]["scores"]
        ds=[float(cs[k])-float(bs[k]) for k in SCORE_KEYS]
        lines.append("| " + " | ".join([rec["case_id"]]+[f"{d:+.1f}" for d in ds]) + " |")

    lines += ["","## Interpretation","",
              "Treat this as paired evidence, not a leaderboard. A candidate with visual gains but a scientific-correctness or coverage regression needs investigation before promotion. Prefer changes that reduce repeated major/critical failure categories across heterogeneous cases. Ablations should be registered as suite variants with `role=ablation` and compared against their declared parent under the same cases and evaluation protocol.",""]
    text="\n".join(lines)
    if a.out: Path(a.out).write_text(text,encoding="utf-8"); print(f"OK: suite comparison -> {a.out}")
    else: print(text)
    return 0


def cmd_matrix(a):
    suite, errors, _ = verify_suite(a.suite)
    if errors:
        for e in errors: print("ERROR:",e)
        return 1
    variants=[v.get("id") for v in suite.get("variants") or []]
    lines=[f"# Benchmark coverage matrix — {suite.get('title') or suite.get('suite_id')}","", "| Case | " + " | ".join(variants) + " |", "|---|"+"---|"*len(variants)]
    for rec in suite.get("cases") or []:
        vals=[]
        for v in variants:
            item,err=find_run(rec["case_locator"],v)
            vals.append("complete" if item else ("missing" if "expected exactly one run" in (err or "") else "incomplete"))
        lines.append("| " + rec["case_id"] + " | " + " | ".join(vals) + " |")
    text="\n".join(lines)+"\n"
    if a.out: Path(a.out).write_text(text,encoding="utf-8"); print(f"OK: suite matrix -> {a.out}")
    else: print(text)
    return 0


def parser():
    ap=argparse.ArgumentParser(description="Optional suite-level paired benchmark analysis for scientific-figure")
    sub=ap.add_subparsers(dest="cmd",required=True)
    p=sub.add_parser("init"); p.add_argument("--suite-id",required=True); p.add_argument("--out",required=True); p.add_argument("--title"); p.add_argument("--notes"); p.add_argument("--overwrite",action="store_true")
    p=sub.add_parser("add-case"); p.add_argument("--suite",required=True); p.add_argument("--case",required=True)
    p=sub.add_parser("add-variant"); p.add_argument("--suite",required=True); p.add_argument("--variant",required=True); p.add_argument("--role",choices=["baseline","candidate","ablation"],required=True); p.add_argument("--parent"); p.add_argument("--change"); p.add_argument("--description")
    p=sub.add_parser("verify"); p.add_argument("--suite",required=True); p.add_argument("--require-variant",action="append",default=[])
    p=sub.add_parser("matrix"); p.add_argument("--suite",required=True); p.add_argument("--out")
    p=sub.add_parser("compare"); p.add_argument("--suite",required=True); p.add_argument("--baseline",required=True); p.add_argument("--candidate",required=True); p.add_argument("--out")
    return ap


def main():
    a=parser().parse_args()
    return {"init":cmd_init,"add-case":cmd_add_case,"add-variant":cmd_add_variant,"verify":cmd_verify,"matrix":cmd_matrix,"compare":cmd_compare}[a.cmd](a)

if __name__=="__main__": raise SystemExit(main())
