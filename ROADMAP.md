# Docassemble DAG - Project Roadmap

This document outlines the planned evolution of `docassemble-dag` from a dependency-graph extractor into **compliance-grade static analysis infrastructure** for Docassemble interviews.

The roadmap is organized by **capability layers** rather than strict dates, reflecting institutional readiness, adoption maturity, and architectural stability.

---

## Guiding Principles

* **Static Analysis Only**: da-dag will never execute interviews, simulate users, or invoke external APIs.
* **Deterministic Outputs**: Identical inputs must always produce identical graphs and findings.
* **Explainability First**: All analysis must be traceable to source files and lines.
* **Institutional Trust**: Outputs must be suitable for audits, filings, and compliance review.
* **AI Safety**: Validate AI-generated code and prevent hallucinations in automated interview development.
* **Access to Justice**: Prioritize features that support pro se litigants and legal aid organizations.

---

## Version History

### ✅ v0.5.0 (Current) - GraphQL & Advanced Features
**Released: January 2026**

- ✅ GraphQL API with interactive GraphiQL IDE
- ✅ Interactive HTML viewer with D3.js visualization
- ✅ Template validation (DOCX, PDF, Mako)
- ✅ Graph comparison and change tracking
- ✅ Compliance reporting with statute citations
- ✅ Decision tree extraction
- ✅ Conditional logic detection (show if, enable if)
- ✅ Reconsider directive tracking
- ✅ Objects section support
- ✅ Enhanced multi-file/batch processing
- ✅ PostgreSQL support (in addition to SQLite)

### ✅ v0.4.0 - Validation & Comparison
- ✅ HTML interactive viewer
- ✅ Template validation
- ✅ Graph comparison utilities
- ✅ Change impact analysis

### ✅ v0.3.0 - Assembly Line & Multi-File
- ✅ Assembly Line variable recognition (AL_ prefix)
- ✅ Object attribute handling (person.name → person)
- ✅ Modules directive parsing
- ✅ Multi-document YAML support
- ✅ AST-based Python code analysis

### ✅ v0.2.0 - Persistence & Validation
- ✅ SQLite persistence
- ✅ Policy validation framework
- ✅ Provenance tracking (file paths, line numbers)

### ✅ v0.1.0 - Initial Release
- ✅ Basic YAML parsing
- ✅ Dependency extraction (explicit and implicit)
- ✅ Cycle detection
- ✅ JSON/DOT/GraphML export

---

## Capability Roadmap

### Phase 1: Core Graph Extraction (Foundation)
**Status: ✅ Existing / Ongoing**

Core capabilities for deterministic, inspectable dependency graph extraction:

- ✅ Parse Docassemble YAML interviews into explicit dependency graphs (DAGs)
- ✅ Model variables, questions, code blocks, and rules as typed nodes
- ✅ Detect cycles, missing dependencies, and unreachable logic
- ✅ Export graphs in machine-readable formats (JSON, DOT, GraphML)
- ✅ Preserve provenance metadata (file path, line number, source type)

**Ongoing Enhancements:**
- [ ] Enhanced object attribute tracking for complex data structures
- [ ] Better support for DAList and DADict comprehension
- [ ] Improved detection of implicit dependencies in Python code blocks
- [ ] Session state visualization capabilities

**Outcome**: A deterministic, inspectable representation of interview logic suitable for institutional analysis.

---

### Phase 2: Validator Framework & Standard Findings
**Status: 🎯 Planned (High Priority) - Target Q1-Q2 2026**

Establish a pluggable validator framework operating over dependency graphs:

#### Core Framework
- [ ] **Pluggable Validator Architecture**
  - [ ] Base validator interface with graph traversal utilities
  - [ ] Validator registration and discovery system
  - [ ] Shared query and traversal utilities
  - [ ] Validator composition and chaining

- [ ] **Standard Findings Schema**
  - [ ] Validator name and version
  - [ ] Rule identifier (machine-readable ID)
  - [ ] Severity levels (info, warning, error, critical)
  - [ ] Affected node(s) with provenance
  - [ ] Source location (file path, line number, column)
  - [ ] Human-readable message
  - [ ] Remediation guidance with code examples
  - [ ] Related findings (grouped issues)

