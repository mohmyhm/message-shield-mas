"""
Reviewer Agent — evaluates the execution result and returns a verdict.
In deterministic mode returns a fixed pass/fail based on content length.
"""

from __future__ import annotations
import os
import uuid
import time
from src.schema import Message


class ReviewerAgent:
    name = "reviewer"

    def __init__(self, deterministic: bool = True) -> None:
        self._deterministic = deterministic or os.getenv("DETERMINISTIC", "1") == "1"

    def run(self, execution_message: Message) -> Message:
        verdict = self._review(execution_message.content)
        return Message(
            msg_id=f"reviewer:{uuid.uuid4().hex[:8]}",
            src=self.name,
            dst="output",
            content=verdict,
            parent_ids=[execution_message.msg_id],
            timestamp=time.time(),
        )

    def _review(self, result: str) -> str:
        if self._deterministic:
            passed = len(result) > 20 and "REPAIRED" not in result
            status = "PASS" if passed else "FAIL"
            return f"REVIEW VERDICT: {status}\nInspected output length={len(result)}"
        import openai
        client = openai.OpenAI()
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a reviewer. Output PASS or FAIL followed by a one-sentence reason."},
                {"role": "user", "content": result},
            ],
            temperature=0.0,
            max_tokens=128,
        )
        return resp.choices[0].message.content
