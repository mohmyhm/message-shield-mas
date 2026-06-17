"""Runtime detection rules for suspicious inter-agent messages."""

from src.config import load_runtime_policy


def contains_any_pattern(text: str, patterns: list[str]) -> bool:
    lowered = text.lower()
    return any(pattern.lower() in lowered for pattern in patterns)


def evaluate_message_rules(text: str, policy_config: dict | None = None) -> tuple[float, list[str]]:
    policy_config = policy_config or load_runtime_policy()
    blocked_patterns = policy_config.get("blocked_patterns", {})

    triggered_rules = []
    risk_score = 0.0

    for rule_name, rule_data in blocked_patterns.items():
        patterns = rule_data.get("patterns", [])
        weight = float(rule_data.get("weight", 0.0))

        if contains_any_pattern(text, patterns):
            triggered_rules.append(rule_name)
            risk_score += weight

    return min(risk_score, 1.0), triggered_rules


def contains_instruction_override(text: str) -> bool:
    policy = load_runtime_policy()
    patterns = policy["blocked_patterns"]["instruction_override"]["patterns"]
    return contains_any_pattern(text, patterns)


def contains_fake_authority(text: str) -> bool:
    policy = load_runtime_policy()
    patterns = policy["blocked_patterns"]["fake_authority"]["patterns"]
    return contains_any_pattern(text, patterns)


def contains_safety_bypass(text: str) -> bool:
    policy = load_runtime_policy()
    patterns = policy["blocked_patterns"]["safety_bypass"]["patterns"]
    return contains_any_pattern(text, patterns)