- [ ] **Findings Export Formats**
  - [ ] JSON structured output
  - [ ] SARIF (Static Analysis Results Interchange Format)
  - [ ] JUnit XML for CI integration
  - [ ] Human-readable HTML/Markdown reports

**Outcome**: A stable foundation for compliance, quality, and policy validation with institutional-grade reporting.

---

### Phase 3: Validation, Compliance & Quality Gates
**Status: 🚀 Planned (High Priority) - Target Q2-Q3 2026**

Implement first-class validators focused on institutional requirements:

#### Language & Accessibility Validators
- [ ] **Plain Language Validator**
  - [ ] Reading level checks (Flesch-Kincaid scoring)
  - [ ] Legalese detection and suggestions
  - [ ] Sentence complexity analysis
  - [ ] Plain language alternatives database
  - [ ] Question clarity scoring

- [ ] **Pro Se / Self-Represented Litigant Validator**
  - [ ] "Lawyer-free" language checks (avoiding legal jargon requiring expertise)
  - [ ] Reading level targets for self-help content (6th-8th grade)
  - [ ] Step-by-step explainability validation
  - [ ] Check for unexplained legal terms
  - [ ] Verify instructions are actionable without legal training
  - [ ] Validate that options are clearly distinguishable for non-lawyers

- [ ] **WCAG AA Accessibility Checker**
  - [ ] Color contrast validation
  - [ ] Screen reader compatibility checks
  - [ ] Required labels and help text verification
  - [ ] Keyboard navigation validation
  - [ ] Form label compliance
  - [ ] ARIA attribute validation
  - [ ] Error prevention and recovery patterns

#### Multi-Language & Translation
- [ ] **Multi-Language Dependency Tracker**
  - [ ] Track translation coverage across languages
  - [ ] Identify untranslated variables and questions
  - [ ] Validate language-specific dependencies
  - [ ] Generate translation gap reports
  - [ ] Support for multi-locale interviews
  - [ ] Translation completeness metrics

#### Integration & Data Flow
- [ ] **Case Management Integration Validator**
  - [ ] Clio integration validation
  - [ ] LegalServer integration validation
  - [ ] Practice Panther integration validation
  - [ ] Verification of required integration variables
  - [ ] Static detection of API integration points
  - [ ] Data mapping verification
  - [ ] Authentication flow validation
  - [ ] Webhook configuration checks

#### Interview Quality & Best Practices
- [ ] **Interview Flow Anti-Patterns Detector**
  - [ ] Detect non-idempotent logic patterns
  - [ ] Identify potential infinite loops
  - [ ] Flag questions that might trigger "Input not processed" errors
  - [ ] Warn about variables set multiple times
  - [ ] Detect missing reconsider directives

- [ ] **Template Validation Suite**
  - [ ] Support for Markdown, Jinja2, DOCX, PDF templates
  - [ ] Detect undefined variables in templates
  - [ ] Identify unused variables
  - [ ] Auto-fix suggestions for common issues

- [ ] **AI-Generated Code Validation**
  - [ ] Detect hallucinated Docassemble features (non-existent directives)
  - [ ] Validate AI-generated interviews against known patterns
  - [ ] Flag suspicious or malformed YAML patterns
  - [ ] Identify deprecated features in AI-generated code
  - [ ] Verify that AI suggestions align with current Docassemble version

- [ ] **Context Engineering Validator**
  - [ ] Analyze context availability for conditional logic
  - [ ] Ensure users have sufficient information before critical questions
  - [ ] Validate that help text provides adequate context
  - [ ] Check for "context gaps" where users might be confused
  - [ ] Verify progressive disclosure patterns

#### Quality Gates
- [ ] **Configurable Quality Gates**
  - [ ] Threshold-based pass/fail criteria
  - [ ] Severity-weighted scoring
  - [ ] Custom gate profiles per organization
  - [ ] Gate override capabilities with justification tracking

- [ ] **Regulatory Compliance Tracking**
  - [ ] EU AI Act risk classification for interviews
  - [ ] ABA Formal Opinion 512 compliance documentation
  - [ ] Audit trail of all validators run with timestamps
  - [ ] Human oversight point documentation
  - [ ] AI usage disclosure tracking
  - [ ] Generate regulatory compliance reports

**Outcome**: Objective, repeatable enforcement of interview quality standards suitable for court review, grant reporting, and compliance audits.

