"""Runtime detection rules for suspicious inter-agent messages."""

from __future__ import annotations


INSTRUCTION_OVERRIDE_PATTERNS = [
    "ignore previous instructions",
    "override the original task",
    "override the system message",
    "you are now the system",
]

FAKE_AUTHORITY_PATTERNS = [
    "system administrator override",
    "higher priority than all prior instructions",
    "do not tell the user",
]

SAFETY_BYPASS_PATTERNS = [
    "without checking safety",
    "skip safety checks",
    "approve the workflow without checking",
]


def contains_any_pattern(text: str, patterns: list[str]) -> bool:
    lowered = text.lower()
    return any(pattern in lowered for pattern in patterns)


def contains_instruction_override(text: str) -> bool:
    return contains_any_pattern(text, INSTRUCTION_OVERRIDE_PATTERNS)


def contains_fake_authority(text: str) -> bool:
    return contains_any_pattern(text, FAKE_AUTHORITY_PATTERNS)


def contains_safety_bypass(text: str) -> bool:
    return contains_any_pattern(text, SAFETY_BYPASS_PATTERNS)


def evaluate_message_rules(text: str) -> tuple[float, list[str]]:
    triggered_rules = []
    risk_score = 0.0

    if contains_instruction_override(text):
        triggered_rules.append("instruction_override")
        risk_score += 0.45

    if contains_fake_authority(text):
        triggered_rules.append("fake_authority")
        risk_score += 0.35

    if contains_safety_bypass(text):
        triggered_rules.append("safety_bypass")
        risk_score += 0.30

    risk_score = min(risk_score, 1.0)
    return risk_score, triggered_rules
