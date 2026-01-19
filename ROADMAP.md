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
  - [ ] Path visualization between two variables
  - [ ] "Critical path" highlighting

- [ ] **Improved Template Validation**
  - [ ] Support for Markdown templates
  - [ ] Jinja2 template validation
  - [ ] Template fragment validation
  - [ ] Auto-fix suggestions for undefined variables
  - [ ] Detect unused variables in templates

- [ ] **Plain Language Validator**
  - [ ] Reading level checks (Flesch-Kincaid scoring)
  - [ ] Legalese detection and suggestions
  - [ ] Sentence complexity analysis
  - [ ] Plain language alternatives database
  - [ ] Question clarity scoring

- [ ] **Interview Flow Anti-Patterns Detector**
  - [ ] Detect non-idempotent logic patterns
  - [ ] Identify potential infinite loops
  - [ ] Flag questions that might trigger "Input not processed" errors
  - [ ] Warn about variables set multiple times
  - [ ] Detect missing reconsider directives

- [ ] **Better Error Messages**
  - [ ] Suggest fixes for common errors
  - [ ] Context-aware error messages
  - [ ] Did-you-mean suggestions for typos
  - [ ] Link to documentation from errors
  - [ ] Show similar working examples

- [ ] **CLI Improvements**
  - [ ] Progress bars for large files
  - [ ] Colorized output
  - [ ] Interactive mode for validation fixes
  - [ ] Watch mode (auto-reload on file changes)

#### Medium Priority
- [ ] **WCAG AA Accessibility Checker**
  - [ ] Color contrast validation
  - [ ] Screen reader compatibility checks
  - [ ] Keyboard navigation validation
  - [ ] Alt text presence verification
  - [ ] Form label compliance
  - [ ] ARIA attribute validation

- [ ] **Question Order Optimizer**
  - [ ] Suggest optimal question ordering
  - [ ] Identify questions that could be consolidated
  - [ ] Detect unnecessary branching
  - [ ] Recommend question grouping strategies

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
  - [ ] Predict likely user paths through interview

- [ ] **Staff Automation Opportunity Detector**
  - [ ] Identify repeated code patterns across interviews
  - [ ] Suggest modularization opportunities
  - [ ] Calculate time savings from automation
  - [ ] Generate refactoring recommendations
  - [ ] Detect copy-paste code duplication
  - [ ] Suggest module extraction for shared logic

- [ ] **Intelligent Question Generation**
  - [ ] Generate question templates from variable names
  - [ ] Suggest field types based on variable usage
  - [ ] Auto-generate help text
  - [ ] Recommend validation rules

- [ ] **Natural Language Queries**
  - [ ] Ask questions about dependencies in plain English
  - [ ] Generate summaries of graph structure
  - [ ] Explain dependency chains in natural language
  - [ ] "What happens if..." scenario exploration

- [ ] **Auto-Documentation**
  - [ ] Generate flowcharts from graphs
  - [ ] Auto-create user guides
  - [ ] Generate test scenarios
  - [ ] Create onboarding documentation

#### Medium Priority
- [ ] **Multi-Language Dependency Tracker**
  - [ ] Track translation coverage across languages
  - [ ] Identify untranslated variables and questions
  - [ ] Validate language-specific dependencies
  - [ ] Generate translation gap reports
  - [ ] Support for multi-locale interviews

- [ ] **Context-Aware Code Completion**
  - [ ] Variable name suggestions
  - [ ] Template variable auto-completion
  - [ ] Import suggestions based on usage

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
  - [ ] Jump-to-definition for variables
  - [ ] Inline documentation on hover

- [ ] **Case Management Integration Validator**
  - [ ] Clio integration validation
  - [ ] LegalServer integration validation
  - [ ] Practice Panther integration validation
  - [ ] API endpoint testing
  - [ ] Data mapping verification
  - [ ] Authentication flow validation
  - [ ] Webhook configuration checks

- [ ] **Automated Testing Suite Generator**
  - [ ] Generate test cases from graph
  - [ ] Coverage analysis (which paths tested?)
  - [ ] Mock data generation
  - [ ] Regression testing for graph changes
  - [ ] API-based automated interview testing
  - [ ] Generate Behave/Gherkin test scenarios
  - [ ] Random path testing

- [ ] **Playground Sync Tools**
  - [ ] Two-way sync with Playground
  - [ ] Conflict resolution helpers
  - [ ] Multi-developer collision detection
  - [ ] Version control integration

- [ ] **Development Server**
  - [ ] Live reload during development
  - [ ] Debug mode with step-through
  - [ ] Dependency visualization overlay
  - [ ] Variable state inspector

#### Medium Priority
- [ ] **Interview Complexity Metrics**
  - [ ] Cyclomatic complexity for interview logic
  - [ ] Maintainability index
  - [ ] Technical debt indicators
  - [ ] Suggested refactoring priorities

- [ ] **Build Tools**
  - [ ] Webpack/Vite plugin
  - [ ] Pre-commit hooks generator
  - [ ] Custom policy plugin system
  - [ ] CI/CD pipeline templates

### 📊 v0.9.0 - Enterprise Features (Q4 2026)
**Focus: Scale & Governance**

#### High Priority
- [ ] **Multi-User Support**
  - [ ] User authentication for GraphQL API
  - [ ] Role-based access control
  - [ ] Audit logging
  - [ ] Collaboration features
  - [ ] Team workspaces

- [ ] **Advanced Persistence**
  - [ ] Graph versioning with diffs
  - [ ] Branching and merging
  - [ ] Rollback capabilities
  - [ ] Graph migrations
  - [ ] Interview snapshot comparison

