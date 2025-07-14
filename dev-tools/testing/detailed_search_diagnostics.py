#!/usr/bin/env python3
"""
Detailed search diagnostics script to identify why search is not working.
Logs all aspects of the search process to help debug issues.
"""

import logging
import sys
import traceback
from pathlib import Path

# Add src to path for imports
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / "src"))

# Set up logging
log_dir = project_root / "logs"
log_dir.mkdir(exist_ok=True)
log_file = log_dir / "detailed_search_diagnostics.log"

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file, mode='w'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

def test_database_connection():
    """Test database connections and content."""
    logger.info("=== TESTING DATABASE CONNECTION ===")
    
    try:
        from poe_search.storage.database import Database

        # Test all database files
        db_files = [
            project_root / "data" / "poe_search.db",
            project_root / "data" / "my_conversations.db", 
            project_root / "data" / "test_conversations.db"
        ]
        
        for db_file in db_files:
            logger.info(f"Testing database: {db_file}")
            if not db_file.exists():
                logger.warning(f"Database file does not exist: {db_file}")
                continue
                
            try:
                db = Database(str(db_file))
                
                # Get conversation count
                conversations = db.get_conversations()
                logger.info(f"  Found {len(conversations)} conversations")
                
                # Show first few conversations
                for i, conv in enumerate(conversations[:3]):
                    logger.info(f"  Conversation {i+1}: ID={conv.get('id')}, Title='{conv.get('title', 'No title')[:50]}...'")
                
                # Test search functionality
                logger.info("  Testing search functionality...")
                search_results = db.search_conversations("test")
                logger.info(f"  Search for 'test' returned {len(search_results)} results")
                
                search_results = db.search_conversations("hello")
                logger.info(f"  Search for 'hello' returned {len(search_results)} results")
                
                # Show available tables
                import sqlite3
                conn = sqlite3.connect(str(db_file))
                cursor = conn.cursor()
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
                tables = cursor.fetchall()
                logger.info(f"  Available tables: {[table[0] for table in tables]}")
                
                # Check conversations table structure
                if any('conversations' in table[0] for table in tables):
                    cursor.execute("PRAGMA table_info(conversations);")
                    columns = cursor.fetchall()
                    logger.info(f"  Conversations table columns: {[col[1] for col in columns]}")
                    
                    # Get sample data
                    cursor.execute("SELECT COUNT(*) FROM conversations;")
                    count = cursor.fetchone()[0]
                    logger.info(f"  Total conversations in table: {count}")
                    
                    if count > 0:
                        cursor.execute("SELECT id, title, created_at FROM conversations LIMIT 3;")
                        samples = cursor.fetchall()
                        for sample in samples:
                            logger.info(f"  Sample: ID={sample[0]}, Title='{sample[1][:30]}...', Created={sample[2]}")
                
                conn.close()
                
            except Exception as e:
                logger.error(f"  Error testing database {db_file}: {e}")
                logger.error(f"  Traceback: {traceback.format_exc()}")
                
    except Exception as e:
        logger.error(f"Failed to import Database class: {e}")
        logger.error(f"Traceback: {traceback.format_exc()}")

def test_search_workers():
    """Test search worker functionality."""
    logger.info("=== TESTING SEARCH WORKERS ===")
    
    try:
        from PyQt6.QtCore import QObject

        from poe_search.gui.workers.search_worker import SearchWorker

        # Create a mock parent for the worker
        class MockParent(QObject):
            def __init__(self):
                super().__init__()
        
        parent = MockParent()
        
        # Test worker creation
        logger.info("Creating SearchWorker...")
        worker = SearchWorker("test query", parent)
        logger.info("SearchWorker created successfully")
        
        # Test worker run method directly
        logger.info("Testing worker run method...")
        try:
            worker.run()
            logger.info("Worker run method completed")
        except Exception as e:
            logger.error(f"Worker run method failed: {e}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            
    except Exception as e:
        logger.error(f"Failed to test SearchWorker: {e}")
        logger.error(f"Traceback: {traceback.format_exc()}")

def test_gui_components():
    """Test GUI components that handle search."""
    logger.info("=== TESTING GUI COMPONENTS ===")
    
    try:
        from PyQt6.QtWidgets import QApplication

        from poe_search.gui.main_window import MainWindow

        # Create QApplication if it doesn't exist
        app = QApplication.instance()
        if app is None:
            app = QApplication([])
        
        logger.info("Creating MainWindow...")
        window = MainWindow()
        logger.info("MainWindow created successfully")
        
        # Test search method
        logger.info("Testing search method...")
        try:
            window.search("test query")
            logger.info("Search method called successfully")
        except Exception as e:
            logger.error(f"Search method failed: {e}")
            logger.error(f"Traceback: {traceback.format_exc()}")
        
        # Check if workers are properly initialized
        logger.info("Checking worker initialization...")
        if hasattr(window, 'search_worker'):
            logger.info("search_worker attribute exists")
        else:
            logger.warning("search_worker attribute missing")
            
        if hasattr(window, 'categorization_worker'):
            logger.info("categorization_worker attribute exists")
        else:
            logger.warning("categorization_worker attribute missing")
            
        if hasattr(window, 'sync_worker'):
            logger.info("sync_worker attribute exists")
        else:
            logger.warning("sync_worker attribute missing")
        
    except Exception as e:
        logger.error(f"Failed to test GUI components: {e}")
        logger.error(f"Traceback: {traceback.format_exc()}")

def test_imports():
    """Test all required imports."""
    logger.info("=== TESTING IMPORTS ===")
    
    imports_to_test = [
        "poe_search.storage.database",
        "poe_search.gui.main_window", 
        "poe_search.gui.workers.search_worker",
        "poe_search.gui.workers.sync_worker",
        "poe_search.gui.workers.categorization_worker",
        "poe_search.utils.browser_tokens"
    ]
    
    for import_name in imports_to_test:
        try:
            __import__(import_name)
            logger.info(f"✓ Successfully imported {import_name}")
        except Exception as e:
            logger.error(f"✗ Failed to import {import_name}: {e}")

def test_file_structure():
    """Test project file structure."""
    logger.info("=== TESTING FILE STRUCTURE ===")
    
    required_files = [
        "src/poe_search/__init__.py",
        "src/poe_search/gui/__init__.py",
        "src/poe_search/gui/main_window.py",
        "src/poe_search/gui/workers/__init__.py",
        "src/poe_search/gui/workers/search_worker.py",
        "src/poe_search/gui/workers/sync_worker.py",
        "src/poe_search/gui/workers/categorization_worker.py",
        "src/poe_search/storage/__init__.py",
        "src/poe_search/storage/database.py",
        "src/poe_search/utils/__init__.py",
        "src/poe_search/utils/browser_tokens.py"
    ]
    
    for file_path in required_files:
        full_path = project_root / file_path
        if full_path.exists():
            logger.info(f"✓ Found {file_path}")
        else:
            logger.error(f"✗ Missing {file_path}")

def main():
    """Run all diagnostic tests."""
    logger.info("Starting detailed search diagnostics...")
    logger.info(f"Project root: {project_root}")
    logger.info(f"Log file: {log_file}")
    
    test_file_structure()
    test_imports()
    test_database_connection()
    test_search_workers()
    test_gui_components()
    
    logger.info("=== DIAGNOSTICS COMPLETE ===")
    logger.info(f"Full log saved to: {log_file}")

if __name__ == "__main__":
    main()
