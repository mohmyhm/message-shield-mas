"""Tests for topology-aware monitor placement."""

import pytest
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.topologies import get_topology
from src.runtime.placement import select_monitored_edges, coverage_ratio


def test_chain_budget_two_covers_all():
    topo = get_topology("chain")
    G = topo.to_graph()
    edges = select_monitored_edges(G, budget=2)
    assert len(edges) == 2
    assert edges == set(topo.edges)


def test_star_budget_one_selects_hub_edge():
    topo = get_topology("star")
    G = topo.to_graph()
    edges = select_monitored_edges(G, budget=1)
    assert len(edges) == 1
    src, dst = next(iter(edges))
    assert "hub" in (src, dst)


def test_mesh_budget_respects_size():
    topo = get_topology("mesh")
    G = topo.to_graph()
    budget = 4
    edges = select_monitored_edges(G, budget=budget)
    assert len(edges) <= budget


def test_zero_budget_returns_empty():
    topo = get_topology("chain")
    G = topo.to_graph()
    assert select_monitored_edges(G, budget=0) == set()


def test_coverage_ratio():
    topo = get_topology("chain")
    G = topo.to_graph()
    monitored = select_monitored_edges(G, budget=1)
    ratio = coverage_ratio(monitored, topo.edges)
    assert 0.0 < ratio <= 1.0


def test_star_full_budget_covers_all():
    topo = get_topology("star")
    G = topo.to_graph()
    edges = select_monitored_edges(G, budget=len(topo.edges))
    assert len(edges) == len(topo.edges)
