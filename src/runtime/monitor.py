"""Runtime monitor for message-level security assessment."""

from src.config import load_runtime_policy
from src.runtime.policy_engine import PolicyEngine
from src.runtime.rules import evaluate_message_rules
from src.schema import RuntimeAssessment


class RuntimeMonitor:
    def __init__(self, policy_engine: PolicyEngine | None = None, policy_config: dict | None = None):
        self.policy_config = policy_config or load_runtime_policy()
        self.policy_engine = policy_engine or PolicyEngine()

    def assess(self, message) -> RuntimeAssessment:
        risk_score, triggered_rules = evaluate_message_rules(
            message.content,
            policy_config=self.policy_config,
        )

        decision = self.policy_engine.decide(risk_score)

        explanation = (
            f"Triggered rules: {', '.join(triggered_rules)}."
            if triggered_rules
            else "No suspicious message-level pattern detected."
        )

        return RuntimeAssessment(
            message_id=message.message_id,
            decision=decision,
            risk_score=risk_score,
            triggered_rules=triggered_rules,
            explanation=explanation,
        )
