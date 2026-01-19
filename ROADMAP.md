# Docassemble DAG - Project Roadmap

This document outlines the planned features, enhancements, and improvements for `docassemble-dag`.

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

## Upcoming Releases

### 🎯 v0.6.0 - Enhanced Analysis & UX (Q1 2026)
**Focus: User Experience & Advanced Analysis**

#### High Priority
- [ ] **Enhanced HTML Viewer**
  - [ ] Save/restore filter states
  - [ ] Export filtered subgraphs
  - [ ] Node search with autocomplete
  - [ ] Minimap navigation for large graphs
  - [ ] Side-by-side comparison view

- [ ] **Improved Template Validation**
  - [ ] Support for Markdown templates
  - [ ] Jinja2 template validation
  - [ ] Template fragment validation
  - [ ] Auto-fix suggestions for undefined variables

- [ ] **Better Error Messages**
  - [ ] Suggest fixes for common errors
  - [ ] Context-aware error messages
  - [ ] Did-you-mean suggestions for typos
  - [ ] Link to documentation from errors

- [ ] **CLI Improvements**
  - [ ] Progress bars for large files
  - [ ] Colorized output
  - [ ] Interactive mode for validation fixes
  - [ ] Watch mode (auto-reload on file changes)

#### Medium Priority
- [ ] **Performance Optimizations**
  - [ ] Parallel file processing
  - [ ] Incremental graph updates
  - [ ] Lazy loading for large graphs
  - [ ] Caching improvements

- [ ] **Documentation**
  - [ ] Video tutorials
  - [ ] Interactive examples
  - [ ] Jupyter notebook examples
  - [ ] API reference documentation

### 🚀 v0.7.0 - AI-Powered Features (Q2 2026)
**Focus: Intelligence & Automation**

#### High Priority
- [ ] **AI-Powered Analysis**
  - [ ] Suggest missing dependencies using ML
  - [ ] Auto-generate authority citations
  - [ ] Detect common anti-patterns
  - [ ] Smart refactoring suggestions

- [ ] **Natural Language Queries**
  - [ ] Ask questions about dependencies in plain English
  - [ ] Generate summaries of graph structure
  - [ ] Explain dependency chains in natural language

- [ ] **Auto-Documentation**
  - [ ] Generate flowcharts from graphs
  - [ ] Auto-create user guides
  - [ ] Generate test scenarios

#### Medium Priority
- [ ] **Intelligent Validation**
  - [ ] Context-aware validation rules
  - [ ] Learn from validation history
  - [ ] Suggest policy improvements

### 🔧 v0.8.0 - Developer Tools (Q3 2026)
**Focus: Developer Experience & Integration**

#### High Priority
- [ ] **IDE Integration**
  - [ ] VS Code extension
  - [ ] Language server protocol (LSP) support
  - [ ] Inline dependency hints
  - [ ] Real-time validation

- [ ] **Testing Tools**
  - [ ] Generate test cases from graph
  - [ ] Coverage analysis (which paths tested?)
  - [ ] Mock data generation
  - [ ] Regression testing for graph changes

- [ ] **Development Server**
  - [ ] Live reload during development
  - [ ] Debug mode with step-through
  - [ ] Dependency visualization overlay

#### Medium Priority
- [ ] **Build Tools**
  - [ ] Webpack/Vite plugin
  - [ ] Pre-commit hooks generator
  - [ ] Custom policy plugin system

### 📊 v0.9.0 - Enterprise Features (Q4 2026)
**Focus: Scale & Governance**

#### High Priority
- [ ] **Multi-User Support**
  - [ ] User authentication for GraphQL API
  - [ ] Role-based access control
  - [ ] Audit logging
  - [ ] Collaboration features

- [ ] **Advanced Persistence**
  - [ ] Graph versioning with diffs
  - [ ] Branching and merging
  - [ ] Rollback capabilities
  - [ ] Graph migrations

