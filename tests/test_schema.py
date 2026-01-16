"""
Tests for YAML schema validation.
"""

import pytest
from docassemble_dag.schema import (
    is_valid_field,
    is_valid_question,
    is_valid_rule,
    is_valid_variable,
    validate_yaml_structure,
)


class TestSchemaValidation:
    """Test YAML schema validation."""
    
    def test_validate_valid_yaml(self):
        """Test validation of valid YAML structure."""
        yaml_dict = {
            "questions": [{"name": "q1", "question": "Test?"}],
            "variables": [{"name": "v1"}],
        }
        errors = validate_yaml_structure(yaml_dict)
        assert len(errors) == 0
    
    def test_validate_invalid_root(self):
        """Test validation of invalid root (not a dict)."""
        errors = validate_yaml_structure([])
        assert len(errors) > 0
        assert "root must be a dictionary" in errors[0]
    
    def test_validate_invalid_questions(self):
        """Test validation of invalid questions."""
        yaml_dict = {
            "questions": [{"variable": "v1"}],  # Missing 'name' or 'question'
        }
        errors = validate_yaml_structure(yaml_dict)
        assert len(errors) > 0
        assert "not a valid question" in errors[0]
    
    def test_validate_invalid_variables(self):
        """Test validation of invalid variables."""
        yaml_dict = {
            "variables": [{}],  # Missing 'name'
        }
        errors = validate_yaml_structure(yaml_dict)
        assert len(errors) > 0
        assert "missing 'name'" in errors[0]
    
    def test_is_valid_question(self):
        """Test question validation function."""
        assert is_valid_question({"name": "q1", "question": "Test?"})
        assert is_valid_question({"question": "Test?"})  # Has 'question'
        assert not is_valid_question({})  # Missing both
        assert not is_valid_question("not a dict")
    
    def test_is_valid_variable(self):
        """Test variable validation function."""
        assert is_valid_variable({"name": "v1"})
        assert not is_valid_variable({})  # Missing 'name'
        assert not is_valid_variable("not a dict")
    
    def test_is_valid_rule(self):
        """Test rule validation function."""
        assert is_valid_rule({"name": "r1"})
        assert not is_valid_rule({})  # Missing 'name'
        assert not is_valid_rule("not a dict")
    
    def test_is_valid_field(self):
        """Test field validation function."""
        assert is_valid_field({"name": "f1"})
        assert not is_valid_field({})  # Missing 'name'
        assert not is_valid_field("not a dict")
