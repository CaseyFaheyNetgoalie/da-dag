# GitHub Actions Workflows

This directory contains CI/CD workflow templates for validating Docassemble interviews.

## validate-interview.yml

Validates Docassemble YAML interviews by:
- Checking for circular dependencies (`--check-cycles`)
- Running policy validation (`--validate`)
- Generating dependency graph artifacts

### Usage

**Automatic** (triggered on push/PR when YAML files change):
- Automatically runs on pushes to `main`, `master`, or `develop` branches
- Triggers when `.yaml` or `.yml` files change
- Validates all YAML files in the repository

**Manual** (workflow_dispatch):
```bash
# Trigger from GitHub Actions UI
# Specify interview_path: 'interviews/' or specific file
```

### Configuration

Edit `validate-interview.yml` to:
- Change default interview path (`interviews/`)
- Adjust branches that trigger validation
- Modify validation policies
- Change artifact retention period

### For Lemma Legal / Production Use

To use with your Docassemble interview repository:

1. Copy this workflow to your repo's `.github/workflows/` directory
2. Update `interview_path` to match your interview location
3. Customize validation policies as needed
4. Enable the workflow

### Artifacts

The workflow generates:
- `dependency-graph.json` - Complete dependency graph for all interviews
- Retention: 30 days (configurable)

Use this artifact for:
- Change impact analysis
- Documentation generation
- Compliance reporting
