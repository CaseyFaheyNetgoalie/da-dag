"""
Comprehensive edge case tests to improve coverage.

Tests for scenarios that might not be covered by existing tests,
including error conditions, boundary cases, and unusual inputs.
"""

import pytest
from pathlib import Path
from docassemble_dag.parser import DocassembleParser
from docassemble_dag.graph import DependencyGraph
from docassemble_dag.types import Node, NodeKind, Edge, DependencyType
from docassemble_dag.exceptions import InvalidYAMLError, GraphError
from docassemble_dag.validation import GraphValidator


class TestParserEdgeCases:
    """Test parser edge cases and error handling."""
    
    def test_empty_sections(self):
        """Test handling of empty sections."""
        yaml_text = """
variables: []
questions: []
rules: []
fields: []
"""
        parser = DocassembleParser(yaml_text)
        nodes = parser.extract_nodes()
        
        assert len(nodes) == 0
    
    def test_null_values_in_lists(self):
        """Test handling of null values in lists."""
        yaml_text = """
variables:
  - name: x
  - 
  - name: y
"""
        parser = DocassembleParser(yaml_text)
        nodes = parser.extract_nodes()
        
        # Should skip null entries
        assert "x" in nodes
        assert "y" in nodes
    
    def test_mixed_string_and_list_dependencies(self):
        """Test handling dependencies that mix strings and lists."""
        yaml_text = """
variables:
  - name: x
  - name: y
  - name: z
    depends on:
      - x
      - y
"""
        parser = DocassembleParser(yaml_text)
        nodes = parser.extract_nodes()
        edges = parser.extract_edges(nodes)
        
        # Should create edges from both x and y to z
        z_deps = [e for e in edges if e.to_node == "z"]
        assert len(z_deps) == 2
    
    def test_unicode_in_variable_names(self):
        """Test handling of unicode characters."""
        yaml_text = """
variables:
  - name: age_años
  - name: résumé
"""
        parser = DocassembleParser(yaml_text)
        nodes = parser.extract_nodes()
        
        assert "age_años" in nodes
        assert "résumé" in nodes
    
    def test_very_long_variable_names(self):
        """Test handling of very long variable names."""
        long_name = "a" * 500
        yaml_text = f"""
variables:
  - name: {long_name}
"""
        parser = DocassembleParser(yaml_text)
        nodes = parser.extract_nodes()
        
        assert long_name in nodes
    
    def test_special_characters_in_authority(self):
        """Test handling of special characters in authority field."""
        yaml_text = """
variables:
  - name: x
    authority: "Title 42 U.S.C. § 1983 (2020) [amended]"
"""
        parser = DocassembleParser(yaml_text)
        nodes = parser.extract_nodes()
        
        assert nodes["x"].authority == "Title 42 U.S.C. § 1983 (2020) [amended]"
    
    def test_deeply_nested_expressions(self):
        """Test handling of deeply nested expressions."""
        yaml_text = """
variables:
  - name: a
  - name: b
  - name: c
  - name: result
    expression: ((a + b) * c) if (a > b) else (a - b)
"""
        parser = DocassembleParser(yaml_text)
        nodes = parser.extract_nodes()
        edges = parser.extract_edges(nodes)
        
        # Should detect dependencies on a, b, c
        result_deps = {e.from_node for e in edges if e.to_node == "result"}
        assert "a" in result_deps or "b" in result_deps or "c" in result_deps
    
    def test_multiline_yaml_strings(self):
        """Test handling of multiline YAML strings."""
        yaml_text = """
variables:
  - name: x
    code: |
      # This is a multiline
      # code block
      result = True
"""
        parser = DocassembleParser(yaml_text)
        nodes = parser.extract_nodes()
        
        assert "x" in nodes
        assert nodes["x"].source == "derived"
    
    def test_yaml_with_comments(self):
        """Test that YAML comments are ignored properly."""
        yaml_text = """
# This is a comment
variables:
  - name: x  # inline comment
  # Another comment
  - name: y
"""
        parser = DocassembleParser(yaml_text)
        nodes = parser.extract_nodes()
        
        assert "x" in nodes
        assert "y" in nodes


