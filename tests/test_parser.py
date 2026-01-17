"""
Comprehensive Unit Tests for DocassembleParser.
Combines all original tests, multi-document logic, framework-specific edge cases, 
Python AST extraction, and filesystem mocking into a single file.
"""

import pytest
import yaml
from unittest.mock import patch, mock_open
from docassemble_dag.parser import (
    DocassembleParser, 
    parse_multi_document_yaml, 
    merge_yaml_documents
)
from docassemble_dag.types import NodeKind, DependencyType
from docassemble_dag.exceptions import InvalidYAMLError


class TestDocassembleParser:
    """Consolidated test suite for DocassembleParser."""

    # --- SECTION 1: ORIGINAL FOUNDATIONAL TESTS ---
    
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
        explicit_edges = [e for e in edges if e.dep_type == DependencyType.EXPLICIT]
        assert len(explicit_edges) >= 2
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
        implicit_edges = [e for e in edges if e.dep_type == DependencyType.IMPLICIT]
        assert len(implicit_edges) > 0
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
        edge_pairs = [(e.from_node, e.to_node) for e in edges]
        # Max 2 (one explicit, one implicit), but no redundant duplicates of the same type
        assert edge_pairs.count(("age", "is_adult")) <= 2

    def test_get_name_from_various_keys(self):
        """Test that _get_name handles different name keys."""
        parser = DocassembleParser("")
        assert parser._get_name({"name": "test"}) == "test"
        assert parser._get_name({"id": "test_id"}) == "test_id"
        assert parser._get_name({"variable": "var_name"}) == "var_name"
        assert parser._get_name({"field": "field_name"}) == "field_name"
        assert parser._get_name("not a dict") is None

    def test_parser_with_file_path(self):
        """Test parser tracks file path in nodes."""
        yaml_text = "variables:\n  - name: age"
        parser = DocassembleParser(yaml_text, file_path="test_interview.yaml")
        nodes = parser.extract_nodes()
        assert nodes["age"].file_path == "test_interview.yaml"

    def test_parser_tracks_line_numbers(self):
        """Test parser attempts to track line numbers."""
        yaml_text = "variables:\n  - name: age"
        parser = DocassembleParser(yaml_text)
        nodes = parser.extract_nodes()
        for node in nodes.values():
            assert node.line_number is None or isinstance(node.line_number, int)

    def test_edges_have_metadata(self):
        """Test that edges include metadata when available."""
        yaml_text = "variables:\n  - name: a\n  - name: b\n    expression: a"
        parser = DocassembleParser(yaml_text)
        nodes = parser.extract_nodes()
        edges = parser.extract_edges(nodes)
        for edge in edges:
            assert hasattr(edge, 'line_number')

    # --- SECTION 2: MULTI-DOCUMENT & MERGING TESTS ---

    def test_parse_multi_document_utility(self):
        """Test the low-level multi-document utility function."""
        yaml_text = "---\nmetadata:\n  title: Doc 1\n---\nmetadata:\n  title: Doc 2"
        docs = parse_multi_document_yaml(yaml_text)
        assert len(docs) == 2
        assert docs[0]["metadata"]["title"] == "Doc 1"

    def test_merge_yaml_documents_logic(self):
        """Test merging logic for lists and scalars."""
        doc1 = {'variables': [{'name': 'age'}], 'metadata': {'version': 1}}
        doc2 = {'variables': [{'name': 'income'}], 'metadata': {'version': 2}}
        merged = merge_yaml_documents([doc1, doc2])
        assert len(merged['variables']) == 2
        assert merged['metadata']['version'] == 2

    def test_parser_multi_document_integration(self):
        """Test parser merges variables from multiple --- sections."""
        yaml_text = "variables:\n  - name: v1\n---\nvariables:\n  - name: v2"
        parser = DocassembleParser(yaml_text)
        nodes = parser.extract_nodes()
        assert "v1" in nodes and "v2" in nodes

    # --- SECTION 3: FRAMEWORK & EDGE CASE TESTS ---

    def test_assembly_line_detection(self):
        """Test that AL_ prefix triggers NodeKind.ASSEMBLY_LINE."""
        parser = DocassembleParser("variables:\n  - name: AL_court_county")
        nodes = parser.extract_nodes()
        assert nodes["AL_court_county"].kind == NodeKind.ASSEMBLY_LINE

    def test_object_attribute_dependency(self):
        """Test that person.name creates a dependency on 'person'."""
        yaml_text = "variables:\n  - name: p\n  - name: s\n    expression: p.is_happy"
        parser = DocassembleParser(yaml_text)
        nodes = parser.extract_nodes()
        edges = parser.extract_edges(nodes)
        assert any(e.from_node == "p" and e.to_node == "s" for e in edges)

    def test_complex_python_ast_extraction(self):
        """Test dependency extraction from multi-line code blocks."""
        yaml_text = """
variables:
  - name: z
    code: |
      if x > 10:
        val = y + 2
"""
        parser = DocassembleParser(yaml_text)
        nodes = parser.extract_nodes()
        nodes["x"] = None; nodes["y"] = None # Mock external references
        edges = parser.extract_edges(nodes)
        edge_pairs = {(e.from_node, e.to_node) for e in edges}
        assert ("x", "z") in edge_pairs
        assert ("y", "z") in edge_pairs

    def test_circular_dependency_prevention(self):
        """Ensure parser does not create self-referencing edges."""
        parser = DocassembleParser("variables:\n  - name: s\n    expression: s + 1")
        nodes = parser.extract_nodes()
        edges = parser.extract_edges(nodes)
        assert not any(e.from_node == e.to_node for e in edges)

    def test_get_modules_formats(self):
        """Test module extraction handles strings and lists."""
        parser = DocassembleParser("modules:\n  - m1\nmodule: m2")
        modules = parser.get_modules()
        assert "m1" in modules and "m2" in modules

    # --- SECTION 4: MOCKING, TOP-LEVEL & ERROR HANDLING ---

    def test_include_file_mock(self):
        """Test handling of 'include' blocks via mocked filesystem."""
        main_yaml = "include:\n  - sub.yml\nvariables:\n  - name: main"
        sub_yaml = "variables:\n  - name: sub"
        with patch("builtins.open", mock_open(read_data=sub_yaml)):
            parser = DocassembleParser(main_yaml)
            if hasattr(parser, 'resolve_includes'):
                parser.resolve_includes()
            nodes = parser.extract_nodes()
            assert "main" in nodes
            assert "sub" in nodes

    def test_top_level_items(self):
        """Test parsing blocks defined at the root (not in sections)."""
        yaml_text = "question: What is your name?\nvariable: user_name"
        parser = DocassembleParser(yaml_text)
        nodes = parser.extract_nodes()
        assert "user_name" in nodes

    def test_invalid_yaml_raises_error(self):
        """Test that corrupted YAML raises InvalidYAMLError."""
        with pytest.raises(InvalidYAMLError):
            DocassembleParser("key: : value")

    def test_non_dict_root_raises_error(self):
        """Ensure a YAML list at root raises InvalidYAMLError."""
        with pytest.raises(InvalidYAMLError):
            DocassembleParser("- item1\n- item2")
