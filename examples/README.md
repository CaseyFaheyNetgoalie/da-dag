# Example Docassemble Interviews

This directory contains sample Docassemble YAML interview files demonstrating various use cases for the DAG extraction tool.

For more examples and Python API usage, see:
- [`../EXAMPLES.md`](../EXAMPLES.md) - Python API examples and workflows
- [`LEGALTECH_GUIDE.md`](LEGALTECH_GUIDE.md) - Detailed legaltech use case guide
- [`../README.md`](../README.md) - Main documentation

## New York CPLR Sample (`ny_cplr_sample.yaml`)

**File**: `ny_cplr_sample.yaml`

A legaltech example showing how dependency graphs work in legal document automation, specifically for New York Civil Practice Law and Rules (CPLR) motion practice.

### Features Demonstrated

- **Statute Citations**: Shows how authority metadata (CPLR citations) flows through the dependency graph
- **Legal Rules**: Demonstrates how legal rules depend on procedural requirements
- **Complex Dependencies**: Shows explicit and implicit dependencies between legal concepts
- **Provenance Tracking**: File paths and line numbers help trace where legal requirements are defined

### Key Dependencies

- Motion filing deadlines depend on court jurisdiction and motion type
- Service validity depends on service method
- Motion requirements depend on multiple procedural elements
- Questions have explicit dependencies (e.g., `required:`, `depends on:`)

### Usage

```bash
# Extract the dependency graph
python -m docassemble_dag examples/ny_cplr_sample.yaml

# Validate for policy violations
python -m docassemble_dag examples/ny_cplr_sample.yaml --validate

# Export as GraphML for visualization
python -m docassemble_dag examples/ny_cplr_sample.yaml --format graphml -o cplr_graph.graphml

# Find all nodes with CPLR authority
python3 << 'EOF'
from docassemble_dag import DocassembleParser, DependencyGraph

with open('examples/ny_cplr_sample.yaml') as f:
    yaml_text = f.read()

parser = DocassembleParser(yaml_text, file_path="examples/ny_cplr_sample.yaml")
nodes = parser.extract_nodes()
edges = parser.extract_edges(nodes)
graph = DependencyGraph(nodes, edges)

# Find all nodes with authority citations
nodes_with_authority = [n for n in nodes.values() if n.authority]
print("Nodes with CPLR citations:")
for node in nodes_with_authority:
    print(f"  {node.name}: {node.authority}")
EOF
```

### Legal Use Cases

This example demonstrates how the DAG tool can help with:

1. **Compliance Checking**: Verify that all required procedural steps are defined
2. **Impact Analysis**: Understand what changes if a CPLR rule is updated
3. **Documentation**: Track which statute citations apply to which variables
4. **Governance**: Ensure legal authority is properly attributed throughout the interview

### Related Documentation

- [`LEGALTECH_GUIDE.md`](LEGALTECH_GUIDE.md) - Comprehensive guide to legaltech use cases
- [`../EXAMPLES.md`](../EXAMPLES.md) - More Python API examples
- [`../README.md`](../README.md) - Main project documentation

### Note

This is a simplified example for demonstration purposes. Real legal interviews would be more complex and should be reviewed by qualified legal professionals.
