from src.runtime.policy_engine import PolicyEngine
from src.schema import PolicyDecision


def test_policy_pass():
    engine = PolicyEngine()
    assert engine.decide(0.10) == PolicyDecision.PASS


def test_policy_annotate():
    engine = PolicyEngine()
    assert engine.decide(0.30) == PolicyDecision.ANNOTATE


def test_policy_confirm():
    engine = PolicyEngine()
    assert engine.decide(0.55) == PolicyDecision.CONFIRM


def test_policy_quarantine():
    engine = PolicyEngine()
    assert engine.decide(0.80) == PolicyDecision.QUARANTINE
