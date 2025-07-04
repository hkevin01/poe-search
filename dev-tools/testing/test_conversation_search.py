#!/usr/bin/env python3
"""
Comprehensive test to verify conversation search and retrieval functionality.
"""

import json
import os
import sys
import tempfile
from datetime import datetime, timedelta

# Add project paths
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
src_path = os.path.join(project_root, 'src')
utils_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'utilities')
sys.path.insert(0, src_path)
sys.path.insert(0, utils_path)

def ensure_dependencies():
    """Ensure required dependencies are available."""
    try:
        from auto_installer import ensure_database_dependencies
        print("Checking database dependencies...")
        return ensure_database_dependencies()
    except ImportError:
        print("Auto-installer not available, proceeding...")
        return True

def create_test_data():
    """Create sample conversation data for testing."""
    now = datetime.now()
    
    test_conversations = [
        {
            "id": "conv_001",
            "bot": "claude-3-5-sonnet",
            "title": "Python Programming Help",
            "created_at": (now - timedelta(days=1)).isoformat(),
            "updated_at": (now - timedelta(days=1)).isoformat(),
            "message_count": 4,
            "data": json.dumps({"tags": ["programming", "python"]})
        },
        {
            "id": "conv_002", 
            "bot": "chinchilla",
            "title": "Recipe for Chocolate Cake",
            "created_at": (now - timedelta(days=2)).isoformat(),
            "updated_at": (now - timedelta(days=2)).isoformat(),
            "message_count": 6,
            "data": json.dumps({"tags": ["cooking", "dessert"]})
        },
        {
            "id": "conv_003",
            "bot": "a2",
            "title": "Machine Learning Concepts",
            "created_at": (now - timedelta(days=3)).isoformat(),
            "updated_at": (now - timedelta(days=3)).isoformat(),
            "message_count": 8,
            "data": json.dumps({"tags": ["ai", "learning"]})
        }
    ]
    
    test_messages = [
        # Conv 1 messages
        {
            "id": "msg_001",
            "conversation_id": "conv_001",
            "role": "user",
            "content": "Can you help me with Python list comprehensions?",
            "timestamp": (now - timedelta(days=1, hours=2)).isoformat(),
            "bot": "claude-3-5-sonnet",
            "data": json.dumps({})
        },
        {
            "id": "msg_002",
            "conversation_id": "conv_001", 
            "role": "bot",
            "content": "Of course! List comprehensions are a concise way to create lists in Python.",
            "timestamp": (now - timedelta(days=1, hours=2, minutes=1)).isoformat(),
            "bot": "claude-3-5-sonnet",
            "data": json.dumps({})
        },
        # Conv 2 messages
        {
            "id": "msg_003",
            "conversation_id": "conv_002",
            "role": "user", 
            "content": "I need a recipe for chocolate cake",
            "timestamp": (now - timedelta(days=2, hours=1)).isoformat(),
            "bot": "chinchilla",
            "data": json.dumps({})
        },
        {
            "id": "msg_004",
            "conversation_id": "conv_002",
            "role": "bot",
            "content": "Here's a delicious chocolate cake recipe with ingredients and instructions.",
            "timestamp": (now - timedelta(days=2, hours=1, minutes=1)).isoformat(),
            "bot": "chinchilla",
            "data": json.dumps({})
        },
        # Conv 3 messages
        {
            "id": "msg_005",
            "conversation_id": "conv_003",
            "role": "user",
            "content": "Explain neural networks to me",
            "timestamp": (now - timedelta(days=3, hours=1)).isoformat(),
            "bot": "a2",
            "data": json.dumps({})
        },
        {
            "id": "msg_006",
            "conversation_id": "conv_003",
            "role": "bot",
            "content": "Neural networks are computational models inspired by biological neural networks.",
            "timestamp": (now - timedelta(days=3, hours=1, minutes=1)).isoformat(),
            "bot": "a2",
            "data": json.dumps({})
        }
    ]
    
    return test_conversations, test_messages

