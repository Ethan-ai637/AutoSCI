#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
import matplotlib.pyplot as plt
import pandas as pd

from _common import read_json, read_artifact_csv, sha256_file, SKILL_VERSION


def main():
    ap = argparse.ArgumentParser(description="Render deterministic scenario-summary plots for prospective power planning")
    ap.add_argument("--plan", required=True)
    ap.add_argument("--results", required=True)
    ap.add_argument("--outdir", required=True)
    args = ap.parse_args()

    plan = read_json(args.plan)
    res = read_artifact_csv(args.results)
    plan_hash = sha256_file(args.plan)
    if "plan_sha256" not in res.columns or set(res["plan_sha256"].dropna().astype(str)) != {plan_hash}:
        raise ValueError("Power results do not match the current power plan hash")
    if "skill_version" not in res.columns or set(res["skill_version"].dropna().astype(str)) != {SKILL_VERSION}:
        raise ValueError(f"Power results do not match current skill version {SKILL_VERSION}")
    outdir = Path(args.outdir); outdir.mkdir(parents=True, exist_ok=True)

    for item in plan.get("planning_items", []):
        pid = item["planning_item_id"]
        sub = res[res["planning_item_id"].astype(str) == str(pid)].copy()
        if sub.empty:
            raise ValueError(f"No power results found for planning_item_id={pid}")
        solve_for = str(item["solve_for"])
        labels = [str(x).replace("_", " ") for x in sub["scenario_id"].tolist()]
        if solve_for == "sample_size":
            vals = pd.to_numeric(sub["n_total_analyzable"], errors="raise").tolist()
            ylabel = "Required analyzable total n"
            title = f"{pid}: sample-size sensitivity"
        elif solve_for == "prospective_power":
            vals = pd.to_numeric(sub["achieved_power"], errors="raise").tolist()
            ylabel = "Prospective power"
            title = f"{pid}: power sensitivity"
        elif solve_for == "minimum_detectable_effect":
            vals = pd.to_numeric(sub["minimum_detectable_effect"], errors="raise").abs().tolist()
            ylabel = "Minimum detectable effect magnitude"
            title = f"{pid}: detectable-effect sensitivity"
        else:
            raise ValueError(f"Unsupported solve_for={solve_for}")

        fig, ax = plt.subplots(figsize=(7.2, 4.6))
        x = list(range(len(labels)))
        ax.bar(x, vals)
        ax.set_xticks(x, labels, rotation=20 if len(labels) > 2 else 0, ha="right" if len(labels) > 2 else "center")
        ax.set_ylabel(ylabel)
        ax.set_title(title.replace("_", " "))
        if solve_for == "prospective_power":
            targets = pd.to_numeric(sub["target_power"], errors="raise").tolist()
            if len({round(float(t), 12) for t in targets}) == 1:
                ax.axhline(float(targets[0]), linestyle="--", linewidth=1, label="Target power")
            else:
                # Scenario-specific targets are benchmarks, not inputs to achieved-power calculation.
                # Plot them at each scenario rather than drawing a misleading single global threshold.
                ax.scatter(x, targets, marker="_", s=220, label="Scenario target power")
            ax.set_ylim(0, 1)
            ax.legend()
        for xi, val in zip(x, vals):
            label = f"{val:.3g}" if solve_for != "sample_size" else f"{int(round(val))}"
            ax.text(xi, val, label, ha="center", va="bottom", fontsize=9)
        ax.grid(axis="y", alpha=0.2)
        fig.tight_layout()
        out = outdir / f"{pid}.png"
        fig.savefig(out, dpi=180)
        plt.close(fig)
        print(f"Wrote {out}")


if __name__ == "__main__":
    main()
