.PHONY: help install install-dev test test-cov lint format type-check check-all clean docs

help:  ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Available targets:'
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  %-20s %s\n", $$1, $$2}'

install:  ## Install package
	pip install -e .

install-dev:  ## Install package with development dependencies
	pip install -e ".[dev]"
	pre-commit install

test:  ## Run tests
	pytest tests/ -v

test-cov:  ## Run tests with coverage report
	pytest tests/ --cov=docassemble_dag --cov-report=html --cov-report=term-missing

test-fast:  ## Run tests quickly (no coverage)
	pytest tests/ -v -x

lint:  ## Run linters
	flake8 docassemble_dag tests --max-line-length=100 --extend-ignore=E203,W503
	ruff check docassemble_dag tests

format:  ## Format code with black and isort
	black docassemble_dag tests
	isort docassemble_dag tests

format-check:  ## Check code formatting without making changes
	black --check docassemble_dag tests
	isort --check-only docassemble_dag tests

type-check:  ## Run type checking with mypy
	mypy docassemble_dag --ignore-missing-imports

check-all: lint type-check test  ## Run all checks (lint, type-check, test)

clean:  ## Clean generated files
	find . -type d -name __pycache__ -exec rm -r {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type d -name "*.egg-info" -exec rm -r {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -r {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -r {} + 2>/dev/null || true
	find . -type d -name "htmlcov" -exec rm -r {} + 2>/dev/null || true
	find . -type f -name ".coverage" -delete

docs:  ## Build documentation (if Sphinx is configured)
	@echo "Documentation building not yet configured"
	@echo "To set up: sphinx-quickstart docs"

benchmark:  ## Run performance benchmarks
	pytest tests/ --benchmark-only

ci: check-all  ## Run all CI checks (alias for check-all)
