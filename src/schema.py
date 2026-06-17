from enum import Enum
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone

from pydantic import BaseModel, Field, ValidationError, model_validator


class AgentRole(str, Enum):
    PLANNER = "planner"
    EXECUTOR = "executor"
    REVIEWER = "reviewer"
    MONITOR = "monitor"
    USER = "user"


class AttackType(str, Enum):
    NONE = "none"
    REWRITE = "rewrite_attack"
    AUTHORITY = "authority_attack"


class SecurityLabel(str, Enum):
    BENIGN = "benign"
    MALICIOUS = "malicious"


class MonitorDecision(str, Enum):
    ALLOW = "allow"
    WARN = "warn"
    BLOCK = "block"


class Message(BaseModel):
    message_id: str
    sender: AgentRole
    receiver: AgentRole
    content: str = Field(min_length=1)
    attack_type: AttackType = AttackType.NONE
    security_label: SecurityLabel = SecurityLabel.BENIGN
    metadata: Dict[str, Any] = Field(default_factory=dict)

    @model_validator(mode="after")
    def check_content_not_empty(self):
        if not self.content or not self.content.strip():
            raise ValueError("Message content cannot be empty or whitespace only")
        return self


class TaskRecord(BaseModel):
    task_id: str
    task_type: "TaskType"
    user_goal: str
    expected_behavior: str
    attack_type: AttackType
    messages: List[Message] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)

    @model_validator(mode="after")
    def attack_type_consistency(self):
        if self.task_type == TaskType.BENIGN and self.attack_type != AttackType.NONE:
            raise ValueError("Benign tasks must have attack_type 'none'")
        if self.task_type == TaskType.ATTACKED and self.attack_type == AttackType.NONE:
            raise ValueError("Attacked tasks must specify an attack_type other than 'none'")
        return self


class TaskType(str, Enum):
    BENIGN = "benign"
    ATTACKED = "attacked"


class RuntimeAssessment(BaseModel):
    message_id: str
    decision: MonitorDecision
    risk_score: float = Field(ge=0.0, le=1.0)
    triggered_rules: List[str] = Field(default_factory=list)
    explanation: Optional[str] = None
    timestamp: float = Field(default_factory=lambda: datetime.now().timestamp())


class TraceRecord(BaseModel):
    trace_id: str
    task_id: str
    started_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    messages: List[Message] = Field(default_factory=list)
    assessments: List[RuntimeAssessment] = Field(default_factory=list)
    completed_at: Optional[datetime] = None
    final_status: Optional[str] = None
