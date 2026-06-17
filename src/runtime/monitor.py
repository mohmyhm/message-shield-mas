"""Runtime monitor for message-level security assessment."""

from src.runtime.policy_engine import PolicyEngine
from src.runtime.rules import evaluate_message_rules
from src.schema import RuntimeAssessment


class RuntimeMonitor:
    def __init__(self, policy_engine: PolicyEngine | None = None):
        self.policy_engine = policy_engine or PolicyEngine()

    def assess(self, message) -> RuntimeAssessment:
        risk_score, triggered_rules = evaluate_message_rules(message.content)
        decision = self.policy_engine.decide(risk_score)

        if triggered_rules:
            explanation = f"Triggered rules: {', '.join(triggered_rules)}."
        else:
            explanation = "No suspicious message-level pattern detected."

        return RuntimeAssessment(
            message_id=message.message_id,
            decision=decision,
            risk_score=risk_score,
            triggered_rules=triggered_rules,
            explanation=explanation,
        )
