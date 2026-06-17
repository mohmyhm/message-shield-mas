"""Detection rules for suspicious messages."""


def contains_instruction_override(text: str) -> bool:
    patterns = [
        "ignore previous instructions",
        "override the system message",
        "you are now the system",
    ]
    lowered = text.lower()
    return any(pattern in lowered for pattern in patterns)
