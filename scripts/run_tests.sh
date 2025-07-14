#!/usr/bin/env bash

# Test runner script for Poe Search project
set -e

echo "🧪 Poe Search Test Suite"
echo "========================"

# Activate virtual environment
if [ -d ".venv" ]; then
    source .venv/bin/activate
    echo "✅ Activated virtual environment"
elif [ -d "venv" ]; then
    source venv/bin/activate
    echo "✅ Activated virtual environment (legacy)"
else
    echo "❌ No virtual environment found"
    exit 1
fi

# Set Python path
export PYTHONPATH="$PWD/src:$PYTHONPATH"

# Run different test suites
echo ""
echo "🔍 Running unit tests..."
python -m pytest tests/ -v --tb=short

echo ""
echo "🚀 Running integration tests..."
python -m pytest tests/integration/ -v --tb=short

echo ""
echo "📊 Running conversation retrieval tests..."
python dev-tools/testing/quick_conversation_test.py

echo ""
echo "🎯 Running database diagnostics..."
python dev-tools/testing/database_status.py

echo ""
echo "✅ All tests completed!"
echo "📝 Check logs/test_results.log for detailed output"
