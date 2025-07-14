#!/usr/bin/env python3
"""
Search diagnostics script to identify and log search issues.
"""

import logging
import shutil
import sys
import tempfile
from datetime import datetime
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

# Configure detailed logging
LOG_DIR = PROJECT_ROOT / "logs"
LOG_DIR.mkdir(exist_ok=True)

# Setup detailed logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(LOG_DIR / "search_diagnostics.log"),
        logging.FileHandler(LOG_DIR / "search_diagnostics_detailed.log")
    ]
)

logger = logging.getLogger(__name__)


def diagnose_search_functionality():
    """Comprehensive search functionality diagnosis."""
    logger.info("=" * 80)
    logger.info("SEARCH FUNCTIONALITY DIAGNOSTICS")
    logger.info("=" * 80)
    logger.info(f"Timestamp: {datetime.now()}")
    
    try:
        # Test 1: Import database module
        logger.info("TEST 1: Database module import")
        from poe_search.storage.database import Database
        logger.info("✅ Database module imported successfully")
        
        # Test 2: Create temporary database
        logger.info("TEST 2: Database creation")
        temp_dir = tempfile.mkdtemp()
        db_path = Path(temp_dir) / "test_search.db"
        db = Database(f"sqlite:///{db_path}")
        logger.info("✅ Database created successfully")
        
        # Test 3: Check database tables
        logger.info("TEST 3: Database schema verification")
        with db._get_connection() as conn:
            cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]
            logger.info(f"Tables found: {tables}")
            
            if "conversations" not in tables:
                logger.error("❌ conversations table missing")
                return False
            if "messages" not in tables:
                logger.error("❌ messages table missing")
                return False
            if "messages_fts" not in tables:
                logger.error("❌ messages_fts table missing")
                return False
            
        logger.info("✅ Database schema is correct")
        
        # Test 4: Create test data
        logger.info("TEST 4: Creating test conversation data")
        now = datetime.now()
        test_conversation = {
            "id": "diag_test_001",
            "bot": "test-bot",
            "title": "Search Diagnostics Test",
            "created_at": now.isoformat(),
            "updated_at": now.isoformat(),
            "message_count": 3,
            "messages": [
                {
                    "id": "diag_msg_001",
                    "conversation_id": "diag_test_001",
                    "role": "user",
                    "content": "This is a test message for search diagnostics",
                    "timestamp": now.isoformat(),
                    "bot": None
                },
                {
                    "id": "diag_msg_002",
                    "conversation_id": "diag_test_001",
                    "role": "bot",
                    "content": "This is a diagnostic response containing keywords: python programming search test",
                    "timestamp": now.isoformat(),
                    "bot": "test-bot"
                },
                {
                    "id": "diag_msg_003",
                    "conversation_id": "diag_test_001",
                    "role": "user",
                    "content": "Another test message with different keywords: javascript debugging help",
                    "timestamp": now.isoformat(),
                    "bot": None
                }
            ]
        }
        
        # Save test conversation
        db.save_conversation(test_conversation)
        logger.info("✅ Test conversation saved successfully")
        
        # Test 5: Basic conversation listing
        logger.info("TEST 5: Conversation listing")
        conversations = db.get_conversations()
        logger.info(f"Found {len(conversations)} conversations")
        if len(conversations) == 0:
            logger.error("❌ No conversations found")
            return False
        
        for conv in conversations:
            logger.info(f"  - Conversation: {conv['id']} - {conv['title']}")
        logger.info("✅ Conversation listing works")
        
        # Test 6: FTS table population
        logger.info("TEST 6: FTS table population check")
        with db._get_connection() as conn:
            cursor = conn.execute("SELECT COUNT(*) FROM messages_fts")
            fts_count = cursor.fetchone()[0]
            logger.info(f"FTS table has {fts_count} entries")
            
            if fts_count == 0:
                logger.warning("⚠️ FTS table is empty - this could cause search issues")
                # Try to manually populate FTS
                logger.info("Attempting to populate FTS table...")
                cursor.execute("""
                    INSERT INTO messages_fts (message_id, content, conversation_id, bot)
                    SELECT id, content, conversation_id, bot FROM messages
                """)
                conn.commit()
                
                cursor = conn.execute("SELECT COUNT(*) FROM messages_fts")
                fts_count = cursor.fetchone()[0]
                logger.info(f"FTS table now has {fts_count} entries")
        
        # Test 7: Search functionality
        logger.info("TEST 7: Search functionality testing")
        
        # Test basic search
        search_terms = ["test", "diagnostic", "python", "javascript", "programming"]
        for term in search_terms:
            try:
                logger.info(f"Searching for: '{term}'")
                results = db.search_messages(term)
                logger.info(f"  Found {len(results)} results for '{term}'")
                
                for i, result in enumerate(results[:3]):  # Show first 3 results
                    logger.info(f"    {i+1}. {result.get('content', '')[:100]}...")
                    
            except Exception as e:
                logger.error(f"❌ Search failed for '{term}': {e}")
                logger.exception("Full error:")
        
        # Test 8: Search with filters
        logger.info("TEST 8: Search with filters")
        try:
            filtered_results = db.search_messages("test", bot="test-bot")
            logger.info(f"Filtered search found {len(filtered_results)} results")
        except Exception as e:
            logger.error(f"❌ Filtered search failed: {e}")
            logger.exception("Full error:")
        
        # Test 9: Check actual database file location
        logger.info("TEST 9: Database file location check")
        default_db_path = PROJECT_ROOT / "poe_search.db"
        data_db_path = PROJECT_ROOT / "data" / "poe_search.db"
        
        for db_path_check in [default_db_path, data_db_path]:
            if db_path_check.exists():
                logger.info(f"Found database file: {db_path_check}")
                logger.info(f"  Size: {db_path_check.stat().st_size} bytes")
                
                # Check real database content
                real_db = Database(f"sqlite:///{db_path_check}")
                real_conversations = real_db.get_conversations()
                logger.info(f"  Real database has {len(real_conversations)} conversations")
                
                # Try search on real database
                try:
                    real_search_results = real_db.search_messages("the")
                    logger.info(f"  Real database search returned {len(real_search_results)} results")
                except Exception as e:
                    logger.error(f"  Real database search failed: {e}")
            else:
                logger.info(f"Database file not found: {db_path_check}")
        
        # Test 10: GUI database connection
        logger.info("TEST 10: GUI database connection test")
        try:
            from poe_search.utils.config import load_config
            config = load_config()
            logger.info(f"Config loaded: {config}")
            
            # Check database URL from config
            if hasattr(config, 'database') and hasattr(config.database, 'url'):
                gui_db_url = config.database.url
                logger.info(f"GUI database URL: {gui_db_url}")
                
                gui_db = Database(gui_db_url)
                gui_conversations = gui_db.get_conversations()
                logger.info(f"GUI database has {len(gui_conversations)} conversations")
                
        except Exception as e:
            logger.error(f"❌ GUI database connection test failed: {e}")
            logger.exception("Full error:")
        
        logger.info("=" * 80)
        logger.info("DIAGNOSTICS COMPLETED")
        logger.info("=" * 80)
        
        return True
        
    except Exception as e:
        logger.error(f"❌ CRITICAL ERROR during diagnostics: {e}")
        logger.exception("Full error:")
        return False
        
    finally:
        # Cleanup
        try:
            shutil.rmtree(temp_dir, ignore_errors=True)
            logger.info("🧹 Cleanup completed")
        except:
            pass


def main():
    """Run search diagnostics."""
    print("🔍 Starting Search Functionality Diagnostics...")
    print(f"📁 Logs will be saved to: {LOG_DIR}")
    
    success = diagnose_search_functionality()
    
    if success:
        print("\n✅ Diagnostics completed successfully!")
        print(f"📋 Check the detailed logs in: {LOG_DIR}/search_diagnostics.log")
    else:
        print("\n❌ Diagnostics found issues!")
        print(f"📋 Check the error logs in: {LOG_DIR}/search_diagnostics.log")
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
