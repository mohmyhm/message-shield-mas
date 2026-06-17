"""Tests for ProvenanceStore — causal trace + R(m) propagation."""

import pytest
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.schema import Message
from src.runtime.provenance import ProvenanceStore


def make_msg(msg_id: str, src: str = "planner", parents: list[str] | None = None) -> Message:
    return Message(
        msg_id=msg_id,
        src=src,
        dst="executor",
        content="Do the task.",
        parent_ids=parents or [],
    )


def test_single_message_no_ancestors():
    store = ProvenanceStore(lam=0.6)
    msg = make_msg("m1")
    rec = store.record(msg, rule_score=0.2, distrust=0.1)
    # g(0.2, 0.1) = 1-(0.8)(0.9) = 0.28; ancestor_max=0 → R=0.28
    assert abs(rec.cumulative_risk - 0.28) < 1e-6


def test_risk_propagates_from_ancestor():
    store = ProvenanceStore(lam=0.6)
    m1 = make_msg("m1")
    store.record(m1, rule_score=0.5, distrust=0.0)   # R(m1)=0.5

    m2 = make_msg("m2", parents=["m1"])
    rec2 = store.record(m2, rule_score=0.1, distrust=0.0)
    # g(0.1,0)=0.1; + 0.6*0.5=0.3 → R=0.4
    assert abs(rec2.cumulative_risk - 0.4) < 1e-6


def test_noisy_or_combines_correctly():
    store = ProvenanceStore(lam=0.0)
    msg = make_msg("m1")
    rec = store.record(msg, rule_score=0.3, distrust=0.4)
    expected = 1.0 - (1.0 - 0.3) * (1.0 - 0.4)   # = 0.58
    assert abs(rec.cumulative_risk - expected) < 1e-6


def test_cumulative_risk_capped_at_one():
    store = ProvenanceStore(lam=1.0)
    m1 = make_msg("m1")
    store.record(m1, rule_score=0.9, distrust=0.9)
    m2 = make_msg("m2", parents=["m1"])
    rec2 = store.record(m2, rule_score=0.9, distrust=0.9)
    assert rec2.cumulative_risk <= 1.0


def test_last_trusted_ancestor_found():
    store = ProvenanceStore(lam=0.6)
    m1 = make_msg("m1")
    store.record(m1, rule_score=0.1, distrust=0.0)   # R≈0.1 (safe)
    m2 = make_msg("m2", parents=["m1"])
    store.record(m2, rule_score=0.8, distrust=0.8)   # R high (risky)
    m3 = make_msg("m3", parents=["m2"])
    store.record(m3, rule_score=0.9, distrust=0.9)   # R very high

    trusted = store.last_trusted_ancestor("m3", theta=0.65)
    assert trusted == "m1"


def test_no_trusted_ancestor_returns_none():
    store = ProvenanceStore(lam=0.6)
    m1 = make_msg("m1")
    store.record(m1, rule_score=0.9, distrust=0.9)
    m2 = make_msg("m2", parents=["m1"])
    store.record(m2, rule_score=0.9, distrust=0.9)
    assert store.last_trusted_ancestor("m2", theta=0.3) is None


def test_reset_clears_store():
    store = ProvenanceStore()
    store.record(make_msg("m1"), 0.5, 0.0)
    store.reset()
    assert store.get("m1") is None
