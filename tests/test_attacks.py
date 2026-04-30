from src.attacks.attack_registry import get_attack
from src.schema import AgentRole, Message


def sample_message():
    return Message(
        task_id="task_test",
        source_agent=AgentRole.PLANNER,
        destination_agent=AgentRole.EXECUTOR,
        stage="planning",
        content="Create a safe password reset policy.",
    )


def test_rewrite_attack_returns_tampered_message_and_record():
    attack = get_attack("rewrite_attack")
    tampered, record = attack.apply(sample_message(), "planner_to_executor")

    assert "emergency bypass" in tampered.content
    assert record.attack_applied is True
    assert record.attack_name == "rewrite_attack"


def test_authority_attack_returns_tampered_message_and_record():
    attack = get_attack("authority_attack")
    tampered, record = attack.apply(sample_message(), "executor_to_reviewer")

    assert "system admin" in tampered.content.lower()
    assert record.attack_name == "authority_attack"
