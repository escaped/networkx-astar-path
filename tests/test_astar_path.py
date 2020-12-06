from typing import Optional

import networkx as nx
import pytest
from networkx.algorithms.shortest_paths.astar import astar_path as original_astar_path
from networkx.algorithms.shortest_paths.astar import (
    astar_path_length as original_astar_path_length,
)

from networkx_astar_path import astar_path, astar_path_length
from networkx_astar_path.astar import Edge


@pytest.fixture
def graph() -> nx.DiGraph:
    """
    The example graph which defines paths from S to T.

    The weights have been chosen in a way that the path `S -> A2 -> B2 -> C2 -> T`
    is shorter when we simply sum up the weights, but longer if the weight of the
    current edge is divided by the weight of the previous edge.
    """
    graph = nx.DiGraph()

    graph.add_edges_from([('S', 'A1')], weight=-2)
    graph.add_edges_from([('A1', 'T')], weight=7)
    graph.add_edges_from(
        [('S', 'A2'), ('A2', 'B2'), ('B2', 'C2'), ('C2', 'T')], weight=1
    )

    return graph


def dependent_weight(
    graph: nx.Graph, prev_edge: Optional[Edge], cur_edge: Edge
) -> float:
    """
    Edge based weight function, which returns a weight value for the given edge.

    If we already visited an edge, the weight is the weight
    of the current edge divided by the previous edge.
    """
    if prev_edge is None:
        return graph.get_edge_data(*cur_edge)['weight']

    prev_weight = graph.get_edge_data(*prev_edge)['weight']
    cur_weight = graph.get_edge_data(*cur_edge)['weight']
    return cur_weight / prev_weight


def test_astar_path__simple_weight_function(graph: nx.DiGraph) -> None:
    """
    Test that the implementation finds the same shortest path as the original implementation.
    """
    expected_path = original_astar_path(graph, source='S', target='T', weight='weight')
    path = astar_path(graph, source='S', target='T', weight='weight')

    assert path == expected_path
    assert path == ['S', 'A2', 'B2', 'C2', 'T']


def test_astar_path__edge_based_path(graph: nx.DiGraph) -> None:
    """
    Make sure, we can provide a weight function based on the current and previous edge.
    """
    path = astar_path(graph, source='S', target='T', weight=dependent_weight)
    assert path == ['S', 'A1', 'T']


def test_astar_path_length__simple_weight_function(graph: nx.DiGraph) -> None:
    """
    Test that the implementation finds the same shortest path as the original implementation.
    """
    expected_length = original_astar_path_length(
        graph, source='S', target='T', weight='weight'
    )
    length = astar_path_length(graph, source='S', target='T', weight='weight')
    assert length == expected_length


def test_astar_path_length__edge_based_path(graph: nx.DiGraph) -> None:
    """
    Make sure, we can provide a weight function based on the current and previous edge.
    """
    length = astar_path_length(graph, source='S', target='T', weight=dependent_weight)
    assert length == -5.5
