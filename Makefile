# Poe Search Development Makefile

.PHONY: help install install-dev install-gui test test-no-cov lint format clean build docs docs-serve security gui cli setup release deps-check deps-update

# Default target
help:
	@echo "Poe Search Development Commands:"
	@echo ""
	@echo "Installation:"
	@echo "  install      - Install production dependencies"
	@echo "  install-dev  - Install development dependencies"
	@echo "  install-gui  - Install GUI dependencies"
	@echo "  setup        - Set up complete development environment"
	@echo ""
	@echo "Development:"
	@echo "  test         - Run tests with coverage"
	@echo "  test-no-cov  - Run tests without coverage"
	@echo "  lint         - Run linting checks"
	@echo "  format       - Format code"
	@echo "  clean        - Clean build artifacts"
	@echo "  security     - Run security checks"
	@echo ""
	@echo "Building:"
	@echo "  build        - Build package"
	@echo "  docs         - Build documentation"
	@echo "  docs-serve   - Serve documentation locally"
	@echo ""
	@echo "Running:"
	@echo "  gui          - Run GUI application"
	@echo "  cli          - Run CLI application (use: make cli ARGS='search \"test\"')"
	@echo ""
	@echo "Dependencies:"
	@echo "  deps-check   - Check for outdated dependencies"
	@echo "  deps-update  - Update dependencies"
	@echo ""
	@echo "Release:"
	@echo "  release      - Create a new release (use: make release VERSION=1.0.0)"

# Installation targets
install:
	python -m pip install -e .

install-dev:
	python -m pip install -e ".[dev]"

install-gui:
	python -m pip install -e ".[gui]"

setup: install-dev install-gui
	pre-commit install
	$(MAKE) lint
	$(MAKE) test-no-cov
	@echo "Development environment setup complete!"

# Testing targets
test:
	pytest tests/ -v --cov=src/poe_search

test-no-cov:
	python -m pytest tests/

# Code quality targets
lint:
	black --check src/ tests/
	isort --check-only src/ tests/
	flake8 src/ tests/
	mypy src/poe_search/

format:
	python -m black src/ tests/
	python -m ruff check --fix src/ tests/

# Cleaning target
clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -name "*.pyc" -delete
	find . -name "*.pyo" -delete
	find . -name "*.pyd" -delete
	rm -rf .pytest_cache
	rm -rf .coverage
	rm -rf htmlcov
	rm -rf dist
	rm -rf build
	rm -rf *.egg-info
	@echo "Project cleaned successfully."

# Security target
security:
	python -m bandit -r src/poe_search/ || true
	python -m safety check || true

# Building targets
build: clean
	python -m build

docs:
	mkdocs build

docs-serve:
	@echo "Documentation will be available at http://localhost:8000"
	python -m mkdocs serve

# Running targets
gui:
	python -m poe_search.gui

cli:
	@if [ -z "$(ARGS)" ]; then \
		echo "Usage: make cli ARGS='search \"test\"'"; \
		exit 1; \
	fi
	python -m poe_search.cli $(ARGS)

# Dependency management targets
deps-check:
	python -m pip list --outdated

deps-update:
	python -m pip install --upgrade pip
	python -m pip install --upgrade -e ".[dev,gui]"

# Release target
release:
	@if [ -z "$(VERSION)" ]; then \
		echo "Usage: make release VERSION=1.0.0"; \
		exit 1; \
	fi
	@echo "Creating release $(VERSION)..."
	@sed -i "s/__version__ = \"0.1.0\"/__version__ = \"$(VERSION)\"/" src/poe_search/__about__.py
	$(MAKE) build
	$(MAKE) test
	$(MAKE) security
	@echo "Release $(VERSION) prepared successfully!"
	@echo "Next steps:"
	@echo "1. Review the changes"
	@echo "2. Commit and tag the release"
	@echo "3. Push to GitHub"
	@echo "4. Create GitHub release"

# Quick development workflow
dev: format lint test

# Full CI workflow
ci: lint test security build

# Quick start for new developers
quickstart: setup
	@echo ""
	@echo "Quick start complete! You can now:"
	@echo "  - Run tests: make test"
	@echo "  - Start GUI: make gui"
	@echo "  - Run CLI: make cli ARGS='search \"test\"'"
	@echo "  - Format code: make format"
	@echo "  - Check linting: make lint"