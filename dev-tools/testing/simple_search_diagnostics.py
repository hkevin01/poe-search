#!/usr/bin/env python3
"""Simple search diagnostics to identify core issues."""

import logging
import sys
from pathlib import Path

# Add src to path for imports
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / "src"))

# Set up logging
log_dir = project_root / "logs"
log_dir.mkdir(exist_ok=True)
log_file = log_dir / "simple_search_diagnostics.log"

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file, mode='w'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)


def main():
    """Run basic diagnostics."""
    logger.info("=== SIMPLE SEARCH DIAGNOSTICS ===")
    
    # Test database import and connection
    try:
        from poe_search.storage.database import Database
        logger.info("✓ Database class imported successfully")
        
        db_file = project_root / "data" / "poe_search.db"
        if db_file.exists():
            logger.info(f"✓ Database file exists: {db_file}")
            db = Database(str(db_file))
            conversations = db.get_conversations()
            logger.info(f"✓ Found {len(conversations)} conversations")
            
            # Test search messages instead of search_conversations
            results = db.search_messages("test")
            logger.info(f"✓ Search for 'test' returned {len(results)} results")
        else:
            logger.error(f"✗ Database file missing: {db_file}")
            
    except Exception as e:
        logger.error(f"✗ Database test failed: {e}")
    
    # Test GUI imports
    try:
        from poe_search.gui.main_window import MainWindow
        logger.info("✓ MainWindow imported successfully")
    except Exception as e:
        logger.error(f"✗ MainWindow import failed: {e}")
    
    # Test worker imports
    try:
        from poe_search.gui.workers.search_worker import SearchWorker
        logger.info("✓ SearchWorker imported successfully")
    except Exception as e:
        logger.error(f"✗ SearchWorker import failed: {e}")
    
    logger.info(f"=== DIAGNOSTICS COMPLETE - Log: {log_file} ===")


if __name__ == "__main__":
    main()
