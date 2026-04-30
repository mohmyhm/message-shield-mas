import json
from pathlib import Path

from src.attacks.attack_registry import get_attack
from src.runtime.monitor import RuntimeMonitor
from src.schema import TaskRecord
from src.workflows.linear_workflow import LinearWorkflow


def load_first_task():
    line = Path("data/tasks/benign_tasks.jsonl").read_text().splitlines()[0]
    return TaskRecord(**json.loads(line))


def test_benign_workflow_completes(tmp_path):
    task = load_first_task()

    workflow = LinearWorkflow(
        condition="benign_no_attack_no_monitor",
        trace_output_dir=str(tmp_path),
    )

    trace = workflow.run(task)

    assert trace.final_status == "completed"
    assert trace.task_success is True
    assert trace.attack_success is False
    assert len(trace.rows) == 2


def test_attacked_without_monitor_corrupts_output(tmp_path):
    task = load_first_task()

    workflow = LinearWorkflow(
        condition="attacked_no_monitor",
        attack=get_attack("rewrite_attack"),
        attack_insertion_point="planner_to_executor",
        monitor=None,
        trace_output_dir=str(tmp_path),
    )

    trace = workflow.run(task)

    assert trace.final_status == "completed"
    assert trace.task_success is False
    assert trace.attack_success is True


def test_attacked_with_monitor_repairs_and_preserves_task(tmp_path):
    task = load_first_task()

    workflow = LinearWorkflow(
        condition="attacked_with_monitor",
        attack=get_attack("rewrite_attack"),
        attack_insertion_point="planner_to_executor",
        monitor=RuntimeMonitor(),
        trace_output_dir=str(tmp_path),
    )

    trace = workflow.run(task)

    decisions = [row.monitor["policy_decision"] for row in trace.rows]

    assert trace.final_status == "completed"
    assert "quarantine" in decisions
    assert trace.task_success is True
    assert trace.attack_success is False
