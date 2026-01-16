"""
Tests for decision tree extraction and visualization.
"""

import pytest
from docassemble_dag.decision_trees import (
    DecisionNode,
    DecisionTree,
    decision_tree_to_dot,
    extract_decision_tree,
)
from docassemble_dag.graph import DependencyGraph
from docassemble_dag.types import Node, NodeKind, Edge, DependencyType
from docassemble_dag.conditional import ConditionalDependency


class TestDecisionTree:
    """Test decision tree extraction."""
    
    def test_simple_decision_tree(self):
        """Test extracting simple decision tree."""
        nodes = {
            "root": Node("root", NodeKind.VARIABLE, "derived"),
            "child1": Node("child1", NodeKind.VARIABLE, "derived"),
            "child2": Node("child2", NodeKind.VARIABLE, "derived"),
        }
        edges = [
            Edge("root", "child1", DependencyType.IMPLICIT),
            Edge("root", "child2", DependencyType.IMPLICIT),
        ]
        graph = DependencyGraph(nodes, edges)
        
        tree = extract_decision_tree(graph, "root")
        
        assert tree is not None
        assert tree.root.name == "root"
        assert len(tree.root.children) == 2
    
    def test_tree_to_dict(self):
        """Test converting decision tree to dictionary."""
        node = DecisionNode("test", condition="age >= 18")
        tree = DecisionTree(node, {"test": node})
        
        tree_dict = tree.to_dict()
        
        assert "root" in tree_dict
        assert "nodes" in tree_dict
        assert tree_dict["root"]["name"] == "test"
        assert tree_dict["root"]["condition"] == "age >= 18"
    
    def test_decision_tree_to_dot(self):
        """Test converting decision tree to DOT format."""
        node = DecisionNode("root")
        tree = DecisionTree(node, {"root": node})
        
        dot = decision_tree_to_dot(tree, "Test Tree")
        
        assert "digraph" in dot
        assert "Test_Tree" in dot
        assert "root" in dot