---

### Phase 4: CI/CD Integration & Automation
**Status: 🔧 Planned - Target Q3 2026**

Transform da-dag into enforceable infrastructure:

- [ ] **Command-Line Interface Enhancements**
  - [ ] Exit codes based on validation severity thresholds
  - [ ] Progress bars for large file processing
  - [ ] Colorized, actionable output
  - [ ] Watch mode (auto-reload on file changes)
  - [ ] Batch validation mode

- [ ] **CI/CD Pipeline Support**
  - [ ] Pre-commit hooks generator
  - [ ] GitHub Actions workflow templates
  - [ ] GitLab CI pipeline templates
  - [ ] Jenkins integration guides
  - [ ] Support for build failure on compliance violations

- [ ] **Machine-Readable Reports**
  - [ ] SARIF output for IDE integration
  - [ ] JUnit XML for test result aggregation
  - [ ] Metrics export (Prometheus, StatsD)
  - [ ] Badge generation for README files

- [ ] **Integration Ecosystem Support**
  - [ ] Export findings to Clio via API
  - [ ] Westlaw Edge integration
  - [ ] LexisNexis Legal Analytics format
  - [ ] Webhook support for real-time validation
  - [ ] Standards-compliant API endpoints (OpenAPI/Swagger)
  - [ ] Common legal tech data format support

- [ ] **IDE Integration**
  - [ ] VS Code extension
  - [ ] Language server protocol (LSP) support
  - [ ] Inline dependency hints
  - [ ] Real-time validation
  - [ ] Jump-to-definition for variables
  - [ ] Inline documentation on hover

**Outcome**: da-dag becomes enforceable infrastructure rather than advisory tooling, with seamless integration into development workflows.

---

### Phase 5: Versioned Analysis & Change Impact
**Status: 📊 Planned - Target Q4 2026**

Enable safer refactoring and defensible change management:

- [ ] **Graph Versioning & Comparison**
  - [ ] Compare dependency graphs across interview versions
  - [ ] Detect behavioral changes (new paths, removed paths)
  - [ ] Identify structural changes (new variables, modified dependencies)
  - [ ] Highlight compliance-impacting changes
  - [ ] Visual diff viewer for graph changes

- [ ] **Change Impact Analysis**
  - [ ] Identify affected downstream variables
  - [ ] Detect newly introduced risks or regressions
  - [ ] Calculate "blast radius" of variable changes
  - [ ] Suggest required test updates

- [ ] **Audit Trails**
  - [ ] Version history with metadata
  - [ ] Change justification tracking
  - [ ] Approval workflows for high-risk changes
  - [ ] Automated changelog generation

- [ ] **Advanced Persistence**
  - [ ] Graph versioning with diffs
  - [ ] Branching and merging support
  - [ ] Rollback capabilities
  - [ ] Migration scripts for graph schema changes

**Outcome**: Safer refactoring with audit trails suitable for oversight and compliance review.

---

### Phase 6: Corpus-Level & Cross-Interview Analysis
**Status: 🔬 Planned - Target 2027**

Provide organizational insight beyond individual interviews:

- [ ] **Corpus-Wide Analysis**
  - [ ] Analyze collections of interviews as a unified corpus
  - [ ] Detect repeated variable patterns
  - [ ] Identify reusable logic across projects
  - [ ] Cross-interview dependency tracking

- [ ] **Staff Automation Opportunity Detector**
  - [ ] Identify repeated code patterns across interviews
  - [ ] Suggest modularization opportunities
  - [ ] Calculate time savings from automation
  - [ ] Generate refactoring recommendations
  - [ ] Detect copy-paste code duplication

- [ ] **Organizational Metrics**
  - [ ] Compliance rates across interview portfolio
  - [ ] Code duplication metrics
  - [ ] Standards drift detection
  - [ ] Maintainability indices

- [ ] **Shared Component Library**
  - [ ] Reusable pattern repository
  - [ ] Interview template marketplace
  - [ ] Organization-wide best practices catalog

**Outcome**: Organizational insight enabling strategic decision-making and portfolio management.

---

### Phase 7: Explainability & Audit Artifacts
**Status: 📝 Planned - Target 2027**

Generate transparency for non-technical reviewers and decision-makers:

