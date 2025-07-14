#!/usr/bin/env python3
"""Import real Poe.com conversation data from JSON export into the database."""

import json
import sys
from pathlib import Path

# Add the src directory to the Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / "src"))

from poe_search.storage.database import Database


def import_real_conversations():
    """Import real Poe.com conversations from JSON export."""
    
    # Paths
    json_file = project_root / "data" / "my_conversations_20250630_225441.json"
    db_file = project_root / "data" / "poe_search.db"
    
    print(f"Importing real conversations from: {json_file}")
    print(f"Into database: {db_file}")
    
    # Load the JSON export
    if not json_file.exists():
        print(f"ERROR: JSON export file not found: {json_file}")
        return False
    
    with open(json_file, 'r') as f:
        conversations = json.load(f)
    
    print(f"Found {len(conversations)} conversations in export")
    
    # Initialize database
    database = Database(str(db_file))
    
    # Import conversations
    imported_count = 0
    for conv in conversations:
        try:
            # The save_conversation method expects Poe.com API format
            # The JSON export should already be in the right format
            database.save_conversation(conv)
            imported_count += 1
            
        except Exception as e:
            print(f"Failed to import conversation {conv.get('id', 'unknown')}: {e}")
    
    # Note: save_conversation handles its own commits, no need to manually commit
    
    print(f"Successfully imported {imported_count} real conversations")
    
    # Verify import
    stored_conversations = database.get_conversations()
    print(f"Database now contains {len(stored_conversations)} conversations")
    
    # Show sample titles
    if stored_conversations:
        print("\nSample conversation titles:")
        for i, conv in enumerate(stored_conversations[:5]):
            title = conv.get('title', 'No title')
            bot = conv.get('bot', 'Unknown bot')
            print(f"  {i+1}. \"{title}\" (Bot: {bot})")
    
    return True


if __name__ == "__main__":
    success = import_real_conversations()
    sys.exit(0 if success else 1)
