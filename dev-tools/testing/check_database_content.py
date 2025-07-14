#!/usr/bin/env python3
"""
Check actual database content and search functionality.
"""

import logging
import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

# Setup logging
LOG_DIR = PROJECT_ROOT / "logs"
LOG_DIR.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(LOG_DIR / "database_content_check.log")
    ]
)

logger = logging.getLogger(__name__)


def check_database_content(db_path):
    """Check content of a specific database."""
    logger.info(f"\n🔍 Checking database: {db_path}")
    
    if not db_path.exists():
        logger.warning(f"❌ Database file not found: {db_path}")
        return
    
    try:
        from poe_search.storage.database import Database

        # Create database connection
        db = Database(f"sqlite:///{db_path}")
        
        # Get database size
        size_mb = db_path.stat().st_size / (1024 * 1024)
        logger.info(f"📁 Database size: {size_mb:.2f} MB")
        
        # Check conversations
        conversations = db.get_conversations()
        logger.info(f"📋 Conversations: {len(conversations)}")
        
        if len(conversations) > 0:
            logger.info("   Recent conversations:")
            for i, conv in enumerate(conversations[:5]):
                logger.info(f"     {i+1}. {conv['id']} - {conv['title']} ({conv['bot']})")
        
        # Check messages
        with db._get_connection() as conn:
            cursor = conn.execute("SELECT COUNT(*) FROM messages")
            message_count = cursor.fetchone()[0]
            logger.info(f"💬 Messages: {message_count}")
            
            # Check FTS table
            cursor = conn.execute("SELECT COUNT(*) FROM messages_fts")
            fts_count = cursor.fetchone()[0]
            logger.info(f"🔎 FTS entries: {fts_count}")
        
        # Test search if there's data
        if message_count > 0:
            logger.info("🔎 Testing search functionality:")
            
            # Test common search terms
            search_terms = ["the", "how", "what", "python", "help", "can", "you"]
            
            for term in search_terms:
                try:
                    results = db.search_messages(term, limit=5)
                    if len(results) > 0:
                        logger.info(f"   '{term}': {len(results)} results")
                        # Show first result snippet
                        first_result = results[0]['content'][:100]
                        logger.info(f"     Example: {first_result}...")
                        break
                except Exception as e:
                    logger.error(f"   Search failed for '{term}': {e}")
            
            # Test broader search
            try:
                all_results = db.search_messages("*", limit=10)
                logger.info(f"   Wildcard search: {len(all_results)} results")
            except Exception as e:
                logger.error(f"   Wildcard search failed: {e}")
        
        # Check bots
        bots = db.get_bots()
        logger.info(f"🤖 Bots: {len(bots)}")
        for bot in bots:
            logger.info(f"     - {bot['name']}: {bot['conversation_count']} conversations")
        
    except Exception as e:
        logger.error(f"❌ Error checking database {db_path}: {e}")
        logger.exception("Full error:")


def main():
    """Check all database files."""
    logger.info("🔍 CHECKING ALL DATABASE FILES")
    logger.info("=" * 60)
    
    # Database files to check
    db_files = [
        PROJECT_ROOT / "poe_search.db",
        PROJECT_ROOT / "data" / "poe_search.db", 
        PROJECT_ROOT / "data" / "my_conversations.db",
        PROJECT_ROOT / "data" / "test_conversations.db"
    ]
    
    for db_path in db_files:
        check_database_content(db_path)
    
    logger.info("\n" + "=" * 60)
    logger.info("DATABASE CONTENT CHECK COMPLETED")
    
    # Check which database the GUI is actually using
    logger.info("\n🖥️ Checking GUI database configuration...")
    try:
        from poe_search.utils.config import load_config
        config = load_config()
        gui_db_url = config.database_url
        logger.info(f"GUI database URL: {gui_db_url}")
        
        # Extract path from URL
        if gui_db_url.startswith("sqlite:///"):
            gui_db_path = Path(gui_db_url[10:])  # Remove "sqlite:///"
            if not gui_db_path.is_absolute():
                gui_db_path = PROJECT_ROOT / gui_db_path
            
            logger.info(f"GUI database path: {gui_db_path}")
            check_database_content(gui_db_path)
        
    except Exception as e:
        logger.error(f"❌ Error checking GUI database config: {e}")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
