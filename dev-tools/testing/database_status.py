#!/usr/bin/env python3
"""
Database status and conversation test diagnostic script.
"""

import sys
import sqlite3
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))


def check_database_status():
    """Check the current status of the database."""
    print("DATABASE STATUS DIAGNOSTIC")
    print("=" * 50)
    
    # Check database exists
    db_path = Path(__file__).parent.parent.parent / "data" / "poe_search.db"
    if not db_path.exists():
        print(f"❌ Database not found: {db_path}")
        return False
    
    print(f"✅ Database found: {db_path}")
    
    # Connect to database directly
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Check conversations table
        cursor.execute("SELECT COUNT(*) FROM conversations")
        conv_count = cursor.fetchone()[0]
        print(f"📊 Conversations table: {conv_count} rows")
        
        # Check messages table
        cursor.execute("SELECT COUNT(*) FROM messages")
        msg_count = cursor.fetchone()[0]
        print(f"📊 Messages table: {msg_count} rows")
        
        # Check conversations with message_count > 0
        cursor.execute("SELECT COUNT(*) FROM conversations WHERE message_count > 0")
        conv_with_msgs = cursor.fetchone()[0]
        print(f"📊 Conversations with message_count > 0: {conv_with_msgs}")
        
        # Check distinct conversation_ids in messages
        cursor.execute("SELECT COUNT(DISTINCT conversation_id) FROM messages")
        distinct_conv_ids = cursor.fetchone()[0]
        print(f"📊 Distinct conversation_ids in messages: {distinct_conv_ids}")
        
        # List conversation_ids that have messages
        cursor.execute("SELECT DISTINCT conversation_id FROM messages")
        conv_ids_with_msgs = [row[0] for row in cursor.fetchall()]
        print(f"📋 Conversation IDs with messages: {conv_ids_with_msgs}")
        
        # Check if these conversation_ids exist in conversations table
        print("\n🔍 Checking conversation_id consistency:")
        for conv_id in conv_ids_with_msgs:
            cursor.execute("SELECT COUNT(*) FROM conversations WHERE id = ?", (conv_id,))
            exists = cursor.fetchone()[0] > 0
            status = "✅" if exists else "❌"
            print(f"   {status} {conv_id} in conversations table: {exists}")
        
        # Sample some real conversations
        print("\n📋 Sample real conversations (first 5):")
        cursor.execute("SELECT id, title, bot, message_count FROM conversations LIMIT 5")
        for row in cursor.fetchall():
            conv_id, title, bot, msg_count = row
            print(f"   ID: {conv_id}, Title: {title[:30]}, Bot: {bot}, Messages: {msg_count}")
        
        # Sample some messages
        print("\n📝 Sample messages (first 3):")
        cursor.execute("SELECT conversation_id, role, substr(content, 1, 50) FROM messages LIMIT 3")
        for row in cursor.fetchall():
            conv_id, role, content = row
            print(f"   {conv_id} ({role}): {content}...")
        
    except Exception as e:
        print(f"❌ Database query error: {e}")
        return False
    finally:
        conn.close()
    
    # Test with our Database class
    print("\n🧪 Testing with Database class:")
    try:
        from poe_search.storage.database import Database
        
        db = Database(f"sqlite:///{db_path}")
        
        # Get conversations
        conversations = db.get_conversations()
        print(f"✅ Retrieved {len(conversations)} conversations via Database class")
        
        # Try to get a conversation that has messages in messages table
        if conv_ids_with_msgs:
            test_conv_id = conv_ids_with_msgs[0]
            full_conv = db.get_conversation(test_conv_id)
            if full_conv:
                messages = full_conv.get("messages", [])
                print(f"✅ Retrieved conversation {test_conv_id} with {len(messages)} messages")
            else:
                print(f"❌ Could not retrieve conversation {test_conv_id}")
        
        # Test search if available
        if hasattr(db, 'search_messages'):
            results = db.search_messages("Python")
            print(f"🔍 Search test: found {len(results)} results for 'Python'")
        else:
            print("⚠️  search_messages method not available in Database class")
            
    except Exception as e:
        print(f"❌ Database class error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    print("\n" + "=" * 50)
    print("DIAGNOSTIC COMPLETE")
    print("=" * 50)
    
    return True


if __name__ == "__main__":
    check_database_status()
