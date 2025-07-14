#!/usr/bin/env python3
"""Test SearchWidget show_all_conversations specifically."""

import sys
from pathlib import Path

# Add the src directory to the Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / "src"))

# Set up minimal GUI environment
import os

os.environ['QT_QPA_PLATFORM'] = 'offscreen'  # Run headless

from PyQt6.QtWidgets import QApplication

from poe_search.gui.widgets.search_widget import SearchWidget
from poe_search.storage.database import Database

app = QApplication(sys.argv)

# Initialize database
db_path = project_root / "data" / "poe_search.db" 
database = Database(str(db_path))
conversations = database.get_conversations()
print(f"Database conversations: {len(conversations)}")

# Create SearchWidget
widget = SearchWidget()
widget.set_database(database)

# Test show_all_conversations with debug info
print("Calling show_all_conversations...")

# Before calling, check the initial state
print(f"Initial row count: {widget.results_table.rowCount()}")
print(f"Widget has database: {widget.database is not None}")

# Call the method
widget.show_all_conversations()

# Check the result
final_row_count = widget.results_table.rowCount()
print(f"Final row count: {final_row_count}")

if final_row_count == 0:
    print("WARNING: No conversations were loaded into the table!")
    
    # Let's check the filters
    print(f"Bot filter: {widget.bot_combo.currentText()}")
    print(f"Category filter: {widget.category_combo.currentText()}")
    print(f"Date from: {widget.date_from.date().toPyDate()}")
    print(f"Date to: {widget.date_to.date().toPyDate()}")
else:
    print(f"SUCCESS: {final_row_count} conversations loaded")

sys.exit(0)
