#!/usr/bin/env python3
"""Test script for database integration and background threading."""

import logging
import sys
import time
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from PyQt6.QtWidgets import QApplication
from poe_search.gui.main_window import MainWindow
from poe_search.storage.database import Database

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def test_database_integration():
    """Test database integration and background threading."""
    logger.info("Starting database integration test")
    
    # Create QApplication
    app = QApplication(sys.argv)
    
    try:
        # Create main window
        logger.info("Creating MainWindow...")
        window = MainWindow()
        
        # Test database initialization
        logger.info("Testing database initialization...")
        assert hasattr(window, 'database'), "MainWindow should have database attribute"
        assert window.database is not None, "Database should be initialized"
        logger.info("✓ Database initialization successful")
        
        # Test resource monitoring
        logger.info("Testing resource monitoring...")
        assert hasattr(window, 'resource_timer'), "Resource timer should be initialized"
        assert hasattr(window, 'memory_threshold'), "Memory threshold should be set"
        assert hasattr(window, 'cpu_threshold'), "CPU threshold should be set"
        logger.info("✓ Resource monitoring setup successful")
        
        # Test logging methods
        logger.info("Testing logging methods...")
        window.log_operation_start("test_operation")
        time.sleep(0.1)  # Small delay to simulate work
        window.log_operation_end("test_operation", success=True)
        logger.info("✓ Logging methods work correctly")
        
        # Test database operations
        logger.info("Testing database operations...")
        conversations = window.database.get_conversations()
        logger.info(f"✓ Retrieved {len(conversations)} conversations from database")
        
        # Test widget database setup
        logger.info("Testing widget database setup...")
        window.setup_widgets_database()
        logger.info("✓ Widget database setup completed")
        
        # Test search functionality (without actual search)
        logger.info("Testing search functionality...")
        search_params = {
            "query": "",
            "bot": None,
            "category": None,
            "date_from": None,
            "date_to": None,
            "use_regex": False,
            "case_sensitive": False
        }
        window.perform_search(search_params)
        logger.info("✓ Search functionality test completed")
        
        logger.info("All tests passed successfully!")
        
        # Show window briefly
        window.show()
        logger.info("Window displayed successfully")
        
        # Run for a few seconds to test resource monitoring
        logger.info("Running for 5 seconds to test resource monitoring...")
        app.exec()
        
    except Exception as e:
        logger.error(f"Test failed: {e}")
        raise
    finally:
        logger.info("Test completed")


if __name__ == "__main__":
    test_database_integration() 