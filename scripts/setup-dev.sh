#!/bin/bash

# Development setup script for poe-search

set -e

echo "🚀 Setting up poe-search development environment..."

# Check Python version
python_version=$(python3 --version 2>&1 | cut -d' ' -f2)
echo "Python version: $python_version"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install development dependencies
echo "Installing development dependencies..."
pip install -e ".[dev,docs]"

# Install pre-commit hooks
echo "Installing pre-commit hooks..."
pre-commit install

# Create necessary directories
mkdir -p logs exports .cache

# Create example .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "Creating example .env file..."
    cat > .env << EOF
# Poe Search Configuration
# Copy this file and add your actual values

# Your Poe authentication token (required)
# Get this from your browser's cookies after logging into poe.com
POE_TOKEN=your_token_here

# Database configuration
DATABASE_URL=sqlite:///poe_search.db

# Logging level (DEBUG, INFO, WARNING, ERROR)
LOG_LEVEL=INFO

# Rate limiting (seconds between requests)
RATE_LIMIT_DELAY=1.0

# Output directories
OUTPUT_DIR=exports
CACHE_DIR=.cache
EOF
fi

# Initialize database
echo "Initializing database..."
python -c "
from poe_search.storage.database import Database
db = Database()
print('Database initialized successfully!')
"

# Run initial tests
echo "Running initial tests..."
pytest tests/ -v --tb=short || echo "Some tests failed - this is normal for initial setup"

echo "✅ Development environment setup complete!"
echo ""
echo "📝 Next steps:"
echo "1. Activate the virtual environment: source venv/bin/activate"
echo "2. Set your Poe token in .env file"
echo "3. Start developing: poe-search --help"
echo "4. Run tests: pytest"
echo "5. Run linting: black . && ruff check ."
