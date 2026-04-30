"""Linear Planner -> Executor -> Reviewer workflow."""

from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from src.agents.executor_agent import ExecutorAgent
from src.agents.planner_agent import PlannerAgent
from src.agents.reviewer_agent import ReviewerAgent
from src.attacks.attack_base import AttackBase
from src.logging_utils import save_trace_jsonl
from src.runtime.monitor import RuntimeMonitor
from src.schema import AgentRole, Message, MonitorDecision, TraceRecord


class LinearWorkflow:
    def __init__(
        self,
        monitor: RuntimeMonitor | None = None,
        attack: AttackBase | None = None,
        attack_insertion_point: str | None = None,
        trace_output_dir: str = "data/traces/raw",
    ):
        self.planner = PlannerAgent()
        self.executor = ExecutorAgent()
        self.reviewer = ReviewerAgent()

        self.monitor = monitor
        self.attack = attack
        self.attack_insertion_point = attack_insertion_point
        self.trace_output_dir = trace_output_dir

    def _maybe_attack(self, message: Message, insertion_point: str) -> Message:
        if self.attack and self.attack_insertion_point == insertion_point:
            return self.attack.apply(message)
        return message

    def _monitor_or_pass(self, trace: TraceRecord, message: Message) -> Message | None:
        if self.monitor is None:
            return message

        assessment = self.monitor.assess(message)
        trace.assessments.append(assessment)

        if assessment.decision == MonitorDecision.BLOCK:
            return None

        message.metadata["monitor_decision"] = assessment.decision.value
        message.metadata["risk_score"] = assessment.risk_score
        message.metadata["triggered_rules"] = assessment.triggered_rules

        return message

    def run(self, task) -> TraceRecord:
        trace = TraceRecord(
            trace_id=f"trace_{uuid4().hex[:12]}",
            task_id=task.task_id,
        )

        planner_message = self.planner.plan(task)
        planner_message = self._maybe_attack(
            planner_message,
            insertion_point="planner_to_executor",
        )
        planner_message = self._monitor_or_pass(trace, planner_message)

        if planner_message is None:
            trace.final_status = "blocked_at_planner_to_executor"
            trace.completed_at = datetime.now(timezone.utc)
            save_trace_jsonl(trace, self.trace_output_dir)
            return trace

        trace.messages.append(planner_message)

        executor_message = self.executor.execute(planner_message)
        executor_message = self._maybe_attack(
            executor_message,
            insertion_point="executor_to_reviewer",
        )
        executor_message = self._monitor_or_pass(trace, executor_message)

        if executor_message is None:
            trace.final_status = "blocked_at_executor_to_reviewer"
            trace.completed_at = datetime.now(timezone.utc)
            save_trace_jsonl(trace, self.trace_output_dir)
            return trace

        trace.messages.append(executor_message)

        reviewer_message = self.reviewer.review(executor_message)
        reviewer_message = self._monitor_or_pass(trace, reviewer_message)

        if reviewer_message is None:
            trace.final_status = "blocked_at_reviewer_to_user"
            trace.completed_at = datetime.now(timezone.utc)
            save_trace_jsonl(trace, self.trace_output_dir)
            return trace

        trace.messages.append(reviewer_message)

        trace.final_status = "completed"
        trace.completed_at = datetime.now(timezone.utc)

        save_trace_jsonl(trace, self.trace_output_dir)

        return trace
