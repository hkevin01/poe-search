#!/usr/bin/env python3
"""
Test script to verify message retrieval from test conversations.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))


def test_message_retrieval():
    """Test message retrieval from conversations that have messages."""
    print("Testing message retrieval from test conversations...")
    
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
        
        # Test specific conversation IDs that have messages
        test_conv_ids = ["conv_001", "conv_002", "conv_003", "conv_004"]
        
        success_count = 0
        total_messages = 0
        
        for conv_id in test_conv_ids:
            print(f"\n📋 Testing conversation: {conv_id}")
            
            # Get full conversation
            full_conv = db.get_conversation(conv_id)
            if not full_conv:
                print(f"   ❌ Could not retrieve conversation {conv_id}")
                continue
            
            messages = full_conv.get("messages", [])
            print(f"   ✅ Retrieved {len(messages)} messages")
            total_messages += len(messages)
            
            if messages:
                # Test first message
                first_msg = messages[0]
                msg_text = first_msg.get("text", "") or first_msg.get("content", "")
                if msg_text:
                    preview = msg_text[:60] + "..." if len(msg_text) > 60 else msg_text
                    print(f"   📝 First message: {preview}")
                    success_count += 1
                else:
                    print(f"   ⚠️  Message has no text content")
                    print(f"   Keys: {list(first_msg.keys())}")
            else:
                print(f"   ⚠️  No messages found")
        
        # Test search functionality if available
        print(f"\n🔍 Testing search functionality...")
        if hasattr(db, 'search_messages'):
            search_results = db.search_messages("Python")
            print(f"   ✅ Search for 'Python' found {len(search_results)} results")
        else:
            print("   ⚠️  search_messages method not available")
        
        # Summary
        print("\n" + "="*50)
        print("MESSAGE RETRIEVAL TEST SUMMARY")
        print("="*50)
        print(f"Test conversations checked: {len(test_conv_ids)}")
        print(f"Conversations with retrievable messages: {success_count}")
        print(f"Total messages retrieved: {total_messages}")
        
        if success_count > 0:
            print("🎉 Message retrieval is working!")
            return True
        else:
            print("❌ No messages could be retrieved")
            return False
            
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_message_retrieval()
    sys.exit(0 if success else 1)
