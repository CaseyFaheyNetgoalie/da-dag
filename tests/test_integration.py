"""
Integration tests for the full pipeline.
"""

import pytest
from docassemble_dag import DocassembleParser, DependencyGraph
from docassemble_dag.types import NodeKind


class TestIntegration:
    """Integration tests for end-to-end functionality."""
    
    def test_example_interview(self):
        """Test parsing the example interview YAML."""
        yaml_text = """
variables:
  - name: age
  - name: is_adult
    expression: age >= 18

fields:
  - name: income
  - name: eligible_for_aid
    expression: income < 30000 and is_adult

questions:
  - name: ask_age
    question: "How old are you?"
    variable: age
  
  - name: ask_income
    question: "What is your annual income?"
    variable: income
    required: is_adult
  
  - name: ask_consent
    question: "Do you consent to the terms?"
    depends on: is_adult

rules:
  - name: eligibility_rule
    expression: "eligible_for_aid and age >= 18"
    authority: "42 U.S.C. § 12345"
"""
        parser = DocassembleParser(yaml_text)
        nodes = parser.extract_nodes()
        edges = parser.extract_edges(nodes)
        graph = DependencyGraph(nodes, edges)
        
        # Verify all expected nodes exist
        expected_nodes = {"age", "is_adult", "income", "eligible_for_aid", 
                         "ask_age", "ask_income", "ask_consent", "eligibility_rule"}
        assert set(nodes.keys()) == expected_nodes
        
        # Verify node kinds
        assert nodes["age"].kind.value.lower() == "variable"
        assert nodes["is_adult"].kind.value.lower() == "variable"
        assert nodes["ask_age"].kind.value.lower() == "question"
        assert nodes["eligibility_rule"].kind.value.lower() == "rule"
        
        # Verify source metadata
        assert nodes["age"].source == "user_input"
        assert nodes["is_adult"].source == "derived"
        
        # Verify authority metadata
        assert nodes["eligibility_rule"].authority == "42 U.S.C. § 12345"
        
        # Verify edges exist
        assert len(edges) > 0
        
        # Verify explicit dependencies
        explicit_edges = [e for e in edges if e.dep_type.value == "explicit"]
        explicit_pairs = {(e.from_node, e.to_node) for e in explicit_edges}
        assert ("is_adult", "ask_income") in explicit_pairs
        assert ("is_adult", "ask_consent") in explicit_pairs
        
        # Verify implicit dependencies
        implicit_edges = [e for e in edges if e.dep_type.value == "implicit"]
        implicit_pairs = {(e.from_node, e.to_node) for e in implicit_edges}
        assert ("age", "is_adult") in implicit_pairs
        assert ("income", "eligible_for_aid") in implicit_pairs
        
        # Verify no cycles
        assert not graph.has_cycles()
        
        # Verify JSON output is valid
        json_struct = graph.to_json_struct()
        assert "nodes" in json_struct
        assert "edges" in json_struct
        assert len(json_struct["nodes"]) == len(nodes)
        assert len(json_struct["edges"]) == len(edges)
    
    def test_minimal_interview(self):
        """Test parsing a minimal valid interview."""
        yaml_text = """
questions:
  - name: ask_name
    question: "What is your name?"
    variable: name
"""
        parser = DocassembleParser(yaml_text)
        nodes = parser.extract_nodes()
        edges = parser.extract_edges(nodes)
        graph = DependencyGraph(nodes, edges)
        
        assert "ask_name" in nodes
        assert "name" in nodes
        assert len(nodes) == 2
        
        # Verify JSON structure
        json_struct = graph.to_json_struct()
        assert len(json_struct["nodes"]) == 2
        
        # Verify metadata fields are present
        for node in json_struct["nodes"]:
            assert "file_path" in node
            assert "line_number" in node
        
        for edge in json_struct["edges"]:
            assert "file_path" in edge
            assert "line_number" in edge
    
    def test_graph_query_methods(self):
        """Test GUAC-inspired query methods work end-to-end."""
        yaml_text = """
variables:
  - name: age
  - name: is_adult
    expression: age >= 18
  - name: income
  - name: eligible
    expression: income < 30000 and is_adult
"""
        parser = DocassembleParser(yaml_text)
        nodes = parser.extract_nodes()
        edges = parser.extract_edges(nodes)
        graph = DependencyGraph(nodes, edges)
        
        # Test query methods
        roots = graph.find_roots()
        assert "age" in roots or "income" in roots
        
        variables = graph.find_nodes_by_kind(NodeKind.VARIABLE)
        assert len(variables) >= 4
        
        # Test transitive dependencies
        deps = graph.get_transitive_dependencies("eligible")
        assert "age" in deps or "is_adult" in deps or "income" in deps
        
        # Test path finding
        path = graph.find_path("age", "eligible")
        assert path is not None or len(path) > 0
    
    def test_export_formats(self):
        """Test all export formats work."""
        yaml_text = """
variables:
  - name: age
  - name: is_adult
    expression: age >= 18
"""
        parser = DocassembleParser(yaml_text)
        nodes = parser.extract_nodes()
        edges = parser.extract_edges(nodes)
        graph = DependencyGraph(nodes, edges)
        
        # Test JSON export
        json_struct = graph.to_json_struct()
        assert "nodes" in json_struct
        assert "edges" in json_struct
        
        # Test DOT export
        dot = graph.to_dot()
        assert "digraph" in dot
        assert "age" in dot
        
        # Test GraphML export
        graphml = graph.to_graphml()
        assert "<?xml" in graphml
        assert "<graphml" in graphml
        assert "age" in graphml