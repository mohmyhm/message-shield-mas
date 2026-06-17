"""Linear workflow with optional attack and monitor."""

from src.agents.executor_agent import ExecutorAgent
from src.agents.planner_agent import PlannerAgent
from src.agents.reviewer_agent import ReviewerAgent
from src.logging_utils import save_trace_jsonl
from src.runtime.monitor import RuntimeMonitor
from src.schema import PolicyDecision, TaskRecord, TraceRecord, TraceRow


class LinearWorkflow:
    def __init__(
        self,
        condition: str,
        attack=None,
        attack_insertion_point: str | None = None,
        monitor: RuntimeMonitor | None = None,
        trace_output_dir: str = "data/traces/raw",
    ):
        self.condition = condition
        self.attack = attack
        self.attack_insertion_point = attack_insertion_point
        self.monitor = monitor
        self.trace_output_dir = trace_output_dir

        self.planner = PlannerAgent()
        self.executor = ExecutorAgent()
        self.reviewer = ReviewerAgent()

    def _process_edge(self, trace, task, edge, original_message):
        attack_record = None
        delivered_message = original_message

        if self.attack and self.attack_insertion_point == edge:
            delivered_message, attack_record = self.attack.apply(original_message, edge)

        monitor_result = None

        if self.monitor:
            monitor_result = self.monitor.assess(delivered_message, task)
            delivered_content = monitor_result.safe_content
            delivered_message.content = delivered_content
        else:
            delivered_content = delivered_message.content

        row = TraceRow(
            run_id=trace.run_id,
            task_id=task.task_id,
            edge=edge,
            original_message={
                "message_id": original_message.message_id,
                "content": original_message.content,
            },
            attack={
                "applied": attack_record is not None,
                "name": attack_record.attack_name if attack_record else "none",
                "tampered_content": attack_record.tampered_content if attack_record else None,
            },
            monitor={
                "risk_score": monitor_result.risk_score if monitor_result else 0.0,
                "policy_decision": monitor_result.policy_decision.value if monitor_result else "none",
                "rule_hits": monitor_result.rule_hits if monitor_result else [],
            },
            delivered_content=delivered_content,
            outcome={
                "task_success": False,
                "attack_success": False,
            },
        )

        trace.rows.append(row)

        if monitor_result and monitor_result.policy_decision == PolicyDecision.QUARANTINE:
            return None

        return delivered_message

    def run(self, task: TaskRecord) -> TraceRecord:
        trace = TraceRecord(
            task_id=task.task_id,
            condition=self.condition,
            final_status="running",
        )

        planner_msg = self.planner.plan(task)
        delivered_to_executor = self._process_edge(
            trace,
            task,
            edge="planner_to_executor",
            original_message=planner_msg,
        )

        if delivered_to_executor is None:
            trace.final_status = "quarantined_at_planner_to_executor"
            trace.task_success = False
            trace.attack_success = False
            save_trace_jsonl(trace, self.trace_output_dir)
            return trace

        executor_msg = self.executor.execute(delivered_to_executor, task)
        delivered_to_reviewer = self._process_edge(
            trace,
            task,
            edge="executor_to_reviewer",
            original_message=executor_msg,
        )

        if delivered_to_reviewer is None:
            trace.final_status = "quarantined_at_executor_to_reviewer"
            trace.task_success = False
            trace.attack_success = False
            save_trace_jsonl(trace, self.trace_output_dir)
            return trace

        review = self.reviewer.review(delivered_to_reviewer, task)

        trace.final_output = review["final_output"]
        trace.task_success = review["approved"]

        final_lower = trace.final_output.lower()
        trace.attack_success = any(
            keyword.lower() in final_lower for keyword in task.forbidden_keywords
        )

        trace.final_status = "completed"

        for row in trace.rows:
            row.outcome["task_success"] = trace.task_success
            row.outcome["attack_success"] = trace.attack_success

        save_trace_jsonl(trace, self.trace_output_dir)
        return trace
