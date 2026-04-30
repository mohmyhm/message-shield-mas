import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from src.schema import (
    AgentRole,
    AttackType,
    Message,
    MonitorDecision,
    RuntimeAssessment,
    SecurityLabel,
    TaskRecord,
    TaskType,
)


def test_valid_message_creation():
    message = Message(
        message_id="msg_001",
        sender=AgentRole.PLANNER,
        receiver=AgentRole.EXECUTOR,
        content="Please execute the approved plan.",
    )

    assert message.message_id == "msg_001"
    assert message.sender == AgentRole.PLANNER
    assert message.receiver == AgentRole.EXECUTOR
    assert message.attack_type == AttackType.NONE
    assert message.security_label == SecurityLabel.BENIGN


def test_message_rejects_empty_content():
    with pytest.raises(ValidationError):
        Message(
            message_id="msg_002",
            sender=AgentRole.PLANNER,
            receiver=AgentRole.EXECUTOR,
            content="   ",
        )


def test_valid_benign_task():
    task = TaskRecord(
        task_id="benign_001",
        task_type=TaskType.BENIGN,
        user_goal="Summarize lab robot safety requirements.",
        expected_behavior="The agents should summarize safety requirements.",
        attack_type=AttackType.NONE,
    )

    assert task.task_type == TaskType.BENIGN
    assert task.attack_type == AttackType.NONE


def test_benign_task_rejects_attack_type():
    with pytest.raises(ValidationError):
        TaskRecord(
            task_id="bad_benign_001",
            task_type=TaskType.BENIGN,
            user_goal="Summarize lab robot safety requirements.",
            expected_behavior="The agents should summarize safety requirements.",
            attack_type=AttackType.REWRITE,
        )


def test_attacked_task_requires_attack_type():
    with pytest.raises(ValidationError):
        TaskRecord(
            task_id="bad_attacked_001",
            task_type=TaskType.ATTACKED,
            user_goal="Summarize lab robot safety requirements.",
            expected_behavior="The monitor should detect the attack.",
            attack_type=AttackType.NONE,
        )


def test_valid_runtime_assessment():
    assessment = RuntimeAssessment(
        message_id="msg_001",
        decision=MonitorDecision.WARN,
        risk_score=0.65,
        triggered_rules=["contains_instruction_override"],
        explanation="The message contains an instruction override pattern.",
    )

    assert assessment.decision == MonitorDecision.WARN
    assert assessment.risk_score == 0.65
    assert "contains_instruction_override" in assessment.triggered_rules


def test_runtime_assessment_rejects_invalid_risk_score():
    with pytest.raises(ValidationError):
        RuntimeAssessment(
            message_id="msg_001",
            decision=MonitorDecision.BLOCK,
            risk_score=1.5,
            triggered_rules=["invalid_score"],
            explanation="Risk score is outside the valid range.",
        )


def test_load_benign_tasks_jsonl():
    path = Path("data/tasks/benign_tasks.jsonl")
    assert path.exists()

    with path.open("r", encoding="utf-8") as file:
        lines = [json.loads(line) for line in file if line.strip()]

    assert len(lines) >= 3

    tasks = [TaskRecord(**line) for line in lines]

    assert all(task.task_type == TaskType.BENIGN for task in tasks)
    assert all(task.attack_type == AttackType.NONE for task in tasks)


def test_load_attacked_tasks_jsonl():
    path = Path("data/tasks/attacked_tasks.jsonl")
    assert path.exists()

    with path.open("r", encoding="utf-8") as file:
        lines = [json.loads(line) for line in file if line.strip()]

    assert len(lines) >= 1

    tasks = [TaskRecord(**line) for line in lines]

    assert all(task.task_type == TaskType.ATTACKED for task in tasks)
    assert all(task.attack_type != AttackType.NONE for task in tasks)
