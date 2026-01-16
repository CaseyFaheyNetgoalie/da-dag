"""
Tests for conditional logic detection.
"""

import pytest
from docassemble_dag.conditional import (
    ConditionalDependency,
    extract_conditionals_from_item,
    extract_conditional_dependencies,
)
from docassemble_dag.parser import DocassembleParser
from docassemble_dag.types import DependencyType
from docassemble_dag.graph import DependencyGraph


class TestConditionalDependency:
    """Test conditional dependency extraction."""
    
    def test_extract_simple_condition(self):
        """Test extracting dependencies from simple conditions."""
        cond_dep = ConditionalDependency(
            directive="show if",
            condition="age >= 18",
            dependent_node="ask_question",
        )
        
        assert "age" in cond_dep.dependencies
    
    def test_extract_complex_condition(self):
        """Test extracting dependencies from complex conditions."""
        cond_dep = ConditionalDependency(
            directive="enable if",
            condition="age >= 18 and is_citizen and income > 0",
            dependent_node="ask_benefits",
        )
        
        assert "age" in cond_dep.dependencies
        assert "is_citizen" in cond_dep.dependencies
        assert "income" in cond_dep.dependencies
    
    def test_extract_object_attributes(self):
        """Test extracting object attributes from conditions."""
        cond_dep = ConditionalDependency(
            directive="show if",
            condition="person.age >= 18",
            dependent_node="ask_question",
        )
        
        assert "person" in cond_dep.dependencies
    
    def test_exclude_python_keywords(self):
        """Test that Python keywords are excluded."""
        cond_dep = ConditionalDependency(
            directive="show if",
            condition="age >= 18 and True",
            dependent_node="ask_question",
        )
        
        assert "age" in cond_dep.dependencies
        assert "True" not in cond_dep.dependencies
        assert "and" not in cond_dep.dependencies


class TestConditionalExtraction:
    """Test conditional extraction from YAML items."""
    
    def test_extract_show_if(self):
        """Test extracting 'show if' directive."""
        item = {"name": "ask_age", "show if": "age >= 18"}
        deps = extract_conditionals_from_item(item, "ask_age")
        
        assert len(deps) == 1
        assert deps[0].directive == "show if"
        assert "age" in deps[0].dependencies
    
    def test_extract_enable_if(self):
        """Test extracting 'enable if' directive."""
        item = {"name": "ask_benefits", "enable if": "is_eligible"}
        deps = extract_conditionals_from_item(item, "ask_benefits")
        
        assert len(deps) == 1
        assert deps[0].directive == "enable if"
        assert "is_eligible" in deps[0].dependencies
    
    def test_extract_multiple_conditionals(self):
        """Test extracting multiple conditional directives."""
        item = {
            "name": "ask_question",
            "show if": "age >= 18",
            "enable if": "is_citizen",
        }
        deps = extract_conditionals_from_item(item, "ask_question")
        
        assert len(deps) >= 1
        directives = [d.directive for d in deps]
        assert "show if" in directives or "enable if" in directives


class TestConditionalInParser:
    """Test conditional logic detection in parser."""
    
    def test_parser_extracts_conditional_dependencies(self):
        """Test that parser extracts conditional dependencies."""
        yaml_text = """
questions:
  - name: ask_age
    question: "What is your age?"
    show if: age >= 18
variables:
  - name: age
"""
        parser = DocassembleParser(yaml_text)
        nodes = parser.extract_nodes()
        edges = parser.extract_edges(nodes)
        
        # Should create edge from age to ask_age
        edge_tuples = [(e.from_node, e.to_node) for e in edges]
        assert ("age", "ask_age") in edge_tuples
    
    def test_parser_handles_enable_if(self):
        """Test that parser handles 'enable if' directive."""
        yaml_text = """
questions:
  - name: ask_benefits
    question: "Do you want benefits?"
    enable if: is_eligible
variables:
  - name: is_eligible
"""
        parser = DocassembleParser(yaml_text)
        nodes = parser.extract_nodes()
        edges = parser.extract_edges(nodes)
        
        # Should create edge from is_eligible to ask_benefits
        edge_tuples = [(e.from_node, e.to_node) for e in edges]
        assert ("is_eligible", "ask_benefits") in edge_tuples
    
    def test_conditional_creates_implicit_edge(self):
        """Test that conditional dependencies create implicit edges."""
        yaml_text = """
questions:
  - name: ask_question
    show if: condition_var
variables:
  - name: condition_var
"""
        parser = DocassembleParser(yaml_text)
        nodes = parser.extract_nodes()
        edges = parser.extract_edges(nodes)
        
        # Find the edge
        conditional_edges = [
            e for e in edges
            if e.from_node == "condition_var" and e.to_node == "ask_question"
        ]
        assert len(conditional_edges) == 1
        assert conditional_edges[0].dep_type == DependencyType.IMPLICIT