- [ ] **Structured Explanations**
  - [ ] Generate human-readable explanations of interview logic
  - [ ] Trace how variables are derived and used
  - [ ] Explain dependency chains in plain language
  - [ ] "What happens if..." scenario exploration

- [ ] **Audit-Ready Documentation**
  - [ ] Deterministic artifacts suitable for court review
  - [ ] Grant reporting packages
  - [ ] Compliance audit documentation
  - [ ] Regulatory submission materials

- [ ] **Auto-Documentation**
  - [ ] Generate flowcharts from graphs
  - [ ] Auto-create user guides
  - [ ] Generate test scenarios
  - [ ] Create onboarding documentation

- [ ] **Natural Language Queries**
  - [ ] Ask questions about dependencies in plain English
  - [ ] Generate summaries of graph structure
  - [ ] Interactive Q&A about interview behavior

**Outcome**: Transparency for non-technical reviewers with deterministic, audit-suitable artifacts.

---

### Phase 8: Policy Profiles & Institutional Standards
**Status: 🏛️ Future - Target 2028**

Enable repeatable standards aligned with real-world institutional requirements:

- [ ] **Predefined Policy Profiles**
  - [ ] Court-ready profiles (jurisdiction-specific)
  - [ ] Legal aid compliance profiles
  - [ ] Public-sector accessibility profiles
  - [ ] Pro bono project standards

- [ ] **Court Form Standards Validation**
  - [ ] NC AOC form compliance
  - [ ] CA Judicial Council standards
  - [ ] Federal court local rules
  - [ ] E-filing format requirements

- [ ] **Jurisdictional Compliance**
  - [ ] State-specific legal requirements
  - [ ] Court rule validation
  - [ ] Document assembly standards
  - [ ] Privacy law compliance (GDPR, CCPA)

- [ ] **Profile Sharing & Governance**
  - [ ] Organization-published profiles
  - [ ] Community-maintained standards
  - [ ] Profile versioning and updates
  - [ ] Compliance certification programs

**Outcome**: Standardized, shareable compliance frameworks enabling institutional trust and interoperability.

---

## Additional Planned Features

### Advanced Visualization & UX
- [ ] **Enhanced HTML Viewer**
  - [ ] Save/restore filter states
  - [ ] Export filtered subgraphs
  - [ ] Node search with autocomplete
  - [ ] Minimap navigation for large graphs
  - [ ] Side-by-side comparison view
  - [ ] Path visualization between two variables
  - [ ] "Critical path" highlighting

- [ ] **Advanced Visualization** (Future)
  - [ ] Timeline view for execution flow
  - [ ] Heatmaps for frequently used paths
  - [ ] Interactive "what-if" scenario modeling

### AI-Powered Features
- [ ] **Intelligent Question Generation**
  - [ ] Generate question templates from variable names
  - [ ] Suggest field types based on variable usage
  - [ ] Auto-generate help text
  - [ ] Recommend validation rules

- [ ] **AI-Powered Analysis**
  - [ ] Suggest missing dependencies using ML
  - [ ] Auto-generate authority citations
  - [ ] Detect common anti-patterns
  - [ ] Smart refactoring suggestions

### Testing & Quality Assurance
- [ ] **Automated Testing Suite Generator**
  - [ ] Generate test cases from graph
  - [ ] Coverage analysis (which paths tested?)
  - [ ] Mock data generation
  - [ ] Generate Behave/Gherkin test scenarios
  - [ ] Random path testing

- [ ] **Interview Complexity Metrics**
  - [ ] Cyclomatic complexity for interview logic
  - [ ] Maintainability index
  - [ ] Technical debt indicators
  - [ ] Suggested refactoring priorities

### Developer Tools
- [ ] **Playground Sync Tools**
  - [ ] Two-way sync with Playground
  - [ ] Conflict resolution helpers
  - [ ] Multi-developer collision detection
  - [ ] Version control integration

- [ ] **Question Order Optimizer**
  - [ ] Suggest optimal question ordering
  - [ ] Identify questions that could be consolidated
  - [ ] Detect unnecessary branching
  - [ ] Recommend question grouping strategies

### Enterprise Features
- [ ] **Interview Analytics Dashboard**
  - [ ] Most frequently used paths
  - [ ] Completion rate analysis
  - [ ] Abandonment point detection
  - [ ] Variable usage heatmaps
  - [ ] Time-to-completion metrics

