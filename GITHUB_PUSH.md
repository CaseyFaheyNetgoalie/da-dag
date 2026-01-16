# Push Repository to GitHub

## Quick Steps

### 1. Initialize Git (if not already done)
```bash
git init
```

### 2. Add All Files
```bash
git add .
```

### 3. Create Initial Commit
```bash
git commit -m "Initial commit: Docassemble DAG v0.5.0

Static dependency graph extractor for Docassemble YAML interviews.

Features:
- Parse Docassemble YAML to extract explicit dependency graphs
- Support for SQLite and PostgreSQL persistence
- Graph validation and policy checks
- Multiple export formats (JSON, DOT, GraphML, HTML)
- Template validation
- Graph comparison and change tracking
- Comprehensive test suite (183+ tests)"
```

### 4. Create GitHub Repository

**Option A: Via Web UI**
1. Go to https://github.com/new
2. Repository name: `docassemble-dag` (or your choice)
3. Description: "Static analyzer for extracting explicit dependency graphs from Docassemble YAML interview files"
4. Choose public or private
5. **DO NOT** initialize with README, .gitignore, or license (we have these)
6. Click "Create repository"
7. Copy the repository URL (e.g., `https://github.com/yourusername/docassemble-dag.git`)

**Option B: Via GitHub CLI**
```bash
gh repo create docassemble-dag --public --description "Static analyzer for Docassemble dependency graphs"
```

### 5. Add Remote and Push
```bash
# Add remote (replace with your repository URL)
git remote add origin https://github.com/YOUR_USERNAME/docassemble-dag.git

# Rename branch to main (if needed)
git branch -M main

# Push to GitHub
git push -u origin main
```

## Alternative: Using SSH

If you have SSH keys set up with GitHub:
```bash
git remote add origin git@github.com:YOUR_USERNAME/docassemble-dag.git
git branch -M main
git push -u origin main
```

## Verify Push

```bash
# Check remote
git remote -v

# View recent commits
git log --oneline -5

# View status
git status
```

## Troubleshooting

### If remote already exists
```bash
# Remove existing remote
git remote remove origin

# Add new remote
git remote add origin <your-repo-url>
```

### If you need to force push (not recommended)
```bash
git push -u origin main --force
```

### If you get authentication errors
- Use GitHub CLI: `gh auth login`
- Or use personal access token instead of password
- Or set up SSH keys

## Next Steps

After pushing:
1. Go to your GitHub repository
2. Verify all files are present
3. Check README.md displays correctly
4. Optional: Create a release tag
   ```bash
   git tag -a v0.5.0 -m "Release v0.5.0"
   git push origin v0.5.0
   ```
