#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy import stats
from _common import read_table, read_json, read_artifact_csv, bootstrap_ci, sha256_file, level_display_labels, categorical_level_mask
from run_stats import _paired_arrays
from validate_plan import validate


def mean_ci(x, level=.95):
    x=np.asarray(x,float); x=x[np.isfinite(x)]
    m=np.mean(x)
    if len(x)<2: return m,None,None
    se=stats.sem(x); q=stats.t.ppf((1+level)/2,len(x)-1)
    return m,m-q*se,m+q*se


def median_ci(x, level=.95, seed=0, n_resamples=1500):
    x=np.asarray(x,float); x=x[np.isfinite(x)]
    m=float(np.median(x))
    lo,hi=bootstrap_ci(lambda z: np.median(z),[x],confidence_level=level,seed=seed,n_resamples=n_resamples)
    return m,lo,hi


def model_plot_cohort(df, a):
    """Return the same complete-case cohort used by model-based inference.

    Plotting must not reintroduce rows excluded from a multivariable model merely
    because the displayed x/y variables are observed. This helper mirrors the
    complete-case selection used by linear regression, ANCOVA, and Poisson.
    """
    typ = a.get("type")
    if typ == "linear_regression":
        cols = [a["outcome"]] + list(a["predictors"])
        sub = df[cols].copy()
        for c in cols:
            sub[c] = pd.to_numeric(sub[c], errors="coerce")
        return sub.dropna()
    if typ == "ancova_two_group":
        cols = [a["outcome"], a["group"]] + list(a["covariates"])
        mask = categorical_level_mask(df[a["group"]], a["group_a"]) | categorical_level_mask(df[a["group"]], a["group_b"])
        sub = df.loc[mask, cols].copy()
        numcols = [a["outcome"]] + list(a["covariates"])
        for c in numcols:
            sub[c] = pd.to_numeric(sub[c], errors="coerce")
        return sub.dropna(subset=numcols)
    if typ == "poisson_regression":
        cols = [a["outcome"]] + list(a["predictors"])
        if a.get("exposure"):
            cols.append(a["exposure"])
        if a.get("offset"):
            cols.append(a["offset"])
        sub = df[cols].copy()
        for c in cols:
            sub[c] = pd.to_numeric(sub[c], errors="coerce")
        sub = sub.dropna()
        if a.get("exposure"):
            sub = sub.loc[sub[a["exposure"]] > 0].copy()
        return sub
    raise ValueError(f"No model plotting cohort helper for analysis type {typ!r}")


def _assert_plot_cohort_matches_result(sub, result_row, aid):
    if result_row is None or "n" not in result_row or pd.isna(result_row.get("n")):
        return
    expected = int(round(float(result_row.get("n"))))
    actual = int(len(sub))
    if actual != expected:
        raise ValueError(
            f"{aid}: plot cohort has {actual} rows but results.csv reports n={expected}; "
            "refusing to render a plot from a different analysis cohort"
        )


def save(fig, outbase):
    fig.savefig(str(outbase)+".png", dpi=180, bbox_inches="tight")
    fig.savefig(str(outbase)+".svg", bbox_inches="tight")
    plt.close(fig)


def get_pairs(df,a):
    xa, xb = _paired_arrays(df, a)
    return xa, xb, [str(i) for i in range(len(xa))]


