"""
GraphQL server integration using FastAPI.
"""

from typing import Optional
from pathlib import Path

try:
    from fastapi import FastAPI
    from strawberry.fastapi import GraphQLRouter
    import uvicorn
except ImportError:
    raise ImportError(
        "FastAPI integration requires additional dependencies. "
        "Install with: pip install docassemble-dag[graphql]"
    )

from ..graph import DependencyGraph
from .schema import create_schema


def create_server(
    graph: DependencyGraph,
    title: str = "Docassemble DAG GraphQL API",
    debug: bool = False,
) -> FastAPI:
    """
    Create FastAPI server with GraphQL endpoint.
    
    Args:
        graph: DependencyGraph to expose via GraphQL
        title: API title
        debug: Enable debug mode
    
    Returns:
        FastAPI application
    """
    app = FastAPI(title=title, debug=debug)
    
    # Create GraphQL schema
    schema = create_schema()
    
    # Create GraphQL router with context
    async def get_context():
        return {"graph": graph}
    
    graphql_app = GraphQLRouter(
        schema,
        context_getter=get_context,
        graphql_ide="graphiql",  # Enable GraphiQL IDE
    )
    
    # Mount GraphQL endpoint
    app.include_router(graphql_app, prefix="/graphql")
    
    # Health check endpoint
    @app.get("/health")
    async def health():
        return {
            "status": "healthy",
            "nodes": len(graph.nodes),
            "edges": len(graph.edges),
        }
    
    return app


def serve(
    graph: DependencyGraph,
    host: str = "0.0.0.0",
    port: int = 8000,
    reload: bool = False,
):
    """
    Start GraphQL server.
    
    Args:
        graph: DependencyGraph to serve
        host: Server host
        port: Server port
        reload: Enable auto-reload on code changes
    """
    app = create_server(graph)
    
    print(f"Starting GraphQL server at http://{host}:{port}/graphql")
    print(f"GraphiQL IDE available at http://{host}:{port}/graphql")
    
    uvicorn.run(
        app,
        host=host,
        port=port,
        reload=reload,
    )
