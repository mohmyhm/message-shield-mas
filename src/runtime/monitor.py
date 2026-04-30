"""Runtime monitor."""

from src.config import load_runtime_policy
from src.runtime.policy_engine import PolicyEngine
from src.runtime.rules import evaluate_message_rules
from src.schema import MonitorResult, PolicyDecision


class RuntimeMonitor:
    def __init__(self, policy_config: dict | None = None):
        self.policy_config = policy_config or load_runtime_policy()
        self.policy_engine = PolicyEngine(self.policy_config)

    def assess(self, message, task) -> MonitorResult:
        risk_score, rule_hits = evaluate_message_rules(
            message=message,
            task=task,
            policy_config=self.policy_config,
        )

        decision = self.policy_engine.decide(risk_score)
        actions = self.policy_config.get("actions", {})

        if decision == PolicyDecision.QUARANTINE:
            safe_content = actions.get("quarantine_message", "[BLOCKED_BY_MONITOR]")
        elif decision == PolicyDecision.CONFIRM:
            safe_content = actions.get("confirm_prefix", "[MONITOR CONFIRM]") + " " + message.content
        elif decision == PolicyDecision.ANNOTATE:
            safe_content = actions.get("annotate_prefix", "[MONITOR WARNING]") + " " + message.content
        else:
            safe_content = message.content

        explanation = (
            "Message triggered monitor rules: " + ", ".join(rule_hits)
            if rule_hits
            else "No suspicious message-level pattern detected."
        )

        return MonitorResult(
            message_id=message.message_id,
            task_id=message.task_id,
            risk_score=risk_score,
            rule_hits=rule_hits,
            policy_decision=decision,
            explanation=explanation,
            safe_content=safe_content,
        )
