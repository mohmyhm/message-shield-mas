"""Base agent interface for deterministic multi-agent workflow."""

from __future__ import annotations

from typing import Any, Dict
from uuid import uuid4

from src.schema import AgentRole, Message


class BaseAgent:
    """Base class used by planner, executor, and reviewer agents."""

    def __init__(self, name: str, role: AgentRole):
        self.name = name
        self.role = role

    def create_message(
        self,
        receiver: AgentRole,
        content: str,
        metadata: Dict[str, Any] | None = None,
    ) -> Message:
        return Message(
            message_id=f"msg_{uuid4().hex[:12]}",
            sender=self.role,
            receiver=receiver,
            content=content,
            metadata=metadata or {},
        )
