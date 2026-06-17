"""
Chain topology: Planner → Executor → Reviewer
All edges have equal betweenness; the degenerate baseline that shows
why topology-aware placement matters in star/mesh.
"""

from __future__ import annotations
import networkx as nx


class ChainTopology:
    name = "chain"

    agents: list[str] = ["planner", "executor", "reviewer"]

    edges: list[tuple[str, str]] = [
        ("planner", "executor"),
        ("executor", "reviewer"),
    ]

    # Ordered message-passing sequence
    schedule: list[tuple[str, str]] = [
        ("planner", "executor"),
        ("executor", "reviewer"),
    ]

    # All reachable (src, dst) pairs (direct + transitive)
    allowed_paths: set[tuple[str, str]] = {
        ("planner", "executor"),
        ("executor", "reviewer"),
        ("planner", "reviewer"),  # transitive
    }

    def to_graph(self) -> nx.DiGraph:
        G = nx.DiGraph()
        G.add_nodes_from(self.agents)
        G.add_edges_from(self.edges)
        return G
