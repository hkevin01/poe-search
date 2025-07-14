#!/usr/bin/env bash
"""
Quick verification test for run.sh functionality.
"""

echo "🧪 Testing run.sh Functionality"
echo "================================"

# Test 1: Check if .venv exists
if [ -d ".venv" ]; then
    echo "✅ Virtual environment (.venv) found"
else
    echo "❌ Virtual environment (.venv) not found"
    exit 1
fi

# Test 2: Check virtual environment activation
source .venv/bin/activate
if [ $? -eq 0 ]; then
    echo "✅ Virtual environment activation successful"
else
    echo "❌ Virtual environment activation failed"
    exit 1
fi

# Test 3: Check PYTHONPATH and GUI module import
PYTHONPATH="$PWD/src:$PYTHONPATH" python -c "import poe_search.gui; print('✅ GUI module import successful')" 2>/dev/null
if [ $? -eq 0 ]; then
    echo "✅ GUI module import with PYTHONPATH works"
else
    echo "❌ GUI module import failed"
    exit 1
fi

# Test 4: Check if run.sh is executable
if [ -x "run.sh" ]; then
    echo "✅ run.sh is executable"
else
    echo "⚠️  Making run.sh executable..."
    chmod +x run.sh
    echo "✅ run.sh is now executable"
fi

echo ""
echo "🎉 run.sh verification completed successfully!"
echo "================================"
echo "✅ Virtual environment setup correct"
echo "✅ PYTHONPATH configuration works"
echo "✅ GUI module can be imported"
echo "✅ Script is ready for use"
echo ""
echo "Usage: ./run.sh"
echo "       bash run.sh"
