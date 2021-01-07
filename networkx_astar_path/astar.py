"""
Shortest paths and path lengths using the A* ("A star") algorithm.
"""
from heapq import heappop, heappush
from itertools import chain, count
from typing import Any, Callable, Dict, List, Optional, Sequence, Tuple, Union

import networkx as nx

__all__ = ["astar_path", "astar_path_length"]


Node = Any
Edge = Tuple[Node, Node]
WeightFunction = Callable[[nx.Graph, Optional[Edge], Edge], float]
HeuristicFunction = Callable[[Node, Node], float]


def _weight_function(
    graph: nx.Graph, weight: Union[str, WeightFunction]
) -> WeightFunction:
    """Returns a function that returns the weight of an edge.
    The returned function is specifically suitable for input to
    functions :func:`_dijkstra` and :func:`_bellman_ford_relaxation`.
    Parameters
    ----------
    graph : NetworkX graph.
    weight : string or function
        If it is callable, `weight` itself is returned. If it is a string,
        it is assumed to be the name of the edge attribute that represents
        the weight of an edge. In that case, a function is returned that
        gets the edge weight according to the specified edge attribute.
    Returns
    -------
    function
        This function returns a callable that accepts exactly three inputs:
        a node, an node adjacent to the first one, and the edge attribute
        dictionary for the eedge joining those nodes. That function returns
        a number representing the weight of an edge.
    If `graph` is a multigraph, and `weight` is not callable, the
    minimum edge weight over all parallel edges is returned. If any edge
    does not have an attribute with key `weight`, it is assumed to
    have weight one.
    """
    if callable(weight):
        return weight

    if graph.is_multigraph():
        raise NotImplementedError(
            "Automatic generation of a weight function for a MultiDiGraph is currently not supported."
        )

    weight_name = weight
    return lambda _G, prev_edge, cur_edge: _G.get_edge_data(*cur_edge)[weight_name]


def _default_heuristic(u: Node, v: Node) -> float:
    return 0


