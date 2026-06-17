"""Schemas for tasks, messages, attacks, monitor outputs, and trace rows."""

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import uuid4

from pydantic import BaseModel, Field, field_validator


class PolicyDecision(str, Enum):
    PASS = "pass"
    ANNOTATE = "annotate"
    CONFIRM = "confirm"
    QUARANTINE = "quarantine"


class AgentRole(str, Enum):
    USER = "user"
    PLANNER = "planner"
    EXECUTOR = "executor"
    REVIEWER = "reviewer"
    RUNTIME_MONITOR = "runtime_monitor"
    SYSTEM = "system"


class TaskRecord(BaseModel):
    task_id: str = Field(..., min_length=1)
    task_family: str = Field(..., min_length=1)
    user_input: str = Field(..., min_length=1)
    constraints: List[str] = Field(default_factory=list)
    expected_keywords: List[str] = Field(default_factory=list)
    forbidden_keywords: List[str] = Field(default_factory=list)


class Message(BaseModel):
    message_id: str = Field(default_factory=lambda: f"msg_{uuid4().hex[:12]}")
    task_id: str = Field(..., min_length=1)
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    source_agent: AgentRole
    destination_agent: AgentRole
    stage: str = Field(..., min_length=1)
    content: str = Field(..., min_length=1)
    parent_message_id: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)

    @field_validator("content")
    @classmethod
    def content_not_empty(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Message content cannot be empty.")
        return value


class AttackedMessage(BaseModel):
    message_id: str
    task_id: str
    attack_applied: bool = True
    attack_name: str
    original_content: str
    tampered_content: str
    insertion_point: str


class MonitorResult(BaseModel):
    message_id: str
    task_id: str
    risk_score: float = Field(..., ge=0.0, le=1.0)
    rule_hits: List[str] = Field(default_factory=list)
    policy_decision: PolicyDecision
    explanation: str
    safe_content: str


class TraceRow(BaseModel):
    run_id: str
    task_id: str
    edge: str
    original_message: Dict[str, Any]
    attack: Dict[str, Any]
    monitor: Dict[str, Any]
    delivered_content: str
    outcome: Dict[str, Any]


class TraceRecord(BaseModel):
    run_id: str = Field(default_factory=lambda: f"run_{uuid4().hex[:12]}")
    task_id: str
    condition: str
    rows: List[TraceRow] = Field(default_factory=list)
    final_output: Optional[str] = None
    final_status: str = "created"
    task_success: bool = False
    attack_success: bool = False
