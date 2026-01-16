# Usage Examples

This document provides practical examples for using `docassemble-dag`. For sample interview files, see the [`examples/`](examples/) directory.

## Docassemble Dependency Patterns

Understanding how Docassemble features create dependencies helps you interpret the dependency graph:

### Assembly Line & Legal Elements Library

```yaml
# Assembly Line variables (AL_ prefix) are recognized as special node kind
variables:
  - name: AL_Document  # Recognized as NodeKind.ASSEMBLY_LINE
  - name: AL_User      # Recognized as NodeKind.ASSEMBLY_LINE
  - name: regular_var  # Recognized as NodeKind.VARIABLE
```

### Object Attributes (Legal Elements Library)

```yaml
variables:
  - name: person
  - name: address
  - name: full_name
    expression: person.name  # Creates dependency: person → full_name
  
  - name: contact_info
    expression: person.name + " " + address.street
    # Creates dependencies: person → contact_info, address → contact_info
```

### Cross-Repository Dependencies

```yaml
# Parse modules: directive to track external package dependencies
modules:
  - docassemble.income
  - docassemble.base.legal
  - docassemble.AssemblyLine

# Use parser.get_modules() to extract these
from docassemble_dag import DocassembleParser
parser = DocassembleParser(yaml_text)
modules = parser.get_modules()  # Returns: ['docassemble.income', ...]
```

### Explicit Dependencies

```yaml
variables:
  - name: age

questions:
  # Question depends explicitly on variable
  - name: ask_consent
    question: "Do you consent?"
    depends on: age  # Creates explicit edge: age -> ask_consent
  
  # Question requires variable to be true
  - name: ask_income
    question: "What is your income?"
    required: age >= 18  # Creates explicit edge (if age >= 18 resolved to a variable)
```

### Implicit Dependencies from Expressions

```yaml
variables:
  - name: age
  - name: income
  - name: is_adult
    expression: age >= 18  # Creates implicit: age -> is_adult
  
  - name: eligible_for_aid
    expression: income < 30000 and is_adult
    # Creates implicit: income -> eligible_for_aid, is_adult -> eligible_for_aid
```

### Implicit Dependencies from Code Blocks

```yaml
variables:
  - name: person
  - name: full_name
    code: |
      if person.first_name and person.last_name:
        return f"{person.first_name} {person.last_name}"
      return ""
    # Creates implicit: person -> full_name
    # Note: object attributes (person.first_name) may not be detected perfectly
```

### Template References

```yaml
questions:
  - name: confirm_info
    question: |
      Your name is ${full_name} and you are ${age} years old.
      # Creates implicit: full_name -> confirm_info, age -> confirm_info
```

## Basic Analysis

```bash
# Extract DAG to JSON
python -m docassemble_dag interview.yaml

# Save to file
python -m docassemble_dag interview.yaml -o dag.json

# Export as DOT for visualization
python -m docassemble_dag interview.yaml --format dot -o graph.dot
```

## Python API Examples

### Basic Graph Analysis

```python
from docassemble_dag import DocassembleParser, DependencyGraph
from docassemble_dag.types import NodeKind

# Parse interview
with open('interview.yaml') as f:
    yaml_text = f.read()

parser = DocassembleParser(yaml_text)
nodes = parser.extract_nodes()
edges = parser.extract_edges(nodes)
graph = DependencyGraph(nodes, edges)

# Check for cycles
if graph.has_cycles():
    print("Warning: Cycles detected!")
    for cycle in graph.find_cycles():
        print(f"  {' -> '.join(cycle)}")
```

### GUAC-Inspired Queries

```python
# Find entry points (root nodes)
roots = graph.find_roots()
print(f"Entry points: {roots}")

# Find isolated nodes (potential unused code)
orphans = graph.find_orphans()
print(f"Isolated nodes: {orphans}")

# Find all variables
variables = graph.find_nodes_by_kind(NodeKind.VARIABLE)
print(f"Variables: {variables}")

# Get all transitive dependencies
all_deps = graph.get_transitive_dependencies("eligible_for_aid")
print(f"All dependencies of 'eligible_for_aid': {all_deps}")

# Get all transitive dependents (impact analysis)
all_dependents = graph.get_transitive_dependents("age")
print(f"Everything that depends on 'age': {all_dependents}")

# Find dependency path between nodes
path = graph.find_path("age", "eligibility_rule")
if path:
    print(f"Path: {' -> '.join(path)}")
```

### Visualization

```python
# Generate DOT format for GraphViz
dot_graph = graph.to_dot(title="Interview DAG")

# Save to file
with open('graph.dot', 'w') as f:
    f.write(dot_graph)

# Then visualize with GraphViz:
# dot -Tpng graph.dot -o graph.png
# Or use online tools like https://dreampuf.github.io/GraphvizOnline/

# Export to GraphML (standard XML format)
graphml_xml = graph.to_graphml(graph_id="interview_dag")
with open('graph.graphml', 'w') as f:
    f.write(graphml_xml)

# GraphML can be imported into:
# - yEd Graph Editor (https://www.yworks.com/products/yed)
# - Gephi (https://gephi.org/)
# - Cytoscape (https://cytoscape.org/)
# - NetworkX (Python library)
# - Many other graph visualization tools
```

For a complete legaltech example with visualization, see [`examples/LEGALTECH_GUIDE.md`](examples/LEGALTECH_GUIDE.md).

### Impact Analysis

```python
# Find what would be affected if we change a variable
def analyze_impact(graph, node_name):
    """Analyze impact of changing a node."""
    dependents = graph.get_transitive_dependents(node_name)
    print(f"Changing '{node_name}' would affect {len(dependents)} nodes:")
    for dep in sorted(dependents):
        print(f"  - {dep}")
    
    # Show the dependency chain
    for dep in dependents:
        path = graph.find_path(node_name, dep)
        if path:
            print(f"    Path: {' -> '.join(path)}")

analyze_impact(graph, "age")
```

### Validation Checks

```python
# Check for common issues
def validate_graph(graph):
    """Run validation checks on the graph."""
    issues = []
    
    # Check for cycles
    if graph.has_cycles():
        issues.append("Cycles detected in dependency graph")
    
    # Check for orphans
    orphans = graph.find_orphans()
    if orphans:
        issues.append(f"Orphan nodes (unused?): {orphans}")
    
    # Check for nodes with no dependencies (entry points)
    roots = graph.find_roots()
    if len(roots) == 0:
        issues.append("No entry points found (all nodes have dependencies)")
    
    return issues

issues = validate_graph(graph)
if issues:
    print("Validation issues found:")
    for issue in issues:
        print(f"  - {issue}")
```

## Policy Validation

For more advanced validation using the built-in `GraphValidator`:

```python
from docassemble_dag import DependencyGraph, GraphValidator

# ... build graph ...

validator = GraphValidator(graph)
violations = validator.validate_all()  # Run all policies

# Or run specific policies
violations = validator.validate_all(["no_cycles", "no_orphans"])

# Check results
if validator.has_errors():
    print("Errors found!")
    validator.print_violations()

# Get summary
summary = validator.get_summary()
print(f"Errors: {summary['errors']}, Warnings: {summary['warnings']}")
```

See the [README](README.md#command-line) for CLI validation options.