def astar_path(  # noqa: C901
    graph: nx.Graph,
    source: Node,
    target: Node,
    heuristic: Optional[HeuristicFunction] = None,
    weight: Union[str, WeightFunction] = "weight",
) -> Sequence[Node]:
    """Returns a list of nodes in a shortest path between source and target
    using the A* ("A-star") algorithm.

    There may be more than one shortest path.  This returns only one.

    Parameters
    ----------
    graph : NetworkX graph

    source : node
       Starting node for path

    target : node
       Ending node for path

    heuristic : function
       A function to evaluate the estimate of the distance
       from the a node to the target.  The function takes
       two nodes arguments and must return a number.

    weight : string or function
       If this is a string, then edge weights will be accessed via the
       edge attribute with this key (that is, the weight of the edge
       joining `u` to `v` will be ``graph.edges[u, v][weight]``). If no
       such edge attribute exists, the weight of the edge is assumed to
       be one.
       If this is a function, the weight of an edge is the value
       returned by the function. The function must accept exactly three
       positional arguments: the graph itself and tuples of the previous and
       the current edge. The function must return a number.

    Raises
    ------
    NetworkXNoPath
        If no path exists between source and target.

    Examples
    --------
    >>> graph = nx.path_graph(5)
    >>> print(nx.astar_path(graph, 0, 4))
    [0, 1, 2, 3, 4]
    >>> graph = nx.grid_graph(dim=[3, 3])  # nodes are two-tuples (x,y)
    >>> nx.set_edge_attributes(graph, {e: e[1][0] * 2 for e in graph.edges()}, "cost")
    >>> def dist(a, b):
    ...     (x1, y1) = a
    ...     (x2, y2) = b
    ...     return ((x1 - x2) ** 2 + (y1 - y2) ** 2) ** 0.5
    >>> print(nx.astar_path(graph, (0, 0), (2, 2), heuristic=dist, weight="cost"))
    [(0, 0), (0, 1), (0, 2), (1, 2), (2, 2)]


    See Also
    --------
    shortest_path, dijkstra_path

    """
    if source not in graph or target not in graph:
        msg = f"Either source {source} or target {target} is not in graph"
        raise nx.NodeNotFound(msg)

    if heuristic is None:
        # The default heuristic is h=0 - same as Dijkstra's algorithm
        heuristic = _default_heuristic

    push = heappush
    pop = heappop
    weight = _weight_function(graph, weight)

    # The queue stores priority, node, cost to reach, the parent and the explored path.
    # Uses Python heapq to keep in priority order.
    # Add a counter to the queue to prevent the underlying heap from
    # attempting to compare the nodes themselves. The hash breaks ties in the
    # priority and is guaranteed unique for all nodes in the graph.
    c = count()
    queue: List[Tuple[int, int, Node, float, Node, List[Node]]] = [
        (0, next(c), source, 0, None, [source])
    ]

    # Maps enqueued nodes to distance of discovered paths and the
    # computed heuristics to target. We avoid computing the heuristics
    # more than once and inserting the node into the queue too many times.
    enqueued: Dict[Node, Tuple[float, float]] = {}
    # Maps explored nodes to parent closest to the source.
    explored: Dict[Node, Node] = {}

    while queue:
        # Pop the smallest item from queue.
        _, __, curnode, dist, parent, explored_path = pop(queue)

        if curnode == target:
            path = [curnode]
            node = parent
            while node is not None:
                path.append(node)
                node = explored[node]
            path.reverse()
            return path

        if curnode in explored:
            # Do not override the parent of starting node
            if explored[curnode] is None:
                continue

            # Skip bad paths that were enqueued before finding a better one
            qcost, h = enqueued[curnode]
            if qcost < dist:
                continue

        explored[curnode] = parent

        for neighbor, w in graph[curnode].items():
            cur_edge = (curnode, neighbor)
            try:
                prev_edge: Optional[Edge] = (explored_path[-2], curnode)
            except IndexError:
                prev_edge = None
            ncost = dist + weight(graph, prev_edge, cur_edge)

            if neighbor in enqueued:
                qcost, h = enqueued[neighbor]
                # if qcost <= ncost, a less costly path from the
                # neighbor to the source was already determined.
                # Therefore, we won't attempt to push this neighbor
                # to the queue
                if qcost <= ncost:
                    continue
            else:
                h = heuristic(neighbor, target)
            enqueued[neighbor] = ncost, h
            push(  # type: ignore
                queue,
                (
                    ncost + h,
                    next(c),
                    neighbor,
                    ncost,
                    curnode,
                    explored_path + [neighbor],
                ),
            )

    raise nx.NetworkXNoPath(f"Node {target} not reachable from {source}")


def astar_path_length(
    graph: nx.Graph,
    source: Node,
    target: Node,
    heuristic: Optional[HeuristicFunction] = None,
    weight: Union[str, WeightFunction] = "weight",
) -> float:
    """Returns the length of the shortest path between source and target using
    the A* ("A-star") algorithm.

    Parameters
    ----------
    graph : NetworkX graph

    source : node
       Starting node for path

    target : node
       Ending node for path

    heuristic : function
       A function to evaluate the estimate of the distance
       from the a node to the target.  The function takes
       two nodes arguments and must return a number.

    Raises
    ------
    NetworkXNoPath
        If no path exists between source and target.

    See Also
    --------
    astar_path

    """
    if source not in graph or target not in graph:
        msg = f"Either source {source} or target {target} is not in graph"
        raise nx.NodeNotFound(msg)

    weight = _weight_function(graph, weight)
    path = astar_path(graph, source, target, heuristic, weight)
    # The weight function looks at the current and the previous edge.
    # Since, when we visit our first edge, we haven't visited any other edge beforehand.
    # This is indicated by an edge with the value `None`.
    path_edges = list(chain([None], list(zip(path[:-1], path[1:]))))

    # ignoring type: we manually added a node and that node will only be passed in as u, which is valid
    return sum(weight(graph, u, v) for u, v in zip(path_edges[:-1], path_edges[1:]))  # type: ignore
