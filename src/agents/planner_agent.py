"""Planner agent."""

from src.agents.base_agent import BaseAgent
from src.schema import AgentRole, Message, TaskRecord


class PlannerAgent(BaseAgent):
    def __init__(self):
        super().__init__(name="Planner Agent", role=AgentRole.PLANNER)

    def plan(self, task: TaskRecord) -> Message:
        content = (
            f"Plan for task {task.task_id}: "
            f"Understand the user goal, break it into steps, and send clear instructions to the executor. "
            f"User goal: {task.user_goal}"
        )
        return self.create_message(
            receiver=AgentRole.EXECUTOR,
            content=content,
            metadata={"task_id": task.task_id, "stage": "planning"},
        )
