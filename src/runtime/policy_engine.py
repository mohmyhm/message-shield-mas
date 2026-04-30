"""Policy engine for converting risk scores into decisions."""

from src.schema import MonitorDecision


class PolicyEngine:
    def __init__(self, warn_threshold: float = 0.30, block_threshold: float = 0.80):
        self.warn_threshold = warn_threshold
        self.block_threshold = block_threshold

    def decide(self, risk_score: float) -> MonitorDecision:
        if risk_score >= self.block_threshold:
            return MonitorDecision.BLOCK

        if risk_score >= self.warn_threshold:
            return MonitorDecision.WARN

        return MonitorDecision.ALLOW
