#!/usr/bin/env python3
"""Debug the SearchWidget database connection issue."""

import sys
from pathlib import Path

# Add the src directory to the Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / "src"))

def debug_search_widget():
    """Debug SearchWidget database issues."""
    import logging

    # Set up logging to see all messages
    logging.basicConfig(level=logging.DEBUG, format='%(name)s - %(levelname)s - %(message)s')
    
    from PyQt6.QtWidgets import QApplication

    from poe_search.storage.database import Database
    
    app = QApplication(sys.argv)
    
    # Test database directly first
    db_path = project_root / "data" / "poe_search.db"
    print(f"Database path: {db_path}")
    print(f"Database exists: {db_path.exists()}")
    
    database = Database(str(db_path))
    conversations = database.get_conversations()
    print(f"Direct database access - conversations: {len(conversations)}")
    
    # Now test SearchWidget
    from poe_search.gui.widgets.search_widget import SearchWidget
    
    print("\nCreating SearchWidget...")
    search_widget = SearchWidget()
    
    print("Setting database...")
    search_widget.set_database(database)
    
    print(f"SearchWidget has database: {search_widget.database is not None}")
    
    # Check results table
    print(f"Results table row count: {search_widget.results_table.rowCount()}")
    
    # Manually call show_all_conversations to see what happens
    print("\nManually calling show_all_conversations...")
    try:
        search_widget.show_all_conversations()
        print(f"After show_all_conversations - row count: {search_widget.results_table.rowCount()}")
    except Exception as e:
        print(f"Error in show_all_conversations: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_search_widget()
