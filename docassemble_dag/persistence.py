"""
Graph persistence for storing and retrieving dependency graphs.

Supports SQLite and PostgreSQL for structured queries, and JSON for simple storage.
"""

import json
import logging
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Iterator, List, Optional, Set, Union

from .db_backends import DatabaseBackend, DBConnection, DBCursor, get_backend
from .exceptions import StorageError
from .graph import DependencyGraph
from .types import DependencyType, Edge, Node, NodeKind

logger = logging.getLogger(__name__)


class GraphStorage:
    """
    Storage interface for dependency graphs.
    
    Supports both SQLite and PostgreSQL for structured queries, and JSON for simple storage.
    
    Connection strings:
    - SQLite: File path (e.g., "graphs.db") or ":memory:" for in-memory
    - PostgreSQL: "postgresql://user:password@host:port/database"
    """
    
    def __init__(
        self,
        connection_string: Optional[Union[str, Path]] = None,
        backend: Optional[DatabaseBackend] = None,
    ) -> None:
        """
        Initialize graph storage.
        
        Args:
            connection_string: Database connection string or path.
                             - SQLite: File path (e.g., "graphs.db") or ":memory:"
                             - PostgreSQL: "postgresql://user:password@host:port/database"
            backend: Optional database backend. If None, auto-detected from connection_string.
        """
        if connection_string is None:
            connection_string = ":memory:"
        
        # Convert Path to string
        if isinstance(connection_string, Path):
            connection_string = str(connection_string)
        
        self.connection_string = connection_string
        
        # Auto-detect backend if not provided
        if backend is None:
            self.backend = get_backend(connection_string)
        else:
            self.backend = backend
        
        self.conn: Optional[DBConnection] = None
        self._initialize_database()
    
    def _initialize_database(self) -> None:
        """Initialize database connection and schema."""
        try:
            self.conn = self.backend.connect(self.connection_string)
            # For PostgreSQL, use RealDictCursor for dict-like row access
            if self.backend.__class__.__name__ == "PostgreSQLBackend":
                try:
                    import psycopg2.extras
                    # Store connection type for later cursor creation
                    self._use_dict_cursor = True
                except ImportError:
                    self._use_dict_cursor = False
            else:
                self._use_dict_cursor = False
            
            cursor = self._get_cursor()
            self.backend.create_schema(cursor)
            self.conn.commit()
            cursor.close()
            logger.debug(f"Initialized {type(self.backend).__name__} database")
        except Exception as e:
            raise StorageError(
                f"Failed to initialize database: {e}",
                operation="initialize_database",
                original_error=e,
            ) from e
    
    def _get_cursor(self) -> DBCursor:
        """Get database cursor, using RealDictCursor for PostgreSQL if available."""
        if self._use_dict_cursor:
            try:
                import psycopg2.extras
                return self.conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            except ImportError:
                pass
        return self.conn.cursor()
    
    @contextmanager
    def _transaction(self) -> Iterator[DBCursor]:
        """
        Context manager for database transactions with automatic rollback on error.
        
        Note: Uses default isolation level (READ COMMITTED for PostgreSQL, 
        SERIALIZABLE for SQLite). For strict consistency requirements, consider
        setting isolation level explicitly at connection time.
        """
        if not self.conn:
            self._initialize_database()
        
        cursor = self._get_cursor()
        try:
            cursor.execute("BEGIN")
            yield cursor
            self.conn.commit()
        except Exception as e:
            self.conn.rollback()
            raise StorageError(
                f"Database transaction failed: {e}",
                operation="transaction",
                original_error=e,
            ) from e
        finally:
            cursor.close()
    
    def save_graph(
        self,
        graph: DependencyGraph,
        name: str,
        version: Optional[str] = None,
        metadata: Optional[Dict] = None,
    ) -> int:
        """
        Save a dependency graph to storage.
        
        Uses transactions to ensure atomicity - if any part fails, entire operation rolls back.
        
        Args:
            graph: Dependency graph to save
            name: Name/identifier for the graph
            version: Optional version string
            metadata: Optional metadata dictionary
        
        Returns:
            Graph ID in database
            
        Raises:
            StorageError: If save operation fails
        """
        if not self.conn:
            self._initialize_database()
        
        try:
            placeholder = self.backend.get_placeholder()
            
            with self._transaction() as cursor:
                # Insert graph record
                # Both SQLite and PostgreSQL use JSON strings for metadata
                metadata_json = json.dumps(metadata) if metadata else None
                
                cursor.execute(
                    f"INSERT INTO graphs (name, version, metadata) VALUES ({placeholder}, {placeholder}, {placeholder})",
                    (name, version, metadata_json)
                )
                graph_id = cursor.lastrowid
                
                # Insert nodes
                for node in graph.nodes.values():
                    node_metadata_json = json.dumps(node.metadata) if node.metadata else None
                    cursor.execute(
                        f"""INSERT INTO nodes 
                           (graph_id, name, kind, source, authority, file_path, line_number, metadata)
                           VALUES ({placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder})""",
                        (
                            graph_id,
                            node.name,
                            node.kind.value,
                            node.source,
                            node.authority,
                            node.file_path,
                            node.line_number,
                            node_metadata_json,
                        )
                    )
                
                # Insert edges
                for edge in graph.edges:
                    edge_metadata_json = json.dumps(edge.metadata) if edge.metadata else None
                    cursor.execute(
                        f"""INSERT INTO edges
                           (graph_id, from_node, to_node, dep_type, file_path, line_number, metadata)
                           VALUES ({placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder})""",
                        (
                            graph_id,
                            edge.from_node,
                            edge.to_node,
                            edge.dep_type.value,
                            edge.file_path,
                            edge.line_number,
                            edge_metadata_json,
                        )
                    )
                
                # Transaction commits automatically via context manager
                logger.info(f"Saved graph '{name}' with {len(graph.nodes)} nodes and {len(graph.edges)} edges")
                return graph_id
        except StorageError:
            raise
        except Exception as e:
            raise StorageError(
                f"Failed to save graph '{name}': {e}",
                operation="save_graph",
                original_error=e,
            ) from e
    
    def load_graph(self, graph_id: int) -> Optional[DependencyGraph]:
        """
        Load a dependency graph from storage.
        
        Args:
            graph_id: Graph ID in database
            
        Returns:
            DependencyGraph or None if not found
            
        Raises:
            StorageError: If load operation fails
        """
        if not self.conn:
            return None
        
        try:
            placeholder = self.backend.get_placeholder()
            cursor = self._get_cursor()
            
            # Load nodes
            cursor.execute(
                f"SELECT * FROM nodes WHERE graph_id = {placeholder}",
                (graph_id,)
            )
            nodes: Dict[str, Node] = {}
            
            for row in cursor.fetchall():
                row_meta = self.backend.get_row_accessor(row, 'metadata')
                metadata = json.loads(row_meta) if row_meta else {}
                nodes[self.backend.get_row_accessor(row, 'name')] = Node(
                    name=self.backend.get_row_accessor(row, 'name'),
                    kind=NodeKind(self.backend.get_row_accessor(row, 'kind')),
                    source=self.backend.get_row_accessor(row, 'source'),
                    authority=self.backend.get_row_accessor(row, 'authority'),
                    file_path=self.backend.get_row_accessor(row, 'file_path'),
                    line_number=self.backend.get_row_accessor(row, 'line_number'),
                    metadata=metadata,
                )
            
            # Load edges
            cursor.execute(
                f"SELECT * FROM edges WHERE graph_id = {placeholder}",
                (graph_id,)
            )
            edges: List[Edge] = []
            
            for row in cursor.fetchall():
                row_meta = self.backend.get_row_accessor(row, 'metadata')
                metadata = json.loads(row_meta) if row_meta else {}
                edges.append(Edge(
                    from_node=self.backend.get_row_accessor(row, 'from_node'),
                    to_node=self.backend.get_row_accessor(row, 'to_node'),
                    dep_type=DependencyType(self.backend.get_row_accessor(row, 'dep_type')),
                    file_path=self.backend.get_row_accessor(row, 'file_path'),
                    line_number=self.backend.get_row_accessor(row, 'line_number'),
                    metadata=metadata,
                ))
            
            if not nodes:
                return None
            
            return DependencyGraph(nodes, edges)
        except Exception as e:
            raise StorageError(
                f"Failed to load graph ID {graph_id}: {e}",
                operation="load_graph",
                original_error=e,
            ) from e
    
    def list_graphs(self) -> List[Dict]:
        """List all saved graphs."""
        if not self.conn:
            return []
        
        cursor = self._get_cursor()
        cursor.execute("SELECT id, name, version, created_at FROM graphs ORDER BY created_at DESC")
        
        return [
            {
                'id': self.backend.get_row_accessor(row, 'id'),
                'name': self.backend.get_row_accessor(row, 'name'),
                'version': self.backend.get_row_accessor(row, 'version'),
                'created_at': self.backend.get_row_accessor(row, 'created_at'),
            }
            for row in cursor.fetchall()
        ]
        cursor.close()
    
    def close(self) -> None:
        """Close database connection."""
        if self.conn:
            self.conn.close()
            self.conn = None


