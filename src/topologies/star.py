"""
Star topology: Hub coordinator with four spoke agents.
Hub edges have maximum betweenness; a single monitor on the hub
captures all traffic — this is what placement.py should find.
"""

from __future__ import annotations
import networkx as nx


class StarTopology:
    name = "star"

    agents: list[str] = ["hub", "agent_a", "agent_b", "agent_c", "agent_d"]

    edges: list[tuple[str, str]] = [
        ("hub", "agent_a"),
        ("hub", "agent_b"),
        ("hub", "agent_c"),
        ("hub", "agent_d"),
        ("agent_a", "hub"),
        ("agent_b", "hub"),
        ("agent_c", "hub"),
        ("agent_d", "hub"),
    ]

    schedule: list[tuple[str, str]] = [
        ("hub", "agent_a"),
        ("agent_a", "hub"),
        ("hub", "agent_b"),
        ("agent_b", "hub"),
        ("hub", "agent_c"),
        ("agent_c", "hub"),
        ("hub", "agent_d"),
        ("agent_d", "hub"),
    ]

    allowed_paths: set[tuple[str, str]] = {
        ("hub", "agent_a"), ("hub", "agent_b"),
        ("hub", "agent_c"), ("hub", "agent_d"),
        ("agent_a", "hub"), ("agent_b", "hub"),
        ("agent_c", "hub"), ("agent_d", "hub"),
        # transitive via hub
        ("agent_a", "agent_b"), ("agent_a", "agent_c"), ("agent_a", "agent_d"),
        ("agent_b", "agent_a"), ("agent_b", "agent_c"), ("agent_b", "agent_d"),
        ("agent_c", "agent_a"), ("agent_c", "agent_b"), ("agent_c", "agent_d"),
        ("agent_d", "agent_a"), ("agent_d", "agent_b"), ("agent_d", "agent_c"),
    }

    def to_graph(self) -> nx.DiGraph:
        G = nx.DiGraph()
        G.add_nodes_from(self.agents)
        G.add_edges_from(self.edges)
        return G
