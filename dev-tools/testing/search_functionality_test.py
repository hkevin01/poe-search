#!/usr/bin/env python3
"""Test search with terms that should return results."""

import logging
import sys
from pathlib import Path

# Add src to path for imports
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / "src"))

from poe_search.storage.database import Database

# Set up logging
log_dir = project_root / "logs"
log_dir.mkdir(exist_ok=True)
log_file = log_dir / "search_functionality_test.log"

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
    """Test search functionality with various terms."""
    logger.info("=== TESTING SEARCH FUNCTIONALITY ===")
    
    db_file = project_root / "data" / "poe_search.db"
    db = Database(str(db_file))
    
    # Test various search terms
    search_terms = [
        "Python",
        "React",
        "machine learning",
        "database",
        "FastAPI",
        "components",
        "normalization",
        "hello",
        "development"
    ]
    
    for term in search_terms:
        results = db.search_messages(term)
        logger.info(f"Search for '{term}': {len(results)} results")
        
        # Show first result if any
        if results:
            first_result = results[0]
            content_preview = first_result.get('content', '')[:100] + "..."
            conv_title = first_result.get('conversation_title', 'Unknown')
            logger.info(f"  First result from '{conv_title}': {content_preview}")
    
    # Test conversation listing
    conversations = db.get_conversations()
    logger.info(f"\nTotal conversations: {len(conversations)}")
    for conv in conversations:
        logger.info(f"  - {conv.get('title', 'No title')} ({conv.get('bot', 'Unknown bot')})")
    
    logger.info(f"\n=== SEARCH TESTING COMPLETE - Log: {log_file} ===")


if __name__ == "__main__":
    main()
