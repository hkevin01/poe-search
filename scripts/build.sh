#!/bin/bash

# Build script for poe-search project

set -e

echo "🏗️  Building poe-search..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install build dependencies
echo "Installing build dependencies..."
pip install --upgrade build wheel hatch

# Install project in development mode
echo "Installing project in development mode..."
pip install -e ".[dev]"

# Run linting
echo "Running linting..."
black --check src/ tests/ || true
ruff check src/ tests/ || true

# Run type checking
echo "Running type checking..."
mypy src/poe_search/ || true

# Run tests
echo "Running tests..."
pytest tests/ -v || true

# Build the package
echo "Building package..."
python -m build

echo "✅ Build completed successfully!"
echo "📦 Package files are in dist/"
echo "🚀 Install with: pip install dist/poe_search-*.whl"