- [ ] **Compliance & Governance**
  - [ ] Custom compliance rules engine
  - [ ] Automated compliance reports
  - [ ] Policy enforcement at CI/CD level
  - [ ] Compliance dashboard

#### Medium Priority
- [ ] **Scalability**
  - [ ] Distributed graph processing
  - [ ] Cloud deployment options
  - [ ] Horizontal scaling for GraphQL
  - [ ] Graph sharding for very large interviews

---

## Future Considerations (v1.0+)

### Advanced Features
- [ ] **Docassemble Runtime Integration**
  - [ ] Hook into Docassemble runtime for dynamic analysis
  - [ ] Trace actual execution paths
  - [ ] Performance profiling
  - [ ] Runtime validation

- [ ] **Advanced Visualization**
  - [ ] 3D graph visualization
  - [ ] Timeline view for execution flow
  - [ ] Heatmaps for frequently used paths
  - [ ] Animated dependency resolution

- [ ] **Machine Learning**
  - [ ] Predict interview completion time
  - [ ] Suggest interview structure improvements
  - [ ] Auto-optimize question ordering
  - [ ] Detect interview logic bugs

- [ ] **Integration Hub**
  - [ ] Slack notifications for validation failures
  - [ ] Jira integration for tracking issues
  - [ ] GitHub issue auto-creation
  - [ ] Email reports

### Platform Support
- [ ] **Web Application**
  - [ ] Hosted SaaS version
  - [ ] Team collaboration features
  - [ ] Shared graph library
  - [ ] Interview marketplace

- [ ] **Mobile Support**
  - [ ] Mobile-friendly HTML viewer
  - [ ] iOS/Android native apps
  - [ ] Offline viewing

### Developer Tools
- [ ] **Code Generation**
  - [ ] Generate Docassemble YAML from visual editor
  - [ ] Scaffold new interviews from templates
  - [ ] Auto-generate documentation
  - [ ] Generate unit tests

- [ ] **Refactoring Tools**
  - [ ] Safe variable renaming
  - [ ] Extract common logic
  - [ ] Merge duplicate variables
  - [ ] Split complex rules

---

## Community-Requested Features

*Features requested by the community. Vote on these by opening/commenting on GitHub issues.*

### High Interest
- [ ] Export to other formats (Mermaid, PlantUML)
- [ ] Better support for DAList and DADict
- [ ] Track question skip logic (show if/enable if)
- [ ] Visual graph editor (drag-and-drop)
- [ ] Import from other interview systems

### Under Consideration
- [ ] Support for non-YAML interview formats
- [ ] Integration with LegalServer
- [ ] A2J Author compatibility
- [ ] Custom metadata extraction
- [ ] Blockchain-based audit trails

---

## How to Contribute

### Request a Feature
1. Check existing [GitHub Issues](https://github.com/yourusername/docassemble-dag/issues)
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

- **Minor versions** (0.x.0): Quarterly
- **Patch versions** (0.x.y): As needed for bug fixes
- **Major version** (1.0.0): When API is stable (estimated Q4 2026)

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

### Adoption
- **Target**: 100+ stars on GitHub by Q2 2026
- **Target**: 50+ organizations using in production by Q4 2026
- **Target**: 10+ community contributors by end of 2026

### Quality
- **Target**: 90%+ test coverage
- **Target**: <5 open critical bugs
- **Target**: <48hr average response time on issues

### Performance
- **Target**: Parse 1000-node graph in <1 second
- **Target**: GraphQL query response <100ms
- **Target**: HTML viewer handles 5000+ nodes smoothly

---

## Questions?

- 💬 Discuss features in [GitHub Discussions](https://github.com/yourusername/docassemble-dag/discussions)
- 🐛 Report bugs in [GitHub Issues](https://github.com/yourusername/docassemble-dag/issues)
- 📧 Contact maintainers by submitting an issue or pull request

---

**Last Updated**: January 2026
**Next Review**: April 2026
