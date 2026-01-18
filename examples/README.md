# Docassemble Interview Examples

This directory contains example Docassemble YAML interview files demonstrating various use cases for the `docassemble-dag` tool, with a focus on legal aid and access to justice workflows.

## Table of Contents

- [Overview](#overview)
- [Examples](#examples)
  - [Housing Eviction Defense](#housing-eviction-defense)
  - [Gender-Affirming Name Change](#gender-affirming-name-change)
  - [Immigration Asylum Intake](#immigration-asylum-intake)
  - [New York CPLR Sample](#new-york-cplr-sample)
- [Running the Examples](#running-the-examples)
- [Analyzing Dependencies](#analyzing-dependencies)
- [Use Case Guides](#use-case-guides)
- [Contributing Examples](#contributing-examples)

## Overview

These examples demonstrate:
- **Real-world legal aid scenarios** (housing, immigration, name changes)
- **Complex dependency patterns** (explicit and implicit)
- **Multi-language support** (English, Spanish, Portuguese, Haitian Creole)
- **Multi-jurisdiction logic** (state-specific requirements)
- **Authority citations** (statutes, regulations, case law)
- **Income eligibility calculations**
- **Conditional logic** (`show if`, `enable if`, `depends on`)
- **Assembly Line integration**
- **Best practices** for legal document automation

All examples are inspired by actual legal aid work, particularly the important work done by organizations like [LemmaLegal](https://lemmalegal.com).

## Examples

### Housing Eviction Defense

**File**: [`housing_eviction.yaml`](housing_eviction.yaml)

**Use Case**: Automated intake for tenants facing eviction, based on work serving thousands of tenants in Ohio.

#### Features Demonstrated

- ✅ **Conditional Logic**: Questions appear based on prior answers (`show if`, `enable if`)
- ✅ **Authority Citations**: Ohio Revised Code § 1923.04, § 5321.17, etc.
- ✅ **Complex Calculations**: Notice period validation, income eligibility
- ✅ **Valid Defense Detection**: Automatically identifies potential defenses
- ✅ **Personalized Recommendations**: File answer, seek rental assistance, or negotiate
- ✅ **Deadline Warnings**: 7-day response deadline calculations
- ✅ **Help Text**: Plain language explanations throughout

#### Dependency Graph Highlights

```
eviction_type → ask_rent_amount (show if)
has_written_notice → ask_notice_details (show if)
notice_date + filing_date → notice_period_valid
income_monthly + area_median_income → tenant_income_eligible
notice_period_valid + has_repair_requests + rent_payment_proof + landlord_retaliation → has_valid_defense
has_valid_defense + tenant_income_eligible + rent_owed → recommended_action
```

#### Key Nodes

- **19 nodes total**: 13 variables, 6 questions
- **17 dependencies**: 4 explicit, 13 implicit
- **3 rules** with authority citations
- **Authority citations**: 9 nodes cite Ohio statutes

#### Running This Example

```bash
# Analyze the dependency graph
python -m docassemble_dag examples/housing_eviction.yaml

# Validate for issues
python -m docassemble_dag examples/housing_eviction.yaml --validate

# Generate interactive HTML visualization
python -m docassemble_dag examples/housing_eviction.yaml --format html -o housing_graph.html

# Find all nodes with Ohio statute citations
python -m docassemble_dag examples/housing_eviction.yaml --find-authority "Ohio Rev. Code"
```

#### Legaltech Lessons

- **Income eligibility gates access** to legal aid services
- **Valid defenses** determine strategy (file answer vs. negotiate)
- **Deadline calculations** are critical for procedural compliance
- **Plain language help** reduces barriers for self-represented litigants

---

### Gender-Affirming Name Change

**File**: [`name_change_gender_affirming.yaml`](name_change_gender_affirming.yaml)

**Use Case**: Multi-jurisdiction name change petition generator supporting gender-affirming name changes across different states.

#### Features Demonstrated

- ✅ **Multi-Jurisdiction Logic**: Different requirements by state
- ✅ **Assembly Line Integration**: Uses `ALIndividual`, `ALCourt`, `ALDocumentBundle`
- ✅ **Fee Waiver Calculations**: Income-based eligibility by state
- ✅ **State-Specific Requirements**: Publication, background checks, hearings
- ✅ **Cost Estimation**: Total cost calculator (filing + publication + background check)
- ✅ **Timeline Projections**: State-specific processing time estimates
- ✅ **Document Checklist**: Required documents vary by jurisdiction

#### Dependency Graph Highlights

```
jurisdiction → requires_publication
jurisdiction → requires_background_check
jurisdiction → requires_hearing
jurisdiction + income_eligible_fee_waiver → AL_filing_fee
requires_publication + requires_background_check + AL_filing_fee → documents_needed
requires_publication + requires_background_check + AL_filing_fee → total_cost_estimate
```

#### Key Nodes

- **23 nodes total**: 15 variables, 6 questions, 2 rules
- **Multi-state support**: MA, OH, CA, NY, TX, FL
- **Variable costs**: $0 (with fee waiver) to $900+ (TX without waiver)
- **Timeline**: 4-12 weeks depending on jurisdiction

#### Running This Example

```bash
# Analyze dependencies
python -m docassemble_dag examples/name_change_gender_affirming.yaml

# Check for cycles
python -m docassemble_dag examples/name_change_gender_affirming.yaml --check-cycles

# Export to GraphML for visualization in yEd
python -m docassemble_dag examples/name_change_gender_affirming.yaml --format graphml -o name_change.graphml

# Compare two versions (if you modify it)
python -m docassemble_dag examples/name_change_gender_affirming.yaml \
  --compare-baseline=name_change_v1.json -o changes.json
```

#### Legaltech Lessons

- **Jurisdiction matters**: Requirements vary dramatically by state
- **Assembly Line patterns**: Standardized variables improve interoperability
- **Fee waivers expand access**: Many states offer waivers based on income
- **Transparency builds trust**: Show costs and timelines upfront

---

### Immigration Asylum Intake

**File**: [`immigration_asylum.yaml`](immigration_asylum.yaml)

**Use Case**: Multi-language asylum application intake supporting English, Spanish, Portuguese, and Haitian Creole.

#### Features Demonstrated

- ✅ **Multi-Language Support**: 4 languages with dynamic text translation
- ✅ **Deadline Calculations**: One-year filing deadline with day counter
- ✅ **Deadline Warnings**: Urgent alerts when approaching deadline
- ✅ **Persecution Basis Tracking**: 5 protected grounds (race, religion, nationality, political opinion, social group)
- ✅ **Work Permit Eligibility**: 150-day rule calculation
- ✅ **Interpreter Detection**: Automatic flag for non-English speakers
- ✅ **Authority Citations**: 8 USC § 1158, 8 CFR § 208.7
- ✅ **Accessible Language**: Plain language help text in all 4 languages

#### Dependency Graph Highlights

```
entry_date → days_since_entry
days_since_entry → application_deadline (if within 1 year)
days_since_entry → deadline_warning (if >335 days)
primary_language → needs_interpreter
application_filed + application_pending_days → eligible_for_work_permit
persecution_basis + persecution_narrative + fear_of_return → asylum_claim
```

#### Key Nodes

- **27 nodes total**: 18 variables, 7 questions, 2 rules
- **Languages**: English, Spanish, Portuguese, Haitian Creole
- **Critical deadline**: 365 days from entry to U.S.
- **Authority**: Immigration and Nationality Act (8 USC § 1158)

#### Running This Example

```bash
# Analyze multi-language dependencies
python -m docassemble_dag examples/immigration_asylum.yaml

# Validate the interview
python -m docassemble_dag examples/immigration_asylum.yaml --validate

# Generate DOT format for GraphViz
python -m docassemble_dag examples/immigration_asylum.yaml --format dot -o asylum.dot
dot -Tpng asylum.dot -o asylum_graph.png

# Start GraphQL server for interactive queries
python -m docassemble_dag examples/immigration_asylum.yaml --serve-graphql
# Visit http://localhost:8000/graphql
```

#### Legaltech Lessons

- **Language justice**: Multi-language support removes barriers
- **Deadline compliance**: Automated deadline calculation prevents missed filings
- **Progressive disclosure**: Start with language selection, then gather details
- **Cultural competence**: Respect for diverse communities through translation

---

### New York CPLR Sample

**File**: [`ny_cplr_sample.yaml`](ny_cplr_sample.yaml)

**Use Case**: Motion practice in New York courts demonstrating complex procedural dependencies.

#### Features Demonstrated

- ✅ **Procedural Dependencies**: Filing deadlines depend on motion type and jurisdiction
- ✅ **Service Requirements**: CPLR 308 service validation
- ✅ **Multi-Factor Logic**: Motion requirements depend on multiple independent factors
- ✅ **Statute Citations**: CPLR 501, 308, 2211, 3212
- ✅ **Conditional Requirements**: Different rules for different motion types
- ✅ **Provenance Tracking**: File paths and line numbers for all nodes

#### Key Nodes

- **19 nodes**: Variables, questions, and rules
- **17 edges**: 4 explicit, 13 implicit dependencies
- **9 authority citations**: Comprehensive CPLR coverage
- **Complex logic**: Multiple statutory requirements must all be satisfied

#### Running This Example

```bash
# Full analysis with validation
python -m docassemble_dag examples/ny_cplr_sample.yaml --validate

# Find all CPLR citations
python -m docassemble_dag examples/ny_cplr_sample.yaml --find-authority "CPLR"

# Generate compliance report
python examples/generate_compliance_report.py ny_cplr_sample.yaml
```

#### Legaltech Lessons

- **Procedural complexity**: Motion practice has many interrelated requirements
- **Citation tracking**: Track which statutes apply to which variables
- **Impact analysis**: See what changes if a CPLR section is amended

For more details, see [`LEGALTECH_GUIDE.md`](LEGALTECH_GUIDE.md).

---

## Running the Examples

### Prerequisites

```bash
# Install docassemble-dag
pip install -e .

# For visualization
pip install graphviz  # Optional

# For PostgreSQL support
pip install psycopg2-binary  # Optional
```

### Basic Analysis

```bash
# Analyze any example
python -m docassemble_dag examples/<filename>.yaml

# Save to JSON file
python -m docassemble_dag examples/<filename>.yaml -o output.json

# Pretty-print JSON (default)
python -m docassemble_dag examples/<filename>.yaml --pretty
```

### Validation

```bash
# Run all validation checks
python -m docassemble_dag examples/<filename>.yaml --validate

# Check for specific issues
python -m docassemble_dag examples/<filename>.yaml --check-cycles
python -m docassemble_dag examples/<filename>.yaml --validate --policies no_orphans

# Fail on errors (useful for CI/CD)
python -m docassemble_dag examples/<filename>.yaml --validate --fail-on-error
```

### Visualization

```bash
# Generate interactive HTML viewer
python -m docassemble_dag examples/<filename>.yaml --format html -o graph.html
# Open graph.html in browser

# Generate GraphViz DOT format
python -m docassemble_dag examples/<filename>.yaml --format dot -o graph.dot
dot -Tpng graph.dot -o graph.png  # Requires GraphViz installed

# Generate GraphML for yEd, Gephi, etc.
python -m docassemble_dag examples/<filename>.yaml --format graphml -o graph.graphml
```

### Advanced Analysis

```bash
# Find nodes by authority (statute citations)
python -m docassemble_dag examples/housing_eviction.yaml --find-authority "Ohio Rev. Code"

# Compare two versions
python -m docassemble_dag examples/housing_eviction_v2.yaml \
  --compare-baseline=housing_eviction_v1.json -o changes.json

# Start GraphQL server for interactive queries
python -m docassemble_dag examples/ny_cplr_sample.yaml --serve-graphql
# Visit http://localhost:8000/graphql for GraphiQL IDE
```

## Analyzing Dependencies

### Example: Housing Eviction Defense

```bash
# Extract the dependency graph
python -m docassemble_dag examples/housing_eviction.yaml -o housing.json

# Validate for issues
python -m docassemble_dag examples/housing_eviction.yaml --validate

# Find all Ohio statute citations
python -m docassemble_dag examples/housing_eviction.yaml --find-authority "Ohio Rev. Code"
```

**Expected Output:**
```
Found 9 node(s) with authority matching 'Ohio Rev. Code':
  - rent_owed (variable): Ohio Rev. Code § 5321.17
    File: examples/housing_eviction.yaml:42
  - notice_period_valid (variable): Ohio Rev. Code § 1923.04
    File: examples/housing_eviction.yaml:54
  - has_valid_defense (variable): Ohio Rev. Code § 5321.02, § 5321.07
    File: examples/housing_eviction.yaml:74
  ...
```

### Example: Impact Analysis

```python
from docassemble_dag import DocassembleParser, DependencyGraph
from pathlib import Path

# Parse the interview
yaml_text = Path("examples/housing_eviction.yaml").read_text()
parser = DocassembleParser(yaml_text, file_path="examples/housing_eviction.yaml")
nodes = parser.extract_nodes()
edges = parser.extract_edges(nodes)
graph = DependencyGraph(nodes, edges)

# Find what depends on 'notice_period_valid'
dependents = graph.get_transitive_dependents("notice_period_valid")
print(f"Changing 'notice_period_valid' would affect: {dependents}")

# Output:
# Changing 'notice_period_valid' would affect:
# {'has_valid_defense', 'recommended_action', 'eviction_defense_eligibility'}
```

### Example: GraphQL Queries

```bash
# Start server
python -m docassemble_dag examples/name_change_gender_affirming.yaml --serve-graphql
```

Then query at http://localhost:8000/graphql:

```graphql
query {
  # Find all variables with authority citations
  nodesByAuthority(pattern: "") {
    name
    authority
    kind
  }
  
  # Get dependency chain
  node(name: "total_cost_estimate") {
    name
    transitiveDependencies {
      name
      kind
    }
  }
}
```

## Use Case Guides

### For Legal Aid Organizations

These examples demonstrate patterns useful for legal aid:

1. **Income Eligibility Screening** (all examples)
   - Calculate eligibility for free legal services
   - Fee waiver determinations
   - Sliding scale calculations

2. **Multi-Language Support** (asylum example)
   - Serve limited English proficient clients
   - Dynamic content translation
   - Interpreter needs detection

3. **Multi-Jurisdiction Support** (name change example)
   - Handle clients across state lines
   - State-specific requirement tracking
   - Cost and timeline transparency

4. **Deadline Management** (all examples)
   - Calculate critical filing deadlines
   - Urgent deadline warnings
   - Procedural compliance

5. **Authority Tracking** (CPLR example)
   - Track statute citations
   - Impact analysis for law changes
   - Compliance reporting

### For Developers

Key patterns demonstrated:

- **Conditional Logic**: Use `show if`, `enable if`, `depends on` effectively
- **Code Blocks**: Prefer `expression:` for simple logic, `code:` for complex
- **Object-Oriented**: Use `objects:` for complex data structures
- **Assembly Line**: Follow AL conventions for interoperability
- **Help Text**: Provide context-sensitive help throughout
- **Authority Citations**: Document legal sources in `authority:` field
- **Validation**: Structure interviews for automated validation

## Contributing Examples

We welcome additional examples! Good examples should:

- ✅ Represent real-world legal aid scenarios
- ✅ Demonstrate specific dependency patterns
- ✅ Include authority citations where applicable
- ✅ Provide helpful context and documentation
- ✅ Use plain language and accessibility features
- ✅ Include comments explaining complex logic

### Example Template

```yaml
---
metadata:
  title: Example Title
  short title: Short Title
  description: |
    Brief description of what this interview does and what it demonstrates.
  authors:
    - name: Your Name
  revision_date: YYYY-MM-DD
---
# Features and modules
features:
  question help button: True
  progress bar: True
---
# Your interview content here
```

### Submitting Examples

1. Create your example YAML file
2. Test it with `docassemble-dag`
3. Add documentation to this README
4. Submit a pull request

Include in your PR:
- Brief description of the use case
- Key features demonstrated
- Example `docassemble-dag` commands
- Expected dependency graph structure

---

## Additional Resources

- **[Main README](../README.md)**: Full documentation
- **[EXAMPLES.md](../EXAMPLES.md)**: Python API examples
- **[LEGALTECH_GUIDE.md](LEGALTECH_GUIDE.md)**: Detailed legaltech use cases
- **[GRAPHQL_API.md](../GRAPHQL_API.md)**: GraphQL query guide

---

**Questions or feedback?** Open an issue or discussion on GitHub!
