"""Summarize experiment CSV results."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from src.eval.metrics import block_rate, completion_rate, detection_rate, false_positive_rate


def summarize_report(report_path: str | Path, output_path: str | Path = "data/reports/summary_table.csv") -> pd.DataFrame:
    df = pd.read_csv(report_path)

    rows = []

    for condition, group in df.groupby("condition"):
        total = len(group)
        completed = int((group["final_status"] == "completed").sum())
        blocked = int(group["was_blocked"].sum())

        total_attacked = int(group["is_attacked"].sum())
        detected = int(((group["is_attacked"]) & ((group["was_blocked"]) | (group["was_warned"]))).sum())

        total_benign = int((~group["is_attacked"]).sum())
        false_positives = int(((~group["is_attacked"]) & ((group["was_blocked"]) | (group["was_warned"]))).sum())

        rows.append(
            {
                "condition": condition,
                "total_runs": total,
                "completed": completed,
                "blocked": blocked,
                "completion_rate": completion_rate(completed, total),
                "block_rate": block_rate(blocked, total),
                "detection_rate": detection_rate(detected, total_attacked),
                "false_positive_rate": false_positive_rate(false_positives, total_benign),
                "avg_max_risk_score": group["max_risk_score"].mean(),
            }
        )

    summary = pd.DataFrame(rows)
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    summary.to_csv(output_path, index=False)

    return summary


def main():
    summary = summarize_report("data/reports/experiment_report.csv")
    print(summary)


if __name__ == "__main__":
    main()
