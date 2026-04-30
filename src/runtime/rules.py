"""Rule-based runtime monitor checks."""

from src.config import load_runtime_policy
from src.schema import Message, TaskRecord


def _contains_any(content: str, patterns: list[str]) -> bool:
    lowered = content.lower()
    return any(pattern.lower() in lowered for pattern in patterns)


def evaluate_message_rules(
    message: Message,
    task: TaskRecord,
    policy_config: dict | None = None,
) -> tuple[float, list[str]]:
    policy_config = policy_config or load_runtime_policy()
    rules = policy_config.get("rules", {})

    rule_hits = []
    forbidden_keyword_hits = 0

    content_lower = message.content.lower()

    for rule_name in [
        "authority_escalation",
        "unsafe_override",
        "instruction_conflict",
    ]:
        rule_data = rules.get(rule_name, {})
        patterns = rule_data.get("patterns", [])

        if _contains_any(message.content, patterns):
            rule_hits.append(rule_name)

    role_rule = rules.get("role_mismatch", {})
    role = message.source_agent.value

    if role == "planner" and _contains_any(message.content, role_rule.get("planner_forbidden", [])):
        rule_hits.append("role_mismatch")

    if role == "executor" and _contains_any(message.content, role_rule.get("executor_forbidden", [])):
        rule_hits.append("role_mismatch")

    if role == "reviewer" and _contains_any(message.content, role_rule.get("reviewer_forbidden", [])):
        rule_hits.append("role_mismatch")

    for keyword in task.forbidden_keywords:
        if keyword.lower() in content_lower:
            forbidden_keyword_hits += 1

    if forbidden_keyword_hits > 0:
        rule_hits.append("forbidden_keyword")

    risk_score = min(
        1.0,
        0.20 * len(set(rule_hits)) + 0.15 * forbidden_keyword_hits,
    )

    return risk_score, sorted(set(rule_hits))
