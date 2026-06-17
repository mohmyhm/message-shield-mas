"""Reviewer agent."""

from src.agents.base_agent import BaseAgent
from src.schema import AgentRole, Message, TaskRecord


class ReviewerAgent(BaseAgent):
    def __init__(self):
        super().__init__(AgentRole.REVIEWER)

    def review(self, message: Message, task: TaskRecord) -> dict:
        content_lower = message.content.lower()

        forbidden_found = [
            keyword for keyword in task.forbidden_keywords
            if keyword.lower() in content_lower
        ]

        expected_found = [
            keyword for keyword in task.expected_keywords
            if keyword.lower() in content_lower
        ]

        approved = len(forbidden_found) == 0 and len(expected_found) >= 1

        return {
            "approved": approved,
            "forbidden_found": forbidden_found,
            "expected_found": expected_found,
            "review_notes": "Approved." if approved else "Output violates constraints or misses expected content.",
            "final_output": message.content,
        }
