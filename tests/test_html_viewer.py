"""
Tests for HTML interactive viewer.
"""

import pytest
from pathlib import Path
from tempfile import NamedTemporaryFile
from docassemble_dag.html_viewer import to_html
from docassemble_dag.graph import DependencyGraph
from docassemble_dag.types import Node, NodeKind, Edge, DependencyType


class TestHTMLViewer:
    """Test HTML viewer generation."""
    
    def test_generate_html_basic(self):
        """Test generating basic HTML viewer."""
        nodes = {
            "x": Node("x", NodeKind.VARIABLE, "derived"),
            "y": Node("y", NodeKind.VARIABLE, "derived"),
        }
        edges = [Edge("x", "y", DependencyType.IMPLICIT)]
        
        graph = DependencyGraph(nodes, edges)
        html = to_html(graph)
        
        assert isinstance(html, str)
        assert len(html) > 1000
        assert "d3.js" in html.lower() or "d3js" in html.lower()
        assert "graphData" in html
    
    def test_generate_html_with_title(self):
        """Test generating HTML with custom title."""
        nodes = {"x": Node("x", NodeKind.VARIABLE, "derived")}
        graph = DependencyGraph(nodes, [])
        
        html = to_html(graph, title="My Custom Graph")
        
        assert "My Custom Graph" in html
    
    def test_generate_html_with_output_path(self):
        """Test generating HTML and saving to file."""
        with NamedTemporaryFile(mode='w', suffix='.html', delete=False) as f:
            output_path = Path(f.name)
        
        try:
            nodes = {"x": Node("x", NodeKind.VARIABLE, "derived")}
            graph = DependencyGraph(nodes, [])
            
            html = to_html(graph, output_path=output_path)
            
            assert output_path.exists()
            assert output_path.read_text() == html
        finally:
            if output_path.exists():
                output_path.unlink()
    
    def test_generate_html_with_custom_dimensions(self):
        """Test generating HTML with custom dimensions."""
        nodes = {"x": Node("x", NodeKind.VARIABLE, "derived")}
        graph = DependencyGraph(nodes, [])
        
        html = to_html(graph, width=1600, height=1200)
        
        assert "1600" in html
        assert "1200" in html
    
    def test_html_contains_graph_data(self):
        """Test that HTML contains graph data in JSON format."""
        nodes = {
            "x": Node("x", NodeKind.VARIABLE, "derived"),
            "y": Node("y", NodeKind.QUESTION, "user_input"),
        }
        edges = [Edge("x", "y", DependencyType.EXPLICIT)]
        
        graph = DependencyGraph(nodes, edges)
        html = to_html(graph)
        
        # Check that node names appear in HTML
        assert "x" in html
        assert "y" in html
    
    def test_html_viewer_method_on_graph(self):
        """Test that DependencyGraph.to_html() method works."""
        nodes = {"x": Node("x", NodeKind.VARIABLE, "derived")}
        graph = DependencyGraph(nodes, [])
        
        html = graph.to_html()
        
        assert isinstance(html, str)
        assert len(html) > 1000
