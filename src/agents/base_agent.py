"""Base agent class."""

from src.schema import AgentRole, Message


class BaseAgent:
    def __init__(self, role: AgentRole):
        self.role = role

    def create_message(
        self,
        task_id: str,
        destination_agent: AgentRole,
        stage: str,
        content: str,
        parent_message_id: str | None = None,
    ) -> Message:
        return Message(
            task_id=task_id,
            source_agent=self.role,
            destination_agent=destination_agent,
            stage=stage,
            content=content,
            parent_message_id=parent_message_id,
        )
