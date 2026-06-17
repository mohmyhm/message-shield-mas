import json
from pathlib import Path

from src.schema import TaskRecord
from src.workflows.linear_workflow import LinearWorkflow


def load_first_benign_task():
    path = Path("data/tasks/benign_tasks.jsonl")
    with path.open("r", encoding="utf-8") as file:
        return TaskRecord(**json.loads(file.readline()))


def test_linear_workflow_baseline_completes(tmp_path):
    task = load_first_benign_task()

    workflow = LinearWorkflow(trace_output_dir=str(tmp_path))
    trace = workflow.run(task)

    assert trace.final_status == "completed"
    assert len(trace.messages) == 3
    assert len(trace.assessments) == 0

    trace_files = list(tmp_path.glob("*.jsonl"))
    assert len(trace_files) == 1
