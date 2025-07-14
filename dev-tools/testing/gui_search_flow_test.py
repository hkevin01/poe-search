#!/usr/bin/env python3
"""
Test the complete search flow in the GUI to verify the fixes work.
This simulates a user entering a search term and executing the search.
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
log_file = log_dir / "gui_search_flow_test.log"

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
    """Test the complete search flow."""
    logger.info("=== TESTING COMPLETE GUI SEARCH FLOW ===")
    
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
        
        # Simulate user entering search text
        search_widget.search_input.setText("Python")
        logger.info("✓ Search input set to 'Python'")
        
        # Get search parameters to verify they're correct
        params = search_widget.get_search_params()
        logger.info(f"✓ Search parameters: {params}")
        
        # Verify the query is not empty
        if params['query']:
            logger.info(f"✓ Query is not empty: '{params['query']}'")
        else:
            logger.error("✗ Query is empty!")
            return False
        
        # Capture search request signal
        search_params_captured = None
        
        def capture_search_request(params):
            nonlocal search_params_captured
            search_params_captured = params
            logger.info(f"✓ Search request signal captured: {params}")
        
        search_widget.search_requested.connect(capture_search_request)
        
        # Simulate user clicking search button
        logger.info("Simulating search button click...")
        search_widget.perform_search()
        
        # Verify the search request was emitted
        if search_params_captured:
            logger.info("✓ Search request signal was emitted successfully")
            logger.info(f"  Query: '{search_params_captured['query']}'")
            logger.info(f"  Bot filter: {search_params_captured['bot']}")
            return True
        else:
            logger.error("✗ Search request signal was NOT emitted")
            return False
        
    except Exception as e:
        logger.error(f"GUI search flow test FAILED: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return False


def test_empty_query_handling():
    """Test that empty queries are handled properly."""
    logger.info("=== TESTING EMPTY QUERY HANDLING IN GUI ===")
    
    try:
        from PyQt6.QtWidgets import QApplication

        from poe_search.gui.widgets.search_widget import SearchWidget
        from poe_search.storage.database import Database
        
        app = QApplication.instance()
        if app is None:
            app = QApplication([])
        
        # Create search widget
        db_file = project_root / "data" / "poe_search.db"
        database = Database(str(db_file))
        search_widget = SearchWidget()
        search_widget.set_database(database)
        
        # Test empty query
        search_widget.search_input.setText("")
        logger.info("Testing empty query...")
        
        # This should not emit search_requested signal
        search_emitted = False
        
        def capture_search(params):
            nonlocal search_emitted
            search_emitted = True
        
        search_widget.search_requested.connect(capture_search)
        search_widget.perform_search()
        
        if not search_emitted:
            logger.info("✓ Empty query correctly prevented search emission")
            return True
        else:
            logger.error("✗ Empty query incorrectly triggered search")
            return False
        
    except Exception as e:
        logger.error(f"Empty query test FAILED: {e}")
        return False


if __name__ == "__main__":
    logger.info("Starting GUI search flow tests...")
    
    test1_passed = main()
    test2_passed = test_empty_query_handling()
    
    logger.info("\n" + "="*50)
    logger.info("FINAL TEST RESULTS:")
    logger.info("="*50)
    logger.info(f"GUI Search Flow: {'✓ PASS' if test1_passed else '✗ FAIL'}")
    logger.info(f"Empty Query Handling: {'✓ PASS' if test2_passed else '✗ FAIL'}")
    
    if test1_passed and test2_passed:
        logger.info("🎉 ALL GUI SEARCH TESTS PASSED!")
        logger.info("Search functionality should now work correctly in the GUI.")
    else:
        logger.warning("⚠️  Some tests failed. Check logs above.")
    
    logger.info(f"\nFull log saved to: {log_file}")
