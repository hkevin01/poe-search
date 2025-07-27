#!/usr/bin/env python3
"""
Test script to verify automatic conversation sync functionality.

This script tests the complete sync workflow including:
1. Direct API client connection
2. Conversation retrieval 
3. Database storage
4. Background sync worker
"""

import sys
import os
import asyncio
import logging
from pathlib import Path

# Add the src directory to the Python path
project_root = Path(__file__).parent.parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_direct_api_client():
    """Test the direct API client functionality."""
    logger.info("=== Testing Direct API Client ===")
    
    try:
        from poe_search.api.direct_client import DirectPoeClient
        from poe_search.utils.browser_tokens import refresh_tokens_if_needed
        
        # Get tokens
        logger.info("Getting authentication tokens...")
        tokens = refresh_tokens_if_needed()
        
        if not tokens:
            logger.error("Failed to get authentication tokens")
            return False
            
        logger.info("Tokens obtained successfully")
        
        # Create client
        client = DirectPoeClient(
            formkey=tokens['formkey'],
            token=tokens['p_b']
        )
        
        # Test connection
        logger.info("Testing connection...")
        if client.test_connection():
            logger.info("✅ Connection test passed")
        else:
            logger.error("❌ Connection test failed")
            return False
            
        # Get conversations
        logger.info("Retrieving conversations...")
        conversations = client.get_conversations(limit=5)
        
        if conversations:
            logger.info(f"✅ Retrieved {len(conversations)} conversations")
            for i, conv in enumerate(conversations[:3]):
                title = conv.get('title', 'Untitled')
                conv_id = conv.get('id', 'Unknown ID')
                logger.info(f"  {i+1}. {title} (ID: {conv_id[:12]}...)")
        else:
            logger.warning("⚠️ No conversations retrieved")
            
        return True
        
    except Exception as e:
        logger.error(f"❌ Direct API client test failed: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False

def test_database_manager():
    """Test the database manager functionality."""
    logger.info("=== Testing Database Manager ===")
    
    try:
        from poe_search.storage.database_manager import DatabaseManager
        
        # Use test database
        test_db_path = project_root / "data" / "test_sync.db"
        test_db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Remove existing test database
        if test_db_path.exists():
            test_db_path.unlink()
            
        db_manager = DatabaseManager(str(test_db_path))
        logger.info("✅ Database manager created")
        
        # Test conversation operations
        test_conv_id = "test_conv_123"
        
        # Test create
        db_manager.create_conversation(
            conversation_id=test_conv_id,
            title="Test Conversation",
            created_at="2024-01-01T00:00:00Z"
        )
        logger.info("✅ Test conversation created")
        
        # Test retrieve
        retrieved = db_manager.get_conversation_by_id(test_conv_id)
        if retrieved:
            logger.info(f"✅ Retrieved conversation: {retrieved['title']}")
        else:
            logger.error("❌ Failed to retrieve test conversation")
            return False
            
        # Test update
        db_manager.update_conversation(
            conversation_id=test_conv_id,
            title="Updated Test Conversation"
        )
        logger.info("✅ Conversation updated")
        
        # Test message operations
        db_manager.create_message(
            message_id="test_msg_123",
            conversation_id=test_conv_id,
            content="This is a test message",
            sender="user"
        )
        logger.info("✅ Test message created")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Database manager test failed: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False

def test_sync_worker():
    """Test the sync worker functionality."""
    logger.info("=== Testing Sync Worker ===")
    
    try:
        import time
        from PyQt6.QtCore import QCoreApplication
        from poe_search.workers.sync_worker import SyncWorker
        from poe_search.storage.database_manager import DatabaseManager
        from poe_search.utils.browser_tokens import refresh_tokens_if_needed
        
        # Create QApplication if needed
        app = QCoreApplication.instance()
        if app is None:
            app = QCoreApplication(sys.argv)
            
        # Get tokens
        tokens = refresh_tokens_if_needed()
        if not tokens:
            logger.error("Failed to get authentication tokens")
            return False
            
        credentials = {
            'formkey': tokens['formkey'],
            'p_b_cookie': tokens['p_b']
        }
        
        # Create database manager
        test_db_path = project_root / "data" / "test_sync_worker.db"
        test_db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Remove existing test database
        if test_db_path.exists():
            test_db_path.unlink()
            
        db_manager = DatabaseManager(str(test_db_path))
        
        # Create sync worker
        sync_worker = SyncWorker(db_manager, credentials)
        
        # Track sync progress
        sync_complete = False
        sync_error = None
        conversations_synced = []
        
        def on_progress(progress):
            logger.info(f"Sync progress: {progress}%")
            
        def on_status(status):
            logger.info(f"Sync status: {status}")
            
        def on_error(error):
            nonlocal sync_error
            sync_error = error
            logger.error(f"Sync error: {error}")
            
        def on_finished():
            nonlocal sync_complete
            sync_complete = True
            logger.info("Sync completed!")
            
        def on_conversation_synced(conversation):
            conversations_synced.append(conversation)
            title = conversation.get('title', 'Untitled')
            logger.info(f"Conversation synced: {title}")
            
        # Connect signals
        sync_worker.progress.connect(on_progress)
        sync_worker.status_update.connect(on_status)
        sync_worker.error.connect(on_error)
        sync_worker.finished.connect(on_finished)
        sync_worker.conversation_synced.connect(on_conversation_synced)
        
        # Start sync
        logger.info("Starting sync worker...")
        sync_worker.start()
        
        # Wait for completion
        timeout = 30  # 30 seconds
        elapsed = 0
        while not sync_complete and sync_error is None and elapsed < timeout:
            app.processEvents()
            time.sleep(0.1)
            elapsed += 0.1
            
        if sync_error:
            logger.error(f"❌ Sync failed: {sync_error}")
            return False
        elif not sync_complete:
            logger.error("❌ Sync timed out")
            sync_worker.stop()
            return False
        else:
            logger.info(f"✅ Sync completed! {len(conversations_synced)} conversations synced")
            return True
            
    except Exception as e:
        logger.error(f"❌ Sync worker test failed: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False

def main():
    """Run all sync tests."""
    logger.info("Starting sync functionality tests...")
    
    results = {
        "Direct API Client": test_direct_api_client(),
        "Database Manager": test_database_manager(),
        "Sync Worker": test_sync_worker()
    }
    
    logger.info("\n=== Test Results ===")
    all_passed = True
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        logger.info(f"{test_name}: {status}")
        if not passed:
            all_passed = False
            
    if all_passed:
        logger.info("\n🎉 All tests passed! Sync functionality is working.")
        return 0
    else:
        logger.error("\n❌ Some tests failed. Check the logs above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
