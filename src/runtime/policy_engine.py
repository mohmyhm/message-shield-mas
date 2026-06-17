"""Policy engine for converting risk scores into decisions."""

from src.config import load_runtime_policy
from src.schema import MonitorDecision


class PolicyEngine:
    def __init__(
        self,
        warn_threshold: float | None = None,
        block_threshold: float | None = None,
    ):
        config = load_runtime_policy()
        monitor_config = config.get("runtime_monitor", {})

        self.warn_threshold = (
            warn_threshold
            if warn_threshold is not None
            else float(monitor_config.get("warn_threshold", 0.30))
        )

        self.block_threshold = (
            block_threshold
            if block_threshold is not None
            else float(monitor_config.get("block_threshold", 0.80))
        )

    def decide(self, risk_score: float) -> MonitorDecision:
        if risk_score >= self.block_threshold:
            return MonitorDecision.BLOCK

        if risk_score >= self.warn_threshold:
            return MonitorDecision.WARN

        return MonitorDecision.ALLOW