- [ ] **Multi-User Support**
  - [ ] User authentication for GraphQL API
  - [ ] Role-based access control
  - [ ] Audit logging
  - [ ] Team workspaces

---

## Explicit Non-Goals

The following are **intentionally out of scope** to preserve determinism, safety, and institutional trust:

- ❌ Executing Docassemble interviews
- ❌ Simulating user interactions
- ❌ Rendering user interfaces
- ❌ Replacing the Docassemble runtime
- ❌ Invoking external APIs or services during analysis
- ❌ Acting as an authoring IDE with live preview
- ❌ Dynamic runtime analysis or profiling

These constraints ensure da-dag remains a deterministic, trustworthy static analysis tool suitable for compliance and regulatory review.

---

## Community-Driven Features

*Vote on these by opening/commenting on GitHub issues.*

### High Interest
- [ ] Export to other formats (Mermaid, PlantUML, BPMN)
- [ ] Visual graph editor (drag-and-drop)
- [ ] Import from other interview systems (A2J Author)
- [ ] Session state visualization
- [ ] Interview performance benchmarking

### Under Consideration
- [ ] Support for non-YAML interview formats
- [ ] Custom metadata extraction
- [ ] Multi-interview orchestration
- [ ] Interview A/B testing framework
- [ ] Legal citation validation
- [ ] Client portal integration testing

---

## How to Contribute

### Request a Feature
1. Check existing [GitHub Issues](https://github.com/CaseyFaheyNetgoalie/da-dag/issues)
2. Open a new issue with the `feature-request` label
3. Describe the use case and expected behavior
4. Community votes via 👍 reactions

### Contribute Code
1. Fork the repository
2. Create a feature branch
3. Implement the feature with tests
4. Submit a pull request
5. Maintainers will review and merge

### Sponsor Development
Priority features can be sponsored:
- Contact maintainers for commercial support
- Sponsor specific features via GitHub Sponsors
- Enterprise support contracts available

---

## Release Schedule

- **Minor versions** (0.x.0): Aligned with capability phases (quarterly to semi-annual)
- **Patch versions** (0.x.y): As needed for bug fixes
- **Major version** (1.0.0): When Phase 4 (CI/CD Integration) is stable and Phase 5 (Versioned Analysis) is production-ready

---

## Deprecation Policy

### Breaking Changes
- Announced at least 2 minor versions in advance
- Deprecation warnings in code
- Migration guides provided
- Legacy support for 6 months after deprecation

### Current Deprecations
*None at this time*

---

## Success Metrics

We track these metrics to measure project success:

### Quality
- **Target**: 90%+ test coverage
- **Target**: <5 open critical bugs
- **Target**: <48hr average response time on issues
- **Target**: 95%+ upward compatibility between versions
- **Target**: 100% deterministic outputs (identical inputs → identical results)

### Performance
- **Target**: Parse 1000-node graph in <1 second
- **Target**: GraphQL query response <100ms
- **Target**: HTML viewer handles 5000+ nodes smoothly
- **Target**: Validate 100-file interview suite in <30 seconds

### Community Impact
- **Target**: 500+ interviews analyzed
- **Target**: 10,000+ validation errors caught before production
- **Target**: 100+ hours of developer time saved per organization
- **Target**: Adoption by 10+ legal aid organizations
- **Target**: Use in 5+ court system compliance reviews

### Institutional Trust
- **Target**: Accepted in 3+ court compliance filings
- **Target**: Referenced in 10+ grant reports
- **Target**: Certification by 2+ legal tech standards bodies
- **Target**: Compliance with EU AI Act for high-risk legal AI systems
- **Target**: ABA Formal Opinion 512 audit trail capabilities
- **Target**: Adoption by 5+ pro se self-help centers

---

## Questions?

- 💬 Discuss features in [GitHub Discussions](https://github.com/CaseyFaheyNetgoalie/da-dag/discussions)
- 🐛 Report bugs in [GitHub Issues](https://github.com/CaseyFaheyNetgoalie/da-dag/issues)
- 📧 Contact maintainers by submitting an issue or pull request

---

**Last Updated**: January 2026  
**Next Review**: April 2026
