# PostgreSQL Support

## Overview

The `docassemble-dag` package now supports both **SQLite** and **PostgreSQL** for graph persistence. The database backend is automatically detected from the connection string.

## Installation

### SQLite (Default)
SQLite support is built-in - no additional dependencies needed.

### PostgreSQL (Optional)
To enable PostgreSQL support, install the optional dependency:

```bash
pip install docassemble-dag[postgresql]
# or
pip install psycopg2-binary>=2.9.0
```

## Usage

### SQLite (Default)

```python
from docassemble_dag.persistence import GraphStorage
from pathlib import Path

# File-based SQLite
storage = GraphStorage(connection_string="graphs.db")

# In-memory SQLite
storage = GraphStorage(connection_string=":memory:")

# Path object (converted to string)
storage = GraphStorage(connection_string=Path("graphs.db"))
```

### PostgreSQL

```python
from docassemble_dag.persistence import GraphStorage

# PostgreSQL connection string
connection_string = "postgresql://user:password@localhost:5432/database_name"

storage = GraphStorage(connection_string=connection_string)

# Save a graph
graph_id = storage.save_graph(graph, name="my_interview", version="1.0")

# Load a graph
loaded_graph = storage.load_graph(graph_id)

# List all graphs
graphs = storage.list_graphs()
```

### Connection String Formats

**SQLite:**
- File path: `"graphs.db"` or `"path/to/graphs.db"`
- In-memory: `":memory:"`
- Path object: `Path("graphs.db")`

**PostgreSQL:**
- Standard: `"postgresql://user:password@host:port/database"`
- Alternative: `"postgres://user:password@host:port/database"`

### Environment Variables

You can use environment variables for PostgreSQL connection:

```python
import os
from docassemble_dag.persistence import GraphStorage

# Read from environment
database_url = os.environ.get("DATABASE_URL")
if database_url:
    storage = GraphStorage(connection_string=database_url)
```

```bash
# Set environment variable
export DATABASE_URL="postgresql://user:password@localhost:5432/dag_database"
python your_script.py
```

## Database Schema

Both SQLite and PostgreSQL use the same logical schema:

### Tables

1. **graphs** - Graph metadata
   - `id` - Primary key (auto-increment)
   - `name` - Graph name/identifier
   - `version` - Optional version string
   - `file_path` - Source file path
   - `created_at` - Timestamp
   - `metadata` - JSON metadata (TEXT in SQLite, JSONB in PostgreSQL)

2. **nodes** - Graph nodes
   - `id` - Primary key
   - `graph_id` - Foreign key to graphs
   - `name` - Node name
   - `kind` - Node kind (variable, question, rule, etc.)
   - `source` - Source type (user_input, derived)
   - `authority` - Legal authority citation
   - `file_path` - Source file path
   - `line_number` - Line number in source
   - `metadata` - JSON metadata

3. **edges** - Graph edges (dependencies)
   - `id` - Primary key
   - `graph_id` - Foreign key to graphs
   - `from_node` - Source node name
   - `to_node` - Target node name
   - `dep_type` - Dependency type (explicit, implicit, conditional, reconsider)
   - `file_path` - Source file path
   - `line_number` - Line number in source
   - `metadata` - JSON metadata

### Differences

| Feature | SQLite | PostgreSQL |
|---------|--------|------------|
| Placeholder | `?` | `%s` |
| Auto-increment | `INTEGER PRIMARY KEY AUTOINCREMENT` | `SERIAL PRIMARY KEY` |
| JSON Storage | `TEXT` (JSON string) | `JSONB` (native JSON) |
| Row Factory | `sqlite3.Row` | `RealDictCursor` |
| VARCHAR | `TEXT` | `VARCHAR(n)` |

## API Compatibility

The API is **fully compatible** between SQLite and PostgreSQL:

```python
# Works the same for both databases
storage = GraphStorage(connection_string="...")  # Auto-detects backend
graph_id = storage.save_graph(graph, name="test")
loaded = storage.load_graph(graph_id)
graphs = storage.list_graphs()
storage.close()
```

## Backend Auto-Detection

The backend is automatically detected from the connection string:

