from src.attacks.attack_registry import get_attack
from src.attacks.authority_attack import AuthorityAttack
from src.attacks.rewrite_attack import RewriteAttack
from src.schema import AgentRole, AttackType, Message, SecurityLabel


def sample_message():
    return Message(
        message_id="msg_test",
        sender=AgentRole.PLANNER,
        receiver=AgentRole.EXECUTOR,
        content="Please complete the assigned task safely.",
    )


def test_rewrite_attack_changes_message():
    attack = RewriteAttack()
    attacked = attack.apply(sample_message())

    assert "Ignore previous instructions" in attacked.content
    assert attacked.attack_type == AttackType.REWRITE
    assert attacked.security_label == SecurityLabel.MALICIOUS
    assert attacked.metadata["attack_applied"] is True


def test_authority_attack_changes_message():
    attack = AuthorityAttack()
    attacked = attack.apply(sample_message())

    assert "System administrator override" in attacked.content
    assert attacked.attack_type == AttackType.AUTHORITY
    assert attacked.security_label == SecurityLabel.MALICIOUS


def test_attack_registry_loads_attack():
    attack = get_attack("rewrite_attack")
    assert isinstance(attack, RewriteAttack)