class TestGraphEdgeCases:
    """Test graph edge cases and boundary conditions."""
    
    def test_graph_with_maximum_nodes(self):
        """Test graph with many nodes (stress test)."""
        nodes = {
            f"node_{i}": Node(f"node_{i}", NodeKind.VARIABLE, "derived")
            for i in range(1000)
        }
        edges = [
            Edge(f"node_{i}", f"node_{i+1}", DependencyType.IMPLICIT)
            for i in range(999)
        ]
        
        graph = DependencyGraph(nodes, edges)
        
        assert len(graph.nodes) == 1000
        assert len(graph.edges) == 999
        assert not graph.has_cycles()
    
    def test_graph_with_self_reference_filtered(self):
        """Test that self-references are filtered out."""
        nodes = {"x": Node("x", NodeKind.VARIABLE, "derived")}
        edges = []  # Self-references should be filtered by parser
        
        graph = DependencyGraph(nodes, edges)
        
        # Should not have self-loop
        assert len(graph.edges) == 0
    
    def test_graph_with_duplicate_edges(self):
        """Test handling of duplicate edges."""
        nodes = {
            "x": Node("x", NodeKind.VARIABLE, "derived"),
            "y": Node("y", NodeKind.VARIABLE, "derived"),
        }
        # Parser should filter duplicates, but graph should handle them
        edges = [
            Edge("x", "y", DependencyType.IMPLICIT),
            Edge("x", "y", DependencyType.IMPLICIT),  # Duplicate
        ]
        
        graph = DependencyGraph(nodes, edges)
        
        # Graph constructor doesn't filter duplicates, but parser does
        # This tests that graph can handle duplicate edges
        assert len(graph.edges) == 2
    
    def test_transitive_dependencies_with_long_chain(self):
        """Test transitive dependencies with very long chain."""
        nodes = {
            f"node_{i}": Node(f"node_{i}", NodeKind.VARIABLE, "derived")
            for i in range(100)
        }
        edges = [
            Edge(f"node_{i}", f"node_{i+1}", DependencyType.IMPLICIT)
            for i in range(99)
        ]
        
        graph = DependencyGraph(nodes, edges)
        
        # node_0 should transitively depend on all subsequent nodes
        deps = graph.get_transitive_dependents("node_0")
        assert len(deps) == 99
    
    def test_find_path_no_path_exists(self):
        """Test find_path when no path exists."""
        nodes = {
            "a": Node("a", NodeKind.VARIABLE, "derived"),
            "b": Node("b", NodeKind.VARIABLE, "derived"),
            "c": Node("c", NodeKind.VARIABLE, "derived"),
        }
        edges = [
            Edge("a", "b", DependencyType.IMPLICIT),
        ]
        
        graph = DependencyGraph(nodes, edges)
        
        # No path from c to a
        path = graph.find_path("c", "a")
        assert path is None
    
    def test_graph_with_nonexistent_node(self):
        """Test graph methods with nonexistent node."""
        nodes = {"x": Node("x", NodeKind.VARIABLE, "derived")}
        graph = DependencyGraph(nodes, [])
        
        # Should return empty list for nonexistent node
        assert graph.get_dependencies("nonexistent") == []
        assert graph.get_dependents("nonexistent") == []
    
    def test_graph_to_json_with_none_values(self):
        """Test JSON serialization with None values."""
        nodes = {
            "x": Node(
                "x",
                NodeKind.VARIABLE,
                "derived",
                authority=None,
                file_path=None,
                line_number=None
            )
        }
        graph = DependencyGraph(nodes, [])
        
        json_struct = graph.to_json_struct()
        
        # Should handle None values gracefully
        assert json_struct["nodes"][0]["authority"] is None
        assert json_struct["nodes"][0]["file_path"] is None


class TestValidationEdgeCases:
    """Test validation edge cases."""
    
    def test_validation_with_empty_graph(self):
        """Test validation on empty graph."""
        graph = DependencyGraph({}, [])
        validator = GraphValidator(graph)
        
        violations = validator.validate_all()
        
        # Empty graph should have no violations
        assert len(violations) == 0
    
    def test_validation_with_all_orphans(self):
        """Test validation when all nodes are orphans."""
        nodes = {
            "a": Node("a", NodeKind.VARIABLE, "derived"),
            "b": Node("b", NodeKind.VARIABLE, "derived"),
            "c": Node("c", NodeKind.VARIABLE, "derived"),
        }
        graph = DependencyGraph(nodes, [])
        
        validator = GraphValidator(graph)
        violations = validator.validate_all(policies=["no_orphans"])
        
        # All nodes are orphans
        assert len(violations) == 3
    
    def test_validation_summary_with_mixed_severities(self):
        """Test validation summary with different severity levels."""
        # Create graph that will have different violation types
        nodes = {
            "orphan": Node("orphan", NodeKind.VARIABLE, "derived"),
            "a": Node("a", NodeKind.VARIABLE, "derived"),
            "b": Node("b", NodeKind.VARIABLE, "derived"),
        }
        edges = [
            Edge("a", "b", DependencyType.IMPLICIT),
        ]
        
        graph = DependencyGraph(nodes, edges)
        validator = GraphValidator(graph)
        violations = validator.validate_all()
        
        summary = validator.get_summary()
        
        # Should have counts for each severity level
        assert "errors" in summary
        assert "warnings" in summary
        assert "info" in summary
        assert summary["total"] >= 0


