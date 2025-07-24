#!/usr/bin/env python3
"""Simple script to test Poe API connection with a token."""

import os
import sys
from pathlib import Path

# Add src to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

from poe_search.api.client import PoeAPIClient
from poe_search.utils.config import ConfigManager


def test_poe_connection():
    """Test Poe API connection with available token."""
    print("🔗 Testing Poe API Connection...")
    print("=" * 50)
    
    # Try to get token from environment
    token = os.getenv("POE_TOKEN")
    
    if not token:
        # Try to get from config
        try:
            config_manager = ConfigManager()
            config = config_manager.get_config()
            if config.has_valid_tokens():
                tokens = config.get_poe_tokens()
                token = tokens.get("p-b", "")
                print(f"📁 Found token in config: {token[:10]}..." if token else "❌ No token found in config")
            else:
                print("❌ No valid tokens found in config")
        except Exception as e:
            print(f"❌ Error loading config: {e}")
    
    if not token:
        print("\n⚠️  No Poe token found!")
        print("To test with a real token:")
        print("1. Set POE_TOKEN environment variable, or")
        print("2. Add your token to config/secrets.json")
        print("3. Run this script again")
        return False
    
    print(f"🔑 Using token: {token[:10]}...")
    
    try:
        # Initialize client
        print("\n🔄 Initializing Poe API client...")
        client = PoeAPIClient(token)
        
        if client.client is None:
            print("❌ Failed to initialize Poe API client")
            print("This could be due to:")
            print("- Invalid token")
            print("- Network connectivity issues")
            print("- Poe.com API changes")
            return False
        
        print("✅ Poe API client initialized successfully!")
        
        # Test bot retrieval
        print("\n🤖 Testing bot retrieval...")
        bots = client.get_bots()
        if bots:
            print(f"✅ Retrieved {len(bots)} bots:")
            for bot_id, bot_info in list(bots.items())[:5]:  # Show first 5
                print(f"   • {bot_info.get('displayName', bot_id)} ({bot_id})")
            if len(bots) > 5:
                print(f"   ... and {len(bots) - 5} more")
        else:
            print("⚠️  No bots retrieved (this might be normal)")
        
        # Test conversation retrieval
        print("\n💬 Testing conversation retrieval...")
        conversations = client.get_recent_conversations(days=1)
        if conversations:
            print(f"✅ Retrieved {len(conversations)} recent conversations:")
            for conv in conversations[:3]:  # Show first 3
                title = conv.get('title', 'Untitled')
                bot_name = conv.get('bot', {}).get('displayName', 'Unknown')
                print(f"   • {title} (with {bot_name})")
            if len(conversations) > 3:
                print(f"   ... and {len(conversations) - 3} more")
        else:
            print("⚠️  No conversations retrieved (this might be normal)")
        
        # Test conversation IDs
        print("\n🆔 Testing conversation ID retrieval...")
        conv_ids = client.get_conversation_ids(days=1)
        if conv_ids:
            print(f"✅ Retrieved {len(conv_ids)} conversation IDs")
            print(f"   First ID: {conv_ids[0]}")
        else:
            print("⚠️  No conversation IDs retrieved")
        
        print("\n🎉 All tests completed successfully!")
        print("The Poe API wrapper is working correctly with your token.")
        return True
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        print("\nThis could be due to:")
        print("- Invalid or expired token")
        print("- Network connectivity issues")
        print("- Poe.com API changes")
        print("- Rate limiting")
        return False


def main():
    """Main function."""
    success = test_poe_connection()
    
    if success:
        print("\n✅ Connection test successful!")
        print("You can now use the Poe API wrapper in your application.")
    else:
        print("\n❌ Connection test failed.")
        print("Please check your token and try again.")
        sys.exit(1)


if __name__ == "__main__":
    main() 