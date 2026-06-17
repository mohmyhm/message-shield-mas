"""
Core data types shared across the entire pipeline.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional
import hashlib
import time


@dataclass
class Message:
    """An inter-agent message travelling across one edge of the agent graph."""
    msg_id: str
    src: str          # sending agent name
    dst: str          # receiving agent name
    content: str      # raw text payload
    parent_ids: list[str] = field(default_factory=list)  # causal predecessors
    timestamp: float = field(default_factory=time.time)

    @property
    def content_hash(self) -> str:
        return hashlib.sha256(self.content.encode()).hexdigest()


@dataclass
class Artifact:
    """
    Structured representation φ(m) extracted from a Message.
    All scoring and judging operates on this, never on raw text.
    """
    msg_id: str
    task_type: str            # e.g. "summarize", "execute_code", "navigate"
    claimed_authority: str    # agent or role the message claims to act as
    payload_tokens: list[str] # tokenised content keywords
    raw: str                  # original content, kept for repair anchoring


@dataclass
class RiskRecord:
    """What the provenance store keeps for each message node."""
    msg_id: str
    src: str
    risk_score: float         # r(m) — rule-based score on φ(m)
    cumulative_risk: float    # R(m) — propagated score
    ancestors: list[str]      # direct parent msg_ids
    content_hash: str
    timestamp: float


@dataclass
class PolicyDecision:
    """Outcome of the policy engine for a single message."""
    msg_id: str
    decision: str             # "pass" | "escalate" | "quarantine"
    cumulative_risk: float
    repaired_content: Optional[str] = None
    judge_verdict: Optional[str] = None
