"""
Advanced graph operations for DependencyGraph.

Provides topological sort, execution order, and other graph algorithms
that are commonly needed for legaltech workflows.
"""

from typing import List, Set, Optional

from .exceptions import CycleError, GraphError
from .graph import DependencyGraph


def topological_sort(graph: DependencyGraph) -> List[str]:
    """
    Return nodes in topological order (dependencies before dependents).
    
    Uses Kahn's algorithm for topological sorting.
    
    Args:
        graph: DependencyGraph to sort
        
    Returns:
        List of node names in topological order
        
    Raises:
        CycleError: If graph contains cycles (cannot be topologically sorted)
        
    Example:
        >>> graph = DependencyGraph(nodes, edges)
        >>> ordered = topological_sort(graph)
        >>> # Nodes are now in dependency order: dependencies come before dependents
    """
    if graph.has_cycles():
        cycles = graph.find_cycles()
        raise CycleError(
            "Cannot topological sort: graph contains cycles",
            cycles=cycles,
        )
    
    # Kahn's algorithm
    # Calculate in-degree for each node
    in_degree: dict[str, int] = {node: 0 for node in graph.nodes}
    for edge in graph.edges:
        in_degree[edge.to_node] += 1
    
    # Queue of nodes with no incoming edges
    queue: List[str] = [node for node, degree in in_degree.items() if degree == 0]
    result: List[str] = []
    
    while queue:
        # Remove node with no dependencies
        node = queue.pop(0)
        result.append(node)
        
        # Update in-degrees of dependents
        for dependent in graph.get_dependents(node):
            in_degree[dependent] -= 1
            if in_degree[dependent] == 0:
                queue.append(dependent)
    
    # If not all nodes processed, there's a cycle (shouldn't happen after has_cycles check)
    if len(result) != len(graph.nodes):
        raise CycleError(
            "Topological sort incomplete - possible cycles detected",
            cycles=graph.find_cycles(),
        )
    
    return result


def get_execution_order(
    graph: DependencyGraph,
    start_nodes: Optional[List[str]] = None,
) -> List[List[str]]:
    """
    Get execution order for interview execution as layers.
    
    Returns list of layers, where each layer can be executed in parallel.
    Earlier layers must complete before later layers.
    
    Args:
        graph: DependencyGraph to analyze
        start_nodes: Optional list of starting nodes. If None, uses graph roots.
        
    Returns:
        List of layers, where each layer is a list of node names that can
        execute in parallel
        
    Example:
        >>> graph = DependencyGraph(nodes, edges)
        >>> layers = get_execution_order(graph)
        >>> # layers[0] can execute first, then layers[1], etc.
        >>> for layer in layers:
        ...     execute_parallel([graph.nodes[n] for n in layer])
    """
    if start_nodes is None:
        start_nodes = graph.find_roots()
    
    # Validate start nodes
    for node_name in start_nodes:
        if node_name not in graph.nodes:
            raise GraphError(f"Start node '{node_name}' not found in graph", node_name=node_name)
    
    layers: List[List[str]] = []
    remaining: Set[str] = set(graph.nodes.keys())
    current_layer: Set[str] = set(start_nodes)
    
    while current_layer:
        # Add current layer to results
        layers.append(list(current_layer))
        remaining -= current_layer
        
        # Find next layer: nodes whose dependencies are all satisfied
        next_layer: Set[str] = set()
        satisfied_nodes: Set[str] = set().union(*[set(layer) for layer in layers])
        
        for node in remaining:
            deps = set(graph.get_dependencies(node))
            if deps.issubset(satisfied_nodes):
                next_layer.add(node)
        
        current_layer = next_layer
    
    # If nodes remain, there might be a cycle
    if remaining:
        # Check for cycles involving remaining nodes
        cycles = graph.find_cycles()
        if cycles:
            raise CycleError(
                f"Execution order incomplete: {len(remaining)} nodes remain. "
                "This may indicate cycles or disconnected components.",
                cycles=cycles,
            )
        # Otherwise, disconnected components
        layers.append(list(remaining))
    
    return layers


def get_dependency_layers(graph: DependencyGraph) -> List[List[str]]:
    """
    Group nodes by dependency depth (number of transitive dependencies).
    
    Useful for understanding the structure of complex dependency graphs.
    
    Args:
        graph: DependencyGraph to analyze
        
    Returns:
        List of layers, where layer[i] contains nodes with i transitive dependencies
        
    Example:
        >>> layers = get_dependency_layers(graph)
        >>> # layers[0] = nodes with 0 dependencies (roots)
        >>> # layers[1] = nodes with 1 dependency
        >>> # etc.
    """
    layers: List[List[str]] = []
    depth_map: dict[str, int] = {}
    
    def calculate_depth(node_name: str) -> int:
        """Calculate dependency depth for a node (memoized)."""
        if node_name in depth_map:
            return depth_map[node_name]
        
        deps = graph.get_dependencies(node_name)
        if not deps:
            depth = 0
        else:
            depth = max(calculate_depth(dep) for dep in deps) + 1
        
        depth_map[node_name] = depth
        return depth
    
    # Calculate depth for all nodes
    for node_name in graph.nodes:
        calculate_depth(node_name)
    
    # Group by depth
    max_depth = max(depth_map.values()) if depth_map else 0
    layers = [[] for _ in range(max_depth + 1)]
    
    for node_name, depth in depth_map.items():
        layers[depth].append(node_name)
    
    return layers
