#!/usr/bin/env python3
"""Test script to verify conversation display functionality."""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from poe_search.storage.database import Database
from poe_search.utils.config import load_config


def test_database_methods():
    """Test the database methods for conversation retrieval."""
    print("Testing database methods...")
    
    # Initialize database
    db = Database()
    
    # Test get_conversation method exists
    if hasattr(db, 'get_conversation'):
        print("✅ get_conversation method exists")
    else:
        print("❌ get_conversation method missing")
        return False
    
    # Test get_conversations method exists
    if hasattr(db, 'get_conversations'):
        print("✅ get_conversations method exists")
    else:
        print("❌ get_conversations method missing")
        return False
    
    # Test conversation count
    count = db.get_conversation_count()
    print(f"📊 Database contains {count} conversations")
    
    if count > 0:
        # Get all conversations
        conversations = db.get_conversations()
        print(f"📋 Retrieved {len(conversations)} conversations")
        
        # Test getting a specific conversation
        if conversations:
            first_conv = conversations[0]
            conv_id = first_conv['id']
            print(f"🔍 Testing get_conversation with ID: {conv_id}")
            
            single_conv = db.get_conversation(conv_id)
            if single_conv:
                print(f"✅ Successfully retrieved conversation: {single_conv.get('title', 'Untitled')}")
                print(f"   Bot: {single_conv.get('bot', 'Unknown')}")
                print(f"   Messages: {single_conv.get('message_count', 0)}")
                return True
            else:
                print(f"❌ Failed to retrieve conversation with ID: {conv_id}")
                return False
        else:
            print("⚠️  No conversations found in database")
            return True
    else:
        print("⚠️  Database is empty - no conversations to test")
        return True

def test_config_loading():
    """Test configuration loading."""
    print("\nTesting configuration loading...")
    
    try:
        config = load_config()
        if hasattr(config, 'poe_token') and config.poe_token:
            print(f"✅ Configuration loaded successfully")
            print(f"   Token: {config.poe_token[:10]}...")
            return True
        else:
            print("⚠️  Configuration loaded but no token found")
            return True
    except Exception as e:
        print(f"❌ Configuration loading failed: {e}")
        return False

def main():
    """Run all tests."""
    print("🧪 Testing Poe Search Conversation Display Functionality")
    print("=" * 60)
    
    # Test configuration
    config_ok = test_config_loading()
    
    # Test database methods
    db_ok = test_database_methods()
    
    print("\n" + "=" * 60)
    print("📋 Test Results Summary:")
    print(f"   Configuration: {'✅ PASS' if config_ok else '❌ FAIL'}")
    print(f"   Database Methods: {'✅ PASS' if db_ok else '❌ FAIL'}")
    
    if config_ok and db_ok:
        print("\n🎉 All tests passed! Conversation display should work correctly.")
        print("💡 You can now test the GUI by:")
        print("   1. Running the application: ./run.sh")
        print("   2. Clicking on any conversation in the search results")
        print("   3. Verifying that conversation details display correctly")
        return True
    else:
        print("\n⚠️  Some tests failed. Please check the issues above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 