"""Evaluation metrics for attack detection."""


def detection_rate(detected: int, total: int) -> float:
    if total == 0:
        return 0.0
    return detected / total
