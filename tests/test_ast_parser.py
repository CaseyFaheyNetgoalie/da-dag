"""
Tests for AST-based Python code parsing.
"""

import pytest
from docassemble_dag.ast_parser import (
    extract_variables_from_python_ast,
    should_use_ast_parsing,
    VariableVisitor,
)
import ast


class TestASTParser:
    """Test AST-based Python code parsing."""
    
    def test_extract_simple_variables(self):
        """Test extraction of simple variable references."""
        code = "result = person.name + age"
        variables, objects, attributes = extract_variables_from_python_ast(code)
        
        assert "person" in variables
        assert "age" in variables
        assert "person" in objects
        assert ("person", "name") in attributes
    
    def test_extract_object_attributes(self):
        """Test extraction of object attribute references."""
        code = "full_name = client.name.first + ' ' + client.name.last"
        variables, objects, attributes = extract_variables_from_python_ast(code)
        
        assert "client" in objects
        assert ("client", "name") in attributes
        # Note: nested attributes like .first and .last are tracked at top level
    
    def test_extract_conditional_variables(self):
        """Test extraction from conditional statements."""
        code = """
if age > 18:
    status = "adult"
elif age > 13:
    status = "teen"
else:
    status = "child"
"""
        variables, objects, attributes = extract_variables_from_python_ast(code)
        
        assert "age" in variables
        assert "status" not in variables  # status is assigned, not read
    
    def test_extract_function_calls(self):
        """Test extraction from function calls."""
        code = "result = calculate_income(annual_salary, deductions)"
        variables, objects, attributes = extract_variables_from_python_ast(code)
        
        assert "annual_salary" in variables
        assert "deductions" in variables
    
    def test_extract_list_comprehensions(self):
        """Test extraction from list comprehensions."""
        code = "[x * 2 for x in numbers if x > threshold]"
        variables, objects, attributes = extract_variables_from_python_ast(code)
        
        assert "numbers" in variables
        assert "threshold" in variables
    
    def test_empty_code(self):
        """Test handling of empty code."""
        variables, objects, attributes = extract_variables_from_python_ast("")
        assert len(variables) == 0
        assert len(objects) == 0
        assert len(attributes) == 0
    
    def test_invalid_syntax(self):
        """Test handling of invalid Python syntax."""
        code = "def incomplete_function("
        variables, objects, attributes = extract_variables_from_python_ast(code)
        # Should return empty sets without raising
        assert isinstance(variables, set)
        assert isinstance(objects, set)
        assert isinstance(attributes, set)
    
    def test_should_use_ast_for_code_blocks(self):
        """Test detection of code blocks that should use AST."""
        # Code with Python keywords
        assert should_use_ast_parsing("if age > 18:\n    return True")
        
        # Code with multiple lines and statements
        assert should_use_ast_parsing("x = 1\ny = 2\nz = x + y")
        
        # Simple expression
        assert not should_use_ast_parsing("person.name")
        
        # Empty string
        assert not should_use_ast_parsing("")


class TestVariableVisitor:
    """Test AST visitor for variable extraction."""
    
    def test_visitor_extracts_variables(self):
        """Test visitor correctly extracts variables."""
        code = "result = a + b"
        tree = ast.parse(code)
        
        visitor = VariableVisitor()
        visitor.visit(tree)
        
        assert "a" in visitor.variables
        assert "b" in visitor.variables
        assert "result" not in visitor.variables  # result is assigned, not read
    
    def test_visitor_handles_attributes(self):
        """Test visitor handles object attributes."""
        code = "name = person.first_name"
        tree = ast.parse(code)
        
        visitor = VariableVisitor()
        visitor.visit(tree)
        
        assert "person" in visitor.objects
        assert ("person", "first_name") in visitor.attributes
