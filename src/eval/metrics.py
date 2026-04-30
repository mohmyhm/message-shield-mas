"""Evaluation metrics for runtime attack detection."""

from __future__ import annotations


def detection_rate(detected: int, total_attacked: int) -> float:
    if total_attacked == 0:
        return 0.0
    return detected / total_attacked


def false_positive_rate(false_positives: int, total_benign: int) -> float:
    if total_benign == 0:
        return 0.0
    return false_positives / total_benign


def block_rate(blocked: int, total: int) -> float:
    if total == 0:
        return 0.0
    return blocked / total


def completion_rate(completed: int, total: int) -> float:
    if total == 0:
        return 0.0
    return completed / total
