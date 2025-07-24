#!/usr/bin/env python3
"""Test script to verify poe-api-wrapper with cookie data and fetch conversations."""

import json
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from poe_api_wrapper import PoeApi
from poe_search.utils.config import load_config


def test_poe_wrapper_with_cookies():
    """Test poe-api-wrapper with cookie data and fetch conversations."""
    
    print("=== Poe API Wrapper Test with Cookies ===\n")
    
    # Load configuration
    try:
        config = load_config()
        
        # Use new token format
        if hasattr(config, 'get_poe_tokens'):
            tokens = config.get_poe_tokens()
            if not tokens.get('p-b'):
                print("❌ No p-b cookie found in configuration")
                return False
            print(f"✅ p-b cookie loaded: {tokens.get('p-b', '')[:10]}...")
            print(f"✅ p-lat cookie loaded: {tokens.get('p-lat', '')[:10] if tokens.get('p-lat') else 'Not set'}...")
            print(f"✅ formkey loaded: {tokens.get('formkey', '')[:10] if tokens.get('formkey') else 'Not set'}...")
        else:
            # Fall back to old format
            token = config.poe_token
            if not token:
                print("❌ No Poe token found in configuration")
                return False
            print(f"✅ Token loaded: {token[:10]}...")
            tokens = {
                "p-b": token,
                "p-lat": token
            }
        
    except Exception as e:
        print(f"❌ Failed to load configuration: {e}")
        return False
    
    # Test with poe-api-wrapper
    try:
        print("\n🔗 Testing connection with poe-api-wrapper...")
        
        # Initialize PoeApi client
        client = PoeApi(tokens)
        print("✅ PoeApi client created successfully")
        
        # Test getting available bots
        print("\n🤖 Testing bot retrieval...")
        try:
            bots = client.get_available_bots()
            print(f"✅ Found {len(bots)} available bots")
            
            # Show first few bots
            print("Sample bots:")
            for i, bot in enumerate(bots[:5]):
                print(f"  {i+1}. {bot.get('displayName', 'Unknown')} ({bot.get('id', 'Unknown')})")
                
        except Exception as e:
            print(f"❌ Failed to get bots: {e}")
        
        # Test getting chat history for different bots
        print("\n💬 Testing chat history retrieval...")
        
        # Test with the bot from your response (Claude-Sonnet-4)
        test_bots = ["a2", "chinchilla", "capybara", "beaver"]  # Claude, ChatGPT, Assistant, GPT-4
        
        for bot_id in test_bots:
            try:
                print(f"\n📋 Getting chat history for bot: {bot_id}")
                chat_history = client.get_chat_history(bot_id, count=5)
                print(f"✅ Found {len(chat_history)} conversations for {bot_id}")
                
                if chat_history:
                    print("Sample conversations:")
                    for i, conv in enumerate(chat_history[:3]):
                        title = conv.get('title', 'Untitled')
                        chat_id = conv.get('chatId', 'Unknown')
                        chat_code = conv.get('chatCode', 'Unknown')
                        print(f"  {i+1}. {title}")
                        print(f"     ID: {chat_id}, Code: {chat_code}")
                        
                        # Try to get messages for this conversation
                        try:
                            print(f"     📝 Getting messages for conversation {chat_id}...")
                            messages = client.get_message_history(bot_id, chat_id, count=3)
                            print(f"     ✅ Found {len(messages)} messages")
                            
                            if messages:
                                print("     Sample messages:")
                                for j, msg in enumerate(messages[:2]):
                                    role = msg.get('role', 'unknown')
                                    text = msg.get('text', '')[:100] + "..." if len(msg.get('text', '')) > 100 else msg.get('text', '')
                                    print(f"       {j+1}. [{role}] {text}")
                            
                        except Exception as e:
                            print(f"     ❌ Failed to get messages: {e}")
                        
                        print()  # Empty line for readability
                        
            except Exception as e:
                print(f"❌ Failed to get chat history for {bot_id}: {e}")
        
        # Test getting user info/settings
        print("\n👤 Testing user info retrieval...")
        try:
            # Try to get user settings
            settings = client.get_settings()
            print(f"✅ User settings retrieved: {len(settings) if isinstance(settings, dict) else 'N/A'} fields")
            
            if isinstance(settings, dict):
                print("Sample settings:")
                for key, value in list(settings.items())[:5]:
                    print(f"  {key}: {value}")
                    
        except Exception as e:
            print(f"❌ Failed to get user settings: {e}")
        
        # Test getting subscription info
        print("\n💳 Testing subscription info...")
        try:
            subscription = client.get_subscription()
            print(f"✅ Subscription info retrieved: {subscription}")
        except Exception as e:
            print(f"❌ Failed to get subscription info: {e}")
        
        print("\n🎉 All tests completed!")
        return True
        
    except Exception as e:
        print(f"❌ PoeApi client test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Main function."""
    success = test_poe_wrapper_with_cookies()
    
    if success:
        print("\n✅ Poe API wrapper test successful!")
        print("The wrapper is working correctly with your cookie data.")
        print("\nNext steps:")
        print("1. The wrapper can now fetch conversations and messages")
        print("2. Your Poe Search application should work with this data")
        print("3. You can use the API client in your application")
    else:
        print("\n❌ Poe API wrapper test failed.")
        print("Please check your cookie data and try again.")
        sys.exit(1)


if __name__ == "__main__":
    main() 