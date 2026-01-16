"""
Tests for graph comparison utility.
"""

import pytest
from docassemble_dag.comparison import (
    compare_graphs,
    get_change_impact,
    GraphDiff,
)
from docassemble_dag.graph import DependencyGraph
from docassemble_dag.types import Node, NodeKind, Edge, DependencyType


class TestGraphComparison:
    """Test graph comparison functionality."""
    
    def test_compare_identical_graphs(self):
        """Test comparing identical graphs."""
        nodes = {
            "x": Node("x", NodeKind.VARIABLE, "derived"),
            "y": Node("y", NodeKind.VARIABLE, "derived"),
        }
        edges = [Edge("x", "y", DependencyType.IMPLICIT)]
        
        graph = DependencyGraph(nodes, edges)
        diff = compare_graphs(graph, graph)
        
        assert len(diff.added_nodes) == 0
        assert len(diff.removed_nodes) == 0
        assert len(diff.changed_nodes) == 0
        assert len(diff.added_edges) == 0
        assert len(diff.removed_edges) == 0
    
    def test_compare_added_nodes(self):
        """Test detecting added nodes."""
        old_nodes = {"x": Node("x", NodeKind.VARIABLE, "derived")}
        new_nodes = {
            "x": Node("x", NodeKind.VARIABLE, "derived"),
            "y": Node("y", NodeKind.VARIABLE, "derived"),
        }
        
        old_graph = DependencyGraph(old_nodes, [])
        new_graph = DependencyGraph(new_nodes, [])
        
        diff = compare_graphs(old_graph, new_graph)
        
        assert len(diff.added_nodes) == 1
        assert diff.added_nodes[0].name == "y"
    
    def test_compare_removed_nodes(self):
        """Test detecting removed nodes."""
        old_nodes = {
            "x": Node("x", NodeKind.VARIABLE, "derived"),
            "y": Node("y", NodeKind.VARIABLE, "derived"),
        }
        new_nodes = {"x": Node("x", NodeKind.VARIABLE, "derived")}
        
        old_graph = DependencyGraph(old_nodes, [])
        new_graph = DependencyGraph(new_nodes, [])
        
        diff = compare_graphs(old_graph, new_graph)
        
        assert len(diff.removed_nodes) == 1
        assert diff.removed_nodes[0].name == "y"
    
    def test_compare_changed_nodes(self):
        """Test detecting changed node properties."""
        old_nodes = {
            "x": Node("x", NodeKind.VARIABLE, "derived", authority="Old Law")
        }
        new_nodes = {
            "x": Node("x", NodeKind.VARIABLE, "derived", authority="New Law")
        }
        
        old_graph = DependencyGraph(old_nodes, [])
        new_graph = DependencyGraph(new_nodes, [])
        
        diff = compare_graphs(old_graph, new_graph)
        
        assert len(diff.changed_nodes) == 1
        assert diff.changed_nodes[0]["name"] == "x"
        assert diff.changed_nodes[0]["authority"]["old"] == "Old Law"
        assert diff.changed_nodes[0]["authority"]["new"] == "New Law"
        assert len(diff.authority_changes) == 1
    
    def test_compare_added_edges(self):
        """Test detecting added edges."""
        nodes = {
            "x": Node("x", NodeKind.VARIABLE, "derived"),
            "y": Node("y", NodeKind.VARIABLE, "derived"),
        }
        
        old_graph = DependencyGraph(nodes, [])
        new_graph = DependencyGraph(nodes, [Edge("x", "y", DependencyType.IMPLICIT)])
        
        diff = compare_graphs(old_graph, new_graph)
        
        assert len(diff.added_edges) == 1
        assert diff.added_edges[0].from_node == "x"
        assert diff.added_edges[0].to_node == "y"
    
    def test_compare_removed_edges(self):
        """Test detecting removed edges."""
        nodes = {
            "x": Node("x", NodeKind.VARIABLE, "derived"),
            "y": Node("y", NodeKind.VARIABLE, "derived"),
        }
        
        old_graph = DependencyGraph(nodes, [Edge("x", "y", DependencyType.IMPLICIT)])
        new_graph = DependencyGraph(nodes, [])
        
        diff = compare_graphs(old_graph, new_graph)
        
        assert len(diff.removed_edges) == 1
        assert diff.removed_edges[0].from_node == "x"
        assert diff.removed_edges[0].to_node == "y"
    
    def test_affected_nodes_calculation(self):
        """Test calculation of affected nodes."""
        old_nodes = {
            "x": Node("x", NodeKind.VARIABLE, "derived"),
            "y": Node("y", NodeKind.VARIABLE, "derived"),
            "z": Node("z", NodeKind.VARIABLE, "derived"),
        }
        old_edges = [
            Edge("x", "y", DependencyType.IMPLICIT),
            Edge("y", "z", DependencyType.IMPLICIT),
        ]
        
        new_nodes = {
            "y": Node("y", NodeKind.VARIABLE, "derived"),
            "z": Node("z", NodeKind.VARIABLE, "derived"),
        }
        new_edges = [Edge("y", "z", DependencyType.IMPLICIT)]
        
        old_graph = DependencyGraph(old_nodes, old_edges)
        new_graph = DependencyGraph(new_nodes, new_edges)
        
        diff = compare_graphs(old_graph, new_graph)
        
        # z depends on y, so removing x->y edge affects y and z
        assert "z" in diff.affected_nodes  # z depends on y
    
    def test_diff_to_dict(self):
        """Test converting diff to dictionary."""
        old_nodes = {"x": Node("x", NodeKind.VARIABLE, "derived")}
        new_nodes = {"y": Node("y", NodeKind.VARIABLE, "derived")}
        
        old_graph = DependencyGraph(old_nodes, [])
        new_graph = DependencyGraph(new_nodes, [])
        
        diff = compare_graphs(old_graph, new_graph)
        diff_dict = diff.to_dict()
        
        assert "added_nodes" in diff_dict
        assert "removed_nodes" in diff_dict
        assert "changed_nodes" in diff_dict
        assert "affected_nodes" in diff_dict


class TestChangeImpact:
    """Test change impact analysis."""
    
    def test_get_change_impact(self):
        """Test getting impact of changed nodes."""
        nodes = {
            "x": Node("x", NodeKind.VARIABLE, "derived"),
            "y": Node("y", NodeKind.VARIABLE, "derived"),
            "z": Node("z", NodeKind.VARIABLE, "derived"),
        }
        edges = [
            Edge("x", "y", DependencyType.IMPLICIT),
            Edge("y", "z", DependencyType.IMPLICIT),
        ]
        
        graph = DependencyGraph(nodes, edges)
        impact = get_change_impact(graph, {"x"})
        
        assert "x" in impact
        # y and z depend on x (transitively)
        assert "y" in impact["x"]
        assert "z" in impact["x"]
    
    def test_get_change_impact_multiple_nodes(self):
        """Test impact analysis for multiple changed nodes."""
        nodes = {
            "a": Node("a", NodeKind.VARIABLE, "derived"),
            "b": Node("b", NodeKind.VARIABLE, "derived"),
            "c": Node("c", NodeKind.VARIABLE, "derived"),
        }
        edges = [
            Edge("a", "c", DependencyType.IMPLICIT),
            Edge("b", "c", DependencyType.IMPLICIT),
        ]
        
        graph = DependencyGraph(nodes, edges)
        impact = get_change_impact(graph, {"a", "b"})
        
        assert "a" in impact
        assert "b" in impact
        assert "c" in impact["a"]
        assert "c" in impact["b"]
