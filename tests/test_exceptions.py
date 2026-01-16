"""
Tests for custom exceptions.
"""

import sqlite3

import pytest
from docassemble_dag.exceptions import (
    CycleError,
    DocassembleDAGError,
    GraphError,
    InvalidYAMLError,
    ParsingError,
    StorageError,
    ValidationError,
)


class TestExceptions:
    """Test custom exception hierarchy."""
    
    def test_base_exception(self):
        """Test base exception."""
        error = DocassembleDAGError("Test error")
        assert str(error) == "Test error"
        assert isinstance(error, Exception)
    
    def test_invalid_yaml_error(self):
        """Test InvalidYAMLError with context."""
        error = InvalidYAMLError(
            "Invalid YAML",
            file_path="test.yaml",
            line_number=42,
        )
        assert error.file_path == "test.yaml"
        assert error.line_number == 42
    
    def test_parsing_error(self):
        """Test ParsingError."""
        original = ValueError("Original error")
        error = ParsingError(
            "Parsing failed",
            file_path="test.yaml",
            original_error=original,
        )
        assert error.file_path == "test.yaml"
        assert error.original_error == original
    
    def test_graph_error(self):
        """Test GraphError with node name."""
        error = GraphError("Graph error", node_name="test_node")
        assert error.node_name == "test_node"
    
    def test_cycle_error(self):
        """Test CycleError with cycles."""
        cycles = [["A", "B", "A"], ["C", "D", "C"]]
        error = CycleError("Cycles found", cycles=cycles)
        assert error.cycles == cycles
    
    def test_validation_error(self):
        """Test ValidationError with violations."""
        violations = [{"rule": "no_cycles", "severity": "error"}]
        error = ValidationError("Validation failed", violations=violations)
        assert error.violations == violations
    
    def test_storage_error(self):
        """Test StorageError with operation and original error."""
        original = sqlite3.Error("DB error")
        error = StorageError(
            "Storage failed",
            operation="save_graph",
            original_error=original,
        )
        assert error.operation == "save_graph"
        assert error.original_error == original
