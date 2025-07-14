#!/usr/bin/env python3
"""Test GUI search functionality with sample data."""

import logging
import sys
from pathlib import Path

# Add src to path for imports  
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / "src"))

# Set up logging
log_dir = project_root / "logs"
log_dir.mkdir(exist_ok=True)
log_file = log_dir / "gui_search_test.log"

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
    """Test GUI search functionality."""
    logger.info("=== TESTING GUI SEARCH FUNCTIONALITY ===")
    
    try:
        from PyQt6.QtCore import QObject
        from PyQt6.QtWidgets import QApplication

        from poe_search.gui.workers.search_worker import SearchWorker

        # Create QApplication
        app = QApplication.instance()
        if app is None:
            app = QApplication([])
        
        logger.info("✓ PyQt6 Application created")
        
        # Create a mock parent for the worker
        class MockParent(QObject):
            def __init__(self):
                super().__init__()
        
        parent = MockParent()
        
        # Test SearchWorker with a query that should return results
        from poe_search.storage.database import Database

        # Create database instance
        db_file = project_root / "data" / "poe_search.db"
        database = Database(str(db_file))
        
        search_params = {
            "query": "Python",
            "bot": None,
            "limit": 10
        }
        
        logger.info("Creating SearchWorker with 'Python' query...")
        worker = SearchWorker(search_params, database)
        logger.info("✓ SearchWorker created successfully")
        
        # Connect signals to capture results
        results_captured = []
        
        def capture_results(results):
            results_captured.extend(results)
            logger.info(f"✓ Captured {len(results)} search results")
            for i, result in enumerate(results[:3]):  # Show first 3
                title = result.get('conversation_title', 'Unknown')
                content = result.get('content', '')[:50] + "..."
                logger.info(f"  Result {i+1}: {title} - {content}")
        
        def capture_error(error):
            logger.error(f"✗ Search error: {error}")
        
        worker.results_ready.connect(capture_results)
        worker.error.connect(capture_error)
        
        # Run worker
        logger.info("Running search worker...")
        worker.run()
        
        if results_captured:
            logger.info(f"✓ GUI search test SUCCESS: {len(results_captured)} results found")
        else:
            logger.warning("✗ GUI search test FAILED: No results captured")
        
    except Exception as e:
        logger.error(f"✗ GUI search test FAILED: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
    
    logger.info(f"=== GUI SEARCH TEST COMPLETE - Log: {log_file} ===")


if __name__ == "__main__":
    main()
