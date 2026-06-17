import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from src.schema import AgentRole, Message, PolicyDecision, TaskRecord


def test_valid_task_record():
    task = TaskRecord(
        task_id="task_test",
        task_family="policy_summary",
        user_input="Write a short password policy.",
        constraints=["under_120_words"],
        expected_keywords=["verification"],
        forbidden_keywords=["master password"],
    )

    assert task.task_id == "task_test"
    assert "verification" in task.expected_keywords


def test_valid_message():
    message = Message(
        task_id="task_test",
        source_agent=AgentRole.PLANNER,
        destination_agent=AgentRole.EXECUTOR,
        stage="planning",
        content="Create a secure draft.",
    )

    assert message.source_agent == AgentRole.PLANNER
    assert message.destination_agent == AgentRole.EXECUTOR


def test_message_rejects_empty_content():
    with pytest.raises(ValidationError):
        Message(
            task_id="task_test",
            source_agent=AgentRole.PLANNER,
            destination_agent=AgentRole.EXECUTOR,
            stage="planning",
            content="   ",
        )


def test_load_practical_tasks():
    path = Path("data/tasks/benign_tasks.jsonl")
    lines = [json.loads(line) for line in path.read_text().splitlines() if line.strip()]
    tasks = [TaskRecord(**line) for line in lines]

    assert len(tasks) == 20
    assert all(task.task_family for task in tasks)
    assert all(len(task.forbidden_keywords) > 0 for task in tasks)
