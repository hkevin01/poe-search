#!/usr/bin/env python3
"""Test script to verify Poe API key and get user information."""

import json
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from poe_api_wrapper import PoeApi

from poe_search.utils.config import load_config


def test_poe_api():
    """Test Poe API connection and get user information."""
    
    print("=== Poe API Test ===\n")
    
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
        
        # Create tokens dict for poe-api-wrapper
        print(f"Using tokens: {tokens}")
        
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
        
        # Test getting chat history
        print("\n💬 Testing chat history retrieval...")
        try:
            # Try with a popular bot first
            bot_id = "chinchilla"  # ChatGPT
            print(f"Getting chat history for bot: {bot_id}")
            
            chat_history = client.get_chat_history(bot_id, count=5)
            print(f"✅ Found {len(chat_history)} conversations for {bot_id}")
            
            if chat_history:
                print("Sample conversations:")
                for i, conv in enumerate(chat_history[:3]):
                    print(f"  {i+1}. {conv.get('title', 'Untitled')} (ID: {conv.get('chatId', 'Unknown')})")
                    
        except Exception as e:
            print(f"❌ Failed to get chat history: {e}")
        
        # Test getting settings/user info
        print("\n👤 Testing user info retrieval...")
        try:
            settings = client.get_settings()
            print("✅ User settings retrieved successfully")
            print(f"Settings keys: {list(settings.keys())}")
            
        except Exception as e:
            print(f"❌ Failed to get user settings: {e}")
        
        # Test sending a message (optional)
        print("\n📝 Testing message sending (optional)...")
        try:
            # This will create a new conversation
            print("Sending test message to ChatGPT...")
            
            response_chunks = []
            for chunk in client.send_message("chinchilla", "Hello! This is a test message from Poe Search."):
                if chunk.get('text'):
                    response_chunks.append(chunk['text'])
                    print(f"Response chunk: {chunk['text'][:50]}...")
                
                if chunk.get('state') == 'complete':
                    break
            
            if response_chunks:
                print("✅ Message sent and response received successfully")
                print(f"Full response: {''.join(response_chunks)}")
            else:
                print("⚠️ No response received")
                
        except Exception as e:
            print(f"❌ Failed to send message: {e}")
        
        print("\n🎉 Poe API test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Poe API test failed: {e}")
        print("\n💡 Troubleshooting tips:")
        print("1. Make sure your token is the 'p-b' cookie value from poe.com")
        print("2. You might also need the 'p-lat' cookie value")
        print("3. Check if your Poe account is active and not restricted")
        print("4. Try refreshing your cookies by logging out and back in to poe.com")
        return False

if __name__ == "__main__":
    success = test_poe_api()
    sys.exit(0 if success else 1) 