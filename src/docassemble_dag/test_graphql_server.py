"""
Integration tests for GraphQL server.
"""

import pytest
from fastapi.testclient import TestClient

from docassemble_dag.graph import DependencyGraph
from docassemble_dag.types import Node, NodeKind, Edge, DependencyType
from docassemble_dag.graphql.server import create_server


@pytest.fixture
def sample_graph():
    """Create sample graph for server testing."""
    nodes = {
        "age": Node("age", NodeKind.VARIABLE, "user_input"),
        "is_adult": Node("is_adult", NodeKind.VARIABLE, "derived"),
    }
    edges = [Edge("age", "is_adult", DependencyType.IMPLICIT)]
    return DependencyGraph(nodes, edges)


@pytest.fixture
def client(sample_graph):
    """Create test client for GraphQL server."""
    app = create_server(sample_graph)
    return TestClient(app)


class TestGraphQLServer:
    """Test GraphQL server endpoints."""
    
    def test_health_endpoint(self, client):
        """Test health check endpoint."""
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["nodes"] == 2
        assert data["edges"] == 1
    
    def test_graphql_query(self, client):
        """Test executing GraphQL query via HTTP."""
        query = """
            query {
                node(name: "age") {
                    name
                    kind
                }
            }
        """
        
        response = client.post(
            "/graphql",
            json={"query": query}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert data["data"]["node"]["name"] == "age"
    
    def test_graphiql_interface(self, client):
        """Test that GraphiQL IDE is accessible."""
        response = client.get("/graphql")
        
        assert response.status_code == 200
        assert "graphiql" in response.text.lower() or "graphql" in response.text.lower()
