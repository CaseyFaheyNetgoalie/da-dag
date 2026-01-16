"""
Tests for template variable validation.
"""

import pytest
from pathlib import Path
from tempfile import NamedTemporaryFile
from docassemble_dag.template_validator import (
    extract_template_variables,
    validate_template,
    validate_templates,
    TemplateValidationResult,
    _parse_template_text,
)
from docassemble_dag.graph import DependencyGraph
from docassemble_dag.types import Node, NodeKind


class TestTemplateTextParsing:
    """Test parsing template text for variables."""
    
    def test_parse_mako_variables(self):
        """Test extracting Mako template variables."""
        text = "Hello ${name}, your age is ${person.age}"
        variables, objects = _parse_template_text(text)
        
        assert "name" in variables
        assert "person" in objects
    
    def test_parse_docassemble_template_variables(self):
        """Test extracting Docassemble template variables."""
        text = "Hello {name}, your age is {person.age}"
        variables, objects = _parse_template_text(text)
        
        assert "name" in variables
        assert "person" in objects
    
    def test_parse_nested_attributes(self):
        """Test parsing nested object attributes."""
        text = "{client.name.first} {client.name.last}"
        variables, objects = _parse_template_text(text)
        
        assert "client" in objects
        assert "name" not in variables  # name is an attribute, not a variable
    
    def test_parse_empty_text(self):
        """Test parsing empty template text."""
        variables, objects = _parse_template_text("")
        assert len(variables) == 0
        assert len(objects) == 0


class TestTemplateValidation:
    """Test template validation against interview graphs."""
    
    def test_validate_text_template(self):
        """Test validating a text template file."""
        # Create a temporary template file
        with NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("Hello {name}, your age is {age}")
            template_path = Path(f.name)
        
        try:
            # Create graph with matching variables
            nodes = {
                "name": Node("name", NodeKind.VARIABLE, "user_input"),
                "age": Node("age", NodeKind.VARIABLE, "user_input"),
            }
            graph = DependencyGraph(nodes, [])
            
            result = validate_template(template_path, graph)
            
            assert result.is_valid
            assert "name" in result.valid_variables
            assert "age" in result.valid_variables
        finally:
            template_path.unlink()
    
    def test_validate_template_with_undefined_variables(self):
        """Test validating template with undefined variables."""
        with NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("Hello {name}, your status is {status}")
            template_path = Path(f.name)
        
        try:
            # Create graph with only 'name' variable
            nodes = {"name": Node("name", NodeKind.VARIABLE, "user_input")}
            graph = DependencyGraph(nodes, [])
            
            result = validate_template(template_path, graph)
            
            assert not result.is_valid
            assert "name" in result.valid_variables
            assert "status" in result.undefined_variables
        finally:
            template_path.unlink()
    
    def test_validate_template_with_object_attributes(self):
        """Test validating template with object attributes."""
        with NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("Hello {person.name}")
            template_path = Path(f.name)
        
        try:
            # Create graph with 'person' object
            nodes = {"person": Node("person", NodeKind.VARIABLE, "derived")}
            graph = DependencyGraph(nodes, [])
            
            result = validate_template(template_path, graph)
            
            assert result.is_valid
            assert "person" in result.valid_objects
        finally:
            template_path.unlink()
    
    def test_validate_template_with_missing_object(self):
        """Test validating template with missing object."""
        with NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("Hello {client.name}")
            template_path = Path(f.name)
        
        try:
            # Create graph without 'client' object
            nodes = {}
            graph = DependencyGraph(nodes, [])
            
            result = validate_template(template_path, graph)
            
            assert not result.is_valid
            assert "client" in result.undefined_objects
        finally:
            template_path.unlink()
    
    def test_validate_multiple_templates(self):
        """Test validating multiple templates."""
        template_paths = []
        try:
            # Create multiple template files
            for i, content in enumerate(["Hello {name}", "Your age is {age}"]):
                with NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
                    f.write(content)
                    template_paths.append(Path(f.name))
            
            # Create graph
            nodes = {
                "name": Node("name", NodeKind.VARIABLE, "user_input"),
                "age": Node("age", NodeKind.VARIABLE, "user_input"),
            }
            graph = DependencyGraph(nodes, [])
            
            results = validate_templates(template_paths, graph)
            
            assert len(results) == 2
            assert all(result.is_valid for result in results.values())
        finally:
            for path in template_paths:
                path.unlink()
    
    def test_validation_result_to_dict(self):
        """Test converting validation result to dictionary."""
        result = TemplateValidationResult("test.txt")
        result.extracted_variables = {"name", "age"}
        result.valid_variables = ["name", "age"]
        result.is_valid = True
        
        result_dict = result.to_dict()
        
        assert "template_path" in result_dict
        assert "extracted_variables" in result_dict
        assert "valid_variables" in result_dict
        assert "is_valid" in result_dict
