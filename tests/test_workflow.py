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
    assert len(trace.rows) == 2


def test_attacked_monitored_workflow_quarantines(tmp_path):
    task = load_first_task()

    workflow = LinearWorkflow(
        condition="attacked_with_monitor",
        attack=get_attack("rewrite_attack"),
        attack_insertion_point="planner_to_executor",
        monitor=RuntimeMonitor(),
        trace_output_dir=str(tmp_path),
    )

    trace = workflow.run(task)

    assert trace.final_status == "quarantined_at_planner_to_executor"
    assert trace.task_success is False
    assert trace.attack_success is False
