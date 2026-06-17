"""Executor agent."""

from src.agents.base_agent import BaseAgent
from src.schema import AgentRole, Message


class ExecutorAgent(BaseAgent):
    def __init__(self):
        super().__init__(name="Executor Agent", role=AgentRole.EXECUTOR)

    def execute(self, planner_message: Message) -> Message:
        content = (
            "Execution result: I followed the planner instruction and produced a safe, task-focused response. "
            f"Planner instruction summary: {planner_message.content}"
        )
        return self.create_message(
            receiver=AgentRole.REVIEWER,
            content=content,
            metadata={
                "parent_message_id": planner_message.message_id,
                "task_id": planner_message.metadata.get("task_id"),
                "stage": "execution",
            },
        )