- [ ] **Compliance & Governance**
  - [ ] Custom compliance rules engine
  - [ ] Automated compliance reports
  - [ ] Policy enforcement at CI/CD level
  - [ ] Compliance dashboard
  - [ ] Regulatory change tracking

- [ ] **Interview Analytics Dashboard**
  - [ ] Most frequently used paths
  - [ ] Completion rate analysis
  - [ ] Abandonment point detection
  - [ ] Variable usage heatmaps
  - [ ] Time-to-completion metrics

#### Medium Priority
- [ ] **Scalability**
  - [ ] Distributed graph processing
  - [ ] Cloud deployment options
  - [ ] Horizontal scaling for GraphQL
  - [ ] Graph sharding for very large interviews

- [ ] **Team Collaboration**
  - [ ] Shared component library
  - [ ] Cross-interview dependency tracking
  - [ ] Reusable pattern repository
  - [ ] Interview template marketplace

---

## Future Considerations (v1.0+)

### Advanced Features
- [ ] **Docassemble Runtime Integration**
  - [ ] Hook into Docassemble runtime for dynamic analysis
  - [ ] Trace actual execution paths
  - [ ] Performance profiling
  - [ ] Runtime validation
  - [ ] Live session debugging

- [ ] **Advanced Visualization**
  - [ ] 3D graph visualization
  - [ ] Timeline view for execution flow
  - [ ] Heatmaps for frequently used paths
  - [ ] Animated dependency resolution
  - [ ] Interactive "what-if" scenario modeling

- [ ] **Visual Interview Builder**
  - [ ] Drag-and-drop question designer
  - [ ] Flow-chart based logic editor
  - [ ] Template visual editor
  - [ ] Real-time preview mode
  - [ ] Export to YAML

- [ ] **Machine Learning**
  - [ ] Predict interview completion time
  - [ ] Suggest interview structure improvements
  - [ ] Auto-optimize question ordering
  - [ ] Detect interview logic bugs
  - [ ] User experience prediction

- [ ] **Cross-Platform Analysis**
  - [ ] Compare Docassemble with A2J Author
  - [ ] Import/export to other interview platforms
  - [ ] Universal interview format converter
  - [ ] Migration assistance tools

- [ ] **Integration Hub**
  - [ ] Slack notifications for validation failures
  - [ ] Jira integration for tracking issues
  - [ ] GitHub issue auto-creation
  - [ ] Email reports
  - [ ] MS Teams integration
  - [ ] Asana/Monday.com task creation

### Platform Support
- [ ] **Web Application**
  - [ ] Hosted SaaS version
  - [ ] Team collaboration features
  - [ ] Shared graph library
  - [ ] Interview marketplace
  - [ ] Community contribution platform

- [ ] **Mobile Support**
  - [ ] Mobile-friendly HTML viewer
  - [ ] iOS/Android native apps
  - [ ] Offline viewing
  - [ ] On-device validation

### Developer Tools
- [ ] **Code Generation**
  - [ ] Generate Docassemble YAML from visual editor
  - [ ] Scaffold new interviews from templates
  - [ ] Auto-generate documentation
  - [ ] Generate unit tests
  - [ ] Create API wrappers

- [ ] **Refactoring Tools**
  - [ ] Safe variable renaming across files
  - [ ] Extract common logic to modules
  - [ ] Merge duplicate variables
  - [ ] Split complex rules
  - [ ] Automated code modernization

- [ ] **Interview Migration Tools**
  - [ ] Upgrade interviews to new Docassemble versions
  - [ ] Migrate from deprecated features
  - [ ] Batch refactoring across interview suites
  - [ ] Breaking change impact analysis

---

## Community-Driven Features

*Vote on these by opening/commenting on GitHub issues.*

### High Interest
- [ ] Export to other formats (Mermaid, PlantUML, BPMN)
- [ ] Better support for DAList and DADict
- [ ] Track question skip logic (show if/enable if)
- [ ] Visual graph editor (drag-and-drop)
- [ ] Import from other interview systems
- [ ] Session state visualization
- [ ] Interview performance benchmarking

### Under Consideration
- [ ] Support for non-YAML interview formats
- [ ] A2J Author compatibility
- [ ] Custom metadata extraction
- [ ] Blockchain-based audit trails
- [ ] Interview monetization/licensing tools
- [ ] Multi-interview orchestration
- [ ] Interview A/B testing framework

### Legal-Specific Features
- [ ] Court form standards validation (e.g., NC AOC, CA Judicial Council)
- [ ] E-filing integration testing
- [ ] Legal citation validation
- [ ] Jurisdiction-specific compliance checks
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

- **Minor versions** (0.x.0): Quarterly
- **Patch versions** (0.x.y): As needed for bug fixes
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

### Performance
- **Target**: Parse 1000-node graph in <1 second
- **Target**: GraphQL query response <100ms
- **Target**: HTML viewer handles 5000+ nodes smoothly
- **Target**: Validate 100-file interview suite in <30 seconds

### Community Impact
- **Target**: 500+ interviews analyzed
- **Target**: 10,000+ validation errors caught before production
- **Target**: 100+ hours of developer time saved per organization

---

## Questions?

- 💬 Discuss features in [GitHub Discussions](https://github.com/CaseyFaheyNetgoalie/da-dag/discussions)
- 🐛 Report bugs in [GitHub Issues](https://github.com/CaseyFaheyNetgoalie/da-dag/issues)
- 📧 Contact maintainers by submitting an issue or pull request
---

**Last Updated**: January 2026
