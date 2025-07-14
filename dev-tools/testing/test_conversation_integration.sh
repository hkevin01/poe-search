#!/usr/bin/env bash

# Test script to verify conversation retrieval through the GUI startup
set -e

echo "=== Testing Poe Search Conversation Functionality ==="
echo

# Check if we're in the right directory
if [ ! -f "run.sh" ]; then
    echo "❌ run.sh not found. Please run from project root."
    exit 1
fi

# Check if database exists
if [ ! -f "data/poe_search.db" ]; then
    echo "❌ Database not found at data/poe_search.db"
    echo "Please ensure the database is populated with conversations."
    exit 1
fi

echo "✅ Found run.sh script"
echo "✅ Found database at data/poe_search.db"

# Test quick conversation retrieval
echo
echo "🧪 Running quick conversation test..."
python dev-tools/testing/quick_conversation_test.py

if [ $? -eq 0 ]; then
    echo "✅ Quick conversation test passed"
else
    echo "❌ Quick conversation test failed"
    exit 1
fi

# Test the run.sh script (dry run style)
echo
echo "🧪 Testing run.sh script initialization..."

# Check virtual environment
if [ -d ".venv" ]; then
    echo "✅ Virtual environment found at .venv"
elif [ -d "venv" ]; then
    echo "✅ Virtual environment found at venv"
else
    echo "❌ No virtual environment found"
    echo "Please create one with: python -m venv .venv"
    exit 1
fi

# Test Python path setup
source .venv/bin/activate 2>/dev/null || source venv/bin/activate 2>/dev/null

PYTHONPATH="$PWD/src:$PYTHONPATH" python -c "
import sys
sys.path.insert(0, '$PWD/src')
try:
    from poe_search.storage.database import Database
    from poe_search.gui.main_window import MainWindow
    print('✅ Core imports successful')
except ImportError as e:
    print(f'❌ Import failed: {e}')
    sys.exit(1)
"

if [ $? -eq 0 ]; then
    echo "✅ Python imports work correctly"
else
    echo "❌ Python import test failed"
    exit 1
fi

# Test database access through GUI modules
echo
echo "🧪 Testing database access through GUI modules..."

PYTHONPATH="$PWD/src:$PYTHONPATH" python -c "
import sys
from pathlib import Path
sys.path.insert(0, '$PWD/src')

from poe_search.storage.database import Database

# Test database connection
db_path = Path('data/poe_search.db')
db = Database(f'sqlite:///{db_path}')

conversations = db.get_conversations(limit=3)
print(f'✅ Retrieved {len(conversations)} conversations through GUI database module')

if conversations:
    conv = conversations[0]
    full_conv = db.get_conversation(conv['id'])
    messages = full_conv.get('messages', [])
    print(f'✅ Retrieved full conversation with {len(messages)} messages')
else:
    print('⚠️  No conversations found in database')
"

if [ $? -eq 0 ]; then
    echo "✅ Database access through GUI modules works"
else
    echo "❌ Database access test failed"
    exit 1
fi

echo
echo "=== All Tests Passed! ==="
echo "🎉 Conversation retrieval functionality is working correctly."
echo "🎉 The run.sh script should be able to start the GUI successfully."
echo
echo "To start the GUI:"
echo "  ./run.sh"
echo
echo "Logs will be written to: logs/gui_startup_and_runtime.log"
