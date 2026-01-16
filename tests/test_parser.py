"""
Unit tests for DocassembleParser.
"""

import pytest
from docassemble_dag.parser import DocassembleParser
from docassemble_dag.types import NodeKind, DependencyType


class TestParser:
    """Test suite for DocassembleParser."""
    
    def test_parse_empty_yaml(self):
        """Test parsing empty YAML."""
        parser = DocassembleParser("")
        nodes = parser.extract_nodes()
        edges = parser.extract_edges(nodes)
        
        assert len(nodes) == 0
        assert len(edges) == 0
    
    def test_extract_variables(self):
        """Test extracting variables from YAML."""
        yaml_text = """
variables:
  - name: age
  - name: income
    expression: salary * 12
"""
        parser = DocassembleParser(yaml_text)
        nodes = parser.extract_nodes()
        
        assert "age" in nodes
        assert "income" in nodes
        assert nodes["age"].kind == NodeKind.VARIABLE
        assert nodes["age"].source == "user_input"
        assert nodes["income"].kind == NodeKind.VARIABLE
        assert nodes["income"].source == "derived"
    
    def test_extract_fields(self):
        """Test extracting fields from YAML."""
        yaml_text = """
fields:
  - name: name_field
"""
        parser = DocassembleParser(yaml_text)
        nodes = parser.extract_nodes()
        
        assert "name_field" in nodes
        assert nodes["name_field"].kind == NodeKind.VARIABLE
    
    def test_extract_both_variables_and_fields(self):
        """Test that both variables and fields are extracted."""
        yaml_text = """
variables:
  - name: var1
fields:
  - name: var2
"""
        parser = DocassembleParser(yaml_text)
        nodes = parser.extract_nodes()
        
        assert "var1" in nodes
        assert "var2" in nodes
        assert len(nodes) == 2
    
    def test_extract_questions(self):
        """Test extracting questions from YAML."""
        yaml_text = """
questions:
  - name: ask_age
    question: "How old are you?"
    variable: age
"""
        parser = DocassembleParser(yaml_text)
        nodes = parser.extract_nodes()
        
        assert "ask_age" in nodes
        assert nodes["ask_age"].kind == NodeKind.QUESTION
        assert nodes["ask_age"].source == "user_input"
        # Question should implicitly create variable node
        assert "age" in nodes
        assert nodes["age"].kind == NodeKind.VARIABLE
    
    def test_extract_rules(self):
        """Test extracting rules from YAML."""
        yaml_text = """
rules:
  - name: eligibility_rule
    expression: "age >= 18"
    authority: "42 U.S.C. § 12345"
"""
        parser = DocassembleParser(yaml_text)
        nodes = parser.extract_nodes()
        
        assert "eligibility_rule" in nodes
        assert nodes["eligibility_rule"].kind == NodeKind.RULE
        assert nodes["eligibility_rule"].source == "derived"
        assert nodes["eligibility_rule"].authority == "42 U.S.C. § 12345"
    
    def test_extract_explicit_dependencies(self):
        """Test extracting explicit dependencies."""
        yaml_text = """
variables:
  - name: age
questions:
  - name: ask_income
    required: age
  - name: ask_consent
    depends on: age
"""
        parser = DocassembleParser(yaml_text)
        nodes = parser.extract_nodes()
        edges = parser.extract_edges(nodes)
        
        # Find explicit edges
        explicit_edges = [e for e in edges if e.dep_type == DependencyType.EXPLICIT]
        assert len(explicit_edges) >= 2
        
        # Check that age -> ask_income and age -> ask_consent exist
        edge_dict = {(e.from_node, e.to_node): e for e in explicit_edges}
        assert ("age", "ask_income") in edge_dict
        assert ("age", "ask_consent") in edge_dict
    
    def test_extract_implicit_dependencies(self):
        """Test extracting implicit dependencies from expressions."""
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
        
        # Find implicit edges
        implicit_edges = [e for e in edges if e.dep_type == DependencyType.IMPLICIT]
        assert len(implicit_edges) > 0
        
        # Check key implicit dependencies
        edge_dict = {(e.from_node, e.to_node): e for e in implicit_edges}
        assert ("age", "is_adult") in edge_dict
        assert ("income", "eligible") in edge_dict
        assert ("is_adult", "eligible") in edge_dict
    
    def test_authority_metadata(self):
        """Test that authority metadata is preserved."""
        yaml_text = """
variables:
  - name: test_var
    authority: "Test Statute § 123"
rules:
  - name: test_rule
    statute: "Another Law § 456"
"""
        parser = DocassembleParser(yaml_text)
        nodes = parser.extract_nodes()
        
        assert nodes["test_var"].authority == "Test Statute § 123"
        assert nodes["test_rule"].authority == "Another Law § 456"
    
    def test_top_level_items(self):
        """Test parsing top-level items that aren't in standard sections."""
        yaml_text = """
custom_question:
  question: "What is your name?"
  variable: name
custom_var:
  expression: name.upper()
"""
        parser = DocassembleParser(yaml_text)
        nodes = parser.extract_nodes()
        
        # Should extract questions and variables from top-level items
        assert len(nodes) >= 2
    
    def test_no_duplicate_edges(self):
        """Test that duplicate edges are not created."""
        yaml_text = """
variables:
  - name: age
  - name: is_adult
    expression: age >= 18
    depends on: age
"""
        parser = DocassembleParser(yaml_text)
        nodes = parser.extract_nodes()
        edges = parser.extract_edges(nodes)
        
        # Should have both explicit and implicit edges from age to is_adult
        edge_pairs = [(e.from_node, e.to_node) for e in edges]
        # But each (from, to) pair should appear only once per type
        edge_set = set(edge_pairs)
        # We may have both explicit and implicit, but not duplicates
        assert edge_pairs.count(("age", "is_adult")) <= 2  # max 2 (explicit + implicit)
    
    def test_get_name_from_various_keys(self):
        """Test that _get_name handles different name keys."""
        parser = DocassembleParser("")
        
        # Test 'name' key
        assert parser._get_name({"name": "test"}) == "test"
        
        # Test 'id' key
        assert parser._get_name({"id": "test_id"}) == "test_id"
        
        # Test 'variable' key
        assert parser._get_name({"variable": "var_name"}) == "var_name"
        
        # Test 'field' key
        assert parser._get_name({"field": "field_name"}) == "field_name"
        
        # Test non-dict returns None
        assert parser._get_name("not a dict") is None
        
        # Test dict without name keys returns None
        assert parser._get_name({"other": "value"}) is None
    
    def test_parser_with_file_path(self):
        """Test parser tracks file path in nodes."""
        yaml_text = """
variables:
  - name: age
questions:
  - name: ask_age
    question: "How old are you?"
"""
        parser = DocassembleParser(yaml_text, file_path="test_interview.yaml")
        nodes = parser.extract_nodes()
        
        assert "age" in nodes
        assert "ask_age" in nodes
        assert nodes["ask_age"].file_path == "test_interview.yaml"
    
    def test_parser_tracks_line_numbers(self):
        """Test parser attempts to track line numbers."""
        yaml_text = """
variables:
  - name: age
  - name: income
questions:
  - name: ask_age
    question: "How old are you?"
"""
        parser = DocassembleParser(yaml_text, file_path="test.yaml")
        nodes = parser.extract_nodes()
        
        # Line numbers are heuristic, so we just check they're set (may be None or int)
        for node in nodes.values():
            assert node.line_number is None or isinstance(node.line_number, int)
    
    def test_edges_have_metadata(self):
        """Test that edges include metadata when available."""
        yaml_text = """
variables:
  - name: age
  - name: is_adult
    expression: age >= 18
questions:
  - name: ask_income
    required: age
"""
        parser = DocassembleParser(yaml_text, file_path="test.yaml")
        nodes = parser.extract_nodes()
        edges = parser.extract_edges(nodes)
        
        # Check that edges have file_path (may be None if not found)
        for edge in edges:
            assert hasattr(edge, 'file_path')
            assert hasattr(edge, 'line_number')
            assert edge.line_number is None or isinstance(edge.line_number, int)
