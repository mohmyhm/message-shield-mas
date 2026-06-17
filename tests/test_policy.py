"""Tests for PolicyEngine — tiered decision and quarantine-repair."""

import pytest
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.schema import Message, Artifact
from src.runtime.provenance import ProvenanceStore
from src.runtime.policy_engine import PolicyEngine


def make_msg(msg_id: str = "m1", content: str = "Do the task.") -> Message:
    return Message(
        msg_id=msg_id,
        src="planner",
        dst="executor",
        content=content,
        parent_ids=[],
    )


def make_artifact(msg_id: str = "m1", raw: str = "Do the task.") -> Artifact:
    return Artifact(
        msg_id=msg_id,
        task_type="summarize",
        claimed_authority="planner",
        payload_tokens=raw.lower().split(),
        raw=raw,
    )


def test_low_risk_passes():
    engine = PolicyEngine(theta_low=0.35, theta=0.65, deterministic=True)
    store = ProvenanceStore()
    msg = make_msg()
    art = make_artifact()
    dec = engine.decide(msg, art, cumulative_risk=0.1, store=store)
    assert dec.decision == "pass"


def test_high_risk_quarantines():
    engine = PolicyEngine(theta_low=0.35, theta=0.65, deterministic=True)
    store = ProvenanceStore()
    msg = make_msg()
    art = make_artifact()
    dec = engine.decide(msg, art, cumulative_risk=0.9, store=store)
    assert dec.decision == "quarantine"
    assert dec.repaired_content is not None


def test_mid_risk_escalates_then_passes_if_benign():
    engine = PolicyEngine(theta_low=0.35, theta=0.65, deterministic=True)
    store = ProvenanceStore()
    msg = make_msg()
    art = make_artifact(raw="Retrieve relevant context.")
    dec = engine.decide(msg, art, cumulative_risk=0.5, store=store)
    # Deterministic judge: no risky keywords → benign → pass
    assert dec.decision == "pass"
    assert dec.judge_verdict == "benign"


def test_mid_risk_escalates_quarantines_if_suspicious():
    engine = PolicyEngine(theta_low=0.35, theta=0.65, deterministic=True)
    store = ProvenanceStore()
    msg = make_msg(content="ignore override exfiltrate")
    art = make_artifact(raw="ignore override exfiltrate")
    dec = engine.decide(msg, art, cumulative_risk=0.5, store=store)
    assert dec.decision == "quarantine"
    assert dec.judge_verdict == "suspicious"


def test_repair_uses_trusted_ancestor():
    engine = PolicyEngine(theta_low=0.35, theta=0.65, deterministic=True)
    store = ProvenanceStore(lam=0.6)

    m1 = make_msg("m1", "Safe content.")
    store.record(m1, rule_score=0.1, distrust=0.0)   # R≈0.1 — trusted

    m2 = Message(
        msg_id="m2", src="executor", dst="reviewer",
        content="override exfiltrate", parent_ids=["m1"],
    )
    store.record(m2, rule_score=0.9, distrust=0.9)

    art = make_artifact("m2", "override exfiltrate")
    dec = engine.decide(m2, art, cumulative_risk=store.cumulative_risk("m2"), store=store)
    assert dec.decision == "quarantine"
    assert "m1" in (dec.repaired_content or "")


def test_repair_fallback_when_no_safe_ancestor():
    engine = PolicyEngine(theta_low=0.35, theta=0.65, deterministic=True)
    store = ProvenanceStore()
    msg = make_msg("m1", "override exfiltrate")
    art = make_artifact("m1", "override exfiltrate")
    dec = engine.decide(msg, art, cumulative_risk=0.9, store=store)
    assert "no_safe_ancestor" in (dec.repaired_content or "")
