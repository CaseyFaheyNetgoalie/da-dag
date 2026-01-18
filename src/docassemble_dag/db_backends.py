"""
Database backend abstraction for graph persistence.

Supports both SQLite and PostgreSQL with a unified interface.
"""

import logging
from abc import ABC, abstractmethod
from contextlib import contextmanager
from typing import Any, Dict, Iterator, List, Optional, Protocol

logger = logging.getLogger(__name__)


class DBCursor(Protocol):
    """Protocol for database cursor objects."""
    
    def execute(self, query: str, params: Optional[tuple] = None) -> None:
        """Execute a query."""
        ...
    
    def fetchall(self) -> List[Any]:
        """Fetch all results."""
        ...
    
    def fetchone(self) -> Optional[Any]:
        """Fetch one result."""
        ...
    
    @property
    def lastrowid(self) -> int:
        """Get last inserted row ID."""
        ...
    
    @property
    def rowcount(self) -> int:
        """Get number of affected rows."""
        ...


class DBConnection(Protocol):
    """Protocol for database connection objects."""
    
    def cursor(self) -> DBCursor:
        """Get a cursor."""
        ...
    
    def commit(self) -> None:
        """Commit transaction."""
        ...
    
    def rollback(self) -> None:
        """Rollback transaction."""
        ...
    
    def close(self) -> None:
        """Close connection."""
        ...


class DatabaseBackend(ABC):
    """
    Abstract base class for database backends.
    
    Provides a unified interface for SQLite and PostgreSQL operations.
    """
    
    @abstractmethod
    def connect(self, connection_string: str) -> DBConnection:
        """Establish database connection."""
        pass
    
    @abstractmethod
    def get_placeholder(self) -> str:
        """Get SQL placeholder for parameterized queries (? for SQLite, %s for PostgreSQL)."""
        pass
    
    @abstractmethod
    def get_auto_increment(self) -> str:
        """Get auto-increment syntax (AUTOINCREMENT for SQLite, SERIAL for PostgreSQL)."""
        pass
    
    @abstractmethod
    def get_timestamp_default(self) -> str:
        """Get timestamp default syntax."""
        pass
    
    @abstractmethod
    def create_schema(self, cursor: DBCursor) -> None:
        """Create database schema (tables and indexes)."""
        pass
    
    @abstractmethod
    def get_row_accessor(self, row: Any, key: str) -> Any:
        """Get value from database row (handles row factory differences)."""
        pass


