"""
Executor Agent — carries out the plan produced by the Planner.
In deterministic mode echoes the plan with a completion marker.
"""

from __future__ import annotations
import os
import uuid
import time
from src.schema import Message


class ExecutorAgent:
    name = "executor"

    def __init__(self, deterministic: bool = True) -> None:
        self._deterministic = deterministic or os.getenv("DETERMINISTIC", "1") == "1"

    def run(self, plan_message: Message) -> Message:
        content = self._execute(plan_message.content)
        return Message(
            msg_id=f"executor:{uuid.uuid4().hex[:8]}",
            src=self.name,
            dst="reviewer",
            content=content,
            parent_ids=[plan_message.msg_id],
            timestamp=time.time(),
        )

    def _execute(self, plan: str) -> str:
        if self._deterministic:
            return (
                f"EXECUTION RESULT:\n{plan}\n"
                "[STATUS: completed successfully in deterministic mode]"
            )
        import openai
        client = openai.OpenAI()
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are an execution agent. Carry out the plan and report the result."},
                {"role": "user", "content": plan},
            ],
            temperature=0.0,
            max_tokens=512,
        )
        return resp.choices[0].message.content
