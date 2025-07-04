#!/usr/bin/env python3
"""
Simple conversation search functionality test.
"""

import shutil
import sys
import tempfile
from datetime import datetime
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))


def test_basic_functionality():
    """Test basic conversation and search functionality."""
    print("🧪 Testing Basic Conversation Search Functionality")
    print("=" * 60)
    
    try:
        from poe_search.storage.database import Database
        print("✅ Database import successful")
    except ImportError as e:
        print(f"❌ Failed to import Database: {e}")
        return False
    
    # Create temporary database
    temp_dir = tempfile.mkdtemp()
    db_path = Path(temp_dir) / "test.db"
    
    try:
        # Initialize database
        print("📊 Creating test database...")
        db = Database(f"sqlite:///{db_path}")
        print("✅ Database created successfully")
        
        # Test empty database
        print("🔍 Testing empty database...")
        conversations = db.get_conversations()
        assert len(conversations) == 0, (
            "Empty database should return no conversations"
        )
        print("✅ Empty database test passed")
        
        # Create test conversation
        print("💾 Creating test conversation...")
        now = datetime.now()
        test_conversation = {
            "id": "test_001",
            "bot": "test-bot",
            "title": "Test Conversation",
            "created_at": now.isoformat(),
            "updated_at": now.isoformat(),
            "message_count": 2,
            "messages": [
                {
                    "id": "msg_001",
                    "conversation_id": "test_001",
                    "role": "user",
                    "content": "Hello world test message",
                    "timestamp": now.isoformat(),
                    "bot": None
                },
                {
                    "id": "msg_002",
                    "conversation_id": "test_001",
                    "role": "bot",
                    "content": "This is a test response from the bot",
                    "timestamp": now.isoformat(),
                    "bot": "test-bot"
                }
            ]
        }
        
        # Save conversation
        db.save_conversation(test_conversation)
        print("✅ Test conversation saved")
        
        # Test conversation listing
        print("📋 Testing conversation listing...")
        conversations = db.get_conversations()
        assert len(conversations) == 1, "Should have one conversation"
        assert conversations[0]["id"] == "test_001", (
            "Conversation ID should match"
        )
        assert conversations[0]["title"] == "Test Conversation", (
            "Title should match"
        )
        print("✅ Conversation listing test passed")
        
        # Test single conversation retrieval
        print("🔍 Testing single conversation retrieval...")
        conversation = db.get_conversation("test_001")
        assert conversation is not None, "Conversation should exist"
        assert conversation["id"] == "test_001", "ID should match"
        print("✅ Single conversation retrieval test passed")
        
        # Test conversation search
        print("🔎 Testing message search...")
        results = db.search_messages("test")
        assert len(results) >= 1, "Should find at least one message"
        found_test_message = any(
            "test" in result["content"].lower() for result in results
        )
        assert found_test_message, "Should find message containing 'test'"
        print("✅ Message search test passed")
        
        # Test search with no results
        print("🔎 Testing search with no results...")
        no_results = db.search_messages("xyznothingmatches")
        assert len(no_results) == 0, (
            "Should return no results for non-existent term"
        )
        print("✅ No results search test passed")
        
        # Test filtering
        print("🔍 Testing bot filtering...")
        bot_conversations = db.get_conversations(bot="test-bot")
        assert len(bot_conversations) == 1, (
            "Should find one conversation for test-bot"
        )
        print("✅ Bot filtering test passed")
        
        print("\n" + "=" * 60)
        print("🎉 All basic functionality tests passed!")
        print("✅ Conversation listing works")
        print("✅ Message search returns results")
        print("✅ Filtering works correctly")
        print("✅ Edge cases handled properly")
        
        return True
        
    except (AssertionError, ValueError, RuntimeError) as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        # Cleanup
        shutil.rmtree(temp_dir)
        print("🧹 Cleanup completed")


def main():
    """Run the basic functionality test."""
    success = test_basic_functionality()
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
