"""
Tests for reconsider directive tracking.
"""

import pytest
from docassemble_dag.reconsider import (
    ReconsiderDirective,
    extract_reconsider_directives,
    check_reconsider_boundaries,
    get_reconsidered_variables,
)
from docassemble_dag.graph import DependencyGraph
from docassemble_dag.types import Node, NodeKind, Edge, DependencyType


class TestReconsiderDirectives:
    """Test reconsider directive extraction."""
    
    def test_extract_reconsider_directive(self):
        """Test extracting reconsider directive from YAML."""
        yaml_dict = {
            "variables": [
                {
                    "name": "x",
                    "reconsider": "y",
                }
            ]
        }
        
        directives = extract_reconsider_directives(yaml_dict)
        
        assert len(directives) == 1
        assert directives[0].node_name == "x"
        assert directives[0].reconsidered_var == "y"
    
    def test_extract_multiple_reconsider(self):
        """Test extracting multiple reconsider directives."""
        yaml_dict = {
            "variables": [
                {"name": "x", "reconsider": ["y", "z"]},
            ]
        }
        
        directives = extract_reconsider_directives(yaml_dict)
        
        assert len(directives) == 2
        assert all(d.node_name == "x" for d in directives)
        reconsidered_vars = {d.reconsidered_var for d in directives}
        assert "y" in reconsidered_vars
        assert "z" in reconsidered_vars


class TestReconsiderBoundaries:
    """Test checking reconsider boundaries."""
    
    def test_check_reconsider_boundaries(self):
        """Test checking if dependencies cross reconsider boundaries."""
        nodes = {
            "x": Node("x", NodeKind.VARIABLE, "derived"),
            "y": Node("y", NodeKind.VARIABLE, "derived"),
            "z": Node("z", NodeKind.VARIABLE, "derived"),
        }
        edges = [
            Edge("x", "y", DependencyType.IMPLICIT),
            Edge("y", "z", DependencyType.IMPLICIT),
        ]
        graph = DependencyGraph(nodes, edges)
        
        directives = [
            ReconsiderDirective("some_node", "x"),
        ]
        
        warnings = check_reconsider_boundaries(graph, directives)
        
        # Should warn about dependency from x to y (x is reconsidered)
        assert len(warnings) >= 1
        assert any(w["from_node"] == "x" for w in warnings)
    
    def test_get_reconsidered_variables(self):
        """Test getting set of reconsidered variables."""
        directives = [
            ReconsiderDirective("node1", "x"),
            ReconsiderDirective("node2", "y"),
        ]
        
        reconsidered = get_reconsidered_variables(directives)
        
        assert "x" in reconsidered
        assert "y" in reconsidered
