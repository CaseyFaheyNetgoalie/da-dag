"""
Tests for database backend abstraction (db_backends.py).
"""

import pytest
from docassemble_dag.db_backends import (
    DatabaseBackend,
    PostgreSQLBackend,
    SQLiteBackend,
    get_backend,
)


class TestBackendDetection:
    """Test backend auto-detection from connection strings."""
    
    def test_detect_sqlite_file(self):
        """Test SQLite detection from file path."""
        backend = get_backend("graphs.db")
        assert isinstance(backend, SQLiteBackend)
    
    def test_detect_sqlite_memory(self):
        """Test SQLite detection from :memory:."""
        backend = get_backend(":memory:")
        assert isinstance(backend, SQLiteBackend)
    
    def test_detect_sqlite_path_object(self):
        """Test SQLite detection from Path-like string."""
        backend = get_backend("/path/to/graphs.db")
        assert isinstance(backend, SQLiteBackend)
    
    def test_detect_postgresql_standard(self):
        """Test PostgreSQL detection from standard connection string."""
        backend = get_backend("postgresql://user:pass@localhost:5432/db")
        assert isinstance(backend, PostgreSQLBackend)
    
    def test_detect_postgresql_alternative(self):
        """Test PostgreSQL detection from postgres:// connection string."""
        backend = get_backend("postgres://user:pass@localhost:5432/db")
        assert isinstance(backend, PostgreSQLBackend)
    
    def test_detect_postgresql_case_insensitive(self):
        """Test PostgreSQL detection is case-insensitive."""
        backend = get_backend("POSTGRESQL://user:pass@localhost/db")
        assert isinstance(backend, PostgreSQLBackend)
        
        backend = get_backend("PostgreSQL://user:pass@localhost/db")
        assert isinstance(backend, PostgreSQLBackend)


class TestSQLiteBackend:
    """Test SQLite backend implementation."""
    
    def test_placeholder(self):
        """Test SQLite placeholder format."""
        backend = SQLiteBackend()
        assert backend.get_placeholder() == "?"
    
    def test_auto_increment(self):
        """Test SQLite auto-increment syntax."""
        backend = SQLiteBackend()
        assert "AUTOINCREMENT" in backend.get_auto_increment()
    
    def test_timestamp_default(self):
        """Test SQLite timestamp default."""
        backend = SQLiteBackend()
        assert backend.get_timestamp_default() == "CURRENT_TIMESTAMP"
    
    def test_connect_memory(self):
        """Test SQLite memory connection."""
        backend = SQLiteBackend()
        conn = backend.connect(":memory:")
        assert conn is not None
        conn.close()
    
    def test_create_schema(self):
        """Test SQLite schema creation."""
        backend = SQLiteBackend()
        conn = backend.connect(":memory:")
        cursor = conn.cursor()
        
        backend.create_schema(cursor)
        conn.commit()
        
        # Verify tables were created
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        
        assert "graphs" in tables
        assert "nodes" in tables
        assert "edges" in tables
        
        cursor.close()
        conn.close()
    
    def test_get_row_accessor(self):
        """Test SQLite row accessor."""
        backend = SQLiteBackend()
        conn = backend.connect(":memory:")
        cursor = conn.cursor()
        
        cursor.execute("CREATE TABLE test (id INTEGER, name TEXT)")
        cursor.execute("INSERT INTO test VALUES (1, 'test')")
        cursor.execute("SELECT * FROM test")
        
        row = cursor.fetchone()
        assert backend.get_row_accessor(row, 'id') == 1
        assert backend.get_row_accessor(row, 'name') == 'test'
        
        cursor.close()
        conn.close()


class TestPostgreSQLBackend:
    """Test PostgreSQL backend implementation."""
    
    def test_placeholder(self):
        """Test PostgreSQL placeholder format."""
        backend = PostgreSQLBackend()
        assert backend.get_placeholder() == "%s"
    
    def test_auto_increment(self):
        """Test PostgreSQL auto-increment syntax."""
        backend = PostgreSQLBackend()
        assert "SERIAL" in backend.get_auto_increment()
    
    def test_timestamp_default(self):
        """Test PostgreSQL timestamp default."""
        backend = PostgreSQLBackend()
        assert backend.get_timestamp_default() == "CURRENT_TIMESTAMP"
    
    def test_connect_requires_psycopg2(self):
        """Test that PostgreSQL requires psycopg2."""
        backend = PostgreSQLBackend()
        
        # This will fail if psycopg2 is not installed
        # We'll test the ImportError path
        try:
            conn = backend.connect("postgresql://test")
            # If connection succeeds, that's fine
            conn.close()
        except ImportError as e:
            assert "psycopg2" in str(e).lower()
    
    @pytest.mark.skip(reason="Requires PostgreSQL instance")
    def test_create_schema_postgresql(self):
        """Test PostgreSQL schema creation (requires DB)."""
        backend = PostgreSQLBackend()
        # This test would require a real PostgreSQL instance
        # Skipped by default, but structure is here
        pass


class TestBackendComparison:
    """Test differences between SQLite and PostgreSQL backends."""
    
    def test_placeholder_difference(self):
        """Test that placeholders differ between backends."""
        sqlite = SQLiteBackend()
        postgres = PostgreSQLBackend()
        
        assert sqlite.get_placeholder() == "?"
        assert postgres.get_placeholder() == "%s"
        assert sqlite.get_placeholder() != postgres.get_placeholder()
    
    def test_auto_increment_difference(self):
        """Test that auto-increment syntax differs."""
        sqlite = SQLiteBackend()
        postgres = PostgreSQLBackend()
        
        sqlite_syntax = sqlite.get_auto_increment()
        postgres_syntax = postgres.get_auto_increment()
        
        assert "AUTOINCREMENT" in sqlite_syntax or "AUTOINCREMENT" in sqlite_syntax.upper()
        assert "SERIAL" in postgres_syntax