```python
from docassemble_dag.db_backends import get_backend

# SQLite
backend = get_backend(":memory:")  # SQLiteBackend
backend = get_backend("graphs.db")  # SQLiteBackend

# PostgreSQL
backend = get_backend("postgresql://...")  # PostgreSQLBackend
backend = get_backend("postgres://...")  # PostgreSQLBackend
```

## Manual Backend Selection

You can also specify the backend explicitly:

```python
from docassemble_dag.persistence import GraphStorage
from docassemble_dag.db_backends import PostgreSQLBackend

backend = PostgreSQLBackend()
storage = GraphStorage(
    connection_string="postgresql://...",
    backend=backend
)
```

## Testing

### SQLite Tests

SQLite tests run by default (no setup required):

```bash
pytest tests/test_persistence.py
```

### PostgreSQL Tests

PostgreSQL tests are marked as integration tests and require a running PostgreSQL instance:

```bash
# Set connection string
export DATABASE_URL="postgresql://user:password@localhost:5432/test_db"

# Run PostgreSQL tests
pytest tests/test_postgresql.py -m integration
```

## Benefits of PostgreSQL

1. **Better Concurrency** - Multiple writers supported
2. **Better JSON Support** - Native JSONB type with indexing
3. **Production Ready** - Better suited for production deployments
4. **Scalability** - Handles larger datasets better
5. **Advanced Features** - Full-text search, JSON queries, etc.

## Migration from SQLite to PostgreSQL

You can migrate graphs between databases:

```python
from docassemble_dag.persistence import GraphStorage

# Load from SQLite
sqlite_storage = GraphStorage("graphs.db")
graph_id = sqlite_storage.list_graphs()[0]['id']
graph = sqlite_storage.load_graph(graph_id)

# Save to PostgreSQL
pg_storage = GraphStorage("postgresql://...")
new_graph_id = pg_storage.save_graph(graph, name=graph.name)
```

## Examples

### Example: Save to PostgreSQL

```python
from docassemble_dag.persistence import GraphStorage
from docassemble_dag.parser import DocassembleParser
from pathlib import Path

# Parse interview
parser = DocassembleParser(Path("interview.yaml").read_text())
nodes = parser.extract_nodes()
edges = parser.extract_edges(nodes)
graph = DependencyGraph(nodes, edges)

# Save to PostgreSQL
storage = GraphStorage("postgresql://user:pass@localhost/dag_db")
graph_id = storage.save_graph(
    graph,
    name="my_interview",
    version="1.0",
    metadata={"author": "John Doe", "description": "Legal interview"}
)
print(f"Saved graph with ID: {graph_id}")
```

### Example: Query Graphs from PostgreSQL

```python
from docassemble_dag.persistence import GraphStorage

storage = GraphStorage("postgresql://user:pass@localhost/dag_db")

# List all graphs
graphs = storage.list_graphs()
for graph_info in graphs:
    print(f"Graph: {graph_info['name']} (ID: {graph_info['id']})")
    
    # Load specific graph
    graph = storage.load_graph(graph_info['id'])
    print(f"  Nodes: {len(graph.nodes)}, Edges: {len(graph.edges)}")
```

## Troubleshooting

### ImportError: No module named 'psycopg2'

**Solution**: Install PostgreSQL support:
```bash
pip install psycopg2-binary
```

### Connection Failed

**Solution**: Check PostgreSQL connection string and database exists:
```python
# Test connection
import psycopg2
conn = psycopg2.connect("postgresql://user:pass@localhost/db")
conn.close()
```

### JSONB Type Errors

**Solution**: Ensure you're using psycopg2 >= 2.9.0 which supports JSONB.

## Performance Considerations

- **SQLite**: Better for single-user applications and small datasets
- **PostgreSQL**: Better for multi-user, concurrent access, and large datasets
- **JSONB**: PostgreSQL's JSONB allows efficient JSON queries and indexing

## Security

**Important**: Never hardcode credentials in connection strings. Use environment variables or secure credential management:

```python
import os
from docassemble_dag.persistence import GraphStorage

# Good: Use environment variable
storage = GraphStorage(os.environ["DATABASE_URL"])

# Bad: Hardcoded credentials
storage = GraphStorage("postgresql://user:password@localhost/db")
```
