#!/usr/bin/env python3
"""Test if SearchWidget is properly loading conversations from the database."""

import sys
from pathlib import Path

# Add the src directory to the Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / "src"))

def test_search_widget_database():
    """Test SearchWidget database connection."""
    from PyQt6.QtWidgets import QApplication

    from poe_search.gui.widgets.search_widget import SearchWidget
    from poe_search.storage.database import Database

    # Create minimal Qt application
    if not QApplication.instance():
        app = QApplication(sys.argv)
    
    # Initialize database with the same path as GUI
    db_path = project_root / "data" / "poe_search.db"
    database = Database(str(db_path))
    
    print(f"Database path: {db_path}")
    print(f"Database exists: {db_path.exists()}")
    
    # Check database contents
    conversations = database.get_conversations()
    print(f"Total conversations in database: {len(conversations)}")
    
    if conversations:
        print("Sample conversations:")
        for i, conv in enumerate(conversations[:3]):
            title = conv.get('title', 'Unknown') if isinstance(conv, dict) else conv.title
            conv_id = conv.get('id', 'Unknown') if isinstance(conv, dict) else conv.id
            print(f"  {i+1}. {title} (ID: {conv_id})")
    
    # Create SearchWidget
    search_widget = SearchWidget()
    search_widget.set_database(database)
    
    print(f"\nSearchWidget database set: {search_widget.database is not None}")
    
    # Test show_all_conversations
    print("Testing show_all_conversations...")
    search_widget.show_all_conversations()
    
    # Check if conversations were loaded into the widget
    row_count = search_widget.results_table.rowCount()
    print(f"Results table row count: {row_count}")
    
    if row_count > 0:
        print("Conversations successfully loaded into SearchWidget!")
        for row in range(min(3, row_count)):
            title_item = search_widget.results_table.item(row, 1)  # Title column
            if title_item:
                print(f"  Row {row}: {title_item.text()}")
    else:
        print("No conversations loaded into SearchWidget - there's an issue!")
    
    return row_count > 0

if __name__ == "__main__":
    success = test_search_widget_database()
    sys.exit(0 if success else 1)
