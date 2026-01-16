"""
Tests for Assembly Line and object attribute support.
"""

import pytest
from docassemble_dag.parser import DocassembleParser
from docassemble_dag.types import NodeKind, DependencyType


class TestAssemblyLineSupport:
    """Test Assembly Line variable recognition (AL_ prefix)."""
    
    def test_assembly_line_variable_recognition(self):
        """Test that AL_ prefix variables are recognized as ASSEMBLY_LINE."""
        yaml = """
variables:
  - name: AL_Document
  - name: AL_User
  - name: regular_variable
"""
        parser = DocassembleParser(yaml)
        nodes = parser.extract_nodes()
        
        assert "AL_Document" in nodes
        assert nodes["AL_Document"].kind == NodeKind.ASSEMBLY_LINE
        assert "AL_User" in nodes
        assert nodes["AL_User"].kind == NodeKind.ASSEMBLY_LINE
        assert "regular_variable" in nodes
        assert nodes["regular_variable"].kind == NodeKind.VARIABLE
    
    def test_assembly_line_in_fields(self):
        """Test Assembly Line variables in fields: section."""
        yaml = """
fields:
  - name: AL_Document
  - name: normal_field
"""
        parser = DocassembleParser(yaml)
        nodes = parser.extract_nodes()
        
        assert "AL_Document" in nodes
        assert nodes["AL_Document"].kind == NodeKind.ASSEMBLY_LINE
        assert "normal_field" in nodes
        assert nodes["normal_field"].kind == NodeKind.VARIABLE


class TestObjectAttributeSupport:
    """Test object attribute handling (person.name → person dependency)."""
    
    def test_object_attribute_creates_dependency(self):
        """Test that person.name creates dependency on person."""
        yaml = """
variables:
  - name: person
  - name: full_name
    expression: person.name
"""
        parser = DocassembleParser(yaml)
        nodes = parser.extract_nodes()
        edges = parser.extract_edges(nodes)
        
        assert "person" in nodes
        assert "full_name" in nodes
        
        # person.name should create dependency: person → full_name
        person_edges = [e for e in edges if e.from_node == "person" and e.to_node == "full_name"]
        assert len(person_edges) == 1
        assert person_edges[0].dep_type == DependencyType.IMPLICIT
    
    def test_object_attribute_with_multiple_attributes(self):
        """Test multiple object attributes in same expression."""
        yaml = """
variables:
  - name: person
  - name: address
  - name: contact_info
    expression: person.name + " " + address.street
"""
        parser = DocassembleParser(yaml)
        nodes = parser.extract_nodes()
        edges = parser.extract_edges(nodes)
        
        assert "person" in nodes
        assert "address" in nodes
        assert "contact_info" in nodes
        
        # person.name and address.street should create dependencies
        person_edges = [e for e in edges if e.from_node == "person" and e.to_node == "contact_info"]
        address_edges = [e for e in edges if e.from_node == "address" and e.to_node == "contact_info"]
        
        assert len(person_edges) == 1
        assert len(address_edges) == 1
    
    def test_object_attribute_avoids_double_matching(self):
        """Test that person.name doesn't create both person.name and person dependencies."""
        yaml = """
variables:
  - name: person
  - name: full_name
    expression: person.name
"""
        parser = DocassembleParser(yaml)
        nodes = parser.extract_nodes()
        edges = parser.extract_edges(nodes)
        
        # Should have only one edge: person → full_name
        # Should NOT have edges for "person" as variable name and "name" as variable name
        full_name_edges = [e for e in edges if e.to_node == "full_name"]
        assert len(full_name_edges) == 1
        assert full_name_edges[0].from_node == "person"
    
    def test_object_attribute_in_template(self):
        """Test object attributes in template fields."""
        yaml = """
variables:
  - name: person
  - name: greeting
    template: "Hello, ${person.name}"
"""
        parser = DocassembleParser(yaml)
        nodes = parser.extract_nodes()
        edges = parser.extract_edges(nodes)
        
        person_edges = [e for e in edges if e.from_node == "person" and e.to_node == "greeting"]
        assert len(person_edges) == 1
    
    def test_object_attribute_in_code_block(self):
        """Test object attributes in code blocks."""
        yaml = """
variables:
  - name: person
  - name: is_adult
    code: |
      return person.age >= 18
"""
        parser = DocassembleParser(yaml)
        nodes = parser.extract_nodes()
        edges = parser.extract_edges(nodes)
        
        person_edges = [e for e in edges if e.from_node == "person" and e.to_node == "is_adult"]
        assert len(person_edges) == 1


class TestModulesSupport:
    """Test modules: directive parsing for cross-repository dependencies."""
    
    def test_modules_directive_extraction(self):
        """Test that modules: directive is extracted."""
        yaml = """
modules:
  - docassemble.income
  - docassemble.base.legal
  
variables:
  - name: age
"""
        parser = DocassembleParser(yaml)
        modules = parser.get_modules()
        
        assert "docassemble.income" in modules
        assert "docassemble.base.legal" in modules
    
    def test_modules_as_single_module(self):
        """Test modules: as single string."""
        yaml = """
modules: docassemble.income

variables:
  - name: age
"""
        parser = DocassembleParser(yaml)
        modules = parser.get_modules()
        
        assert "docassemble.income" in modules
    
    def test_module_key_singular(self):
        """Test module: (singular) key."""
        yaml = """
module: docassemble.income

variables:
  - name: age
"""
        parser = DocassembleParser(yaml)
        modules = parser.get_modules()
        
        assert "docassemble.income" in modules
    
    def test_no_modules(self):
        """Test when no modules are specified."""
        yaml = """
variables:
  - name: age
"""
        parser = DocassembleParser(yaml)
        modules = parser.get_modules()
        
        assert modules == []


class TestCombinedFeatures:
    """Test combinations of Assembly Line, object attributes, and modules."""
    
    def test_assembly_line_with_object_attributes(self):
        """Test Assembly Line variable with object attributes."""
        yaml = """
modules:
  - docassemble.AssemblyLine

variables:
  - name: AL_Document
  - name: person
  - name: document_name
    expression: AL_Document.title + " - " + person.name
"""
        parser = DocassembleParser(yaml)
        nodes = parser.extract_nodes()
        edges = parser.extract_edges(nodes)
        modules = parser.get_modules()
        
        # Assembly Line variable
        assert nodes["AL_Document"].kind == NodeKind.ASSEMBLY_LINE
        
        # Object attributes should create dependencies
        al_edges = [e for e in edges if e.from_node == "AL_Document" and e.to_node == "document_name"]
        person_edges = [e for e in edges if e.from_node == "person" and e.to_node == "document_name"]
        
        assert len(al_edges) == 1
        assert len(person_edges) == 1
        
        # Modules should be extracted
        assert "docassemble.AssemblyLine" in modules
