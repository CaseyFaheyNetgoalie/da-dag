# Legaltech Use Case: New York CPLR Analysis

This guide demonstrates how `docassemble-dag` can be used for legal document automation workflows, specifically for analyzing dependency graphs in Docassemble interviews that implement legal procedures.

## Overview

The New York CPLR (Civil Practice Law and Rules) sample demonstrates how legal rules, statutes, and procedural requirements create explicit dependency relationships that can be analyzed, validated, and visualized.

## Sample Analysis

### Graph Statistics

- **19 nodes**: Variables, questions, and rules
- **17 edges**: Dependencies (4 explicit, 13 implicit)
- **9 nodes with CPLR citations**: Authority metadata tracked throughout

### CPLR Citations Tracked

| Node | CPLR Citation |
|------|---------------|
| `ask_court_jurisdiction` | CPLR 501 |
| `ask_service_method` | CPLR 308 |
| `ask_proof_of_service` | CPLR 308 |
| `filing_deadline` | CPLR 2211 |
| `service_complete` | CPLR 308 |
| `motion_filed_on_time` | CPLR 2211, 308 |
| `motion_requirements_rule` | CPLR 2211, 308, 3212 |
| `deadline_calculation_rule` | CPLR 3212 |
| `service_validity_rule` | CPLR 308 |

## Key Legal Dependencies

### 1. Motion Filing Requirements

```
court_jurisdiction → filing_deadline → motion_filed_on_time → motion_requirements_rule
motion_type → filing_deadline → motion_filed_on_time → motion_requirements_rule
```

**Legal Insight**: Filing deadlines depend on both jurisdiction and motion type, creating a multi-factor dependency that must be satisfied for a valid motion.

### 2. Service Requirements

```
service_method → service_complete → motion_filed_on_time → motion_requirements_rule
service_method → service_complete → ask_proof_of_service → motion_requirements_rule
```

**Legal Insight**: Service method determines validity, which cascades through multiple procedural requirements.

### 3. Complete Motion Requirements

The `motion_requirements_rule` depends on:
- `motion_filed_on_time` (which depends on deadline and service)
- `proof_of_service_filed` (which depends on service completion)
- `opposing_party_served` (which depends on service completion and date)

**Legal Insight**: Multiple independent requirements must all be satisfied, creating a complex dependency graph.

## Use Cases for Legal Professionals

### 1. Compliance Verification

```bash
# Check if all required procedural steps are defined
python -m docassemble_dag examples/ny_cplr_sample.yaml --validate
```

This identifies:
- Missing dependencies
- Orphaned nodes (unused code)
- Undefined references
- Circular dependencies

### 2. Impact Analysis

When a CPLR rule changes, you can quickly see what depends on it:

```python
from docassemble_dag import DocassembleParser, DependencyGraph

# Load the interview
parser = DocassembleParser(yaml_text, file_path="interview.yaml")
nodes = parser.extract_nodes()
edges = parser.extract_edges(nodes)
graph = DependencyGraph(nodes, edges)

# Find everything that depends on CPLR 308 (service rules)
service_nodes = [n for n in nodes.values() if n.authority and "308" in n.authority]
for node in service_nodes:
    dependents = graph.get_transitive_dependents(node.name)
    print(f"If {node.name} changes, affects: {dependents}")
```

### 3. Statute Citation Tracking

Track which CPLR sections apply to which parts of your interview:

```python
# Find all nodes citing a specific CPLR section
cplr_308_nodes = [n for n in nodes.values() if n.authority and "308" in n.authority]
for node in cplr_308_nodes:
    print(f"{node.name}: {node.authority} (line {node.line_number})")
```

### 4. Visualization for Documentation

Generate visual graphs for legal documentation:

```bash
# Create GraphML for legal documentation
python -m docassemble_dag examples/ny_cplr_sample.yaml --format graphml -o cplr_flow.graphml

# Create DOT for presentations
python -m docassemble_dag examples/ny_cplr_sample.yaml --format dot -o cplr_flow.dot
```

## Governance and Audit

The provenance tracking enables:

- **Audit Trails**: See exactly where each legal requirement is defined (file, line number)
- **Authority Verification**: Ensure all legal rules cite appropriate CPLR sections
- **Change Impact**: Understand downstream effects of modifying legal rules
- **Compliance Reporting**: Generate reports showing which statutes apply to which procedures

## Example Workflow

1. **Extract DAG**: Analyze your Docassemble interview
2. **Validate**: Check for missing dependencies or policy violations
3. **Query**: Find all nodes affected by a specific CPLR section
4. **Visualize**: Generate graphs for documentation or presentations
5. **Track Changes**: Use provenance metadata to audit modifications

## Integration with Legal Workflows

This tool can be integrated into:

- **CI/CD Pipelines**: Validate legal interviews before deployment
- **Documentation Generation**: Auto-generate dependency documentation
- **Compliance Tools**: Verify statute citations are complete
- **Training Materials**: Visualize legal procedure flows

## Notes

- This is a simplified example for demonstration
- Real legal interviews would be more complex
- Always have qualified legal professionals review legal automation
- CPLR citations are examples; verify actual requirements with legal counsel
