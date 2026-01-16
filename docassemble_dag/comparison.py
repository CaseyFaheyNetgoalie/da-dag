"""
Graph comparison utility for change tracking and impact analysis.

Enables comparing two dependency graphs to identify:
- Added/removed/changed nodes
- Added/removed/changed edges
- Authority changes
- Impact analysis for downstream dependencies
"""

from dataclasses import dataclass, field
from typing import Dict, List, Set, Optional, Any

from .graph import DependencyGraph
from .types import Node, Edge, NodeKind


@dataclass
class GraphDiff:
    """
    Represents differences between two dependency graphs.
    
    Provides detailed information about what changed, enabling
    change tracking and impact analysis.
    """
    # Node changes
    added_nodes: List[Node] = field(default_factory=list)
    removed_nodes: List[Node] = field(default_factory=list)
    changed_nodes: List[Dict[str, Any]] = field(default_factory=list)
    
    # Edge changes
    added_edges: List[Edge] = field(default_factory=list)
    removed_edges: List[Edge] = field(default_factory=list)
    
    # Authority changes
    authority_changes: List[Dict[str, Any]] = field(default_factory=list)
    
    # Impact analysis
    affected_nodes: Set[str] = field(default_factory=set)  # Nodes affected by changes
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert diff to dictionary for JSON serialization."""
        return {
            "added_nodes": [self._node_to_dict(n) for n in self.added_nodes],
            "removed_nodes": [self._node_to_dict(n) for n in self.removed_nodes],
            "changed_nodes": self.changed_nodes,
            "added_edges": [self._edge_to_dict(e) for e in self.added_edges],
            "removed_edges": [self._edge_to_dict(e) for e in self.removed_edges],
            "authority_changes": self.authority_changes,
            "affected_nodes": sorted(list(self.affected_nodes)),
        }
    
    @staticmethod
    def _node_to_dict(node: Node) -> Dict[str, Any]:
        """Convert Node to dictionary."""
        return {
            "name": node.name,
            "kind": node.kind.value,
            "source": node.source,
            "authority": node.authority,
            "file_path": node.file_path,
            "line_number": node.line_number,
        }
    
    @staticmethod
    def _edge_to_dict(edge: Edge) -> Dict[str, Any]:
        """Convert Edge to dictionary."""
        return {
            "from_node": edge.from_node,
            "to_node": edge.to_node,
            "dep_type": edge.dep_type.value,
            "file_path": edge.file_path,
            "line_number": edge.line_number,
        }


def compare_graphs(old_graph: DependencyGraph, new_graph: DependencyGraph) -> GraphDiff:
    """
    Compare two dependency graphs and return differences.
    
    Identifies added, removed, and changed nodes and edges,
    as well as authority changes and affected downstream nodes.
    
    Args:
        old_graph: Previous version of the dependency graph
        new_graph: Current version of the dependency graph
        
    Returns:
        GraphDiff object containing all differences
        
    Example:
        >>> old = DependencyGraph(old_nodes, old_edges)
        >>> new = DependencyGraph(new_nodes, new_edges)
        >>> diff = compare_graphs(old, new)
        >>> print(f"Added {len(diff.added_nodes)} nodes")
    """
    diff = GraphDiff()
    
    old_node_names = set(old_graph.nodes.keys())
    new_node_names = set(new_graph.nodes.keys())
    
    # Find added nodes
    added_names = new_node_names - old_node_names
    diff.added_nodes = [new_graph.nodes[name] for name in added_names]
    
    # Find removed nodes
    removed_names = old_node_names - new_node_names
    diff.removed_nodes = [old_graph.nodes[name] for name in removed_names]
    
    # Find changed nodes (same name, different properties)
    common_names = old_node_names & new_node_names
    for name in common_names:
        old_node = old_graph.nodes[name]
        new_node = new_graph.nodes[name]
        
        # Check for changes in node properties
        changes: Dict[str, Any] = {"name": name}
        has_changes = False
        
        if old_node.kind != new_node.kind:
            changes["kind"] = {"old": old_node.kind.value, "new": new_node.kind.value}
            has_changes = True
        
        if old_node.source != new_node.source:
            changes["source"] = {"old": old_node.source, "new": new_node.source}
            has_changes = True
        
        if old_node.authority != new_node.authority:
            changes["authority"] = {"old": old_node.authority, "new": new_node.authority}
            has_changes = True
            # Track authority changes separately
            diff.authority_changes.append({
                "node": name,
                "old_authority": old_node.authority,
                "new_authority": new_node.authority,
            })
        
        if old_node.file_path != new_node.file_path:
            changes["file_path"] = {"old": old_node.file_path, "new": new_node.file_path}
            has_changes = True
        
        if old_node.line_number != new_node.line_number:
            changes["line_number"] = {"old": old_node.line_number, "new": new_node.line_number}
            has_changes = True
        
        if has_changes:
            diff.changed_nodes.append(changes)
    
    # Compare edges
    old_edges_set = _edges_to_set(old_graph.edges)
    new_edges_set = _edges_to_set(new_graph.edges)
    
    # Find added edges
    added_edge_keys = new_edges_set - old_edges_set
    diff.added_edges = [
        edge for edge in new_graph.edges
        if _edge_to_key(edge) in added_edge_keys
    ]
    
    # Find removed edges
    removed_edge_keys = old_edges_set - new_edges_set
    diff.removed_edges = [
        edge for edge in old_graph.edges
        if _edge_to_key(edge) in removed_edge_keys
    ]
    
    # Calculate affected nodes (downstream impact analysis)
    # Nodes affected by:
    # 1. Removed nodes (anything depending on them)
    # 2. Removed edges (target nodes of removed dependencies)
    # 3. Changed nodes (transitive dependents)
    affected: Set[str] = set()
    
    # Find nodes that depend on removed nodes
    # Only if removed nodes exist in new graph (they shouldn't, but check anyway)
    for removed_name in removed_names:
        if removed_name in new_graph.nodes:
            dependents = new_graph.get_transitive_dependents(removed_name)
            affected.update(dependents)
    
    # Find nodes affected by removed edges
    for removed_edge in diff.removed_edges:
        if removed_edge.to_node in new_node_names:
            affected.add(removed_edge.to_node)
            # Also include transitive dependents
            dependents = new_graph.get_transitive_dependents(removed_edge.to_node)
            affected.update(dependents)
    
    # Find nodes affected by changed nodes (authority changes, etc.)
    for change in diff.changed_nodes:
        node_name = change["name"]
        if node_name in new_node_names:
            affected.add(node_name)
            # Include transitive dependents
            dependents = new_graph.get_transitive_dependents(node_name)
            affected.update(dependents)
    
    diff.affected_nodes = affected
    
    return diff


def _edge_to_key(edge: Edge) -> tuple:
    """Convert Edge to a hashable key for set operations."""
    return (edge.from_node, edge.to_node, edge.dep_type.value)


def _edges_to_set(edges: List[Edge]) -> Set[tuple]:
    """Convert list of edges to set of keys."""
    return {_edge_to_key(edge) for edge in edges}


def get_change_impact(
    graph: DependencyGraph,
    changed_node_names: Set[str]
) -> Dict[str, List[str]]:
    """
    Calculate impact of changes on downstream nodes.
    
    For each changed node, returns list of nodes that transitively
    depend on it (impact analysis).
    
    Args:
        graph: Dependency graph to analyze
        changed_node_names: Set of node names that changed
        
    Returns:
        Dictionary mapping changed node name to list of affected dependent nodes
        
    Example:
        >>> impact = get_change_impact(graph, {"age", "income"})
        >>> print(impact["age"])  # ["eligibility", "final_result"]
    """
    impact: Dict[str, List[str]] = {}
    
    for node_name in changed_node_names:
        if node_name not in graph.nodes:
            continue
        
        dependents = graph.get_transitive_dependents(node_name)
        impact[node_name] = sorted(list(dependents))
    
    return impact
