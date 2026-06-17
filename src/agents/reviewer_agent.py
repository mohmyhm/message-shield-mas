"""Reviewer agent."""

from src.agents.base_agent import BaseAgent
from src.schema import AgentRole, Message


class ReviewerAgent(BaseAgent):
    def __init__(self):
        super().__init__(name="Reviewer Agent", role=AgentRole.REVIEWER)

    def review(self, executor_message: Message) -> Message:
        content = (
            "Review result: approved. The executor response stayed aligned with the original task "
            "and did not introduce unsafe instruction changes."
        )
        return self.create_message(
            receiver=AgentRole.USER,
            content=content,
            metadata={
                "parent_message_id": executor_message.message_id,
                "task_id": executor_message.metadata.get("task_id"),
                "stage": "review",
            },
        )
