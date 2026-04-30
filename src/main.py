"""Run one benign task through the linear workflow."""

import os
import sys
from pathlib import Path

# Add the directory containing 'src' to sys.path
script_dir = Path(__file__).resolve().parent.parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

import json

from src.attacks.attack_registry import get_attack
from src.runtime.monitor import RuntimeMonitor
from src.schema import TaskRecord
from src.workflows.linear_workflow import LinearWorkflow


def load_first_task(path: str) -> TaskRecord:
    with Path(path).open("r", encoding="utf-8") as file:
        first_line = file.readline()
    return TaskRecord(**json.loads(first_line))


def main():
    task = load_first_task("data/tasks/benign_tasks.jsonl")

    workflow = LinearWorkflow()
    trace = workflow.run(task)

    print("Baseline run")
    print(f"Trace ID: {trace.trace_id}")
    print(f"Task ID: {trace.task_id}")
    print(f"Final status: {trace.final_status}")
    print(f"Messages: {len(trace.messages)}")
    print(f"Assessments: {len(trace.assessments)}")

    print("\nAttacked + monitored run")
    attack = get_attack("rewrite_attack")
    monitor = RuntimeMonitor()

    attacked_workflow = LinearWorkflow(
        monitor=monitor,
        attack=attack,
        attack_insertion_point="planner_to_executor",
    )
    attacked_trace = attacked_workflow.run(task)

    print(f"Trace ID: {attacked_trace.trace_id}")
    print(f"Task ID: {attacked_trace.task_id}")
    print(f"Final status: {attacked_trace.final_status}")
    print(f"Messages: {len(attacked_trace.messages)}")
    print(f"Assessments: {len(attacked_trace.assessments)}")


if __name__ == "__main__":
    main()
