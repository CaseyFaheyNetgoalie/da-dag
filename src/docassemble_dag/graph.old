"""
Dependency graph construction and validation.

Builds an explicit DAG from nodes and edges, with cycle detection.
"""

from collections import defaultdict
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Set

from .exceptions import CycleError, GraphError
from .types import Edge, Node, NodeKind

if TYPE_CHECKING:
    from .graph_operations import get_dependency_layers, get_execution_order, topological_sort


class DependencyGraph:
    """
    Explicit directed acyclic graph of dependencies.
    
    Provides graph operations and validation, with cycle detection.
    Uses memoization for efficient transitive dependency queries.
    """
    
    def __init__(self, nodes: Dict[str, Node], edges: List[Edge]):
        """
        Initialize graph from nodes and edges.
        
        Args:
            nodes: Dictionary mapping node name to Node
            edges: List of Edge objects
            
        Raises:
            GraphError: If nodes or edges are invalid
        """
        if not isinstance(nodes, dict):
            raise GraphError(f"nodes must be a dictionary, got {type(nodes).__name__}")
        
        if not isinstance(edges, list):
            raise GraphError(f"edges must be a list, got {type(edges).__name__}")
        
        # Validate all edges reference valid nodes
        node_names = set(nodes.keys())
        for edge in edges:
            if not isinstance(edge, Edge):
                raise GraphError(f"All edges must be Edge objects, got {type(edge).__name__}")
            if edge.from_node not in node_names:
                raise GraphError(
                    f"Edge references non-existent node '{edge.from_node}'",
                    node_name=edge.from_node,
                )
            if edge.to_node not in node_names:
                raise GraphError(
                    f"Edge references non-existent node '{edge.to_node}'",
                    node_name=edge.to_node,
                )
        
        self.nodes = nodes
        self.edges = edges
        
        # Build adjacency lists for efficient traversal
        # adj: from_node -> list of to_nodes (dependencies flow from -> to)
        # rev: to_node -> list of from_nodes (reverse for upstream queries)
        self.adj: Dict[str, List[str]] = defaultdict(list)
        self.rev: Dict[str, List[str]] = defaultdict(list)
        
        for edge in edges:
            self.adj[edge.from_node].append(edge.to_node)
            self.rev[edge.to_node].append(edge.from_node)
        
        # Cache for transitive closures (invalidate on graph modification)
        self._transitive_deps_cache: Dict[str, Set[str]] = {}
        self._transitive_dependents_cache: Dict[str, Set[str]] = {}
        self._cache_valid = True
    
    def find_cycles(self) -> List[List[str]]:
        """
        Detect cycles in the dependency graph using DFS.
        
        Returns:
            List of cycles, where each cycle is a list of node names
        """
        visited: Set[str] = set()
        stack: Set[str] = set()  # Track current path
        cycles: List[List[str]] = []
        
        def dfs(node: str, path: List[str]) -> None:
            """Depth-first search to find cycles."""
            if node in stack:
                # Found a cycle: from first occurrence of node to current
                cycle_start = path.index(node)
                cycle = path[cycle_start:] + [node]
                cycles.append(cycle)
                return
            
            if node in visited:
                return
            
            visited.add(node)
            stack.add(node)
            
            # Explore neighbors (dependencies of this node)
            for neighbor in self.adj.get(node, []):
                dfs(neighbor, path + [node])
            
            stack.remove(node)
        
        # Check all nodes (handles disconnected components)
        for node_name in self.nodes:
            if node_name not in visited:
                dfs(node_name, [])
        
        return cycles
    
    def has_cycles(self) -> bool:
        """Check if graph contains any cycles."""
        return len(self.find_cycles()) > 0
    
    def get_dependencies(self, node_name: str) -> List[str]:
        """
        Get direct dependencies of a node (nodes it depends on).
        
        Args:
            node_name: Name of the node
        
        Returns:
            List of node names that this node depends on
        """
        return self.rev.get(node_name, [])
    
    def get_dependents(self, node_name: str) -> List[str]:
        """
        Get direct dependents of a node (nodes that depend on it).
        
        Args:
            node_name: Name of the node
        
        Returns:
            List of node names that depend on this node
        """
        return self.adj.get(node_name, [])
    
    def get_transitive_dependencies(self, node_name: str) -> Set[str]:
        """
        Get all transitive dependencies of a node (direct + indirect).
        
        Similar to GUAC's dependency traversal queries.
        
        Args:
            node_name: Name of the node
        
        Returns:
            Set of all node names that this node (transitively) depends on
        """
        visited: Set[str] = set()
        result: Set[str] = set()
        
        def dfs(node: str):
            """Depth-first search to collect all dependencies."""
            if node in visited:
                return
            visited.add(node)
            
            for dep in self.rev.get(node, []):
                result.add(dep)
                dfs(dep)
        
        dfs(node_name)
        return result
    
    def get_transitive_dependents(self, node_name: str) -> Set[str]:
        """
        Get all transitive dependents of a node (direct + indirect).
        
        Similar to GUAC's reverse dependency queries.
        Uses memoization for O(1) lookup after first calculation.
        
        Args:
            node_name: Name of the node
        
        Returns:
            Set of all node names that (transitively) depend on this node
            
        Raises:
            GraphError: If node_name is not in the graph
        """
        if node_name not in self.nodes:
            raise GraphError(f"Node '{node_name}' not found in graph", node_name=node_name)
        
        # Check cache
        if self._cache_valid and node_name in self._transitive_dependents_cache:
            return self._transitive_dependents_cache[node_name]
        
        # Calculate transitive dependents
        visited: Set[str] = set()
        result: Set[str] = set()
        MAX_DEPTH = 10000  # Prevent infinite recursion on malformed graphs
        
        def dfs(node: str, depth: int = 0):
            """Depth-first search to collect all dependents with depth limit."""
            if depth > MAX_DEPTH:
                raise GraphError(
                    f"Maximum depth {MAX_DEPTH} exceeded while traversing dependents of '{node_name}'. "
                    "This may indicate a very deep or malformed graph."
                )
            
            if node in visited:
                return
            visited.add(node)
            
            for dependent in self.adj.get(node, []):
                result.add(dependent)
                dfs(dependent, depth + 1)
        
        dfs(node_name)
        
        # Cache result
        self._transitive_dependents_cache[node_name] = result
        
        return result
    
    def find_path(self, from_node: str, to_node: str) -> Optional[List[str]]:
        """
        Find a dependency path from one node to another.
        
        Similar to GUAC's path queries for understanding relationships.
        Finds a path following the dependency chain: from_node -> ... -> to_node
        where each step follows "what depends on the current node".
        
        Args:
            from_node: Starting node name
            to_node: Target node name
        
        Returns:
            List of node names forming the path, or None if no path exists
        """
        if from_node not in self.nodes or to_node not in self.nodes:
            return None
        
        if from_node == to_node:
            return [from_node]
        
        # BFS to find shortest path following dependency chain
        # We follow adj (dependents) to traverse forward in the dependency chain
        queue: List[tuple] = [(from_node, [from_node])]
        visited: Set[str] = {from_node}
        
        while queue:
            current, path = queue.pop(0)
            
            # Check all nodes that depend on current (follow dependency chain forward)
            for neighbor in self.adj.get(current, []):
                if neighbor == to_node:
                    return path + [neighbor]
                
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append((neighbor, path + [neighbor]))
        
        return None
    
    def find_nodes_by_kind(self, kind: NodeKind) -> List[str]:
        """
        Find all nodes of a specific kind.
        
        Similar to GUAC's filtering queries by artifact type.
        
        Args:
            kind: NodeKind enum value
        
        Returns:
            List of node names matching the kind
        """
        return [name for name, node in self.nodes.items() if node.kind == kind]
    
    def find_roots(self) -> List[str]:
        """
        Find root nodes (nodes with no dependencies).
        
        These are entry points in the dependency graph, similar to GUAC's
        identification of source artifacts.
        
        Returns:
            List of root node names
        """
        return [name for name in self.nodes if len(self.rev.get(name, [])) == 0]
    
    def find_orphans(self) -> List[str]:
        """
        Find orphan nodes (nodes with no dependencies and no dependents).
        
        These are isolated nodes that may indicate unused code or missing connections.
        
        Returns:
            List of orphan node names
        """
        return [
            name for name in self.nodes
            if len(self.rev.get(name, [])) == 0 and len(self.adj.get(name, [])) == 0
        ]
    
    def to_dot(self, title: str = "Dependency Graph") -> str:
        """
        Export graph to DOT format for GraphViz visualization.
        
        Inspired by GUAC's visualization capabilities. This enables
        generating visual graphs using tools like GraphViz or online renderers.
        
        Args:
            title: Title for the graph
        
        Returns:
            DOT format string
        """
        lines = [f'digraph "{title}" {{']
        lines.append('  rankdir=LR;')
        lines.append('  node [shape=box, style=rounded];')
        lines.append('')
        
        # Add nodes with styling based on kind
        for node in self.nodes.values():
            color_map = {
                "variable": "lightblue",
                "question": "lightgreen",
                "rule": "lightyellow"
            }
            color = color_map.get(node.kind.value, "lightgray")
            
            label = f'{node.name}\\n[{node.kind.value}]'
            if node.authority:
                label += f'\\n{node.authority[:30]}...'
            
            lines.append(f'  "{node.name}" [label="{label}", fillcolor="{color}", style="rounded,filled"];')
        
        lines.append('')
        
        # Add edges with styling based on type
        for edge in self.edges:
            style = "solid" if edge.dep_type.value == "explicit" else "dashed"
            lines.append(f'  "{edge.from_node}" -> "{edge.to_node}" [style={style}, label="{edge.dep_type.value}"];')
        
        lines.append('}')
        return '\n'.join(lines)
    
    def to_graphml(self, graph_id: str = "dag") -> str:
        """
        Export graph to GraphML format (standard XML graph format).
        
        GraphML is widely supported by graph visualization tools and can be
        imported into systems like GUAC for further analysis.
        
        Args:
            graph_id: Identifier for the graph
        
        Returns:
            GraphML XML string
        """
        lines = ['<?xml version="1.0" encoding="UTF-8"?>']
        lines.append('<graphml xmlns="http://graphml.graphdrawing.org/xmlns"')
        lines.append('         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"')
        lines.append('         xsi:schemaLocation="http://graphml.graphdrawing.org/xmlns')
        lines.append('         http://graphml.graphdrawing.org/xmlns/1.0/graphml.xsd">')
        lines.append('')
        
        # Define attribute keys for nodes
        lines.append('  <!-- Node attributes -->')
        lines.append('  <key id="kind" for="node" attr.name="kind" attr.type="string"/>')
        lines.append('  <key id="source" for="node" attr.name="source" attr.type="string"/>')
        lines.append('  <key id="authority" for="node" attr.name="authority" attr.type="string"/>')
        lines.append('  <key id="file_path" for="node" attr.name="file_path" attr.type="string"/>')
        lines.append('  <key id="line_number" for="node" attr.name="line_number" attr.type="int"/>')
        lines.append('')
        
        # Define attribute keys for edges
        lines.append('  <!-- Edge attributes -->')
        lines.append('  <key id="dep_type" for="edge" attr.name="type" attr.type="string"/>')
        lines.append('  <key id="edge_file_path" for="edge" attr.name="file_path" attr.type="string"/>')
        lines.append('  <key id="edge_line_number" for="edge" attr.name="line_number" attr.type="int"/>')
        lines.append('')
        
        # Graph element
        lines.append(f'  <graph id="{graph_id}" edgedefault="directed">')
        lines.append('')
        
        # Add nodes
        for node in self.nodes.values():
            lines.append(f'    <node id="{self._escape_xml(node.name)}">')
            lines.append(f'      <data key="kind">{self._escape_xml(node.kind.value)}</data>')
            lines.append(f'      <data key="source">{self._escape_xml(node.source)}</data>')
            if node.authority:
                lines.append(f'      <data key="authority">{self._escape_xml(node.authority)}</data>')
            if node.file_path:
                lines.append(f'      <data key="file_path">{self._escape_xml(node.file_path)}</data>')
            if node.line_number is not None:
                lines.append(f'      <data key="line_number">{node.line_number}</data>')
            lines.append('    </node>')
        
        lines.append('')
        
        # Add edges
        for i, edge in enumerate(self.edges):
            lines.append(f'    <edge id="e{i}" source="{self._escape_xml(edge.from_node)}" target="{self._escape_xml(edge.to_node)}">')
            lines.append(f'      <data key="dep_type">{self._escape_xml(edge.dep_type.value)}</data>')
            if edge.file_path:
                lines.append(f'      <data key="edge_file_path">{self._escape_xml(edge.file_path)}</data>')
            if edge.line_number is not None:
                lines.append(f'      <data key="edge_line_number">{edge.line_number}</data>')
            lines.append('    </edge>')
        
        lines.append('  </graph>')
        lines.append('</graphml>')
        
        return '\n'.join(lines)
    
    def _escape_xml(self, text: str) -> str:
        """Escape XML special characters."""
        if not isinstance(text, str):
            text = str(text)
        return (text.replace('&', '&amp;')
                   .replace('<', '&lt;')
                   .replace('>', '&gt;')
                   .replace('"', '&quot;')
                   .replace("'", '&apos;'))
    
    def to_html(
        self,
        output_path: Optional[Path] = None,
        title: str = "Dependency Graph",
        width: int = 1200,
        height: int = 800,
    ) -> str:
        """
        Generate interactive HTML visualization of the dependency graph.
        
        Args:
            output_path: Optional path to save HTML file
            title: Title for the visualization
            width: Canvas width in pixels
            height: Canvas height in pixels
            
        Returns:
            HTML content as string
        """
        from .html_viewer import to_html
        return to_html(self, output_path, title, width, height)
    
    def to_json_struct(self) -> Dict[str, Any]:
        """
        Convert graph to JSON-serializable dictionary.
        
        Returns:
            Dictionary with 'nodes' and 'edges' keys, ready for JSON serialization
        """
        nodes_list = [
            {
                "name": node.name,
                "kind": node.kind.value,
                "source": node.source,
                "authority": node.authority,
                "file_path": node.file_path,
                "line_number": node.line_number,
                "metadata": node.metadata if node.metadata else None
            }
            for node in self.nodes.values()
        ]
        
        edges_list = [
            {
                "from": edge.from_node,
                "to": edge.to_node,
                "type": edge.dep_type.value,
                "file_path": edge.file_path,
                "line_number": edge.line_number,
                "metadata": edge.metadata if edge.metadata else None
            }
            for edge in self.edges
        ]
        
        return {
            "nodes": nodes_list,
            "edges": edges_list
        }
    
    def topological_sort(self) -> List[str]:
        """
        Return nodes in topological order (dependencies before dependents).
        
        Convenience method for topological_sort(graph).
        
        Returns:
            List of node names in topological order
            
        Raises:
            CycleError: If graph contains cycles
        """
        # Import here to avoid circular dependency
        from .graph_operations import topological_sort
        return topological_sort(self)
    
    def get_execution_order(self, start_nodes: Optional[List[str]] = None) -> List[List[str]]:
        """
        Get execution order as layers (for parallel execution).
        
        Convenience method for get_execution_order(graph).
        
        Args:
            start_nodes: Optional starting nodes. If None, uses graph roots.
            
        Returns:
            List of layers, where each layer can execute in parallel
        """
        # Import here to avoid circular dependency
        from .graph_operations import get_execution_order
        return get_execution_order(self, start_nodes)
    
    def get_dependency_layers(self) -> List[List[str]]:
        """
        Group nodes by dependency depth.
        
        Convenience method for get_dependency_layers(graph).
        
        Returns:
            List of layers, where layer[i] contains nodes with i dependencies
        """
        # Import here to avoid circular dependency
        from .graph_operations import get_dependency_layers
        return get_dependency_layers(self)