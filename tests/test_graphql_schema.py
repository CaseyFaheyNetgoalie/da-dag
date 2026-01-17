"""
Tests for GraphQL schema and queries.
"""

import pytest
from docassemble_dag.graph import DependencyGraph
from docassemble_dag.types import Node, NodeKind, Edge, DependencyType
from docassemble_dag.graphql.schema import create_schema

@pytest.fixture
def sample_graph():
    """Create a sample graph for testing."""
    nodes = {
        "age": Node(
            "age", 
            NodeKind.VARIABLE, 
            "user_input", 
            file_path="test.yaml", 
            line_number=5,
            metadata={"priority": "high"}
        ),
        "income": Node("income", NodeKind.VARIABLE, "user_input", file_path="test.yaml", line_number=10),
        "is_adult": Node(
            "is_adult", 
            NodeKind.VARIABLE, 
            "derived", 
            file_path="test.yaml", 
            line_number=15
        ),
        "eligible": Node(
            "eligible", 
            NodeKind.RULE, 
            "derived", 
            authority="42 U.S.C. § 12345",
            file_path="test.yaml", 
            line_number=20
        ),
    }
    # age -> is_adult -> eligible
    # income -> eligible
    edges = [
        Edge("age", "is_adult", DependencyType.IMPLICIT, file_path="test.yaml", line_number=15),
        Edge("income", "eligible", DependencyType.IMPLICIT, file_path="test.yaml", line_number=20),
        Edge("is_adult", "eligible", DependencyType.IMPLICIT, file_path="test.yaml", line_number=20),
    ]
    return DependencyGraph(nodes, edges)


@pytest.fixture
def schema():
    """Create GraphQL schema."""
    return create_schema()

class TestGraphQLSchema:
    """Test GraphQL schema structure and queries."""

    def test_query_node_metadata(self, schema, sample_graph):
        """Test that JSON metadata is correctly returned."""
        query = """
            query {
                node(name: "age") {
                    metadata
                }
            }
        """
        result = schema.execute_sync(query, context_value={"graph": sample_graph})
        assert result.errors is None
        assert result.data["node"]["metadata"]["priority"] == "high"

    def test_query_transitive_dependents(self, schema, sample_graph):
        """Test the reverse lookup for downstream impacts."""
        query = """
            query {
                node(name: "age") {
                    transitiveDependents {
                        name
                    }
                }
            }
        """
        result = schema.execute_sync(query, context_value={"graph": sample_graph})
        assert result.errors is None
        names = [n["name"] for n in result.data["node"]["transitiveDependents"]]
        # Downstream from age: is_adult AND eligible
        assert "is_adult" in names
        assert "eligible" in names
        assert len(names) == 2

    def test_query_path_aliased_arguments(self, schema, sample_graph):
        """Test the path query using 'from' and 'to' aliases."""
        query = """
            query {
                path(from: "age", to: "eligible") {
                    nodes
                    length
                }
            }
        """
        result = schema.execute_sync(query, context_value={"graph": sample_graph})
        assert result.errors is None
        assert result.data["path"]["nodes"] == ["age", "is_adult", "eligible"]

    def test_query_nodes_by_kind_enum(self, schema, sample_graph):
        """Verify Enum mapping (VARIABLE in Python -> VARIABLE in GQL)."""
        query = """
            query {
                nodes(kind: VARIABLE) {
                    name
                }
            }
        """
        result = schema.execute_sync(query, context_value={"graph": sample_graph})
        assert result.errors is None
        # age, income, and is_adult are VARIABLES
        assert len(result.data["nodes"]) == 3

    def test_query_graph_stats_all_fields(self, schema, sample_graph):
        """Verify comprehensive graph statistics."""
        query = """
            query {
                graphStats {
                    nodeCount
                    edgeCount
                    rootCount
                    orphanCount
                    hasCycles
                }
            }
        """
        result = schema.execute_sync(query, context_value={"graph": sample_graph})
        assert result.errors is None
        stats = result.data["graphStats"]
        assert stats["nodeCount"] == 4
        assert stats["edgeCount"] == 3
        assert stats["hasCycles"] is False

    def test_query_nodes_by_authority_partial_match(self, schema, sample_graph):
        """Verify authority substring matching."""
        query = """
            query {
                nodesByAuthority(pattern: "12345") {
                    name
                }
            }
        """
        result = schema.execute_sync(query, context_value={"graph": sample_graph})
        assert result.errors is None
        assert result.data["nodesByAuthority"][0]["name"] == "eligible"
