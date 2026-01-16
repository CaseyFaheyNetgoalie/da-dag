"""
Tests for PostgreSQL backend support.

These tests require PostgreSQL to be running and accessible.
They are marked as integration tests and can be skipped if PostgreSQL is not available.
"""

import os
import pytest

# Check if PostgreSQL connection string is available
POSTGRESQL_URL = os.environ.get("DATABASE_URL", os.environ.get("POSTGRES_URL"))

pytestmark = pytest.mark.skipif(
    not POSTGRESQL_URL,
    reason="PostgreSQL connection string not provided (set DATABASE_URL or POSTGRES_URL env var)"
)


@pytest.mark.integration
class TestPostgreSQLBackend:
    """Test PostgreSQL backend for graph persistence."""
    
    @pytest.fixture(autouse=True)
    def setup_teardown(self):
        """Setup and teardown for PostgreSQL tests."""
        from docassemble_dag.persistence import GraphStorage
        
        # Create storage instance
        self.storage = GraphStorage(connection_string=POSTGRESQL_URL)
        yield
        # Cleanup: close connection
        if self.storage:
            self.storage.close()
    
    def test_save_and_load_graph_postgresql(self):
        """Test saving and loading a graph using PostgreSQL."""
        from docassemble_dag.graph import DependencyGraph
        from docassemble_dag.types import Node, NodeKind, Edge, DependencyType
        
        nodes = {
            "x": Node("x", NodeKind.VARIABLE, "derived"),
            "y": Node("y", NodeKind.QUESTION, "user_input"),
        }
        edges = [Edge("x", "y", DependencyType.IMPLICIT)]
        graph = DependencyGraph(nodes, edges)
        
        graph_id = self.storage.save_graph(graph, "test_postgresql_graph", version="1.0")
        
        loaded = self.storage.load_graph(graph_id)
        
        assert loaded is not None
        assert len(loaded.nodes) == 2
        assert len(loaded.edges) == 1
        assert "x" in loaded.nodes
        assert "y" in loaded.nodes
    
    def test_list_graphs_postgresql(self):
        """Test listing saved graphs in PostgreSQL."""
        from docassemble_dag.graph import DependencyGraph
        from docassemble_dag.types import Node, NodeKind
        
        nodes = {"x": Node("x", NodeKind.VARIABLE, "derived")}
        graph = DependencyGraph(nodes, [])
        
        self.storage.save_graph(graph, "postgresql_graph1")
        self.storage.save_graph(graph, "postgresql_graph2")
        
        graphs = self.storage.list_graphs()
        assert len(graphs) >= 2
        graph_names = [g["name"] for g in graphs]
        assert "postgresql_graph1" in graph_names
        assert "postgresql_graph2" in graph_names


@pytest.mark.integration
class TestBackendDetection:
    """Test backend auto-detection from connection strings."""
    
    def test_detect_sqlite_from_path(self):
        """Test SQLite backend detection from file path."""
        from docassemble_dag.db_backends import get_backend
        
        backend = get_backend("test.db")
        assert backend.__class__.__name__ == "SQLiteBackend"
    
    def test_detect_sqlite_memory(self):
        """Test SQLite backend detection from :memory:."""
        from docassemble_dag.db_backends import get_backend
        
        backend = get_backend(":memory:")
        assert backend.__class__.__name__ == "SQLiteBackend"
    
    def test_detect_postgresql(self):
        """Test PostgreSQL backend detection from connection string."""
        from docassemble_dag.db_backends import get_backend
        
        backend = get_backend("postgresql://user:pass@localhost/db")
        assert backend.__class__.__name__ == "PostgreSQLBackend"
        
        backend = get_backend("postgres://user:pass@localhost/db")
        assert backend.__class__.__name__ == "PostgreSQLBackend"
