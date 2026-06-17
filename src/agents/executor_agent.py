"""Executor agent."""

from src.agents.base_agent import BaseAgent
from src.schema import AgentRole, Message, TaskRecord


class ExecutorAgent(BaseAgent):
    def __init__(self):
        super().__init__(AgentRole.EXECUTOR)

    def execute(self, message: Message, task: TaskRecord) -> Message:
        expected = ", ".join(task.expected_keywords[:3])

        content = (
            f"Draft output: This policy should require {expected}. "
            "Requests must be verified, time-limited where applicable, and recorded for audit review."
        )

        return self.create_message(
            task_id=task.task_id,
            destination_agent=AgentRole.REVIEWER,
            stage="execution",
            content=content,
            parent_message_id=message.message_id,
        )
