"""
Test file for objects: section support.
"""

import pytest
from docassemble_dag.parser import DocassembleParser
from docassemble_dag.types import NodeKind


class TestObjectsSection:
    """Test support for Docassemble objects: section."""
    
    def test_extract_simple_objects(self):
        """Test extracting simple object definitions."""
        yaml_text = """
objects:
  - person: Individual
  - household: DAList
"""
        parser = DocassembleParser(yaml_text)
        nodes = parser.extract_nodes()
        
        # Objects should be extracted as nodes
        assert "person" in nodes
        assert "household" in nodes
        
        # Objects should be VARIABLE kind
        assert nodes["person"].kind == NodeKind.VARIABLE
        assert nodes["household"].kind == NodeKind.VARIABLE
        
        # Objects should be marked as "derived" (instantiated)
        assert nodes["person"].source == "derived"
        assert nodes["household"].source == "derived"
    
    def test_objects_have_type_metadata(self):
        """Test that object type is stored in metadata."""
        yaml_text = """
objects:
  - person: Individual
  - court: Court
"""
        parser = DocassembleParser(yaml_text)
        nodes = parser.extract_nodes()
        
        # Check metadata contains object type
        assert nodes["person"].metadata.get("object_type") == "Individual"
        assert nodes["court"].metadata.get("object_type") == "Court"
    
    def test_objects_with_complex_types(self):
        """Test objects with complex type definitions."""
        yaml_text = """
objects:
  - people: DAList.using(object_type=Individual)
  - documents: DAList.using(object_type=DAObject, complete_attribute='is_complete')
"""
        parser = DocassembleParser(yaml_text)
        nodes = parser.extract_nodes()
        
        assert "people" in nodes
        assert "documents" in nodes
        
        # Complex types should be stored as strings
        assert "DAList" in nodes["people"].metadata.get("object_type", "")
        assert "Individual" in nodes["people"].metadata.get("object_type", "")
    
    def test_objects_create_dependencies(self):
        """Test that object attributes create dependencies."""
        yaml_text = """
objects:
  - person: Individual
variables:
  - name: full_name
    expression: person.name.full()
"""
        parser = DocassembleParser(yaml_text)
        nodes = parser.extract_nodes()
        edges = parser.extract_edges(nodes)
        
        # Should have dependency: person -> full_name
        assert any(
            e.from_node == "person" and e.to_node == "full_name"
            for e in edges
        )
    
    def test_objects_mixed_with_variables(self):
        """Test objects section works alongside variables."""
        yaml_text = """
objects:
  - person: Individual
variables:
  - name: age
  - name: is_adult
    expression: person.age >= 18
"""
        parser = DocassembleParser(yaml_text)
        nodes = parser.extract_nodes()
        edges = parser.extract_edges(nodes)
        
        # All nodes should be extracted
        assert "person" in nodes
        assert "age" in nodes
        assert "is_adult" in nodes
        
        # Should have dependencies
        assert any(e.from_node == "person" for e in edges)
    
    def test_empty_objects_section(self):
        """Test handling of empty objects section."""
        yaml_text = """
objects: []
variables:
  - name: age
"""
        parser = DocassembleParser(yaml_text)
        nodes = parser.extract_nodes()
        
        # Should not crash, should just extract variables
        assert "age" in nodes
        assert len(nodes) == 1
    
    def test_objects_with_assembly_line(self):
        """Test objects section with Assembly Line objects."""
        yaml_text = """
objects:
  - AL_Document: ALDocument
  - AL_User: Individual
variables:
  - name: doc_title
    expression: AL_Document.title
"""
        parser = DocassembleParser(yaml_text)
        nodes = parser.extract_nodes()
        
        # AL_ prefix should be recognized even for objects
        # Note: Currently they'd be VARIABLE kind since we check prefix
        # after creating the node. You might want to adjust this.
        assert "AL_Document" in nodes
        assert "AL_User" in nodes


# Example usage in real Docassemble YAML:
EXAMPLE_DOCASSEMBLE_YAML = """
---
# Metadata block
metadata:
  title: My Interview
  short title: Interview
---
# Objects section
objects:
  - user: Individual
  - spouse: Individual
  - children: DAList.using(object_type=Individual)
  - court: Court
---
# Variables using those objects
variables:
  - name: household_size
    code: |
      size = 1  # User
      if user.is_married:
        size += 1
      size += children.number()
      household_size = size
---
# Questions
questions:
  - name: ask_user_name
    question: What is your name?
    fields:
      - First Name: user.name.first
      - Last Name: user.name.last
  
  - name: ask_marriage_status
    question: Are you married?
    yesno: user.is_married
"""

# How it should parse:
def test_complete_docassemble_example():
    """Test parsing complete multi-document YAML with objects."""
    parser = DocassembleParser(EXAMPLE_DOCASSEMBLE_YAML)
    nodes = parser.extract_nodes()
    edges = parser.extract_edges(nodes)
    
    # Objects should be extracted
    assert "user" in nodes
    assert "spouse" in nodes
    assert "children" in nodes
    assert "court" in nodes
    
    # Variables should be extracted
    assert "household_size" in nodes
    
    # Questions should be extracted
    assert "ask_user_name" in nodes
    assert "ask_marriage_status" in nodes
    
    # Dependencies should be created
    # household_size depends on user (via user.is_married)
    assert any(
        e.from_node == "user" and e.to_node == "household_size"
        for e in edges
    )
