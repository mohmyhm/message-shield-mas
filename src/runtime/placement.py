"""
Topology-aware monitor placement using edge betweenness centrality.

select_monitored_edges(graph, budget) returns the top-`budget` edges
ranked by betweenness. On a chain all edges tie; on star/mesh the
high-traffic edges score highest, giving disproportionate coverage.
"""

from __future__ import annotations
import networkx as nx


def select_monitored_edges(
    graph: nx.DiGraph,
    budget: int,
) -> set[tuple[str, str]]:
    """
    Return the `budget` edges with highest edge betweenness centrality.
    Ties are broken by edge insertion order (stable sort).
    """
    if budget <= 0:
        return set()

    centrality: dict[tuple, float] = nx.edge_betweenness_centrality(
        graph, normalized=True
    )
    ranked = sorted(centrality.items(), key=lambda kv: kv[1], reverse=True)
    return {edge for edge, _ in ranked[:budget]}


def coverage_ratio(
    monitored: set[tuple[str, str]],
    all_edges: list[tuple[str, str]],
) -> float:
    """Fraction of edges under monitoring."""
    if not all_edges:
        return 0.0
    return len(monitored & set(all_edges)) / len(all_edges)
