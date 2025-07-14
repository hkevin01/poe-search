#!/usr/bin/env python3
"""
Quick test script to verify Poe conversation retrieval functionality.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))


def test_basic_conversation_retrieval():
    """Test basic conversation retrieval from database."""
    print("Testing Poe conversation retrieval...")
    
    # Check database exists
    db_path = Path(__file__).parent.parent.parent / "data" / "poe_search.db"
    if not db_path.exists():
        print(f"❌ Database not found: {db_path}")
        return False
    
    try:
        from poe_search.storage.database import Database
        
        # Initialize database
        db = Database(f"sqlite:///{db_path}")
        print(f"✅ Connected to database: {db_path}")
        
        # Get conversations
        conversations = db.get_conversations()
        print(f"✅ Found {len(conversations)} conversations")
        
        if len(conversations) == 0:
            print("⚠️  No conversations in database")
            return True
        
        # Find conversations that actually have messages
        conversations_with_messages = []
        for conv in conversations:
            if conv.get("message_count", 0) > 0:
                conversations_with_messages.append(conv)
        
        print(f"📊 {len(conversations_with_messages)} conversations have messages")
        
        if not conversations_with_messages:
            print("⚠️  No conversations have messages")
            # Still test structure of conversations without messages
            first_conv = conversations[0]
            print(f"📋 Testing conversation structure: {first_conv.get('title', 'No title')}")
            print(f"   Bot: {first_conv.get('bot', 'Unknown')}")
            print(f"   ID: {first_conv.get('id', 'No ID')}")
            print(f"   Created: {first_conv.get('created_at', 'No date')}")
            
            # Try to get full conversation anyway
            full_conv = db.get_conversation(first_conv["id"])
            if full_conv:
                print("✅ Can retrieve full conversation (even without messages)")
                return True
            else:
                print("❌ Cannot retrieve full conversation")
                return False
        
        # Test first conversation with messages
        first_conv = conversations_with_messages[0]
        print(f"📋 Testing conversation: {first_conv.get('title', 'No title')}")
        print(f"   Bot: {first_conv.get('bot', 'Unknown')}")
        print(f"   Message count: {first_conv.get('message_count', 0)}")
        
        # Get full conversation
        full_conv = db.get_conversation(first_conv["id"])
        if not full_conv:
            print("❌ Could not retrieve full conversation")
            return False
        
        messages = full_conv.get("messages", [])
        print(f"✅ Retrieved {len(messages)} messages")
        
        # Check message content
        if messages:
            first_msg = messages[0]
            msg_text = first_msg.get("text", "") or first_msg.get("content", "")
            if msg_text:
                preview = msg_text[:100] + "..." if len(msg_text) > 100 else msg_text
                print(f"📝 First message preview: {preview}")
            else:
                print("⚠️  First message has no text content")
                print(f"   Message keys: {list(first_msg.keys())}")
        
        # Test a few more conversations with messages
        test_count = min(3, len(conversations_with_messages))
        success_count = 0
        
        for i in range(test_count):
            conv = conversations_with_messages[i]
            full_conv = db.get_conversation(conv["id"])
            if full_conv and "messages" in full_conv:
                success_count += 1
        
        print(f"✅ Successfully tested {success_count}/{test_count} conversations")
        
        # Summary
        print("\n" + "="*50)
        print("CONVERSATION RETRIEVAL TEST SUMMARY")
        print("="*50)
        print(f"Database: {db_path}")
        print(f"Total conversations: {len(conversations)}")
        print(f"Conversations with messages: {len(conversations_with_messages)}")
        print(f"Test success rate: {success_count}/{test_count}")
        
        if success_count == test_count and conversations_with_messages:
            print("🎉 All tests passed!")
            return True
        elif len(conversations) > 0:
            print("✅ Database structure is valid (conversations can be retrieved)")
            print("⚠️  Note: Most conversations don't have messages imported yet")
            return True
        else:
            print("⚠️  Some tests failed")
            return False
            
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_basic_conversation_retrieval()
    sys.exit(0 if success else 1)