def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--data",required=True); ap.add_argument("--plan",required=True); ap.add_argument("--results",required=True); ap.add_argument("--outdir",required=True); args=ap.parse_args()
    df=read_table(args.data); plan=read_json(args.plan); res=read_artifact_csv(args.results); outdir=Path(args.outdir); outdir.mkdir(parents=True,exist_ok=True)
    errors,warnings=validate(plan)
    if errors: raise ValueError("Invalid analysis plan: " + "; ".join(errors))
    for w in warnings: print(f"WARNING: {w}")
    if "data_sha256" in res.columns and set(res["data_sha256"].dropna().astype(str).unique()) != {sha256_file(args.data)}:
        raise ValueError("results.csv does not match the supplied analysis-ready data")
    if "plan_sha256" in res.columns and set(res["plan_sha256"].dropna().astype(str).unique()) != {sha256_file(args.plan)}:
        raise ValueError("results.csv does not match the supplied analysis plan")
    amap={a["analysis_item_id"]:a for a in plan.get("analyses",[])}; rmap={str(r["analysis_item_id"]):r for _,r in res.iterrows()} if "analysis_item_id" in res.columns else {}; rng=np.random.default_rng(int(plan.get("random_seed",0))); level=float(plan.get("confidence_level",.95)); base_seed=int(plan.get("random_seed",0)); n_resamples=int(plan.get("resampling",{}).get("n_resamples",2000))
    for j,p in enumerate(plan.get("plots",[])):
        aid=p["analysis_item_id"]; a=amap[aid]; kind=p.get("kind")
        fig,ax=plt.subplots(figsize=(5.4,4.2))
        if kind=="group_comparison" and a["type"] in {"independent_t","mann_whitney","equivalence_tost_independent","ancova_two_group","welch_anova","welch_contrast"}:
            groups = ([t["level"] for t in a.get("contrast_terms", [])] if a["type"] == "welch_contrast" else (a.get("group_levels") if a["type"] == "welch_anova" else [a["group_a"], a["group_b"]]))
            plot_df = df
            if a["type"] == "ancova_two_group":
                plot_df = model_plot_cohort(df, a)
                _assert_plot_cohort_matches_result(plot_df, rmap.get(str(aid)), aid)
            for pos,grp in enumerate(groups):
                y=pd.to_numeric(plot_df.loc[categorical_level_mask(plot_df[a["group"]], grp),a["outcome"]],errors="coerce").dropna().to_numpy(float)
                jitter=rng.normal(0,0.045,size=len(y)); ax.scatter(np.full(len(y),pos)+jitter,y,s=28,alpha=.75)
                if a["type"] in {"independent_t","equivalence_tost_independent","ancova_two_group","welch_anova","welch_contrast"}: center,lo,hi=mean_ci(y,level)
                else: center,lo,hi=median_ci(y,level,base_seed+j+pos,n_resamples)
                if lo is not None and hi is not None:
                    ax.errorbar([pos],[center],yerr=[[center-lo],[hi-center]],fmt="o",capsize=4)
                else: ax.plot([pos],[center],"o")
            labels=level_display_labels(groups)
            if a["type"] == "welch_contrast":
                weights=[float(t["weight"]) for t in a.get("contrast_terms", [])]
                labels=[f"{lv}\nw={w:g}" for lv,w in zip(labels,weights)]
                ax.text(.02,.98,"Prespecified weights; group mean/CI summaries are descriptive",transform=ax.transAxes,va="top",fontsize=8)
            elif a["type"] == "ancova_two_group":
                ax.text(.02,.98,"Raw summaries, ANCOVA-complete cases\nAdjusted group effect reported in results",transform=ax.transAxes,va="top",fontsize=8)
            ax.set_xticks(list(range(len(groups))), labels)
            ax.set_ylabel(p.get("ylabel",a["outcome"])); ax.set_title(p.get("title",aid))
        elif kind=="paired_comparison" and a["type"] in {"paired_t","wilcoxon","equivalence_tost_paired"}:
            xa,xb,_=get_pairs(df,a)
            for u,v in zip(xa,xb): ax.plot([0,1],[u,v],marker="o",alpha=.45,linewidth=.8)
            d=xb-xa
            if a["type"] in {"paired_t","equivalence_tost_paired"}: center,lo,hi=mean_ci(d,level)
            else: center,lo,hi=median_ci(d,level,base_seed+j,n_resamples)
            # Difference summary in a small text annotation; trajectories remain the primary paired display.
            if lo is not None:
                ax.text(.02,.98,f"Change: {center:.3g} [{lo:.3g}, {hi:.3g}]",transform=ax.transAxes,va="top")
            if a.get("outcome_a") and a.get("outcome_b"):
                labels=[a.get("outcome_a","A"),a.get("outcome_b","B")]
            else:
                labels=level_display_labels([a.get("condition_a"),a.get("condition_b")])
            ax.set_xticks([0,1],labels); ax.set_ylabel(p.get("ylabel",a.get("outcome","Value"))); ax.set_title(p.get("title",aid))
        elif kind=="correlation" and a["type"] in {"pearson","spearman"}:
            xcol,ycol=a["x"],a["y"]
            sub=df[[xcol,ycol]].apply(pd.to_numeric,errors="coerce").dropna(); ax.scatter(sub[xcol],sub[ycol],s=30,alpha=.75)
            ax.set_xlabel(p.get("xlabel",xcol)); ax.set_ylabel(p.get("ylabel",ycol)); ax.set_title(p.get("title",aid))
        elif kind=="regression" and a["type"]=="linear_regression":
            xcol=a.get("report_predictor") or a["predictors"][0]; ycol=a["outcome"]
            sub=model_plot_cohort(df,a); _assert_plot_cohort_matches_result(sub,rmap.get(str(aid)),aid)
            ax.scatter(sub[xcol],sub[ycol],s=30,alpha=.75)
            if len(a["predictors"])==1:
                slope,intercept=np.polyfit(sub[xcol],sub[ycol],1); xx=np.linspace(sub[xcol].min(),sub[xcol].max(),100); ax.plot(xx,intercept+slope*xx)
            else:
                ax.text(.02,.98,"Raw x-y, model-complete cases\nAdjusted coefficient reported in results",transform=ax.transAxes,va="top",fontsize=8)
            ax.set_xlabel(p.get("xlabel",xcol)); ax.set_ylabel(p.get("ylabel",ycol)); ax.set_title(p.get("title",aid))
        elif kind=="count_regression" and a["type"]=="poisson_regression":
            xcol=a.get("report_predictor") or a["predictors"][0]; ycol=a["outcome"]
            sub=model_plot_cohort(df,a); _assert_plot_cohort_matches_result(sub,rmap.get(str(aid)),aid)
            yy=sub[ycol].to_numpy(float); base_ylabel=p.get("ylabel", ycol); ylabel=base_ylabel
            rate_scaled=False
            if a.get("exposure"):
                expv=sub[a["exposure"]].to_numpy(float)
                keep=expv>0; sub=sub.loc[keep].copy(); yy=yy[keep]/expv[keep]; ylabel=f"Observed {base_ylabel} / {a['exposure']}"; rate_scaled=True
            elif a.get("offset"):
                scale=np.exp(sub[a["offset"]].to_numpy(float)); keep=np.isfinite(scale)&(scale>0); sub=sub.loc[keep].copy(); yy=yy[keep]/scale[keep]; ylabel=f"Observed {base_ylabel} / exp({a['offset']})"; rate_scaled=True
            ax.scatter(sub[xcol].to_numpy(float),yy,s=30,alpha=.75)
            ax.set_xlabel(p.get("xlabel",xcol)); ax.set_ylabel(p.get("rate_ylabel",ylabel) if rate_scaled else base_ylabel); ax.set_title(p.get("title",aid))
            ax.text(.02,.98,"Observed rate only; model-adjusted IRR is reported in results",transform=ax.transAxes,va="top",fontsize=8)
        else:
            plt.close(fig); print(f"Skipping unsupported plot {p.get('plot_id')}: {kind}/{a['type']}"); continue
        ax.spines[["top","right"]].set_visible(False)
        save(fig,outdir/p["plot_id"]); print(f"Wrote {p['plot_id']}.png/.svg")

if __name__=="__main__": main()
