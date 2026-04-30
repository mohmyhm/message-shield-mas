"""Run batch experiments for benign, attacked, and defended workflows."""

from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path

# Add the directory containing 'src' to sys.path
script_dir = Path(__file__).resolve().parent.parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

import pandas as pd

from src.attacks.attack_registry import get_attack
from src.config import load_task_config
from src.runtime.monitor import RuntimeMonitor
from src.schema import TaskRecord
from src.workflows.linear_workflow import LinearWorkflow
from src.eval.summarize_results import summarize_report


def load_jsonl_tasks(path: str | Path, max_tasks: int | None = None) -> list[TaskRecord]:
    tasks = []

    with Path(path).open("r", encoding="utf-8") as file:
        for line in file:
            if line.strip():
                tasks.append(TaskRecord(**json.loads(line)))

    if max_tasks is not None:
        tasks = tasks[:max_tasks]

    return tasks


def duplicate_tasks_to_n(tasks: list[TaskRecord], n: int) -> list[TaskRecord]:
    expanded = []

    for i in range(n):
        original = tasks[i % len(tasks)]
        copied = original.model_copy(deep=True)
        copied.task_id = f"{original.task_id}_run_{i + 1:02d}"
        expanded.append(copied)

    return expanded


def run_condition(
    condition: str,
    tasks: list[TaskRecord],
    attack_name: str | None,
    use_monitor: bool,
    trace_output_dir: str,
) -> list[dict]:
    rows = []

    attack = get_attack(attack_name) if attack_name else None
    monitor = RuntimeMonitor() if use_monitor else None

    for task in tasks:
        workflow = LinearWorkflow(
            monitor=monitor,
            attack=attack,
            attack_insertion_point="planner_to_executor" if attack else None,
            trace_output_dir=trace_output_dir,
        )

        trace = workflow.run(task)

        max_risk = 0.0
        decisions = []
        triggered_rules = []

        for assessment in trace.assessments:
            max_risk = max(max_risk, assessment.risk_score)
            decisions.append(assessment.decision.value)
            triggered_rules.extend(assessment.triggered_rules)

        rows.append(
            {
                "condition": condition,
                "task_id": task.task_id,
                "trace_id": trace.trace_id,
                "is_attacked": attack is not None,
                "use_monitor": use_monitor,
                "attack_name": attack_name or "none",
                "final_status": trace.final_status,
                "num_messages": len(trace.messages),
                "num_assessments": len(trace.assessments),
                "was_blocked": str(trace.final_status).startswith("blocked"),
                "was_warned": "warn" in decisions,
                "max_risk_score": max_risk,
                "decisions": "|".join(decisions),
                "triggered_rules": "|".join(sorted(set(triggered_rules))),
            }
        )

    return rows


def make_simple_figure(report_path: str | Path, figure_path: str | Path = "figures/detection_summary.png") -> None:
    import matplotlib.pyplot as plt

    df = pd.read_csv(report_path)

    summary = (
        df.groupby("condition")
        .agg(
            completed=("final_status", lambda x: (x == "completed").sum()),
            blocked=("was_blocked", "sum"),
            avg_risk=("max_risk_score", "mean"),
        )
        .reset_index()
    )

    figure_path = Path(figure_path)
    figure_path.parent.mkdir(parents=True, exist_ok=True)

    plt.figure(figsize=(9, 5))
    plt.bar(summary["condition"], summary["blocked"])
    plt.xticks(rotation=25, ha="right")
    plt.ylabel("Number of blocked runs")
    plt.title("Blocked Runs by Experiment Condition")
    plt.tight_layout()
    plt.savefig(figure_path, dpi=200)
    plt.close()


def main():
    task_config = load_task_config()

    max_tasks = int(task_config.get("experiment", {}).get("max_tasks", 20))
    benign_path = task_config["task_files"]["benign"]

    trace_dir = Path("data/traces/raw")
    report_dir = Path("data/reports")

    trace_dir.mkdir(parents=True, exist_ok=True)
    report_dir.mkdir(parents=True, exist_ok=True)

    # Optional: clean old traces before new experiment.
    for old_trace in trace_dir.glob("*.jsonl"):
        old_trace.unlink()

    base_tasks = load_jsonl_tasks(benign_path)
    tasks = duplicate_tasks_to_n(base_tasks, max_tasks)

    all_rows = []

    all_rows.extend(
        run_condition(
            condition="benign_no_attack_no_monitor",
            tasks=tasks,
            attack_name=None,
            use_monitor=False,
            trace_output_dir=str(trace_dir),
        )
    )

    all_rows.extend(
        run_condition(
            condition="attacked_no_monitor",
            tasks=tasks,
            attack_name="rewrite_attack",
            use_monitor=False,
            trace_output_dir=str(trace_dir),
        )
    )

    all_rows.extend(
        run_condition(
            condition="attacked_with_monitor",
            tasks=tasks,
            attack_name="rewrite_attack",
            use_monitor=True,
            trace_output_dir=str(trace_dir),
        )
    )

    report_path = report_dir / "experiment_report.csv"
    df = pd.DataFrame(all_rows)
    df.to_csv(report_path, index=False)

    summary_path = report_dir / "summary_table.csv"
    summary = summarize_report(report_path, summary_path)

    make_simple_figure(report_path)

    print(f"Saved experiment report to: {report_path}")
    print(f"Saved summary table to: {summary_path}")
    print("Saved figure to: figures/detection_summary.png")
    print()
    print(summary)


if __name__ == "__main__":
    main()
