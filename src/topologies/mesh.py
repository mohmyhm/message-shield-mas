"""
Mesh topology: four agents fully connected (directed).
Multiple routing paths mean a single monitor can be bypassed;
placement must cover bridge edges. Containment hops will be higher
than chain/star unless the budget covers the right edges.
"""

from __future__ import annotations
import networkx as nx
from itertools import permutations


_AGENTS = ["alpha", "beta", "gamma", "delta"]


class MeshTopology:
    name = "mesh"

    agents: list[str] = _AGENTS

    edges: list[tuple[str, str]] = [
        (a, b) for a, b in permutations(_AGENTS, 2)
    ]

    # Round-robin schedule in alphabetical order
    schedule: list[tuple[str, str]] = [
        ("alpha", "beta"),
        ("beta", "gamma"),
        ("gamma", "delta"),
        ("delta", "alpha"),
        ("alpha", "gamma"),
        ("beta", "delta"),
    ]

    allowed_paths: set[tuple[str, str]] = set(permutations(_AGENTS, 2))

    def to_graph(self) -> nx.DiGraph:
        G = nx.DiGraph()
        G.add_nodes_from(self.agents)
        G.add_edges_from(self.edges)
        return G
