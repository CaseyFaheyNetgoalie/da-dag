"""
Unit tests for DependencyGraph.
"""

import pytest
from docassemble_dag.graph import DependencyGraph
from docassemble_dag.types import Node, NodeKind, Edge, DependencyType


class TestDependencyGraph:
    """Test suite for DependencyGraph."""
    
    def test_empty_graph(self):
        """Test creating an empty graph."""
        graph = DependencyGraph({}, [])
        
        assert len(graph.nodes) == 0
        assert len(graph.edges) == 0
        assert not graph.has_cycles()
        assert graph.find_cycles() == []
    
    def test_simple_acyclic_graph(self):
        """Test a simple acyclic dependency graph."""
        nodes = {
            "A": Node("A", NodeKind.VARIABLE, "user_input"),
            "B": Node("B", NodeKind.VARIABLE, "derived"),
            "C": Node("C", NodeKind.VARIABLE, "derived"),
        }
        edges = [
            Edge("A", "B", DependencyType.IMPLICIT),
            Edge("B", "C", DependencyType.IMPLICIT),
        ]
        
        graph = DependencyGraph(nodes, edges)
        
        assert len(graph.nodes) == 3
        assert len(graph.edges) == 2
        assert not graph.has_cycles()
    
    def test_cycle_detection_simple(self):
        """Test detecting a simple cycle."""
        nodes = {
            "A": Node("A", NodeKind.VARIABLE, "derived"),
            "B": Node("B", NodeKind.VARIABLE, "derived"),
        }
        edges = [
            Edge("A", "B", DependencyType.IMPLICIT),
            Edge("B", "A", DependencyType.IMPLICIT),  # Creates cycle
        ]
        
        graph = DependencyGraph(nodes, edges)
        
        assert graph.has_cycles()
        cycles = graph.find_cycles()
        assert len(cycles) > 0
    
    def test_cycle_detection_long_chain(self):
        """Test detecting a cycle in a longer chain."""
        nodes = {
            "A": Node("A", NodeKind.VARIABLE, "derived"),
            "B": Node("B", NodeKind.VARIABLE, "derived"),
            "C": Node("C", NodeKind.VARIABLE, "derived"),
            "D": Node("D", NodeKind.VARIABLE, "derived"),
        }
        edges = [
            Edge("A", "B", DependencyType.IMPLICIT),
            Edge("B", "C", DependencyType.IMPLICIT),
            Edge("C", "D", DependencyType.IMPLICIT),
            Edge("D", "A", DependencyType.IMPLICIT),  # Creates cycle A->B->C->D->A
        ]
        
        graph = DependencyGraph(nodes, edges)
        
        assert graph.has_cycles()
        cycles = graph.find_cycles()
        assert len(cycles) > 0
    
    def test_no_cycles_with_self_reference(self):
        """Test that self-reference doesn't count as a cycle (since we filter those)."""
        nodes = {
            "A": Node("A", NodeKind.VARIABLE, "derived"),
        }
        edges = []  # Self-references are filtered in parser
        
        graph = DependencyGraph(nodes, edges)
        
        assert not graph.has_cycles()
    
    def test_get_dependencies(self):
        """Test getting direct dependencies of a node."""
        nodes = {
            "A": Node("A", NodeKind.VARIABLE, "user_input"),
            "B": Node("B", NodeKind.VARIABLE, "derived"),
            "C": Node("C", NodeKind.VARIABLE, "derived"),
        }
        edges = [
            Edge("A", "B", DependencyType.IMPLICIT),  # B depends on A
            Edge("B", "C", DependencyType.IMPLICIT),  # C depends on B
        ]
        
        graph = DependencyGraph(nodes, edges)
        
        # B depends on A, C depends on B
        assert graph.get_dependencies("B") == ["A"]  # B depends on A
        assert graph.get_dependencies("C") == ["B"]  # C depends on B
        assert graph.get_dependencies("A") == []  # A doesn't depend on anything
    
    def test_get_dependents(self):
        """Test getting direct dependents of a node."""
        nodes = {
            "A": Node("A", NodeKind.VARIABLE, "user_input"),
            "B": Node("B", NodeKind.VARIABLE, "derived"),
            "C": Node("C", NodeKind.VARIABLE, "derived"),
        }
        edges = [
            Edge("A", "B", DependencyType.IMPLICIT),
            Edge("B", "C", DependencyType.IMPLICIT),
        ]
        
        graph = DependencyGraph(nodes, edges)
        
        assert graph.get_dependents("A") == ["B"]
        assert graph.get_dependents("B") == ["C"]
        assert graph.get_dependents("C") == []
    
    def test_to_json_struct(self):
        """Test converting graph to JSON structure."""
        nodes = {
            "age": Node("age", NodeKind.VARIABLE, "user_input"),
            "is_adult": Node("is_adult", NodeKind.VARIABLE, "derived", "42 U.S.C. § 12345"),
        }
        edges = [
            Edge("age", "is_adult", DependencyType.IMPLICIT),
        ]
        
        graph = DependencyGraph(nodes, edges)
        json_struct = graph.to_json_struct()
        
        assert "nodes" in json_struct
        assert "edges" in json_struct
        assert len(json_struct["nodes"]) == 2
        assert len(json_struct["edges"]) == 1
        
        # Check node structure
        age_node = next(n for n in json_struct["nodes"] if n["name"] == "age")
        assert age_node["kind"].lower() == "variable"
        assert age_node["source"] == "user_input"
        assert age_node["authority"] is None
        
        adult_node = next(n for n in json_struct["nodes"] if n["name"] == "is_adult")
        assert adult_node["authority"] == "42 U.S.C. § 12345"
        
        # Check edge structure
        edge = json_struct["edges"][0]
        assert edge["from"] == "age"
        assert edge["to"] == "is_adult"
        assert edge["type"] == "implicit"
    
    def test_disconnected_components(self):
        """Test graph with disconnected components."""
        nodes = {
            "A": Node("A", NodeKind.VARIABLE, "user_input"),
            "B": Node("B", NodeKind.VARIABLE, "derived"),
            "C": Node("C", NodeKind.VARIABLE, "user_input"),
            "D": Node("D", NodeKind.VARIABLE, "derived"),
        }
        edges = [
            Edge("A", "B", DependencyType.IMPLICIT),
            Edge("C", "D", DependencyType.IMPLICIT),
        ]
        
        graph = DependencyGraph(nodes, edges)
        
        assert len(graph.nodes) == 4
        assert len(graph.edges) == 2
        assert not graph.has_cycles()
        # Edge("A", "B") means B depends on A, so A's dependents are [B]
        # Edge("C", "D") means D depends on C, so C's dependents are [D]
        assert graph.get_dependents("A") == ["B"]
        assert graph.get_dependents("C") == ["D"]
        # B depends on A, D depends on C
        assert graph.get_dependencies("B") == ["A"]
        assert graph.get_dependencies("D") == ["C"]
    
    def test_get_transitive_dependencies(self):
        """Test getting all transitive dependencies."""
        nodes = {
            "A": Node("A", NodeKind.VARIABLE, "user_input"),
            "B": Node("B", NodeKind.VARIABLE, "derived"),
            "C": Node("C", NodeKind.VARIABLE, "derived"),
        }
        edges = [
            Edge("A", "B", DependencyType.IMPLICIT),  # B depends on A
            Edge("B", "C", DependencyType.IMPLICIT),  # C depends on B
        ]
        
        graph = DependencyGraph(nodes, edges)
        
        # C depends on B, which depends on A, so C transitively depends on A and B
        deps = graph.get_transitive_dependencies("C")
        assert "A" in deps
        assert "B" in deps
        assert len(deps) == 2
    
    def test_get_transitive_dependents(self):
        """Test getting all transitive dependents."""
        nodes = {
            "A": Node("A", NodeKind.VARIABLE, "user_input"),
            "B": Node("B", NodeKind.VARIABLE, "derived"),
            "C": Node("C", NodeKind.VARIABLE, "derived"),
        }
        edges = [
            Edge("A", "B", DependencyType.IMPLICIT),  # B depends on A
            Edge("B", "C", DependencyType.IMPLICIT),  # C depends on B
        ]
        
        graph = DependencyGraph(nodes, edges)
        
        # A has B as direct dependent, and C as transitive dependent
        dependents = graph.get_transitive_dependents("A")
        assert "B" in dependents
        assert "C" in dependents
        assert len(dependents) == 2
    
    def test_find_path(self):
        """Test finding dependency path between nodes."""
        nodes = {
            "A": Node("A", NodeKind.VARIABLE, "user_input"),
            "B": Node("B", NodeKind.VARIABLE, "derived"),
            "C": Node("C", NodeKind.VARIABLE, "derived"),
        }
        edges = [
            Edge("A", "B", DependencyType.IMPLICIT),
            Edge("B", "C", DependencyType.IMPLICIT),
        ]
        
        graph = DependencyGraph(nodes, edges)
        
        # Path from A to C should be A -> B -> C
        path = graph.find_path("A", "C")
        assert path == ["A", "B", "C"]
        
        # Path from A to B should be A -> B
        path = graph.find_path("A", "B")
        assert path == ["A", "B"]
        
        # No path from C to A
        path = graph.find_path("C", "A")
        assert path is None
    
    def test_find_nodes_by_kind(self):
        """Test finding nodes by kind."""
        nodes = {
            "var1": Node("var1", NodeKind.VARIABLE, "user_input"),
            "var2": Node("var2", NodeKind.VARIABLE, "derived"),
            "q1": Node("q1", NodeKind.QUESTION, "user_input"),
            "r1": Node("r1", NodeKind.RULE, "derived"),
        }
        edges = []
        
        graph = DependencyGraph(nodes, edges)
        
        variables = graph.find_nodes_by_kind(NodeKind.VARIABLE)
        assert len(variables) == 2
        assert "var1" in variables
        assert "var2" in variables
        
        questions = graph.find_nodes_by_kind(NodeKind.QUESTION)
        assert questions == ["q1"]
        
        rules = graph.find_nodes_by_kind(NodeKind.RULE)
        assert rules == ["r1"]
    
    def test_find_roots(self):
        """Test finding root nodes."""
        nodes = {
            "A": Node("A", NodeKind.VARIABLE, "user_input"),  # Root
            "B": Node("B", NodeKind.VARIABLE, "derived"),
            "C": Node("C", NodeKind.VARIABLE, "user_input"),  # Root
            "D": Node("D", NodeKind.VARIABLE, "derived"),
        }
        edges = [
            Edge("A", "B", DependencyType.IMPLICIT),
            Edge("C", "D", DependencyType.IMPLICIT),
        ]
        
        graph = DependencyGraph(nodes, edges)
        
        roots = graph.find_roots()
        assert "A" in roots
        assert "C" in roots
        assert "B" not in roots
        assert "D" not in roots
    
    def test_find_orphans(self):
        """Test finding orphan nodes."""
        nodes = {
            "A": Node("A", NodeKind.VARIABLE, "user_input"),  # Orphan
            "B": Node("B", NodeKind.VARIABLE, "derived"),
            "C": Node("C", NodeKind.VARIABLE, "derived"),
        }
        edges = [
            Edge("B", "C", DependencyType.IMPLICIT),
        ]
        
        graph = DependencyGraph(nodes, edges)
        
        orphans = graph.find_orphans()
        assert "A" in orphans
        assert "B" not in orphans  # B has C as dependent
        assert "C" not in orphans  # C depends on B
    
    def test_to_dot(self):
        """Test DOT format export."""
        nodes = {
            "age": Node("age", NodeKind.VARIABLE, "user_input"),
            "is_adult": Node("is_adult", NodeKind.VARIABLE, "derived"),
        }
        edges = [
            Edge("age", "is_adult", DependencyType.IMPLICIT),
        ]
        
        graph = DependencyGraph(nodes, edges)
        dot = graph.to_dot(title="Test Graph")
        
        assert "digraph" in dot
        assert "Test Graph" in dot
        assert "age" in dot
        assert "is_adult" in dot
        assert "->" in dot  # Edge indicator
        assert "implicit" in dot
    
    def test_to_graphml(self):
        """Test GraphML format export."""
        nodes = {
            "age": Node("age", NodeKind.VARIABLE, "user_input", file_path="test.yaml", line_number=5),
            "is_adult": Node("is_adult", NodeKind.VARIABLE, "derived"),
        }
        edges = [
            Edge("age", "is_adult", DependencyType.IMPLICIT, file_path="test.yaml", line_number=10),
        ]
        
        graph = DependencyGraph(nodes, edges)
        graphml = graph.to_graphml(graph_id="test")
        
        assert "<?xml" in graphml
        assert "<graphml" in graphml
        assert "<graph" in graphml
        assert 'id="test"' in graphml
        assert "<node id=\"age\">" in graphml
        assert "<edge" in graphml
        assert "age" in graphml
        assert "is_adult" in graphml
    
    def test_to_json_struct_with_metadata(self):
        """Test JSON output includes metadata fields."""
        nodes = {
            "age": Node("age", NodeKind.VARIABLE, "user_input", file_path="test.yaml", line_number=5),
            "is_adult": Node("is_adult", NodeKind.VARIABLE, "derived", authority="Test Law"),
        }
        edges = [
            Edge("age", "is_adult", DependencyType.IMPLICIT, file_path="test.yaml", line_number=10),
        ]
        
        graph = DependencyGraph(nodes, edges)
        json_struct = graph.to_json_struct()
        
        # Check node metadata
        age_node = next(n for n in json_struct["nodes"] if n["name"] == "age")
        assert age_node["file_path"] == "test.yaml"
        assert age_node["line_number"] == 5
        
        adult_node = next(n for n in json_struct["nodes"] if n["name"] == "is_adult")
        assert adult_node["authority"] == "Test Law"
        
        # Check edge metadata
        edge = json_struct["edges"][0]
        assert edge["file_path"] == "test.yaml"
        assert edge["line_number"] == 10
