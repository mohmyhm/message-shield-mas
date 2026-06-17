"""
Planner Agent — decomposes a user task into an ordered action list.
In deterministic mode returns a fixed stub plan.
"""

from __future__ import annotations
import os
import uuid
import time
from src.schema import Message


class PlannerAgent:
    name = "planner"

    def __init__(self, deterministic: bool = True) -> None:
        self._deterministic = deterministic or os.getenv("DETERMINISTIC", "1") == "1"

    def run(self, task: str, parent_ids: list[str] | None = None) -> Message:
        content = self._plan(task)
        return Message(
            msg_id=f"planner:{uuid.uuid4().hex[:8]}",
            src=self.name,
            dst="executor",
            content=content,
            parent_ids=parent_ids or [],
            timestamp=time.time(),
        )

    def _plan(self, task: str) -> str:
        if self._deterministic:
            return (
                f"PLAN for task: {task}\n"
                "Step 1: Retrieve relevant context.\n"
                "Step 2: Execute primary action.\n"
                "Step 3: Verify output meets requirements."
            )
        # LLM-backed path (used in full-mode runs)
        import openai
        client = openai.OpenAI()
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a planning agent. Output a numbered action plan."},
                {"role": "user", "content": task},
            ],
            temperature=0.0,
            max_tokens=256,
        )
        return resp.choices[0].message.content
