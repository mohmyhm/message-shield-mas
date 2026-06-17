"""
Aggregates per-seed CSVs into mean ± std tables and saves figures.

Usage:
  python src/eval/summarize_results.py --input data/reports/ --output figures/
"""

from __future__ import annotations
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default="data/reports")
    parser.add_argument("--output", default="figures")
    args = parser.parse_args()

    try:
        import pandas as pd
        import matplotlib.pyplot as plt
        import numpy as np
    except ImportError:
        print("pandas, matplotlib, numpy are required. Run: pip install -r requirements.txt")
        sys.exit(1)

    in_dir  = Path(args.input)
    out_dir = Path(args.output)
    out_dir.mkdir(parents=True, exist_ok=True)

    csv_files = list(in_dir.glob("*.csv"))
    if not csv_files:
        print(f"No CSV files found in {in_dir}")
        return

    df = pd.concat([pd.read_csv(f) for f in csv_files], ignore_index=True)
    print(f"Loaded {len(df)} rows from {len(csv_files)} file(s).")

    group_cols = ["topology", "defense", "attack", "ablate"]
    metric_cols = ["ASR", "BU", "UA", "FPR", "containment_hops", "semantic_drift"]

    agg = (
        df.groupby(group_cols)[metric_cols]
        .agg(["mean", "std"])
        .round(4)
    )
    agg.columns = ["_".join(c) for c in agg.columns]
    agg = agg.reset_index()

    summary_path = out_dir / "summary.csv"
    agg.to_csv(summary_path, index=False)
    print(f"Summary table → {summary_path}")

    # Table 2: ASR by defense × attack (chain topology, no ablation)
    t2 = df[(df.topology == "chain") & (df.ablate == "none")]
    if not t2.empty:
        pivot = t2.groupby(["defense", "attack"])["ASR"].mean().unstack(fill_value=0.0)
        print("\nTable 2 — ASR (chain, no ablation):")
        print(pivot.round(3).to_string())
        pivot.to_csv(out_dir / "table2_asr.csv")

    # Figure 4: containment_hops by topology × defense
    t4 = df[df.ablate == "none"]
    if not t4.empty:
        fig, ax = plt.subplots(figsize=(7, 4))
        for defense, grp in t4.groupby("defense"):
            means = grp.groupby("topology")["containment_hops"].mean()
            ax.plot(means.index, means.values, marker="o", label=defense)
        ax.set_xlabel("Topology")
        ax.set_ylabel("Avg Containment Hops")
        ax.set_title("Figure 4 — Containment Hops vs Topology")
        ax.legend()
        fig.tight_layout()
        fig_path = out_dir / "figure4_containment_hops.png"
        fig.savefig(fig_path, dpi=150)
        plt.close(fig)
        print(f"Figure 4 → {fig_path}")

    # RQ3 ablation bar chart
    abl = df[df.defense == "message_shield"]
    if not abl.empty:
        fig, ax = plt.subplots(figsize=(7, 4))
        ablate_groups = abl.groupby("ablate")["ASR"].mean()
        ablate_groups.plot(kind="bar", ax=ax, color="steelblue")
        ax.set_xlabel("Ablated Component")
        ax.set_ylabel("ASR")
        ax.set_title("RQ3 Ablation — ASR by Disabled Component")
        fig.tight_layout()
        fig_path = out_dir / "figure_rq3_ablation.png"
        fig.savefig(fig_path, dpi=150)
        plt.close(fig)
        print(f"RQ3 ablation figure → {fig_path}")


if __name__ == "__main__":
    main()
