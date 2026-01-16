"""
Tests for advanced graph operations (topological sort, execution order).
"""

import pytest
from docassemble_dag.exceptions import CycleError
from docassemble_dag.graph import DependencyGraph
from docassemble_dag.graph_operations import (
    get_dependency_layers,
    get_execution_order,
    topological_sort,
)
from docassemble_dag.types import DependencyType, Edge, Node, NodeKind


class TestTopologicalSort:
    """Test topological sort functionality."""
    
    def test_topological_sort_simple(self):
        """Test topological sort of simple graph."""
        nodes = {
            "A": Node("A", NodeKind.VARIABLE, "derived"),
            "B": Node("B", NodeKind.VARIABLE, "derived"),
            "C": Node("C", NodeKind.VARIABLE, "derived"),
        }
        edges = [
            Edge("A", "B", DependencyType.IMPLICIT),  # B depends on A
            Edge("B", "C", DependencyType.IMPLICIT),  # C depends on B
        ]
        graph = DependencyGraph(nodes, edges)
        
        sorted_nodes = topological_sort(graph)
        
        # A should come before B, B should come before C
        assert "A" in sorted_nodes
        assert "B" in sorted_nodes
        assert "C" in sorted_nodes
        assert sorted_nodes.index("A") < sorted_nodes.index("B")
        assert sorted_nodes.index("B") < sorted_nodes.index("C")
    
    def test_topological_sort_with_cycles(self):
        """Test topological sort raises CycleError on cycles."""
        nodes = {
            "A": Node("A", NodeKind.VARIABLE, "derived"),
            "B": Node("B", NodeKind.VARIABLE, "derived"),
        }
        edges = [
            Edge("A", "B", DependencyType.IMPLICIT),
            Edge("B", "A", DependencyType.IMPLICIT),  # Cycle
        ]
        graph = DependencyGraph(nodes, edges)
        
        with pytest.raises(CycleError):
            topological_sort(graph)
    
    def test_topological_sort_method_on_graph(self):
        """Test topological_sort method on DependencyGraph."""
        nodes = {"A": Node("A", NodeKind.VARIABLE, "derived")}
        graph = DependencyGraph(nodes, [])
        
        sorted_nodes = graph.topological_sort()
        
        assert sorted_nodes == ["A"]


class TestExecutionOrder:
    """Test execution order (layered) functionality."""
    
    def test_get_execution_order_simple(self):
        """Test getting execution order as layers."""
        nodes = {
            "A": Node("A", NodeKind.VARIABLE, "derived"),
            "B": Node("B", NodeKind.VARIABLE, "derived"),
            "C": Node("C", NodeKind.VARIABLE, "derived"),
        }
        edges = [
            Edge("A", "B", DependencyType.IMPLICIT),  # B depends on A
            Edge("B", "C", DependencyType.IMPLICIT),  # C depends on B
        ]
        graph = DependencyGraph(nodes, edges)
        
        layers = get_execution_order(graph)
        
        assert len(layers) == 3  # Three layers
        assert "A" in layers[0]  # A has no dependencies
        assert "B" in layers[1]  # B depends on A
        assert "C" in layers[2]  # C depends on B
    
    def test_get_execution_order_method_on_graph(self):
        """Test get_execution_order method on DependencyGraph."""
        nodes = {"A": Node("A", NodeKind.VARIABLE, "derived")}
        graph = DependencyGraph(nodes, [])
        
        layers = graph.get_execution_order()
        
        assert len(layers) == 1
        assert "A" in layers[0]


class TestDependencyLayers:
    """Test dependency layer grouping."""
    
    def test_get_dependency_layers(self):
        """Test grouping nodes by dependency depth."""
        nodes = {
            "A": Node("A", NodeKind.VARIABLE, "derived"),
            "B": Node("B", NodeKind.VARIABLE, "derived"),
            "C": Node("C", NodeKind.VARIABLE, "derived"),
        }
        edges = [
            Edge("A", "B", DependencyType.IMPLICIT),
            Edge("B", "C", DependencyType.IMPLICIT),
        ]
        graph = DependencyGraph(nodes, edges)
        
        layers = get_dependency_layers(graph)
        
        assert len(layers) >= 1
        # Layer 0 should have nodes with 0 dependencies (A)
        assert any("A" in layer for layer in layers)
