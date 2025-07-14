#!/usr/bin/env python3
"""
Comprehensive test to identify why search is failing in the GUI.
This will test both the search functionality and the GUI integration.
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
log_file = log_dir / "search_failure_diagnosis.log"

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file, mode='w'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)


def test_database_search():
    """Test database search functionality directly."""
    logger.info("=== TESTING DATABASE SEARCH DIRECTLY ===")
    
    try:
        from poe_search.storage.database import Database
        
        db_file = project_root / "data" / "poe_search.db"
        db = Database(str(db_file))
        
        # Test with non-empty queries
        test_queries = ["Python", "React", "machine learning", "database"]
        
        for query in test_queries:
            results = db.search_messages(query)
            logger.info(f"Direct DB search for '{query}': {len(results)} results")
            
            if results:
                first_result = results[0]
                logger.info(f"  Sample result: {first_result.get('content', '')[:50]}...")
        
        # Test conversations
        conversations = db.get_conversations()
        logger.info(f"Total conversations in database: {len(conversations)}")
        
        return True
        
    except Exception as e:
        logger.error(f"Database search test FAILED: {e}")
        return False


def test_search_widget():
    """Test the search widget functionality."""
    logger.info("=== TESTING SEARCH WIDGET ===")
    
    try:
        from PyQt6.QtWidgets import QApplication

        from poe_search.gui.widgets.search_widget import SearchWidget
        from poe_search.storage.database import Database
        
        app = QApplication.instance()
        if app is None:
            app = QApplication([])
        
        logger.info("✓ QApplication created")
        
        # Create database instance
        db_file = project_root / "data" / "poe_search.db"
        database = Database(str(db_file))
        
        # Create search widget
        search_widget = SearchWidget()
        search_widget.set_database(database)
        logger.info("✓ SearchWidget created and database set")
        
        # Test search parameters extraction
        search_params = search_widget.get_search_params()
        logger.info(f"Default search params: {search_params}")
        
        # Test manual search with parameters
        manual_params = {
            'query': 'Python',
            'bot': None,
            'category': None,
            'date_from': None,
            'date_to': None,
            'use_regex': False,
            'case_sensitive': False
        }
        
        logger.info(f"Testing search with manual params: {manual_params}")
        
        # Check if there's a perform_search method
        if hasattr(search_widget, 'perform_search'):
            logger.info("SearchWidget has perform_search method")
        else:
            logger.warning("SearchWidget missing perform_search method")
        
        # Check if there's a search method
        if hasattr(search_widget, 'search'):
            logger.info("SearchWidget has search method")
        else:
            logger.warning("SearchWidget missing search method")
        
        return True
        
    except Exception as e:
        logger.error(f"Search widget test FAILED: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return False


def test_search_worker():
    """Test the search worker functionality."""
    logger.info("=== TESTING SEARCH WORKER ===")
    
    try:
        from PyQt6.QtWidgets import QApplication

        from poe_search.gui.workers.search_worker import SearchWorker
        from poe_search.storage.database import Database
        
        app = QApplication.instance()
        if app is None:
            app = QApplication([])
        
        # Create database instance
        db_file = project_root / "data" / "poe_search.db"
        database = Database(str(db_file))
        
        # Test with non-empty search parameters
        search_params = {
            'query': 'Python',
            'bot': None,
            'limit': 10
        }
        
        logger.info(f"Creating SearchWorker with params: {search_params}")
        worker = SearchWorker(search_params, database)
        
        # Capture results
        results_captured = []
        errors_captured = []
        
        def capture_results(results):
            results_captured.extend(results)
            logger.info(f"✓ SearchWorker returned {len(results)} results")
            for i, result in enumerate(results[:2]):
                content = result.get('content', '')[:50] + "..."
                logger.info(f"  Result {i+1}: {content}")
        
        def capture_error(error):
            errors_captured.append(error)
            logger.error(f"✗ SearchWorker error: {error}")
        
        worker.results_ready.connect(capture_results)
        worker.error.connect(capture_error)
        
        # Run the worker
        logger.info("Running SearchWorker...")
        worker.run()
        
        if results_captured:
            logger.info(f"✓ SearchWorker test SUCCESS: {len(results_captured)} results")
            return True
        elif errors_captured:
            logger.error(f"✗ SearchWorker test FAILED with errors: {errors_captured}")
            return False
        else:
            logger.warning("✗ SearchWorker test returned no results and no errors")
            return False
        
    except Exception as e:
        logger.error(f"Search worker test FAILED: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return False


def test_empty_query_behavior():
    """Test what happens when searching with empty query."""
    logger.info("=== TESTING EMPTY QUERY BEHAVIOR ===")
    
    try:
        from poe_search.storage.database import Database
        
        db_file = project_root / "data" / "poe_search.db"
        db = Database(str(db_file))
        
        # Test empty query
        empty_results = db.search_messages("")
        logger.info(f"Empty query search results: {len(empty_results)}")
        
        # Test whitespace query
        whitespace_results = db.search_messages("   ")
        logger.info(f"Whitespace query search results: {len(whitespace_results)}")
        
        # Test None query
        try:
            none_results = db.search_messages(None)
            logger.info(f"None query search results: {len(none_results)}")
        except Exception as e:
            logger.info(f"None query throws exception (expected): {e}")
        
        return True
        
    except Exception as e:
        logger.error(f"Empty query test FAILED: {e}")
        return False


def main():
    """Run all diagnostic tests."""
    logger.info("=" * 60)
    logger.info("SEARCH FAILURE DIAGNOSIS - COMPREHENSIVE TESTING")
    logger.info("=" * 60)
    
    tests = [
        ("Database Search", test_database_search),
        ("Search Widget", test_search_widget),
        ("Search Worker", test_search_worker),
        ("Empty Query Behavior", test_empty_query_behavior)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        logger.info(f"\n{'='*20} {test_name} {'='*20}")
        try:
            results[test_name] = test_func()
        except Exception as e:
            logger.error(f"Test '{test_name}' crashed: {e}")
            results[test_name] = False
    
    # Summary
    logger.info(f"\n{'='*60}")
    logger.info("TEST RESULTS SUMMARY:")
    logger.info(f"{'='*60}")
    
    for test_name, passed in results.items():
        status = "✓ PASS" if passed else "✗ FAIL"
        logger.info(f"{test_name}: {status}")
    
    passed_tests = sum(results.values())
    total_tests = len(results)
    
    logger.info(f"\nOverall: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        logger.info("🎉 All tests passed! Search should be working.")
    else:
        logger.warning("⚠️  Some tests failed. Check individual test results above.")
    
    logger.info(f"\nFull log saved to: {log_file}")


if __name__ == "__main__":
    main()