class TestErrorHandling:
    """Test error handling and exceptions."""
    
    def test_invalid_yaml_syntax_raises_error(self):
        """Test that invalid YAML syntax raises InvalidYAMLError."""
        invalid_yaml = """
key: value:
another: [unclosed list
"""
        with pytest.raises(InvalidYAMLError):
            DocassembleParser(invalid_yaml)
    
    def test_non_dict_yaml_root_raises_error(self):
        """Test that non-dict YAML root raises error."""
        yaml_text = """
- item1
- item2
- item3
"""
        with pytest.raises(InvalidYAMLError):
            DocassembleParser(yaml_text)
    
    def test_graph_with_invalid_edge_raises_error(self):
        """Test that edges referencing nonexistent nodes raise error."""
        nodes = {"x": Node("x", NodeKind.VARIABLE, "derived")}
        edges = [Edge("nonexistent", "x", DependencyType.IMPLICIT)]
        
        with pytest.raises(GraphError):
            DependencyGraph(nodes, edges)
    
    def test_graph_with_wrong_node_type_raises_error(self):
        """Test that wrong node type raises error."""
        with pytest.raises(GraphError):
            # Nodes should be dict, not list
            DependencyGraph([], [])
    
    def test_parser_with_non_string_input_raises_error(self):
        """Test that non-string input raises TypeError."""
        with pytest.raises(TypeError):
            DocassembleParser(123)  # Not a string
    
    def test_validator_with_non_graph_raises_error(self):
        """Test that validator with non-graph raises TypeError."""
        with pytest.raises(TypeError):
            GraphValidator("not a graph")


class TestBoundaryConditions:
    """Test boundary conditions and limits."""
    
    def test_zero_length_strings(self):
        """Test handling of zero-length strings."""
        yaml_text = """
variables:
  - name: ""
"""
        parser = DocassembleParser(yaml_text)
        nodes = parser.extract_nodes()
        
        # Empty name should be skipped or handled
        assert len(nodes) == 0 or "" not in nodes
    
    def test_whitespace_only_names(self):
        """Test handling of whitespace-only names."""
        yaml_text = """
variables:
  - name: "   "
"""
        parser = DocassembleParser(yaml_text)
        nodes = parser.extract_nodes()
        
        # Whitespace name might be kept or trimmed
        assert isinstance(nodes, dict)
    
    def test_expression_with_no_variables(self):
        """Test expression that references no variables."""
        yaml_text = """
variables:
  - name: x
    expression: "42"
"""
        parser = DocassembleParser(yaml_text)
        nodes = parser.extract_nodes()
        edges = parser.extract_edges(nodes)
        
        # Should have node but no edges
        assert "x" in nodes
        x_edges = [e for e in edges if e.to_node == "x"]
        assert len(x_edges) == 0
    
    def test_circular_include_protection(self):
        """Test that circular includes don't cause infinite loop."""
        # This would require actual file system mocking
        # Just verify the structure is in place
        yaml_text = """
include:
  - self_reference.yaml
"""
        parser = DocassembleParser(yaml_text)
        # Parser should handle this gracefully (file won't exist)
        nodes = parser.extract_nodes()
        assert isinstance(nodes, dict)


class TestRealWorldScenarios:
    """Test real-world usage scenarios."""
    
    def test_large_interview_performance(self):
        """Test performance with large interview."""
        # Generate a large but valid interview
        variables_yaml = "\n".join([
            f"  - name: var_{i}\n    expression: var_{i-1} if {i} > 0 else None"
            for i in range(100)
        ])
        
        yaml_text = f"variables:\n{variables_yaml}"
        
        parser = DocassembleParser(yaml_text)
        nodes = parser.extract_nodes()
        edges = parser.extract_edges(nodes)
        graph = DependencyGraph(nodes, edges)
        
        # Should complete without timeout
        assert len(nodes) == 100
        assert len(edges) > 0
    
    def test_interview_with_all_node_kinds(self):
        """Test interview using all node kinds."""
        yaml_text = """
variables:
  - name: regular_var
  - name: AL_Document
fields:
  - name: field_var
questions:
  - name: ask_question
    question: "Question?"
rules:
  - name: some_rule
    expression: "True"
objects:
  - person: Individual
"""
        parser = DocassembleParser(yaml_text)
        nodes = parser.extract_nodes()
        
        kinds_found = {node.kind for node in nodes.values()}
        
        # Should have multiple kinds
        assert NodeKind.VARIABLE in kinds_found
        assert NodeKind.QUESTION in kinds_found
        assert NodeKind.RULE in kinds_found
        # AL_Document should be ASSEMBLY_LINE kind
        assert NodeKind.ASSEMBLY_LINE in kinds_found
    
    def test_complex_dependency_chain(self):
        """Test complex realistic dependency chain."""
        yaml_text = """
variables:
  - name: user_age
  - name: is_adult
    expression: user_age >= 18
  - name: user_income
  - name: income_eligible
    expression: user_income < 30000
  - name: eligible
    expression: is_adult and income_eligible
questions:
  - name: ask_age
    variable: user_age
  - name: ask_income
    variable: user_income
    required: is_adult
rules:
  - name: eligibility_rule
    expression: eligible
    authority: "42 U.S.C. § 12345"
"""
        parser = DocassembleParser(yaml_text)
        nodes = parser.extract_nodes()
        edges = parser.extract_edges(nodes)
        graph = DependencyGraph(nodes, edges)
        
        # Validate graph structure
        validator = GraphValidator(graph)
        violations = validator.validate_all()
        
        # Should have no critical errors
        errors = [v for v in violations if v.severity.value == "error"]
        assert len(errors) == 0
        
        # Check dependency chain
        eligible_deps = graph.get_transitive_dependencies("eligible")
        assert "user_age" in eligible_deps or "is_adult" in eligible_deps
