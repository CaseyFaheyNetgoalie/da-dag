"""
Tests for graph persistence (SQLite and JSON).
"""

import pytest
import json
from pathlib import Path
from tempfile import NamedTemporaryFile
from docassemble_dag.persistence import (
    GraphStorage,
    load_graph_json,
    save_graph_json,
)
from docassemble_dag.graph import DependencyGraph
from docassemble_dag.types import Node, NodeKind, Edge, DependencyType


class TestGraphStorage:
    """Test SQLite graph storage."""
    
    def test_save_and_load_graph(self):
        """Test saving and loading a graph."""
        nodes = {
            "x": Node("x", NodeKind.VARIABLE, "derived"),
            "y": Node("y", NodeKind.QUESTION, "user_input"),
        }
        edges = [Edge("x", "y", DependencyType.IMPLICIT)]
        graph = DependencyGraph(nodes, edges)
        
        storage = GraphStorage(Path(":memory:"))
        graph_id = storage.save_graph(graph, "test_graph", version="1.0")
        
        loaded = storage.load_graph(graph_id)
        
        assert loaded is not None
        assert len(loaded.nodes) == 2
        assert len(loaded.edges) == 1
        assert "x" in loaded.nodes
        assert "y" in loaded.nodes
    
    def test_list_graphs(self):
        """Test listing saved graphs."""
        storage = GraphStorage(Path(":memory:"))
        
        nodes = {"x": Node("x", NodeKind.VARIABLE, "derived")}
        graph = DependencyGraph(nodes, [])
        
        storage.save_graph(graph, "graph1")
        storage.save_graph(graph, "graph2")
        
        graphs = storage.list_graphs()
        assert len(graphs) == 2
        assert "graph1" in [g["name"] for g in graphs]
        assert "graph2" in [g["name"] for g in graphs]
    
    def test_save_with_metadata(self):
        """Test saving graph with metadata."""
        nodes = {"x": Node("x", NodeKind.VARIABLE, "derived")}
        graph = DependencyGraph(nodes, [])
        
        storage = GraphStorage(Path(":memory:"))
        metadata = {"author": "test", "description": "test graph"}
        graph_id = storage.save_graph(graph, "test", metadata=metadata)
        
        graphs = storage.list_graphs()
        assert len(graphs) == 1


class TestJSONPersistence:
    """Test JSON-based graph persistence."""
    
    def test_save_and_load_json(self):
        """Test saving and loading graph as JSON."""
        with NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json_path = Path(f.name)
        
        try:
            nodes = {
                "x": Node("x", NodeKind.VARIABLE, "derived"),
                "y": Node("y", NodeKind.QUESTION, "user_input"),
            }
            edges = [Edge("x", "y", DependencyType.IMPLICIT)]
            graph = DependencyGraph(nodes, edges)
            
            save_graph_json(graph, json_path)
            
            loaded = load_graph_json(json_path)
            
            assert len(loaded.nodes) == 2
            assert len(loaded.edges) == 1
            assert "x" in loaded.nodes
            assert "y" in loaded.nodes
        finally:
            if json_path.exists():
                json_path.unlink()
    
    def test_json_preserves_metadata(self):
        """Test that JSON preserves node and edge metadata."""
        with NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json_path = Path(f.name)
        
        try:
            nodes = {
                "x": Node(
                    "x",
                    NodeKind.VARIABLE,
                    "derived",
                    authority="CPLR 123",
                    file_path="test.yaml",
                    line_number=42,
                )
            }
            nodes["y"] = Node(
                "y",
                NodeKind.VARIABLE,
                "derived",
            )
            edges = [
                Edge(
                    "x",
                    "y",
                    DependencyType.IMPLICIT,
                    file_path="test.yaml",
                    line_number=43,
                )
            ]
            graph = DependencyGraph(nodes, edges)
            
            save_graph_json(graph, json_path)
            loaded = load_graph_json(json_path)
            
            assert loaded.nodes["x"].authority == "CPLR 123"
            assert loaded.nodes["x"].file_path == "test.yaml"
            assert loaded.nodes["x"].line_number == 42
        finally:
            if json_path.exists():
                json_path.unlink()