class SQLiteBackend(DatabaseBackend):
    """SQLite database backend."""
    
    def connect(self, connection_string: str) -> DBConnection:
        """Establish SQLite connection."""
        import sqlite3
        
        # Handle :memory: and file paths
        if connection_string == ":memory:":
            conn = sqlite3.connect(":memory:")
        else:
            conn = sqlite3.connect(connection_string)
        
        conn.row_factory = sqlite3.Row
        return conn
    
    def get_placeholder(self) -> str:
        """SQLite uses ? for placeholders."""
        return "?"
    
    def get_auto_increment(self) -> str:
        """SQLite uses INTEGER PRIMARY KEY AUTOINCREMENT."""
        return "INTEGER PRIMARY KEY AUTOINCREMENT"
    
    def get_timestamp_default(self) -> str:
        """SQLite uses CURRENT_TIMESTAMP."""
        return "CURRENT_TIMESTAMP"
    
    def create_schema(self, cursor: DBCursor) -> None:
        """Create SQLite schema."""
        placeholder = self.get_placeholder()
        
        # Graphs table
        cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS graphs (
                id {self.get_auto_increment()},
                name TEXT NOT NULL,
                version TEXT,
                file_path TEXT,
                created_at TIMESTAMP DEFAULT {self.get_timestamp_default()},
                metadata TEXT
            )
        """)
        
        # Nodes table
        cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS nodes (
                id {self.get_auto_increment()},
                graph_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                kind TEXT NOT NULL,
                source TEXT NOT NULL,
                authority TEXT,
                file_path TEXT,
                line_number INTEGER,
                metadata TEXT,
                FOREIGN KEY (graph_id) REFERENCES graphs(id) ON DELETE CASCADE,
                UNIQUE(graph_id, name)
            )
        """)
        
        # Edges table
        cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS edges (
                id {self.get_auto_increment()},
                graph_id INTEGER NOT NULL,
                from_node TEXT NOT NULL,
                to_node TEXT NOT NULL,
                dep_type TEXT NOT NULL,
                file_path TEXT,
                line_number INTEGER,
                metadata TEXT,
                FOREIGN KEY (graph_id) REFERENCES graphs(id) ON DELETE CASCADE
            )
        """)
        
        # Create indexes
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_nodes_graph ON nodes(graph_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_nodes_name ON nodes(name)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_edges_graph ON edges(graph_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_edges_from ON edges(from_node)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_edges_to ON edges(to_node)")
    
    def get_row_accessor(self, row: Any, key: str) -> Any:
        """SQLite Row objects support dictionary-like access."""
        return row[key]


class PostgreSQLBackend(DatabaseBackend):
    """PostgreSQL database backend."""
    
    def connect(self, connection_string: str) -> DBConnection:
        """Establish PostgreSQL connection."""
        try:
            import psycopg2
            from psycopg2.extras import RealDictCursor
        except ImportError:
            raise ImportError(
                "PostgreSQL support requires psycopg2. "
                "Install with: pip install psycopg2-binary"
            )
        
        conn = psycopg2.connect(connection_string)
        return conn
    
    def get_placeholder(self) -> str:
        """PostgreSQL uses %s for placeholders."""
        return "%s"
    
    def get_auto_increment(self) -> str:
        """PostgreSQL uses SERIAL PRIMARY KEY."""
        return "SERIAL PRIMARY KEY"
    
    def get_timestamp_default(self) -> str:
        """PostgreSQL uses CURRENT_TIMESTAMP."""
        return "CURRENT_TIMESTAMP"
    
    def create_schema(self, cursor: DBCursor) -> None:
        """Create PostgreSQL schema."""
        placeholder = self.get_placeholder()
        
        # Graphs table
        cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS graphs (
                id {self.get_auto_increment()},
                name VARCHAR(255) NOT NULL,
                version VARCHAR(50),
                file_path VARCHAR(512),
                created_at TIMESTAMP DEFAULT {self.get_timestamp_default()},
                metadata JSONB
            )
        """)
        
        # Nodes table
        cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS nodes (
                id {self.get_auto_increment()},
                graph_id INTEGER NOT NULL REFERENCES graphs(id) ON DELETE CASCADE,
                name VARCHAR(255) NOT NULL,
                kind VARCHAR(50) NOT NULL,
                source VARCHAR(50) NOT NULL,
                authority TEXT,
                file_path VARCHAR(512),
                line_number INTEGER,
                metadata JSONB,
                UNIQUE(graph_id, name)
            )
        """)
        
        # Edges table
        cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS edges (
                id {self.get_auto_increment()},
                graph_id INTEGER NOT NULL REFERENCES graphs(id) ON DELETE CASCADE,
                from_node VARCHAR(255) NOT NULL,
                to_node VARCHAR(255) NOT NULL,
                dep_type VARCHAR(50) NOT NULL,
                file_path VARCHAR(512),
                line_number INTEGER,
                metadata JSONB
            )
        """)
        
        # Create indexes
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_nodes_graph ON nodes(graph_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_nodes_name ON nodes(name)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_edges_graph ON edges(graph_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_edges_from ON edges(from_node)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_edges_to ON edges(to_node)")
    
    def get_row_accessor(self, row: Any, key: str) -> Any:
        """PostgreSQL row access - supports both dict and tuple-like rows."""
        # Try dictionary-like access first (RealDictCursor)
        if hasattr(row, '__getitem__') and key in row:
            return row[key]
        # Fallback to attribute access (named tuples)
        if hasattr(row, key):
            return getattr(row, key)
        # Last resort: try index access if row is tuple-like
        return row[key] if hasattr(row, '__getitem__') else None
    
    def connect(self, connection_string: str) -> DBConnection:
        """Establish PostgreSQL connection with RealDictCursor."""
        try:
            import psycopg2
            from psycopg2.extras import RealDictCursor
        except ImportError:
            raise ImportError(
                "PostgreSQL support requires psycopg2. "
                "Install with: pip install psycopg2-binary"
            )
        
        conn = psycopg2.connect(connection_string)
        # Configure connection to use RealDictCursor for dict-like row access
        # Note: This is set per-query, not globally
        return conn


def get_backend(connection_string: str) -> DatabaseBackend:
    """
    Detect and return appropriate database backend.
    
    Args:
        connection_string: Database connection string or path
        
    Returns:
        DatabaseBackend instance (SQLiteBackend or PostgreSQLBackend)
        
    Raises:
        ValueError: If connection string format is invalid
    """
    connection_string_lower = connection_string.lower().strip()
    
    # PostgreSQL connection strings start with postgresql:// or postgres://
    if connection_string_lower.startswith(('postgresql://', 'postgres://')):
        return PostgreSQLBackend()
    
    # SQLite for :memory:, .db files, or other file paths
    if connection_string == ":memory:" or connection_string.endswith('.db'):
        return SQLiteBackend()
    
    # Default to SQLite for backward compatibility
    return SQLiteBackend()
