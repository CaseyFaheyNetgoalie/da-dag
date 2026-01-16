"""
Decision tree extraction and visualization for Docassemble interviews.

Extracts decision trees from conditional logic (show if, enable if, etc.)
and provides visualization capabilities.
"""

import logging
from typing import Dict, List, Optional, Set

from .conditional import ConditionalDependency
from .exceptions import GraphError
from .graph import DependencyGraph
from .types import NodeKind

# Maximum depth for decision tree traversal (prevents stack overflow)
MAX_DECISION_TREE_DEPTH = 1000

logger = logging.getLogger(__name__)


class DecisionNode:
    """Represents a node in a decision tree."""
    
    def __init__(
        self,
        name: str,
        condition: Optional[str] = None,
        true_branch: Optional['DecisionNode'] = None,
        false_branch: Optional['DecisionNode'] = None,
        children: Optional[List['DecisionNode']] = None,
    ) -> None:
        """
        Initialize decision tree node.
        
        Args:
            name: Node name
            condition: Conditional expression (if any)
            true_branch: Node to follow if condition is true
            false_branch: Node to follow if condition is false
            children: List of child nodes
        """
        self.name = name
        self.condition = condition
        self.true_branch = true_branch
        self.false_branch = false_branch
        self.children = children or []
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization."""
        result = {"name": self.name}
        if self.condition:
            result["condition"] = self.condition
        if self.true_branch:
            result["true_branch"] = self.true_branch.to_dict()
        if self.false_branch:
            result["false_branch"] = self.false_branch.to_dict()
        if self.children:
            result["children"] = [child.to_dict() for child in self.children]
        return result


class DecisionTree:
    """Represents a decision tree extracted from conditional logic."""
    
    def __init__(self, root: DecisionNode, nodes: Dict[str, DecisionNode]) -> None:
        """
        Initialize decision tree.
        
        Args:
            root: Root node of the tree
            nodes: Dictionary of all nodes in the tree
        """
        self.root = root
        self.nodes = nodes
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "root": self.root.to_dict(),
            "nodes": {name: node.to_dict() for name, node in self.nodes.items()},
        }


def extract_decision_tree(
    graph: DependencyGraph,
    root_node_name: str,
    conditionals: Optional[Dict[str, List[ConditionalDependency]]] = None,
) -> Optional[DecisionTree]:
    """
    Extract decision tree from a dependency graph.
    
    Traverses conditional dependencies to build a decision tree structure.
    
    Args:
        graph: Dependency graph
        root_node_name: Name of root node to start from
        conditionals: Optional dictionary mapping node names to conditional dependencies
        
    Returns:
        DecisionTree or None if root node not found
    """
    if root_node_name not in graph.nodes:
        return None
    
    # Build decision nodes from conditional dependencies
    decision_nodes: Dict[str, DecisionNode] = {}
    
    # Traverse graph to build decision tree
    visited: Set[str] = set()
    
    def build_tree(node_name: str, depth: int = 0) -> DecisionNode:
        """
        Recursively build decision tree with depth limit.
        
        Args:
            node_name: Name of node to build tree for
            depth: Current recursion depth (for cycle detection)
            
        Returns:
            DecisionNode for the given node
            
        Raises:
            GraphError: If maximum depth exceeded
        """
        if depth > MAX_DECISION_TREE_DEPTH:
            raise GraphError(
                f"Maximum depth {MAX_DECISION_TREE_DEPTH} exceeded while building decision tree. "
                "This may indicate a very deep or malformed graph."
            )
        
        if node_name in visited:
            # Already processed, return existing node
            return decision_nodes.get(node_name, DecisionNode(name=node_name))
        
        visited.add(node_name)
        
        # Get or create decision node
        if node_name in decision_nodes:
            decision_node = decision_nodes[node_name]
        else:
            decision_node = DecisionNode(name=node_name)
            decision_nodes[node_name] = decision_node
        
        # Find conditional dependencies for this node
        if conditionals and node_name in conditionals:
            cond_deps = conditionals[node_name]
            for cond_dep in cond_deps:
                # Create decision branches based on condition
                decision_node.condition = cond_dep.condition
        
        # Find children (dependents) from graph - these are nodes that depend on this node
        dependents = graph.get_dependents(node_name)
        for dep_name in dependents:
            if dep_name not in visited:  # Only process if not already visited
                child = build_tree(dep_name)
                # Avoid duplicate children
                if not any(c.name == child.name for c in decision_node.children):
                    decision_node.children.append(child)
        
        return decision_node
    
    # Build tree starting from root
    root_decision = build_tree(root_node_name)
    
    return DecisionTree(root=root_decision, nodes=decision_nodes)


def decision_tree_to_dot(tree: DecisionTree, title: str = "Decision Tree") -> str:
    """
    Convert decision tree to GraphViz DOT format.
    
    Args:
        tree: Decision tree to convert
        title: Title for the graph
        
    Returns:
        DOT format string
    """
    lines = [f"digraph {title.replace(' ', '_')} {{"]
    lines.append(f'  label="{title}";')
    lines.append("  rankdir=TB;")
    lines.append("  node [shape=box];")
    
    def add_node(node: DecisionNode, parent: Optional[str] = None) -> None:
        """Recursively add nodes and edges."""
        node_id = node.name.replace(' ', '_').replace('-', '_')
        
        label = node.name
        if node.condition:
            label += f"\\n[{node.condition}]"
        
        lines.append(f'  "{node_id}" [label="{label}"];')
        
        if parent:
            lines.append(f'  "{parent}" -> "{node_id}";')
        
        if node.true_branch:
            add_node(node.true_branch, node_id)
        if node.false_branch:
            add_node(node.false_branch, node_id)
        for child in node.children:
            add_node(child, node_id)
    
    add_node(tree.root)
    lines.append("}")
    
    return "\n".join(lines)
