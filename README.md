# Docassemble DAG

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Python](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)

Static analyzer for extracting explicit dependency graphs from [Docassemble](https://docassemble.org/) YAML interview files.

## Table of Contents

- [Overview](#overview)
- [What is Docassemble?](#what-is-docassemble)
  - [How Docassemble Dependencies Work](#how-docassemble-dependencies-work)
  - [Explicit Dependencies](#explicit-dependencies)
  - [Implicit Dependencies](#implicit-dependencies)
  - [Docassemble Constructs](#docassemble-constructs)
  - [What This Tool Does](#what-this-tool-does)
- [Quick Start](#quick-start)
- [Installation](#installation)
- [Usage](#usage)
  - [Command Line](#command-line)
  - [Python Library](#python-library)
- [Output Format](#output-format)
- [Examples](#examples)
- [Limitations](#limitations)
- [Development](#development)
- [GUAC-Inspired Features](#guac-inspired-features)
- [Architecture](#architecture)
- [License](#license)

## Overview

[Docassemble](https://docassemble.org/) resolves questions, variables, and rules using an implicit dependency graph (DAG). This tool statically analyzes Docassemble interview files and outputs the dependency graph explicitly, enabling:

- **Explainability**: Understand what depends on what
- **Impact analysis**: See downstream effects of changes
- **Governance**: Track provenance and authority of rules
- **Validation**: Detect cycles, missing dependencies, and policy violations
- **Visualization**: Export to GraphViz (DOT) and GraphML formats

Inspired by [GUAC](https://github.com/guacsec/guac) (Graph for Understanding Artifact Composition) and provenance-rich data graphs.

## What is Docassemble?

[Docassemble](https://docassemble.org/) is a free, open-source expert system for guided interviews and document assembly. It's widely used in legaltech, healthcare, and government services to create interactive forms that gather information and generate documents based on user responses.

Docassemble interviews are defined in YAML files that contain:
- **Questions**: Interactive prompts for users
- **Variables**: Data fields and computed values
- **Rules**: Logic that determines what to ask and when

These elements form an implicit dependency graph—this tool makes that graph explicit and analyzable.

### How Docassemble Dependencies Work

Docassemble uses **lazy evaluation**: variables are computed only when needed, based on their dependencies. Understanding these dependencies is crucial for:

- **Question Ordering**: Docassemble automatically determines which questions to ask based on dependencies
- **Variable Resolution**: Computed variables are evaluated only after their dependencies are satisfied
- **Interview Flow**: The dependency graph determines the logical flow of your interview

#### Explicit Dependencies

These are **declared explicitly** in the YAML:

- **`depends on:`** - Question or variable depends on another variable being defined first
  ```yaml
  questions:
    - name: ask_consent
      question: "Do you consent?"
      depends on: is_adult  # Explicit: ask_consent depends on is_adult
  ```

- **`required:`** - Question requires another variable to be true/defined
  ```yaml
  questions:
    - name: ask_income
      question: "What is your income?"
      required: is_adult  # Explicit: ask_income requires is_adult
  ```

- **`mandatory:`** - Variable must be defined before proceeding (similar to `required`)

#### Implicit Dependencies

These are **inferred from code and templates**:

- **`code:` blocks** - Python code that references variables
  ```yaml
  variables:
    - name: is_adult
      code: |
        return age >= 18  # Implicit: is_adult depends on age
  ```

- **Object attributes** - `person.name`, `address.street` create dependencies on the object
  ```yaml
  variables:
    - name: person
    - name: full_name
      expression: person.name  # Implicit: full_name depends on person
  ```

- **`expression:`** - Python expressions referencing other variables
  ```yaml
  variables:
    - name: eligible_for_aid
      expression: income < 30000 and is_adult  # Implicit: depends on income, is_adult
  ```

- **Template references** - `$variable` or `${variable}` in templates
  ```yaml
  questions:
    - name: confirm_info
      question: |
        Your age is ${age} and income is ${income}.
        # Implicit: confirm_info depends on age, income
  ```

- **`choices:`** - Dynamic choice lists that may reference variables
  ```yaml
  questions:
    - name: ask_category
      choices: ${category_list}  # Implicit: depends on category_list
  ```

#### Docassemble Constructs

- **Variables (`variables:` / `fields:`)** - Data storage and computed values
  - **User Input**: Variables that users provide answers for
  - **Derived**: Variables computed from expressions or code blocks

- **Questions (`questions:`)** - Interactive prompts shown to users
  - May depend on variables being defined first
  - May set values for variables

- **Rules (`rules:`)** - Conditional logic and computations
  - Often contain expressions that reference multiple variables
  - Create complex dependency chains

#### What This Tool Does

This tool extracts both **explicit** and **implicit** dependencies from your Docassemble YAML files, creating an explicit dependency graph you can:

- **Analyze**: Understand the complete dependency structure
- **Validate**: Detect cycles, missing dependencies, and logical errors
- **Visualize**: See the flow and relationships between variables, questions, and rules
- **Document**: Generate dependency documentation automatically

## Quick Start

```bash
# Install
pip install -e .

# Analyze a sample interview
python -m docassemble_dag examples/ny_cplr_sample.yaml

# Validate for issues
python -m docassemble_dag examples/ny_cplr_sample.yaml --validate

# Export as GraphML for visualization
python -m docassemble_dag examples/ny_cplr_sample.yaml --format graphml -o graph.graphml
```

## Installation

```bash
# Basic installation (SQLite support included)
pip install -e .

# With PostgreSQL support (optional)
pip install -e ".[postgresql]"
# or
pip install psycopg2-binary
```

**Database Support:**
- **SQLite** (default) - No additional dependencies needed
- **PostgreSQL** (optional) - Install `psycopg2-binary` for PostgreSQL support

See [`POSTGRESQL_SUPPORT.md`](POSTGRESQL_SUPPORT.md) for detailed PostgreSQL setup instructions.

## Examples

See the [`examples/`](examples/) directory for sample interviews and detailed guides:

- **New York CPLR Sample** (`examples/ny_cplr_sample.yaml`) - Legaltech use case demonstrating:
  - Statute citations (CPLR 2211, 308, 3212, etc.)
  - Legal rule dependencies
  - Procedural requirement tracking
  - Authority metadata throughout the dependency graph

```bash
# Analyze the CPLR sample
python -m docassemble_dag examples/ny_cplr_sample.yaml --validate

# See all CPLR citations
python -m docassemble_dag examples/ny_cplr_sample.yaml | python -m json.tool | grep -A 2 '"authority"'
```

For more examples and use cases, see:
- [`EXAMPLES.md`](EXAMPLES.md) - Python API examples and workflows
- [`examples/README.md`](examples/README.md) - Example file documentation
- [`examples/LEGALTECH_GUIDE.md`](examples/LEGALTECH_GUIDE.md) - Legaltech use case guide

## Usage

### Command Line

#### Basic Usage

```bash
# Extract DAG to stdout (JSON format)
python -m docassemble_dag interview.yaml

# Save to file
python -m docassemble_dag interview.yaml -o output.json

# Compact JSON output (no pretty printing)
python -m docassemble_dag interview.yaml --no-pretty
```

#### Validation and Checks

```bash
# Check for cycles (exit with error if cycles found)
python -m docassemble_dag interview.yaml --check-cycles

# Run all policy validation checks
python -m docassemble_dag interview.yaml --validate

# Run specific policies and fail on errors
python -m docassemble_dag interview.yaml --validate --policies no_cycles no_undefined_references --fail-on-error
```

#### Export Formats

```bash
# Export as DOT format for GraphViz visualization
python -m docassemble_dag interview.yaml --format dot -o graph.dot

# Export as GraphML (standard XML format for graph tools)
python -m docassemble_dag interview.yaml --format graphml -o graph.graphml

# Export as interactive HTML viewer (v0.4+)
python -m docassemble_dag interview.yaml --format html -o graph.html
# Opens in browser with interactive D3.js visualization
```

#### Graph Comparison & Change Tracking (v0.4+)

```bash
# Compare two versions of an interview to see what changed
python -m docassemble_dag interview.yaml --compare-baseline=old_graph.json -o diff.json

# Shows: added/removed nodes, changed nodes, authority updates, affected downstream nodes
```

#### Template Validation (v0.4+)

```bash
# Validate template files against interview graph
python -m docassemble_dag interview.yaml --validate-templates letter.docx contract.pdf template.mako

# Checks that all variables in templates are defined in the interview
# Prevents production errors from undefined template variables
```

#### Batch Processing & Multi-File Support

```bash
# Analyze entire directory (recursively)
python -m docassemble_dag interviews/ -o combined_graph.json

# Analyze directory (non-recursive)
python -m docassemble_dag interviews/ --no-recursive

# Parse include: directives (multi-file interviews)
python -m docassemble_dag main.yaml --include-files

# Find all nodes with specific authority (statute citations)
python -m docassemble_dag interviews/ --find-authority "CPLR 308"
```

#### Complete CLI Options

| Option | Description |
|--------|-------------|
| `input` | Path to Docassemble YAML interview file **or directory** (required) |
| `-o, --output OUTPUT` | Path to output file (default: stdout) |
| `--check-cycles` | Check for cycles and exit with error code if found |
| `--validate` | Run policy validation checks on the graph |
| `--policies POLICIES` | Specific policies to check (default: all). Options: `no_cycles`, `no_orphans`, `no_missing_dependencies`, `all_nodes_used`, `no_undefined_references` |
| `--fail-on-error` | Exit with error code if validation finds any errors |
| `--format {json,dot,graphml,html}` | Output format: `json` (default), `dot` (GraphViz), `graphml` (GraphML XML), or `html` (interactive viewer) |
| `--compare-baseline BASELINE` | Compare current graph with baseline JSON file (v0.4+) |
| `--validate-templates FILES` | Validate template files (DOCX, PDF, Mako) against interview (v0.4+) |
| `--pretty` | Pretty-print JSON output (default: True) |
| `--no-pretty` | Output compact JSON (disable pretty printing) |
| `--find-authority PATTERN` | Find all nodes with authority matching pattern (case-insensitive) |
| `--recursive` | When input is directory, search recursively (default: True) |
| `--no-recursive` | When input is directory, only search top-level |
| `--include-files` | Parse `include:` directives and analyze included files |
| `-h, --help` | Show help message and exit |

See `python -m docassemble_dag --help` for the latest options.

### Python Library

```python
from docassemble_dag import DocassembleParser, DependencyGraph
from docassemble_dag.types import NodeKind

# Parse interview file
with open('interview.yaml') as f:
    yaml_text = f.read()

parser = DocassembleParser(yaml_text, file_path="interview.yaml")
nodes = parser.extract_nodes()
edges = parser.extract_edges(nodes)
graph = DependencyGraph(nodes, edges)

# Get JSON representation
dag_json = graph.to_json_struct()

# GUAC-inspired query methods
roots = graph.find_roots()  # Entry points (no dependencies)
orphans = graph.find_orphans()  # Isolated nodes
variables = graph.find_nodes_by_kind(NodeKind.VARIABLE)
all_deps = graph.get_transitive_dependencies("node_name")  # All dependencies
all_dependents = graph.get_transitive_dependents("node_name")  # All dependents
path = graph.find_path("from_node", "to_node")  # Dependency path

# Cycle detection
if graph.has_cycles():
    cycles = graph.find_cycles()
    print(f"Found {len(cycles)} cycles")

# Export to DOT format for visualization
dot_graph = graph.to_dot(title="My Interview DAG")

# Export to GraphML (standard XML format, compatible with many graph tools)
graphml_xml = graph.to_graphml(graph_id="my_interview")
```

#### Multi-File & Batch Processing

```python
from docassemble_dag import parse_multiple_files, find_nodes_by_authority, parse_with_includes
from pathlib import Path

# Batch process multiple files
files = list(Path("interviews/").glob("*.yaml"))
graph = parse_multiple_files(files)

# Parse with includes (multi-file interview)
graph, visited = parse_with_includes(Path("main.yaml"))
print(f"Parsed {len(visited)} files including includes")

# Find nodes by authority
cplr_308_nodes = find_nodes_by_authority(graph, "CPLR 308")
print(f"Found {len(cplr_308_nodes)} nodes citing CPLR 308")
```

For more examples, see [`EXAMPLES.md`](EXAMPLES.md) and the [`examples/`](examples/) directory.

## Output Format

The tool outputs JSON with the following structure:

```json
{
  "nodes": [
    {
      "name": "age",
      "kind": "variable",
      "source": "user_input",
      "authority": null,
      "file_path": "interview.yaml",
      "line_number": 5,
      "metadata": {}
    },
    {
      "name": "is_adult",
      "kind": "variable",
      "source": "derived",
      "authority": null,
      "file_path": "interview.yaml",
      "line_number": 12,
      "metadata": {}
    }
  ],
  "edges": [
    {
      "from": "age",
      "to": "is_adult",
      "type": "implicit",
      "file_path": "interview.yaml",
      "line_number": 12,
      "metadata": {}
    }
  ]
}
```

### Node Kinds

- `variable`: A field or computed variable
- `question`: A question block
- `rule`: A rule or computation
- `assembly_line`: Assembly Line variable (AL_ prefix) - Legal Elements Library convention

### Dependency Types

- **`explicit`**: Declared dependency using Docassemble keywords:
  - `depends on:` / `depends_on:`
  - `required:` / `requires:`
  - `mandatory:`
  
- **`implicit`**: Inferred from variable references in:
  - `code:` blocks (Python code)
  - `expression:` fields (Python expressions)
  - `template:` text (template strings with `${variable}` references)
  - `question:` text (question text with variable references)
  - `choices:` (dynamic choice lists)
  - `default:` values

The tool uses pattern matching to find variable names in these contexts. Since this is static analysis, it may occasionally match non-variable identifiers or miss dependencies in complex code.

### Node Metadata

- `source`: `"user_input"` or `"derived"`
- `authority`: Optional statute citation or rule reference
- `file_path`: Source file path (for provenance tracking)
- `line_number`: Line number in source file (approximate)
- `metadata`: Additional metadata dictionary

### Edge Metadata

- `file_path`: Source file path where dependency is defined
- `line_number`: Line number where dependency is expressed
- `metadata`: Additional metadata dictionary

## Production Use & Roadmap

This tool is an MVP designed for static analysis of individual Docassemble interviews. For production use in legaltech organizations (like [Lemma Legal](https://lemmalegal.com)), see:

- **[`PRODUCTION_ENHANCEMENTS.md`](PRODUCTION_ENHANCEMENTS.md)** - Comprehensive plan for production-ready features
- **[`LEMMA_LEGAL_INTEGRATION.md`](LEMMA_LEGAL_INTEGRATION.md)** - Specific integration opportunities with Lemma Legal workflows
- **[`TOBYFEY_REPOS_ANALYSIS.md`](TOBYFEY_REPOS_ANALYSIS.md)** - Analysis of real-world Docassemble repositories and patterns (e.g., Assembly Line, Legal Elements Library)

### Planned Production Features

**Priority 1 (Critical for Production)**:
- **Multi-file interview support** - Analyze interviews across multiple files (`include:`, modules)
- **CI/CD integration** - Pre-deployment validation in deployment pipelines (GitHub Actions, pre-commit hooks)
- **Batch analysis** - Analyze multiple interviews at once

**Priority 2 (High Value for Legal Compliance)**:
- **Change impact analysis** - Track statute citations and detect affected interviews
- **Authority queries** - `--find-authority "CPLR 308"` to find all affected nodes
- **Compliance reporting** - Generate reports mapping statutes to interviews

**Priority 3 (Enhanced User Experience)**:
- **HTML visualization** - Interactive viewers for non-technical stakeholders
- **Cross-interview analysis** - Identify reusable components across template libraries
- **Documentation generation** - Auto-generate dependency docs

### Current Version Suitability

**Suitable for**:
- ✅ Analyzing individual interview files
- ✅ Understanding dependency structures
- ✅ Validating interview logic (cycles, missing dependencies)
- ✅ Generating dependency documentation
- ✅ Statute citation tracking (basic)

**Now available in v0.2.0+**:
- ✅ Multi-file interviews with `include:` (`--include-files`)
- ✅ CI/CD pipeline integration (GitHub Actions template included)
- ✅ Batch processing directories (directory input support)
- ✅ Authority queries (`--find-authority "CPLR 308"`)
- ✅ Cross-interview analysis (batch processing merges graphs)

**Now available in v0.3+**:
- ✅ Assembly Line support (AL_ prefix recognition)
- ✅ Object attribute handling (person.name → person dependency)
- ✅ Modules directive parsing (cross-repository dependencies)

**Not yet available**:
- ❌ Graph comparison utilities (planned for v0.4)
- ❌ HTML interactive viewer (planned for v0.4)
- ❌ Change impact reports (planned for v0.4)
- ❌ Template variable validation (planned for v0.4)

### Contributing to Production Features

See [`PRODUCTION_ENHANCEMENTS.md`](PRODUCTION_ENHANCEMENTS.md) for detailed implementation plans. Priority features for organizations like Lemma Legal are clearly marked.

For a comprehensive roadmap of remaining features and code improvements, see [`ROADMAP.md`](ROADMAP.md).

## Limitations

This is an MVP focused on core functionality:

- **Static analysis only**: Does not execute or validate Docassemble interviews. The tool analyzes YAML structure, not runtime behavior.
- **Basic heuristics**: Implicit dependency detection uses simple pattern matching (regex) to find variable-like identifiers. This means:
  - May match non-variable identifiers (false positives)
  - May miss dependencies in complex Python code
  - Does not understand Python imports or function calls
- **Limited feature coverage**: Not all Docassemble features are fully supported:
  - ✅ Multi-file interviews (`include:` / `modules:`) - **Now supported** (v0.2+)
  - ✅ Assembly line variables (`AL_` prefix) - **Now supported** (v0.3+) - recognized as `assembly_line` node kind
  - ❌ `reconsider:` directives - dependencies may break but tool doesn't account for this
  - ❌ Object attributes (e.g., `person.name`) - treats as variable `person_name`
  - ❌ Dynamic variable names - only static variable references are detected
  - ❌ `show if:` / `enable if:` - not parsed as dependencies (could be added)
- **Approximation**: The dependency graph is an approximation. Docassemble's actual runtime dependency resolution may differ due to lazy evaluation, reconsider logic, and dynamic features not captured in static analysis.

### Known Limitations in Detail

1. **Implicit Dependency Detection**: Uses regex pattern `\b([a-zA-Z_][a-zA-Z0-9_]*)\b` which matches any identifier-looking string. This is intentionally broad but imprecise.

2. **Multi-file Support**: Currently analyzes one YAML file at a time. Docassemble interviews often span multiple files using `include:` or module imports.

3. **Python Code Analysis**: For `code:` blocks and complex expressions, the tool doesn't parse Python AST—it just looks for identifier patterns.

4. **Conditional Logic**: `show if:`, `enable if:`, and similar conditional features create implicit dependencies that aren't always detected.

5. **Reconsider Logic**: Docassemble's `reconsider:` can break dependencies by forcing re-evaluation, but this tool treats dependencies as static.

## Development

```bash
# Install in development mode
pip install -e ".[dev]"

# Run tests
pytest

# Run tests with coverage
pytest --cov=docassemble_dag --cov-report=html
```

See [`TEST_SUMMARY.md`](TEST_SUMMARY.md) for test coverage details.

## GUAC-Inspired Features

Inspired by [GUAC](https://github.com/guacsec/guac)'s graph query capabilities, the tool includes:

- **Graph Query API**: Find roots, orphans, paths, and transitive dependencies
- **Multiple Export Formats**: JSON, DOT (GraphViz), and GraphML (standard XML format)
- **Provenance Tracking**: File paths, line numbers, and authority metadata (similar to GUAC's artifact provenance)
- **Policy Validation**: Configurable policy rules to detect issues (cycles, orphans, missing dependencies, etc.)
- **Cycle Detection**: Identify circular dependencies
- **Enhanced Metadata**: Track where nodes and edges are defined in source files

## Architecture

The codebase is organized into framework-agnostic modules:

- **`types.py`**: Core data structures (`Node`, `Edge`, `NodeKind`, `DependencyType`, `PolicySeverity`, `PolicyViolation`)
- **`parser.py`**: YAML parsing and extraction logic (`DocassembleParser`)
- **`graph.py`**: DAG construction, validation, and query methods (`DependencyGraph`)
- **`validation.py`**: Policy validation rules (`GraphValidator`)
- **`cli.py`**: Command-line interface

Core graph logic is independent of I/O, making it easy to extend to other formats or use cases.

### Module Dependencies

```
cli.py → parser.py → types.py
      → graph.py → types.py
      → validation.py → graph.py → types.py
```

All modules depend on `types.py` for core data structures. The graph module is independent of parsing, enabling reuse with other input formats.

## License

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the LICENSE file for the full text.
