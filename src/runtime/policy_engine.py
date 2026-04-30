"""Policy decision engine."""

from src.config import load_runtime_policy
from src.schema import PolicyDecision


class PolicyEngine:
    def __init__(self, policy_config: dict | None = None):
        self.policy_config = policy_config or load_runtime_policy()
        self.thresholds = self.policy_config.get("thresholds", {})

    def decide(self, risk_score: float) -> PolicyDecision:
        confirm_threshold = float(self.thresholds.get("confirm", 0.75))
        annotate_threshold = float(self.thresholds.get("annotate", 0.50))
        pass_threshold = float(self.thresholds.get("pass", 0.25))

        if risk_score >= confirm_threshold:
            return PolicyDecision.QUARANTINE

        if risk_score >= annotate_threshold:
            return PolicyDecision.CONFIRM

        if risk_score >= pass_threshold:
            return PolicyDecision.ANNOTATE

        return PolicyDecision.PASS
