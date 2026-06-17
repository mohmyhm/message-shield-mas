"""Tests for TrustLedger — Beta distribution per-agent distrust."""

import pytest
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.runtime.trust_ledger import TrustLedger


def test_initial_distrust_is_half():
    ledger = TrustLedger(alpha_init=1, beta_init=1)
    assert ledger.distrust("agent_x") == 0.5


def test_benign_updates_reduce_distrust():
    ledger = TrustLedger()
    for _ in range(9):
        ledger.update_benign("agent_a")
    # alpha=10, beta=1 → distrust = 1/11 ≈ 0.0909
    assert ledger.distrust("agent_a") < 0.15


def test_suspicious_updates_raise_distrust():
    ledger = TrustLedger()
    for _ in range(9):
        ledger.update_suspicious("agent_b")
    # alpha=1, beta=10 → distrust = 10/11 ≈ 0.909
    assert ledger.distrust("agent_b") > 0.85


def test_mixed_updates():
    ledger = TrustLedger()
    for _ in range(4):
        ledger.update_benign("agent_c")
    for _ in range(2):
        ledger.update_suspicious("agent_c")
    # alpha=5, beta=3 → trust = 5/8 = 0.625 → distrust = 0.375
    assert abs(ledger.distrust("agent_c") - 0.375) < 1e-6


def test_independent_agents():
    ledger = TrustLedger()
    ledger.update_suspicious("agent_x")
    ledger.update_benign("agent_y")
    assert ledger.distrust("agent_x") > ledger.distrust("agent_y")


def test_snapshot_covers_all_seen_agents():
    ledger = TrustLedger()
    ledger.update_benign("a1")
    ledger.update_suspicious("a2")
    snap = ledger.snapshot()
    assert "a1" in snap and "a2" in snap


def test_reset_clears_ledger():
    ledger = TrustLedger()
    ledger.update_benign("agent_z")
    ledger.reset()
    # After reset, back to prior
    assert ledger.distrust("agent_z") == 0.5
