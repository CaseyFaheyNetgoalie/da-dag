from __future__ import annotations
from typing import List, Optional, Annotated
import strawberry
from strawberry.scalars import JSON
from strawberry.types import Info
from enum import Enum

from ..graph import DependencyGraph

# --- Enums ---

@strawberry.enum
class NodeKind(Enum):
    VARIABLE = "variable"
    QUESTION = "question"
    RULE = "rule"
    ASSEMBLY_LINE = "assembly_line"

@strawberry.enum
class DependencyType(Enum):
    EXPLICIT = "explicit"
    IMPLICIT = "implicit"

# --- Types ---

@strawberry.type
class Node:
    name: str
    kind: NodeKind
    source: str
    authority: Optional[str] = None
    file_path: Optional[str] = strawberry.field(name="filePath", default=None)
    line_number: Optional[int] = strawberry.field(name="lineNumber", default=None)
    metadata: JSON = strawberry.field(default_factory=dict)
    
    @strawberry.field
    def dependencies(self, info: Info) -> List[Node]:
        graph: DependencyGraph = info.context["graph"]
        dep_names = graph.get_dependencies(self.name)
        return [node_to_graphql(graph.nodes[name]) for name in dep_names if name in graph.nodes]
    
    @strawberry.field
    def dependents(self, info: Info) -> List[Node]:
        graph: DependencyGraph = info.context["graph"]
        dep_names = graph.get_dependents(self.name)
        return [node_to_graphql(graph.nodes[name]) for name in dep_names if name in graph.nodes]

    @strawberry.field
    def transitive_dependencies(self, info: Info) -> List[Node]:
        graph: DependencyGraph = info.context["graph"]
        dep_names = graph.get_transitive_dependencies(self.name)
        return [node_to_graphql(graph.nodes[name]) for name in dep_names if name in graph.nodes]

    @strawberry.field
    def transitive_dependents(self, info: Info) -> List[Node]:
        graph: DependencyGraph = info.context["graph"]
        # This calls the reverse lookup in your DependencyGraph logic
        dep_names = graph.get_transitive_dependents(self.name)
        return [node_to_graphql(graph.nodes[name]) for name in dep_names if name in graph.nodes]

@strawberry.type
class Edge:
    from_node: str = strawberry.field(name="fromNode")
    to_node: str = strawberry.field(name="toNode")
    type: DependencyType
    file_path: Optional[str] = strawberry.field(name="filePath", default=None)
    line_number: Optional[int] = strawberry.field(name="lineNumber", default=None)
    metadata: JSON = strawberry.field(default_factory=dict)

@strawberry.type
class Path:
    nodes: List[str]
    length: int

@strawberry.type
class GraphStats:
    node_count: int = strawberry.field(name="nodeCount")
    edge_count: int = strawberry.field(name="edgeCount")
    root_count: int = strawberry.field(name="rootCount")
    orphan_count: int = strawberry.field(name="orphanCount")
    has_cycles: bool = strawberry.field(name="hasCycles")

# --- Query ---

@strawberry.type
class Query:
    @strawberry.field
    def node(self, info: Info, name: str) -> Optional[Node]:
        graph: DependencyGraph = info.context["graph"]
        node_obj = graph.nodes.get(name)
        return node_to_graphql(node_obj) if node_obj else None
    
    @strawberry.field
    def nodes(self, info: Info, kind: Optional[NodeKind] = None, source: Optional[str] = None) -> List[Node]:
        graph: DependencyGraph = info.context["graph"]
        nodes = graph.nodes.values()
        if kind:
            nodes = [n for n in nodes if n.kind.value.lower() == kind.value.lower()]
        if source:
            nodes = [n for n in nodes if n.source == source]
        return [node_to_graphql(n) for n in nodes]

    @strawberry.field
    def nodes_by_authority(self, info: Info, pattern: str) -> List[Node]:
        graph: DependencyGraph = info.context["graph"]
        # Basic substring match; adjust if your graph has a specific search method
        nodes = [n for n in graph.nodes.values() if n.authority and pattern in n.authority]
        return [node_to_graphql(n) for n in nodes]

    @strawberry.field
    def edges(
        self,
        info: Info,
        from_node: Annotated[Optional[str], strawberry.argument(name="from")] = None,
        to_node: Annotated[Optional[str], strawberry.argument(name="to")] = None,
    ) -> List[Edge]:
        graph: DependencyGraph = info.context["graph"]
        edges = graph.edges
        if from_node:
            edges = [e for e in edges if e.from_node == from_node]
        if to_node:
            edges = [e for e in edges if e.to_node == to_node]
        return [edge_to_graphql(e) for e in edges]

    @strawberry.field
    def path(
        self,
        info: Info,
        from_node: Annotated[str, strawberry.argument(name="from")],
        to_node: Annotated[str, strawberry.argument(name="to")],
    ) -> Optional[Path]:
        graph: DependencyGraph = info.context["graph"]
        path_nodes = graph.find_path(from_node, to_node)
        if not path_nodes: return None
        return Path(nodes=path_nodes, length=len(path_nodes) - 1)

    @strawberry.field
    def graph_stats(self, info: Info) -> GraphStats:
        graph: DependencyGraph = info.context["graph"]
        return GraphStats(
            node_count=len(graph.nodes),
            edge_count=len(graph.edges),
            root_count=len(graph.find_roots()),
            orphan_count=len(graph.find_orphans()),
            has_cycles=graph.has_cycles(),
        )

# --- Helpers ---

def node_to_graphql(node) -> Node:
    """Converts internal graph node to Strawberry GraphQL Type"""
    return Node(
        name=node.name,
        kind=NodeKind(node.kind.value.lower()),
        source=node.source,
        authority=getattr(node, 'authority', None),
        file_path=getattr(node, 'file_path', None),
        line_number=getattr(node, 'line_number', None),
        metadata=getattr(node, 'metadata', {}) or {},
    )

def edge_to_graphql(edge) -> Edge:
    """Converts internal graph edge to Strawberry GraphQL Type"""
    return Edge(
        from_node=edge.from_node,
        to_node=edge.to_node,
        type=DependencyType(edge.dep_type.value.lower()),
        file_path=getattr(edge, 'file_path', None),
        line_number=getattr(edge, 'line_number', None),
        metadata=getattr(edge, 'metadata', {}) or {},
    )

def create_schema() -> strawberry.Schema:
    return strawberry.Schema(query=Query)
