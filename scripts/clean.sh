#!/bin/bash

# Cleanup script for poe-search project

set -e

echo "🧹 Cleaning up poe-search project..."

# Remove build artifacts
echo "Removing build artifacts..."
rm -rf build/
rm -rf dist/
rm -rf *.egg-info/
rm -rf src/*.egg-info/

# Remove Python cache files
echo "Removing Python cache files..."
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find . -type f -name "*.pyc" -delete 2>/dev/null || true
find . -type f -name "*.pyo" -delete 2>/dev/null || true

# Remove test artifacts
echo "Removing test artifacts..."
rm -rf .pytest_cache/
rm -rf .coverage
rm -rf htmlcov/
rm -rf .tox/
rm -rf .mypy_cache/

# Clean logs and temporary files
echo "Cleaning logs and temporary files..."
rm -rf logs/*.log 2>/dev/null || true
rm -rf temp/ 2>/dev/null || true

# Optionally remove virtual environment
if [ "$1" == "--all" ]; then
    echo "Removing virtual environment..."
    rm -rf venv/
    
    echo "Removing database and exports..."
    rm -rf *.db *.sqlite *.sqlite3 2>/dev/null || true
    rm -rf exports/ 2>/dev/null || true
    rm -rf .cache/ 2>/dev/null || true
fi

echo "✅ Cleanup completed!"

if [ "$1" == "--all" ]; then
    echo "🔄 Run ./scripts/setup-dev.sh to reinitialize the project"
fi
