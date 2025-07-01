#!/usr/bin/env python3
"""Debug script to understand what poe-api-wrapper is returning."""

import json
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from poe_api_wrapper import PoeApi
from poe_search.utils.config import load_config


def debug_poe_wrapper_response():
    """Debug what poe-api-wrapper is returning."""
    
    print("=== Poe API Wrapper Response Debug ===\n")
    
    # Load configuration
    try:
        config = load_config()
        tokens = config.get_poe_tokens()
        print(f"✅ Tokens loaded: {tokens.get('p-b', '')[:10]}...")
    except Exception as e:
        print(f"❌ Failed to load configuration: {e}")
        return False
    
    # Test with poe-api-wrapper
    try:
        print("\n🔗 Testing poe-api-wrapper responses...")
        
        # Initialize PoeApi client
        client = PoeApi(tokens)
        print("✅ PoeApi client created successfully")
        
        # Test getting chat history for a specific bot
        bot_id = "a2"  # Claude
        print(f"\n📋 Testing chat history for bot: {bot_id}")
        
        try:
            chat_history = client.get_chat_history(bot_id, count=5)
            print(f"✅ Chat history response type: {type(chat_history)}")
            print(f"✅ Chat history response: {chat_history}")
            
            if isinstance(chat_history, dict):
                print("Chat history dictionary keys:")
                for key, value in chat_history.items():
                    print(f"  {key}: {type(value)} = {value}")
                    
                # Check if data field has content
                if 'data' in chat_history and isinstance(chat_history['data'], dict):
                    data = chat_history['data']
                    print(f"Data field keys: {list(data.keys())}")
                    for key, value in data.items():
                        print(f"  {key}: {type(value)} = {value}")
                        
        except Exception as e:
            print(f"❌ Failed to get chat history: {e}")
            import traceback
            traceback.print_exc()
        
        # Try different bot IDs
        print(f"\n🔄 Testing different bot IDs...")
        test_bots = ["a2", "chinchilla", "capybara", "beaver", "claude-3-5-sonnet"]
        
        for bot_id in test_bots:
            try:
                print(f"\n📋 Testing bot: {bot_id}")
                chat_history = client.get_chat_history(bot_id, count=3)
                
                if isinstance(chat_history, dict) and 'data' in chat_history:
                    data = chat_history['data']
                    if isinstance(data, dict) and data:
                        print(f"  ✅ Found data: {len(data)} keys")
                        for key, value in data.items():
                            print(f"    {key}: {type(value)} = {value}")
                    else:
                        print(f"  ⚠️  Empty data field")
                else:
                    print(f"  ❌ Unexpected response format")
                    
            except Exception as e:
                print(f"  ❌ Failed: {e}")
        
        # Test getting settings
        print(f"\n👤 Testing settings...")
        try:
            settings = client.get_settings()
            print(f"✅ Settings response type: {type(settings)}")
            print(f"✅ Settings response: {settings}")
            
            if isinstance(settings, dict):
                print("Settings keys:")
                for key, value in settings.items():
                    print(f"  {key}: {type(value)} = {value}")
                    
        except Exception as e:
            print(f"❌ Failed to get settings: {e}")
        
        print("\n🎉 Debug completed!")
        return True
        
    except Exception as e:
        print(f"❌ Debug failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Main function."""
    success = debug_poe_wrapper_response()
    
    if success:
        print("\n✅ Debug completed successfully!")
        print("Check the output above to understand the response structure.")
    else:
        print("\n❌ Debug failed.")
        sys.exit(1)


if __name__ == "__main__":
    main() 