def test_conversation_retrieval():
    """Test conversation listing and retrieval functionality."""
    print("🔍 TESTING CONVERSATION RETRIEVAL")
    print("=" * 50)
    
    try:
        # Ensure dependencies
        if not ensure_dependencies():
            print("❌ Failed to install dependencies")
            return False
        
        from poe_search.search.engine import SearchEngine
        from poe_search.storage.database import Database

        # Create temporary database
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp_db:
            db_path = tmp_db.name
        
        print(f"📁 Using test database: {db_path}")
        
        # Initialize database
        database = Database(f"sqlite:///{db_path}")
        print("✅ Database initialized")
        
        # Create test data
        test_conversations, test_messages = create_test_data()
        print(f"📊 Created {len(test_conversations)} test conversations and {len(test_messages)} test messages")
        
        # Insert test data
        print("\n1️⃣ Inserting test conversations...")
        for conv in test_conversations:
            database.save_conversation(conv)
        print("✅ Test conversations saved")
        
        print("\n2️⃣ Inserting test messages...")
        for msg in test_messages:
            database.save_message(msg, msg["conversation_id"])
        print("✅ Test messages saved")
        
        # Test 1: Get all conversations
        print("\n3️⃣ Testing get_conversations()...")
        all_conversations = database.get_conversations()
        print(f"✅ Retrieved {len(all_conversations)} conversations")
        
        if len(all_conversations) == 0:
            print("❌ No conversations found!")
            return False
        
        for conv in all_conversations:
            print(f"   📝 {conv['id']}: {conv['title']} (bot: {conv['bot']})")
        
        # Test 2: Get conversations by bot
        print("\n4️⃣ Testing get_conversations(bot='claude-3-5-sonnet')...")
        claude_convs = database.get_conversations(bot="claude-3-5-sonnet")
        print(f"✅ Retrieved {len(claude_convs)} Claude conversations")
        
        # Test 3: Get conversations with limit
        print("\n5️⃣ Testing get_conversations(limit=2)...")
        limited_convs = database.get_conversations(limit=2)
        print(f"✅ Retrieved {len(limited_convs)} conversations (limited)")
        
        # Test 4: Get conversations by date
        print("\n6️⃣ Testing get_conversations(days=2)...")
        recent_convs = database.get_conversations(days=2)
        print(f"✅ Retrieved {len(recent_convs)} recent conversations")
        
        # Test 5: Get single conversation
        print("\n7️⃣ Testing get_conversation('conv_001')...")
        single_conv = database.get_conversation("conv_001")
        if single_conv:
            print(f"✅ Retrieved conversation: {single_conv['title']}")
        else:
            print("❌ Failed to retrieve specific conversation")
            return False
        
        # Test 6: Search functionality
        print("\n8️⃣ Testing search functionality...")
        search_engine = SearchEngine(database)
        
        # Search for Python
        python_results = search_engine.search("Python")
        print(f"✅ Search for 'Python': {len(python_results)} results")
        
        # Search for chocolate
        chocolate_results = search_engine.search("chocolate")
        print(f"✅ Search for 'chocolate': {len(chocolate_results)} results")
        
        # Search for neural
        neural_results = search_engine.search("neural")
        print(f"✅ Search for 'neural': {len(neural_results)} results")
        
        # Test 7: Message search directly
        print("\n9️⃣ Testing direct message search...")
        message_results = database.search_messages("Python", limit=5)
        print(f"✅ Direct message search: {len(message_results)} results")
        
        for result in message_results:
            print(f"   💬 {result['conversation_title']}: {result['content'][:50]}...")
        
        # Clean up
        os.unlink(db_path)
        print(f"\n🧹 Cleaned up test database")
        
        print("\n🎉 ALL CONVERSATION RETRIEVAL TESTS PASSED!")
        return True
        
    except Exception as e:
        print(f"\n❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_empty_database():
    """Test behavior with empty database."""
    print("\n🔍 TESTING EMPTY DATABASE BEHAVIOR")
    print("=" * 50)
    
    try:
        from poe_search.search.engine import SearchEngine
        from poe_search.storage.database import Database

        # Create temporary database
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp_db:
            db_path = tmp_db.name
        
        # Initialize empty database
        database = Database(f"sqlite:///{db_path}")
        
        # Test empty operations
        empty_convs = database.get_conversations()
        print(f"✅ Empty get_conversations(): {len(empty_convs)} results")
        
        empty_search = database.search_messages("test")
        print(f"✅ Empty search_messages(): {len(empty_search)} results")
        
        missing_conv = database.get_conversation("nonexistent")
        print(f"✅ Missing conversation: {missing_conv}")
        
        # Test search engine with empty database
        search_engine = SearchEngine(database)
        empty_search_results = search_engine.search("anything")
        print(f"✅ Empty search engine: {len(empty_search_results)} results")
        
        # Clean up
        os.unlink(db_path)
        
        print("✅ Empty database tests passed")
        return True
        
    except Exception as e:
        print(f"❌ Error testing empty database: {e}")
        return False

if __name__ == "__main__":
    print("🚀 CONVERSATION SEARCH AND RETRIEVAL TESTS")
    print("=" * 60)
    
    success = True
    
    # Test with data
    success &= test_conversation_retrieval()
    
    # Test empty database
    success &= test_empty_database()
    
    print(f"\n{'✅ ALL TESTS PASSED' if success else '❌ SOME TESTS FAILED'}")
    sys.exit(0 if success else 1)
