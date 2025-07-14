#!/usr/bin/env python3
"""
Test the new empty search behavior - should show all conversations.
"""

import logging
import sys
from pathlib import Path

# Add src to path for imports
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / "src"))

# Set up logging
log_dir = project_root / "logs"
log_dir.mkdir(exist_ok=True)
log_file = log_dir / "empty_search_shows_all_test.log"

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file, mode='w'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)


def main():
    """Test the empty search shows all conversations behavior."""
    logger.info("=== TESTING EMPTY SEARCH SHOWS ALL CONVERSATIONS ===")
    
    try:
        from PyQt6.QtWidgets import QApplication

        from poe_search.gui.widgets.search_widget import SearchWidget
        from poe_search.storage.database import Database
        
        app = QApplication.instance()
        if app is None:
            app = QApplication([])
        
        logger.info("✓ QApplication created")
        
        # Create database and search widget
        db_file = project_root / "data" / "poe_search.db"
        database = Database(str(db_file))
        search_widget = SearchWidget()
        search_widget.set_database(database)
        
        logger.info("✓ SearchWidget created and database set")
        
        # First, check how many conversations are in the database
        all_conversations = database.get_conversations()
        logger.info(f"Database contains {len(all_conversations)} conversations")
        
        # Test 1: Empty search should show all conversations
        logger.info("Test 1: Empty search query")
        search_widget.search_input.setText("")
        
        # Call show_all_conversations directly
        search_widget.show_all_conversations()
        
        # Check the results table
        table_row_count = search_widget.results_table.rowCount()
        logger.info(f"Results table shows {table_row_count} rows")
        
        # Check the results label
        results_text = search_widget.results_label.text()
        logger.info(f"Results label shows: '{results_text}'")
        
        if table_row_count == len(all_conversations):
            logger.info("✓ Empty search correctly shows all conversations")
            test1_passed = True
        else:
            logger.error(f"✗ Expected {len(all_conversations)} rows, got {table_row_count}")
            test1_passed = False
        
        # Test 2: Empty search via perform_search should also show all
        logger.info("\nTest 2: Empty search via perform_search()")
        search_widget.search_input.setText("   ")  # Whitespace only
        
        # Track if search_requested signal is emitted (it shouldn't be for empty search)
        search_signal_emitted = False
        
        def track_search_signal(params):
            nonlocal search_signal_emitted
            search_signal_emitted = True
            logger.info(f"Search signal emitted: {params}")
        
        search_widget.search_requested.connect(track_search_signal)
        search_widget.perform_search()
        
        # Check results again
        table_row_count2 = search_widget.results_table.rowCount()
        logger.info(f"Results table shows {table_row_count2} rows after perform_search")
        
        if table_row_count2 == len(all_conversations) and not search_signal_emitted:
            logger.info("✓ Empty search via perform_search correctly shows all conversations")
            test2_passed = True
        else:
            logger.error(f"✗ Expected {len(all_conversations)} rows and no signal, got {table_row_count2} rows, signal: {search_signal_emitted}")
            test2_passed = False
        
        # Test 3: Non-empty search should work normally
        logger.info("\nTest 3: Non-empty search should work normally")
        search_widget.search_input.setText("Python")
        
        search_signal_emitted = False
        search_widget.perform_search()
        
        if search_signal_emitted:
            logger.info("✓ Non-empty search correctly emits search signal")
            test3_passed = True
        else:
            logger.error("✗ Non-empty search failed to emit search signal")
            test3_passed = False
        
        # Summary
        logger.info("\n" + "="*50)
        logger.info("TEST RESULTS SUMMARY:")
        logger.info("="*50)
        logger.info(f"Empty search shows all: {'✓ PASS' if test1_passed else '✗ FAIL'}")
        logger.info(f"Empty search via perform_search: {'✓ PASS' if test2_passed else '✗ FAIL'}")
        logger.info(f"Non-empty search works: {'✓ PASS' if test3_passed else '✗ FAIL'}")
        
        all_passed = test1_passed and test2_passed and test3_passed
        
        if all_passed:
            logger.info("🎉 ALL TESTS PASSED!")
            logger.info("Empty search now correctly shows all conversations!")
        else:
            logger.warning("⚠️  Some tests failed.")
        
        return all_passed
        
    except Exception as e:
        logger.error(f"Test FAILED: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return False


if __name__ == "__main__":
    logger.info("Testing empty search shows all conversations behavior...")
    success = main()
    logger.info(f"\nFull log saved to: {log_file}")
    
    if success:
        logger.info("🚀 Search functionality ready for use!")
    else:
        logger.warning("⚠️  Issues found, check logs above.")
