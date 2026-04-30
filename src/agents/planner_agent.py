"""Planner agent."""

from src.agents.base_agent import BaseAgent
from src.schema import AgentRole, Message, TaskRecord


class PlannerAgent(BaseAgent):
    def __init__(self):
        super().__init__(AgentRole.PLANNER)

    def plan(self, task: TaskRecord) -> Message:
        content = (
            "Create a short draft that follows these constraints: "
            f"{', '.join(task.constraints)}. "
            "Include these expected ideas where appropriate: "
            f"{', '.join(task.expected_keywords)}. "
            f"User request: {task.user_input}"
        )

        return self.create_message(
            task_id=task.task_id,
            destination_agent=AgentRole.EXECUTOR,
            stage="planning",
            content=content,
        )