def save_graph_json(graph: DependencyGraph, file_path: Path) -> None:
    """
    Save graph to JSON file.
    
    Args:
        graph: Dependency graph to save
        file_path: Path to JSON file
        
    Raises:
        StorageError: If save operation fails
    """
    try:
        graph_dict = graph.to_json_struct()
        graph_dict['_metadata'] = {
            'saved_at': datetime.now().isoformat(),
            'version': '0.5.1',
        }
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(graph_dict, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Saved graph to {file_path}")
    except Exception as e:
        raise StorageError(
            f"Failed to save graph to {file_path}: {e}",
            operation="save_graph_json",
            original_error=e,
        ) from e


def load_graph_json(file_path: Path) -> DependencyGraph:
    """
    Load graph from JSON file.
    
    Args:
        file_path: Path to JSON file
        
    Returns:
        DependencyGraph
        
    Raises:
        StorageError: If load operation fails
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            graph_dict = json.load(f)
        
        # Reconstruct nodes
        nodes: Dict[str, Node] = {}
        for node_data in graph_dict.get('nodes', []):
            nodes[node_data['name']] = Node(
                name=node_data['name'],
                kind=NodeKind(node_data['kind']),
                source=node_data['source'],
                authority=node_data.get('authority'),
                file_path=node_data.get('file_path'),
                line_number=node_data.get('line_number'),
                metadata=node_data.get('metadata', {}),
            )
        
        # Reconstruct edges
        edges: List[Edge] = []
        for edge_data in graph_dict.get('edges', []):
            edges.append(Edge(
                from_node=edge_data['from'],
                to_node=edge_data['to'],
                dep_type=DependencyType(edge_data['type']),
                file_path=edge_data.get('file_path'),
                line_number=edge_data.get('line_number'),
                metadata=edge_data.get('metadata', {}),
            ))
        
        return DependencyGraph(nodes, edges)
    except Exception as e:
        raise StorageError(
            f"Failed to load graph from {file_path}: {e}",
            operation="load_graph_json",
            original_error=e,
        ) from e
