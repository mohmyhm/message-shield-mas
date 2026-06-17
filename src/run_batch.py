"""Run practical experiments."""

import json
import sys
from pathlib import Path

# Add the directory containing 'src' to sys.path
script_dir = Path(__file__).resolve().parent.parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

import pandas as pd

from src.attacks.attack_registry import get_attack
from src.runtime.monitor import RuntimeMonitor
from src.schema import TaskRecord
from src.workflows.linear_workflow import LinearWorkflow


def load_tasks(path: str = "data/tasks/benign_tasks.jsonl") -> list[TaskRecord]:
    tasks = []
    with Path(path).open("r", encoding="utf-8") as file:
        for line in file:
            if line.strip():
                tasks.append(TaskRecord(**json.loads(line)))
    return tasks


def run_condition(condition: str, tasks: list[TaskRecord], attack=None, monitor=None):
    rows = []

    for task in tasks:
        workflow = LinearWorkflow(
            condition=condition,
            attack=attack,
            attack_insertion_point="planner_to_executor" if attack else None,
            monitor=monitor,
        )

        trace = workflow.run(task)

        max_risk_score = max(
            [row.monitor["risk_score"] for row in trace.rows],
            default=0.0,
        )

        decisions = [
            row.monitor["policy_decision"]
            for row in trace.rows
            if row.monitor["policy_decision"] != "none"
        ]

        rows.append(
            {
                "condition": condition,
                "run_id": trace.run_id,
                "task_id": trace.task_id,
                "final_status": trace.final_status,
                "task_success": trace.task_success,
                "attack_success": trace.attack_success,
                "was_quarantined": trace.final_status.startswith("quarantined"),
                "max_risk_score": max_risk_score,
                "policy_decisions": "|".join(decisions),
            }
        )

    return rows


def make_summary(report_path: str = "data/reports/experiment_report.csv"):
    df = pd.read_csv(report_path)

    summary = (
        df.groupby("condition")
        .agg(
            total_runs=("run_id", "count"),
            task_success_rate=("task_success", "mean"),
            attack_success_rate=("attack_success", "mean"),
            malicious_message_block_rate=("was_quarantined", "mean"),
            average_risk_score=("max_risk_score", "mean"),
        )
        .reset_index()
    )

    summary.to_csv("data/reports/summary_table.csv", index=False)
    return summary


def make_figure(summary_path: str = "data/reports/summary_table.csv"):
    import matplotlib.pyplot as plt

    summary = pd.read_csv(summary_path)

    Path("figures").mkdir(exist_ok=True)

    plt.figure(figsize=(9, 5))
    plt.bar(summary["condition"], summary["malicious_message_block_rate"])
    plt.ylabel("Block / quarantine rate")
    plt.title("Runtime Monitor Blocking Rate by Condition")
    plt.xticks(rotation=25, ha="right")
    plt.tight_layout()
    plt.savefig("figures/detection_summary.png", dpi=200)
    plt.close()


def main():
    Path("data/reports").mkdir(parents=True, exist_ok=True)

    trace_dir = Path("data/traces/raw")
    trace_dir.mkdir(parents=True, exist_ok=True)

    for old_trace in trace_dir.glob("*.jsonl"):
        old_trace.unlink()

    tasks = load_tasks()

    rows = []

    rows.extend(
        run_condition(
            condition="benign_no_attack_no_monitor",
            tasks=tasks,
            attack=None,
            monitor=None,
        )
    )

    rows.extend(
        run_condition(
            condition="attacked_no_monitor",
            tasks=tasks,
            attack=get_attack("rewrite_attack"),
            monitor=None,
        )
    )

    rows.extend(
        run_condition(
            condition="attacked_with_monitor",
            tasks=tasks,
            attack=get_attack("rewrite_attack"),
            monitor=RuntimeMonitor(),
        )
    )

    report = pd.DataFrame(rows)
    report.to_csv("data/reports/experiment_report.csv", index=False)

    summary = make_summary()
    make_figure()

    print("Saved experiment report to: data/reports/experiment_report.csv")
    print("Saved summary table to: data/reports/summary_table.csv")
    print("Saved figure to: figures/detection_summary.png")
    print()
    print(summary)


if __name__ == "__main__":
    main()
