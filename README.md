# Docassemble DAG

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Python](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)

**Static analyzer and dependency graph toolkit for [Docassemble](https://docassemble.org/) YAML interview files.**

Extracts explicit dependency graphs, validates interviews, tracks legal citations, and provides powerful querying capabilities for legal tech workflows.

## Table of Contents

- [Overview](#overview)
- [What is Docassemble?](#what-is-docassemble)
- [Key Features](#key-features)
- [Quick Start](#quick-start)
- [Installation](#installation)
- [Usage](#usage)
  - [Command Line](#command-line)
  - [Python Library](#python-library)
  - [GraphQL API](#graphql-api)
- [Advanced Features](#advanced-features)
- [Examples](#examples)
- [Legaltech Use Cases](#legaltech-use-cases)
- [Documentation](#documentation)
- [Development](#development)
- [License](#license)

## Overview

[Docassemble](https://docassemble.org/) resolves questions, variables, and rules using an implicit dependency graph. This tool statically analyzes Docassemble interview files and outputs the dependency graph explicitly, enabling:

- **Explainability**: Understand what depends on what
- **Impact Analysis**: See downstream effects of changes
- **Governance**: Track provenance and authority of rules
- **Validation**: Detect cycles, missing dependencies, and policy violations
- **Visualization**: Export to GraphViz, GraphML, and interactive HTML
- **Template Validation**: Verify template variables are defined
- **Compliance Reporting**: Generate audit-ready reports with statute citations
- **Interactive Querying**: GraphQL API for programmatic access

Inspired by [GUAC](https://github.com/guacsec/guac) (Graph for Understanding Artifact Composition) and provenance-rich data graphs.

## What is Docassemble?

[Docassemble](https://docassemble.org/) is a free, open-source expert system for guided interviews and document assembly. It's widely used in legaltech, healthcare, and government services to create interactive forms that gather information and generate documents based on user responses.

Docassemble interviews are defined in YAML files containing questions, variables, and rules that form an implicit dependency graph—this tool makes that graph explicit and analyzable.

## Key Features

### 🔍 **Dependency Analysis**
- Extract explicit and implicit dependencies from YAML
- Support for `depends on:`, `required:`, `show if:`, `enable if:` directives
- AST-based Python code analysis for accurate variable detection
- Object attribute handling (`person.name` → `person` dependency)
- Assembly Line variable recognition (`AL_` prefix)

### 📊 **Multiple Output Formats**
- **JSON**: Structured dependency data
- **DOT**: GraphViz visualization
- **GraphML**: Standard XML format (import into yEd, Gephi, Cytoscape)
- **HTML**: Interactive D3.js viewer with search, filtering, zoom/pan

### ✅ **Validation & Policy Enforcement**
- Cycle detection
- Orphan node detection
- Missing dependency checks
- Undefined reference detection
- Template variable validation (DOCX, PDF, Mako)
- Configurable policy rules with severity levels

### 📝 **Template Validation**
- Validate DOCX, PDF, and Mako templates
- Check that all template variables are defined in interview
- Prevent production errors from undefined variables
- Support for nested object attributes (`{client.name.first}`)

### 📈 **Change Tracking & Comparison**
- Compare two versions of an interview
- Identify added/removed/changed nodes and edges
- Track authority (statute) changes
- Impact analysis for downstream dependencies

### 📋 **Compliance & Governance**
- Generate compliance reports with statute citations
- Track legal authority throughout dependency graph
- Audit trails with file paths and line numbers
- Change impact analysis for regulatory compliance

### 🔌 **GraphQL API**
- Interactive query interface (GraphiQL IDE)
- Query nodes, edges, paths, and graph statistics
- Filter by kind, authority, source
- Transitive dependency/dependent lookups
- RESTful health check endpoint

### 🗂️ **Multi-File & Batch Processing**
- Parse entire directories recursively
- Support for `include:` directives
- Merge multiple interviews into single graph
- Cross-repository dependency tracking via `modules:`

### 💾 **Persistence**
- SQLite support (default, no dependencies)
- PostgreSQL support (optional, for production)
- JSON file storage
- Graph versioning and metadata

## Quick Start

```bash
# Install
pip install -e .

# Analyze a sample interview
python -m docassemble_dag examples/ny_cplr_sample.yaml

# Validate for issues
python -m docassemble_dag examples/ny_cplr_sample.yaml --validate

# Generate interactive HTML viewer
python -m docassemble_dag examples/ny_cplr_sample.yaml --format html -o graph.html

# Start GraphQL server
python -m docassemble_dag examples/ny_cplr_sample.yaml --serve-graphql
# Visit http://localhost:8000/graphql for GraphiQL IDE
```

## Installation

### Basic Installation (SQLite)
```bash
pip install -e .
```

### With PostgreSQL Support
```bash
pip install -e ".[postgresql]"
```

### With GraphQL Support
```bash
pip install -e ".[graphql]"
```

### Troubleshooting

### Common Issues

#### Installation Issues

**Problem: `ImportError: No module named 'psycopg2'`**
```
Solution: Install PostgreSQL support
$ pip install psycopg2-binary
# or
$ pip install -e ".[postgresql]"
```

**Problem: `ImportError: No module named 'strawberry'`**
```
Solution: Install GraphQL dependencies
$ pip install -e ".[graphql]"
# or
$ pip install strawberry-graphql[fastapi] uvicorn
```

**Problem: Pre-commit hooks fail**
```
Solution: Install pre-commit and dependencies
$ pip install -e ".[dev]"
$ pre-commit install
$ pre-commit run --all-files  # Fix any issues
```

#### Parsing Issues

**Problem: `InvalidYAMLError: Failed to parse YAML`**
```
Cause: Malformed YAML syntax
Solution: Check YAML syntax
$ python -c "import yaml; yaml.safe_load(open('interview.yaml'))"

Common issues:
- Missing colons after keys
- Incorrect indentation (use spaces, not tabs)
- Unclosed quotes
- Invalid --- document separators
```

**Problem: `InvalidYAMLError: YAML document must be a dictionary`**
```
Cause: YAML root is a list instead of dict
Solution: Ensure top level is a dictionary

# Wrong:
- item1
- item2

# Correct:
variables:
  - name: item1
  - name: item2
```

**Problem: Variables not detected**
```
Cause: Variables defined outside standard sections
Solution: Use 'variables:', 'fields:', or 'questions:' sections

# Wrong:
my_var:
  expression: age >= 18

# Correct:
variables:
  - name: my_var
    expression: age >= 18
```

**Problem: Dependencies not detected**
```
Cause: Complex Python code or dynamic variable names
Solution: Use AST-parseable code or explicit dependencies

# Hard to detect (dynamic):
var_name = f"{prefix}_status"
value = eval(var_name)

# Easy to detect (static):
variables:
  - name: status
  - name: result
    expression: status == "approved"
    depends on: status  # Explicit
```

#### Graph Issues

**Problem: `CycleError: Cycles detected in dependency graph`**
```
Cause: Circular dependencies
Solution: Review cycle and break the loop

$ python -m docassemble_dag interview.yaml --check-cycles

Example cycle: age -> is_adult -> eligibility -> age
Fix: Remove one dependency or restructure logic
```

**Problem: `GraphError: Node 'xyz' not found in graph`**
```
Cause: Typo in variable name or undefined variable
Solution: Check spelling and ensure variable is defined

$ python -m docassemble_dag interview.yaml --validate

Look for "no_undefined_references" violations
```

**Problem: Many orphan nodes warning**
```
Cause: Unused variables or disconnected logic
Solution: Review orphan nodes and remove if truly unused

$ python -m docassemble_dag interview.yaml --validate

Orphan nodes may be:
- Leftover from refactoring
- Imported but unused variables
- Entry points (roots) - these are OK
```

#### Template Validation Issues

**Problem: Template validation fails for valid variables**
```
Cause: Template uses object attributes not recognized
Solution: Ensure parent objects are defined

# Template uses: {client.name.first}
# Interview must have:
objects:
  - client: Individual
```

**Problem: `ValueError: Unsupported template format`**
```
Cause: Template file type not supported
Solution: Use .docx, .pdf, .mako, .html, or .txt

Supported formats:
- DOCX: requires python-docx (pip install python-docx)
- PDF: requires pdfplumber or PyPDF2
- Mako/HTML/TXT: built-in support
```

**Problem: PDF template validation fails**
```
Cause: PDF parsing libraries not installed
Solution: Install PDF support

$ pip install pdfplumber
# or
$ pip install PyPDF2
```

#### Database Issues

**Problem: PostgreSQL connection fails**
```
Solution: Check connection string format

Correct format:
postgresql://username:password@host:port/database

# Test connection manually:
$ python -c "import psycopg2; psycopg2.connect('postgresql://...')"
```

**Problem: SQLite database locked**
```
Cause: Another process has database open
Solution: Close other connections or use different file

$ lsof graphs.db  # Find processes using file
# Or use :memory: for testing
```

**Problem: `StorageError: Failed to save graph`**
```
Cause: Database permissions or schema issues
Solution: Check write permissions and reinitialize

$ chmod 644 graphs.db
# Or delete and recreate:
$ rm graphs.db
$ python -m docassemble_dag interview.yaml  # Recreates automatically
```

#### GraphQL Server Issues

**Problem: Server won't start**
```
Cause: Port already in use or missing dependencies
Solution: Use different port or install dependencies

$ python -m docassemble_dag interview.yaml --serve-graphql --graphql-port 8080

# Check if port in use:
$ lsof -i :8000

# Install dependencies:
$ pip install -e ".[graphql]"
```

**Problem: GraphQL query returns null**
```
Cause: Node name doesn't exist or query syntax error
Solution: Check node names and query syntax

# List all nodes first:
query {
  nodes {
    name
  }
}

# Then query specific node with exact name
```

**Problem: CORS errors in browser**
```
Cause: GraphQL server doesn't allow browser requests
Solution: Access GraphiQL IDE directly

Visit: http://localhost:8000/graphql (not from another domain)
```

#### Performance Issues

**Problem: Slow graph generation for large interviews**
```
Solution: Process files selectively or use batch mode

# Process only specific files:
$ python -m docassemble_dag specific_file.yaml

# Disable recursive processing:
$ python -m docassemble_dag interviews/ --no-recursive

# For very large graphs, use PostgreSQL:
$ pip install psycopg2-binary
$ export DATABASE_URL="postgresql://..."
```

**Problem: Memory errors with large graphs**
```
Solution: Use database persistence instead of in-memory

from docassemble_dag.persistence import GraphStorage

# Instead of keeping graph in memory:
storage = GraphStorage("postgresql://...")
graph_id = storage.save_graph(graph, "large_graph")

# Load only when needed:
graph = storage.load_graph(graph_id)
```

#### Multi-File Issues

**Problem: Include directives not resolved**
```
Cause: Include files not found or circular includes
Solution: Use --include-files and check paths

$ python -m docassemble_dag main.yaml --include-files

# Ensure include paths are correct:
include:
  - shared/common.yaml  # Relative to main.yaml
```

**Problem: Duplicate nodes when merging files**
```
Cause: Same variable defined in multiple files
Solution: Expected behavior - first definition wins

# Review merged graph:
$ python -m docassemble_dag interviews/ -o merged.json
# Check for duplicates manually
```

### Getting Help

#### Debug Mode
Enable detailed logging:
```python
import logging
logging.basicConfig(level=logging.DEBUG)

from docassemble_dag import DocassembleParser
parser = DocassembleParser(yaml_text)
# ... now shows detailed debug output
```

#### Verbose Output
```bash
# More verbose CLI output (not yet implemented, but you could add)
$ python -m docassemble_dag interview.yaml --verbose
```

#### Check Version
```python
import docassemble_dag
print(docassemble_dag.__version__)  # Should be 0.5.0 or higher
```

#### Validate Installation
```bash
# Run test suite
$ pytest tests/

# Check specific features
$ python -c "from docassemble_dag import GraphValidator; print('✓ Core installed')"
$ python -c "from docassemble_dag.graphql.server import create_server; print('✓ GraphQL installed')"
$ python -c "import psycopg2; print('✓ PostgreSQL support installed')"
```

#### Minimal Reproducible Example
When reporting issues, provide:
```yaml
# minimal_example.yaml
variables:
  - name: age
  - name: is_adult
    expression: age >= 18
```

```bash
# Command that fails
$ python -m docassemble_dag minimal_example.yaml --validate

# Include full error output
```

#### Common Gotchas

1. **Variable names are case-sensitive**: `Age` ≠ `age`

2. **Docassemble uses lazy evaluation**: Static analysis shows dependencies but not execution order

3. **Object attributes**: `person.name` creates dependency on `person`, not `name`

4. **Reconsider directive**: Not fully modeled - use with caution

5. **Template variables**: Must use exact same names as in interview (case-sensitive)

6. **Multi-document YAML**: Multiple `---` separators are merged automatically

7. **Python keywords**: Excluded from dependencies (e.g., `if`, `else`, `True`)

8. **Graph modification**: After loading from database, regenerate caches:
   ```python
   graph._cache_valid = False
   graph._transitive_deps_cache.clear()
   ```

### Platform-Specific Issues

#### Windows

**Problem: Path separators in file paths**
```python
# Use Path objects for cross-platform compatibility
from pathlib import Path
file_path = Path("interviews") / "main.yaml"
```

**Problem: Long paths**
```
Enable long path support in Windows 10+:
Settings > Update & Security > For developers > Enable long paths
```

#### macOS

**Problem: Permission denied on /usr/local**
```
Use virtual environment:
$ python -m venv venv
$ source venv/bin/activate
$ pip install -e .
```

#### Linux

**Problem: PostgreSQL development headers missing**
```
$ sudo apt-get install libpq-dev  # Debian/Ubuntu
$ sudo yum install postgresql-devel  # RHEL/CentOS
```

### Still Having Issues?

1. Check the [GitHub Issues](https://github.com/yourusername/docassemble-dag/issues)
2. Review [EXAMPLES.md](EXAMPLES.md) for working code
3. Check the [test suite](tests/) for usage patterns
4. Create a minimal reproducible example
5. Open a new issue with:
   - Python version (`python --version`)
   - Package version (`pip show docassemble-dag`)
   - Full error traceback
   - Minimal example that reproduces the issue

## Development Installation
```bash
pip install -e ".[dev]"
pre-commit install
```

## Usage

### Command Line

#### Basic Analysis
```bash
# Extract DAG to stdout (JSON format)
python -m docassemble_dag interview.yaml

# Save to file
python -m docassemble_dag interview.yaml -o output.json

# Compact JSON output
python -m docassemble_dag interview.yaml --no-pretty
```

#### Validation
```bash
# Check for cycles
python -m docassemble_dag interview.yaml --check-cycles

# Run all policy validations
python -m docassemble_dag interview.yaml --validate

# Run specific policies and fail on errors
python -m docassemble_dag interview.yaml --validate \
  --policies no_cycles no_undefined_references --fail-on-error
```

#### Export Formats
```bash
# GraphViz DOT format
python -m docassemble_dag interview.yaml --format dot -o graph.dot
dot -Tpng graph.dot -o graph.png

# GraphML (import into yEd, Gephi, Cytoscape)
python -m docassemble_dag interview.yaml --format graphml -o graph.graphml

# Interactive HTML viewer
python -m docassemble_dag interview.yaml --format html -o graph.html
```

#### Template Validation
```bash
# Validate template files against interview
python -m docassemble_dag interview.yaml \
  --validate-templates letter.docx contract.pdf template.mako \
  --fail-on-error
```

#### Change Tracking
```bash
# Compare two versions of an interview
python -m docassemble_dag interview_v2.yaml \
  --compare-baseline=interview_v1.json -o diff.json
```

#### Batch Processing
```bash
# Analyze entire directory
python -m docassemble_dag interviews/ -o combined_graph.json

# Non-recursive directory analysis
python -m docassemble_dag interviews/ --no-recursive

# Parse include: directives (multi-file interviews)
python -m docassemble_dag main.yaml --include-files

# Find nodes by authority (statute citations)
python -m docassemble_dag interviews/ --find-authority "CPLR 308"
```

#### GraphQL Server
```bash
# Start GraphQL server
python -m docassemble_dag interview.yaml --serve-graphql

# Custom port
python -m docassemble_dag interview.yaml --serve-graphql --graphql-port 8080

# Visit http://localhost:8000/graphql for GraphiQL IDE
```

### Python Library

#### Basic Analysis
```python
from docassemble_dag import DocassembleParser, DependencyGraph

# Parse interview
with open('interview.yaml') as f:
    yaml_text = f.read()

parser = DocassembleParser(yaml_text, file_path="interview.yaml")
nodes = parser.extract_nodes()
edges = parser.extract_edges(nodes)
graph = DependencyGraph(nodes, edges)

# Get JSON representation
dag_json = graph.to_json_struct()

# Check for cycles
if graph.has_cycles():
    print("Warning: Cycles detected!")
    for cycle in graph.find_cycles():
        print(f"  {' -> '.join(cycle)}")
```

#### GUAC-Inspired Queries
```python
# Find entry points (root nodes)
roots = graph.find_roots()

# Find isolated nodes
orphans = graph.find_orphans()

# Get all transitive dependencies
all_deps = graph.get_transitive_dependencies("eligible_for_aid")

# Get all transitive dependents (impact analysis)
all_dependents = graph.get_transitive_dependents("age")

# Find dependency path between nodes
path = graph.find_path("age", "eligibility_rule")
if path:
    print(f"Path: {' -> '.join(path)}")

# Find nodes by kind
from docassemble_dag.types import NodeKind
variables = graph.find_nodes_by_kind(NodeKind.VARIABLE)
```

#### Validation
```python
from docassemble_dag import GraphValidator

validator = GraphValidator(graph)
violations = validator.validate_all()

if validator.has_errors():
    validator.print_violations()

summary = validator.get_summary()
print(f"Errors: {summary['errors']}, Warnings: {summary['warnings']}")
```

#### Template Validation
```python
from docassemble_dag.template_validator import validate_templates
from pathlib import Path

template_paths = [Path("letter.docx"), Path("contract.pdf")]
results = validate_templates(template_paths, graph)

for template_path, result in results.items():
    if not result.is_valid:
        print(f"❌ {template_path}")
        print(f"  Undefined: {result.undefined_variables}")
    else:
        print(f"✅ {template_path}")
```

#### Graph Comparison
```python
from docassemble_dag.comparison import compare_graphs

old_graph = DependencyGraph(old_nodes, old_edges)
new_graph = DependencyGraph(new_nodes, new_edges)

diff = compare_graphs(old_graph, new_graph)

print(f"Added nodes: {len(diff.added_nodes)}")
print(f"Removed nodes: {len(diff.removed_nodes)}")
print(f"Authority changes: {len(diff.authority_changes)}")
print(f"Affected downstream: {len(diff.affected_nodes)}")
```

#### Compliance Reporting
```python
from docassemble_dag.compliance import generate_compliance_report

report = generate_compliance_report(
    graph,
    interview_name="Motion Practice Interview",
    baseline_graph=old_graph,  # Optional
    output_path=Path("compliance_report.html")
)

# Access statute mappings
for statute, nodes in report.authority_mapping.items():
    print(f"{statute}: {', '.join(nodes)}")
```

#### Batch Processing
```python
from docassemble_dag.utils import parse_multiple_files, find_yaml_files
from pathlib import Path

# Find all YAML files in directory
files = find_yaml_files(Path("interviews/"), recursive=True)

# Parse and merge into single graph
graph = parse_multiple_files(files)

# Find nodes by authority
from docassemble_dag.utils import find_nodes_by_authority
cplr_nodes = find_nodes_by_authority(graph, "CPLR 308")
```

#### Persistence
```python
from docassemble_dag.persistence import GraphStorage

# SQLite (default)
storage = GraphStorage("graphs.db")

# PostgreSQL
storage = GraphStorage("postgresql://user:pass@localhost/db")

# Save graph
graph_id = storage.save_graph(
    graph,
    name="my_interview",
    version="1.0",
    metadata={"author": "Jane Doe"}
)

# Load graph
loaded_graph = storage.load_graph(graph_id)

# List all graphs
graphs = storage.list_graphs()
```

### GraphQL API

#### Starting the Server
```python
from docassemble_dag.graphql.server import serve

serve(graph, host="0.0.0.0", port=8000)
# Visit http://localhost:8000/graphql
```

#### Example Queries

**Get Node with Full Details:**
```graphql
query {
  node(name: "age") {
    name
    kind
    source
    authority
    filePath
    lineNumber
    metadata
    dependencies {
      name
      kind
      authority
    }
    dependents {
      name
      kind
    }
  }
}
```

**Find Path Between Nodes:**
```graphql
query {
  path(from: "age", to: "eligibility_rule") {
    nodes
    length
  }
}
```

**Complex Path Analysis:**
```graphql
query {
  # Find all paths between multiple node pairs
  path1: path(from: "income", to: "eligible") {
    nodes
    length
  }
  path2: path(from: "age", to: "eligible") {
    nodes
    length
  }
}
```

**Filter Nodes by Authority:**
```graphql
query {
  nodesByAuthority(pattern: "CPLR") {
    name
    authority
    kind
    filePath
    lineNumber
  }
}
```

**Find All Nodes of Specific Kind:**
```graphql
query {
  # Get all variables
  variables: nodes(kind: VARIABLE) {
    name
    source
    authority
  }
  
  # Get all questions
  questions: nodes(kind: QUESTION) {
    name
    filePath
    lineNumber
  }
}
```

**Filter by Source Type:**
```graphql
query {
  # Get all user input nodes
  userInputs: nodes(source: "user_input") {
    name
    kind
  }
  
  # Get all derived nodes
  derived: nodes(source: "derived") {
    name
    kind
    authority
  }
}
```

**Graph Statistics:**
```graphql
query {
  graphStats {
    nodeCount
    edgeCount
    hasCycles
    rootCount
    orphanCount
  }
}
```

**Comprehensive Graph Overview:**
```graphql
query {
  graphStats {
    nodeCount
    edgeCount
    hasCycles
    rootCount
    orphanCount
  }
  
  # Get all nodes with authority
  authorityNodes: nodesByAuthority(pattern: "") {
    name
    authority
    kind
  }
  
  # Get all edges
  edges {
    fromNode
    toNode
    type
    filePath
    lineNumber
  }
}
```

**Transitive Dependents (Impact Analysis):**
```graphql
query {
  node(name: "age") {
    name
    transitiveDependents {
      name
      kind
      authority
    }
  }
}
```

**Full Dependency Chain Analysis:**
```graphql
query {
  node(name: "eligibility_rule") {
    name
    
    # Direct dependencies
    dependencies {
      name
      kind
    }
    
    # All transitive dependencies
    transitiveDependencies {
      name
      kind
      source
    }
    
    # What depends on this
    dependents {
      name
    }
  }
}
```

**Multi-Node Impact Analysis:**
```graphql
query {
  # Analyze impact of changing multiple nodes
  age: node(name: "age") {
    name
    transitiveDependents { name }
  }
  
  income: node(name: "income") {
    name
    transitiveDependents { name }
  }
  
  service_method: node(name: "service_method") {
    name
    transitiveDependents { name }
  }
}
```

**Legal Citation Tracking:**
```graphql
query {
  # Find all CPLR 308 references
  cplr308: nodesByAuthority(pattern: "308") {
    name
    authority
    kind
    filePath
    lineNumber
    
    # What depends on this legal rule
    transitiveDependents {
      name
      kind
    }
  }
}
```

**Complex Filtering and Aggregation:**
```graphql
query {
  # Get all derived variables with authority
  derivedWithAuthority: nodes(source: "derived") {
    name
    authority
    kind
    
    # Show their dependencies
    dependencies {
      name
      source
    }
  }
  
  stats: graphStats {
    nodeCount
    edgeCount
  }
}
```

#### Python Client Example
```python
import requests

query = """
query {
  nodesByAuthority(pattern: "CPLR") {
    name
    authority
  }
}
"""

response = requests.post(
    "http://localhost:8000/graphql",
    json={"query": query}
)

data = response.json()
for node in data["data"]["nodesByAuthority"]:
    print(f"{node['name']}: {node['authority']}")
```

## Advanced Features

### Decision Trees
Extract decision tree structures from conditional logic:

```python
from docassemble_dag.decision_trees import extract_decision_tree

tree = extract_decision_tree(graph, root_node_name="ask_eligibility")
tree_dict = tree.to_dict()
```

### Reconsider Directive Tracking
Track `reconsider:` directives that break static assumptions:

```python
from docassemble_dag.reconsider import extract_reconsider_directives, check_reconsider_boundaries

directives = extract_reconsider_directives(yaml_dict)
warnings = check_reconsider_boundaries(graph, directives)
```

### Conditional Logic Detection
Extract dependencies from `show if:`, `enable if:`, etc.:

```python
from docassemble_dag.conditional import extract_conditionals_from_item

conditionals = extract_conditionals_from_item(item, node_name="ask_question")
for cond in conditionals:
    print(f"{cond.directive}: {cond.condition}")
    print(f"  Dependencies: {cond.dependencies}")
```

## Examples

See the [`examples/`](examples/) directory for sample interviews:

- **`ny_cplr_sample.yaml`**: Legaltech example with CPLR citations
- **`example_interview.yaml`**: Basic dependency patterns

See [`EXAMPLES.md`](EXAMPLES.md) for detailed Python API examples and [`examples/LEGALTECH_GUIDE.md`](examples/LEGALTECH_GUIDE.md) for legaltech use cases.

## Legaltech Use Cases

### 1. Compliance Verification
Ensure all procedural requirements are properly defined and connected:

```bash
# Run full validation suite
python -m docassemble_dag interview.yaml --validate --fail-on-error
```

**Detects:**
- Missing dependencies (incomplete logic chains)
- Orphaned nodes (unused variables/questions)
- Undefined references (typos, missing definitions)
- Circular dependencies (infinite loops)

**Example Output:**
```
Validation Results:
  Total: 3
  Errors: 1
  Warnings: 2

Violations:
  ✗ [no_undefined_references] Implicit reference to undefined variable 'opposing_party' in 'motion_requirements'
      Node: motion_requirements
      File: interview.yaml:45
  ⚠ [no_orphans] Orphan node 'unused_var' has no dependencies or dependents
      Node: unused_var
      File: interview.yaml:78
```

### 2. Impact Analysis
When legal rules change, quickly identify all affected downstream logic:

```python
from docassemble_dag import parse_multiple_files, find_nodes_by_authority

# Parse your interview
files = find_yaml_files(Path("interviews/"))
graph = parse_multiple_files(files)

# Find all nodes citing CPLR 308 (service rules)
cplr_308_nodes = find_nodes_by_authority(graph, "CPLR 308")

# Analyze impact of changes
for node in cplr_308_nodes:
    affected = graph.get_transitive_dependents(node.name)
    print(f"\n📋 Changing {node.name} ({node.authority})")
    print(f"   Affects {len(affected)} downstream nodes:")
    for dep in sorted(affected):
        dep_node = graph.nodes[dep]
        print(f"   - {dep} ({dep_node.kind.value})")
```

**Example Output:**
```
📋 Changing service_method (CPLR 308)
   Affects 5 downstream nodes:
   - service_complete (variable)
   - motion_filed_on_time (variable)
   - ask_proof_of_service (question)
   - opposing_party_served (variable)
   - motion_requirements_rule (rule)
```

### 3. Statute Citation Tracking
Track which legal authorities apply to which parts of your interview:

```bash
# Find all nodes referencing CPLR 308
python -m docassemble_dag interviews/ --find-authority "CPLR 308"
```

**Example Output:**
```
Found 4 node(s) with authority matching 'CPLR 308':
  - ask_service_method (question): CPLR 308
    File: interviews/motion_practice.yaml:47
  - service_complete (variable): CPLR 308
    File: interviews/motion_practice.yaml:17
  - ask_proof_of_service (question): CPLR 308
    File: interviews/motion_practice.yaml:63
  - service_validity_rule (rule): CPLR 308
    File: interviews/motion_practice.yaml:80
```

**Programmatic Access:**
```python
# Generate citation report
from collections import defaultdict

authority_map = defaultdict(list)
for node in graph.nodes.values():
    if node.authority:
        # Handle multiple citations (e.g., "CPLR 2211, 308")
        citations = [c.strip() for c in node.authority.split(',')]
        for citation in citations:
            authority_map[citation].append(node)

# Print citation summary
for citation, nodes in sorted(authority_map.items()):
    print(f"\n{citation}: {len(nodes)} references")
    for node in nodes:
        print(f"  - {node.name} ({node.kind.value})")
```

### 4. Template Validation
Prevent production errors by validating all template variables are defined:

```bash
# Validate all templates in templates/ directory
python -m docassemble_dag interview.yaml \
  --validate-templates templates/*.docx templates/*.pdf \
  --fail-on-error
```

**Example Output:**
```
Template Validation Results:

✓ VALID: templates/motion_letter.docx
✗ INVALID: templates/notice.docx
  Undefined variables: opposing_counsel_name, case_number
  Undefined objects: court
✓ VALID: templates/proof_of_service.pdf
```

**Common Issues Caught:**
- Typos in template variable names
- Variables removed from interview but still in templates
- Object attributes referencing undefined objects
- Nested attributes (`{client.name.first}`) with missing parent objects

### 5. Change Management
Track and analyze changes between interview versions:

```bash
# Compare current version with baseline
python -m docassemble_dag interview_v2.yaml \
  --compare-baseline=interview_v1.json \
  -o changes.json
```

**Example Output:**
```
Graph Comparison Results:
  Added nodes: 3
  Removed nodes: 1
  Changed nodes: 2
  Added edges: 5
  Removed edges: 2
  Authority changes: 1
  Affected nodes: 8
```

**Detailed Analysis:**
```python
from docassemble_dag.comparison import compare_graphs

diff = compare_graphs(baseline_graph, current_graph)

# Review authority changes
for change in diff.authority_changes:
    print(f"Authority updated: {change['node']}")
    print(f"  Old: {change['old_authority']}")
    print(f"  New: {change['new_authority']}")

# Impact analysis
print(f"\n{len(diff.affected_nodes)} nodes affected by changes:")
for node_name in sorted(diff.affected_nodes):
    print(f"  - {node_name}")
```

### 6. Compliance Reporting
Generate audit-ready reports with complete statute citations:

```python
from docassemble_dag.compliance import generate_compliance_report

# Generate HTML report
report = generate_compliance_report(
    graph,
    interview_name="Summary Judgment Motion Practice",
    baseline_graph=old_graph,  # Optional: include change analysis
    output_path=Path("compliance_reports/motion_practice.html")
)

# Access data programmatically
print(f"Total statute citations: {len(report.authority_mapping)}")
print(f"Missing authority: {len(report.missing_authorities)} nodes")

# Generate summary for stakeholders
for statute, nodes in report.authority_mapping.items():
    print(f"\n{statute}:")
    print(f"  Referenced in {len(nodes)} locations")
    for node_name in nodes:
        node = graph.nodes[node_name]
        print(f"  - {node_name} at line {node.line_number}")
```

**Report Includes:**
- Complete statute citation mapping
- Nodes lacking authority (compliance gaps)
- Change summary vs. baseline
- File locations and line numbers
- Visual HTML output for stakeholders

### 7. Multi-Repository Workflows
Track dependencies across multiple Docassemble packages:

```python
from docassemble_dag import DocassembleParser

# Parse modules directive
parser = DocassembleParser(yaml_text)
modules = parser.get_modules()

print("External dependencies:")
for module in modules:
    print(f"  - {module}")
```

**Example:**
```
External dependencies:
  - docassemble.income
  - docassemble.base.legal
  - docassemble.AssemblyLine
```

### 8. CI/CD Integration
Automate validation in your deployment pipeline:

**GitHub Actions Workflow:**
```yaml
name: Validate Interview

on: [push, pull_request]

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.9'
      - run: pip install -e .
      - name: Validate interview
        run: |
          python -m docassemble_dag interviews/main.yaml \
            --validate \
            --fail-on-error \
            --recursive
      - name: Validate templates
        run: |
          python -m docassemble_dag interviews/main.yaml \
            --validate-templates templates/*.docx \
            --fail-on-error
```

### 9. Documentation Generation
Auto-generate dependency documentation:

```python
# Generate multiple formats for documentation
import subprocess

# Interactive HTML for stakeholders
subprocess.run([
    "python", "-m", "docassemble_dag",
    "interview.yaml",
    "--format", "html",
    "-o", "docs/dependencies.html"
])

# GraphML for technical documentation (import to yEd)
subprocess.run([
    "python", "-m", "docassemble_dag",
    "interview.yaml",
    "--format", "graphml",
    "-o", "docs/dependencies.graphml"
])

# DOT for PDF generation
subprocess.run([
    "python", "-m", "docassemble_dag",
    "interview.yaml",
    "--format", "dot",
    "-o", "docs/dependencies.dot"
])
subprocess.run(["dot", "-Tpdf", "docs/dependencies.dot", "-o", "docs/dependencies.pdf"])
```

### 10. Training & Onboarding
Use dependency graphs to train new developers:

```python
# Generate simplified graph for training
from docassemble_dag import DependencyGraph

# Extract only high-level rules and questions
training_nodes = {
    name: node for name, node in graph.nodes.items()
    if node.kind in (NodeKind.QUESTION, NodeKind.RULE)
}
training_edges = [
    edge for edge in graph.edges
    if edge.from_node in training_nodes and edge.to_node in training_nodes
]

training_graph = DependencyGraph(training_nodes, training_edges)
training_graph.to_html(Path("training/simplified_flow.html"), title="Interview Flow (Simplified)")
```

### 11. Legal Rule Versioning
Track when legal rules change over time:

```python
# Version tracking workflow
from datetime import datetime
from docassemble_dag.persistence import GraphStorage

storage = GraphStorage("postgresql://user:pass@localhost/legal_graphs")

# Save new version
graph_id = storage.save_graph(
    graph,
    name="motion_practice",
    version=f"v{datetime.now().strftime('%Y.%m.%d')}",
    metadata={
        "author": "Jane Doe",
        "description": "Updated for CPLR amendment effective Jan 2026",
        "statute_changes": ["CPLR 308(2)", "CPLR 3212(a)"]
    }
)

# Compare with previous version
previous_versions = [
    g for g in storage.list_graphs()
    if g['name'] == 'motion_practice'
]
previous_versions.sort(key=lambda x: x['created_at'], reverse=True)

if len(previous_versions) > 1:
    old_graph = storage.load_graph(previous_versions[1]['id'])
    diff = compare_graphs(old_graph, graph)
    
    print(f"Changes in {previous_versions[0]['version']}:")
    print(f"  Authority changes: {len(diff.authority_changes)}")
    for change in diff.authority_changes:
        print(f"    - {change['node']}: {change['old_authority']} → {change['new_authority']}")
```

### 12. Quality Assurance
Automated QA checks before production deployment:

```python
from docassemble_dag import GraphValidator

def qa_check(graph, interview_name):
    """Run comprehensive QA checks."""
    validator = GraphValidator(graph)
    violations = validator.validate_all()
    
    # Check for critical issues
    summary = validator.get_summary()
    
    print(f"\n{'='*60}")
    print(f"QA Report: {interview_name}")
    print(f"{'='*60}")
    
    # Critical errors block deployment
    if summary['errors'] > 0:
        print(f"\n❌ DEPLOYMENT BLOCKED: {summary['errors']} critical errors")
        for v in violations:
            if v.severity.value == 'error':
                print(f"   - {v.message}")
        return False
    
    # Warnings require review
    if summary['warnings'] > 0:
        print(f"\n⚠️  REVIEW REQUIRED: {summary['warnings']} warnings")
        for v in violations:
            if v.severity.value == 'warning':
                print(f"   - {v.message}")
    
    # Check coverage
    nodes_with_authority = sum(1 for n in graph.nodes.values() if n.authority)
    coverage = (nodes_with_authority / len(graph.nodes)) * 100
    print(f"\n📊 Authority Citation Coverage: {coverage:.1f}%")
    
    if coverage < 80:
        print("   ⚠️  Warning: Low citation coverage")
    
    print(f"\n✅ QA Passed - Ready for deployment")
    return True

# Run QA
passed = qa_check(graph, "Motion Practice Interview")
if not passed:
    exit(1)
```

## Documentation

- **[README.md](README.md)**: This file
- **[EXAMPLES.md](EXAMPLES.md)**: Python API examples and workflows
- **[GRAPHQL_API.md](GRAPHQL_API.md)**: GraphQL API guide
- **[POSTGRESQL_SUPPORT.md](POSTGRESQL_SUPPORT.md)**: PostgreSQL setup and usage
- **[examples/LEGALTECH_GUIDE.md](examples/LEGALTECH_GUIDE.md)**: Legaltech use cases
- **[examples/README.md](examples/README.md)**: Example files documentation

## Development

### Setup
```bash
# Install with dev dependencies
pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install

# Run tests
pytest

# Run tests with coverage
pytest --cov=docassemble_dag --cov-report=html
```

### Testing
```bash
# Run all tests
make test

# Run with coverage
make test-cov

# Lint and type check
make lint
make type-check

# Format code
make format

# Run all checks
make check-all
```

### CI/CD
GitHub Actions workflows in `.github/workflows/`:
- **ci.yml**: Tests across Python 3.7-3.11
- **validate-interview.yml**: Validates Docassemble interviews

## Limitations

- **Static analysis only**: Does not execute interviews
- **AST parsing limitations**: May not detect all implicit dependencies in complex Python code
- **Reconsider directive**: Not fully modeled (warnings only)
- **Dynamic variable names**: Only static references detected

See [README.md](README.md#limitations) for detailed limitations.

## Roadmap

See [`ROADMAP.md`](ROADMAP.md) for planned features and enhancements.

## License

Licensed under the Apache License, Version 2.0. See [LICENSE](LICENSE) for details.

---

**Built with ❤️ for the legaltech community**
