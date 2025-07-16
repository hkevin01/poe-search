#!/usr/bin/env python3
"""Direct test of Poe API to find conversations - minimal dependencies."""

import json
import os
import sys

# Set Python path
sys.path.insert(0, '/home/kevin/Projects/poe-search/src')

try:
    from poe_api_wrapper import PoeApi
    print("✓ PoeApi imported successfully")
except ImportError as e:
    print(f"❌ Failed to import PoeApi: {e}")
    sys.exit(1)

def load_simple_config():
    """Load config using the proper config system."""
    try:
        from poe_search.utils.config import load_poe_tokens_from_file
        return load_poe_tokens_from_file()
    except Exception as e:
        print(f"Failed to load tokens: {e}")
        return None

def main():
    print("=== Direct Poe API Test ===")
    
    # Load config
    config = load_simple_config()
    if not config:
        return
    
    formkey = config.get('formkey')
    p_b = config.get('p_b') or config.get('p-b')  # Try both keys
    p_lat = config.get('p_lat') or config.get('p-lat')  # Get p-lat cookie
    
    if not formkey or not p_b or not p_lat:
        print("❌ Missing credentials in config")
        print(f"   formkey: {'✓' if formkey else '❌'}")
        print(f"   p_b: {'✓' if p_b else '❌'}")
        print(f"   p_lat: {'✓' if p_lat else '❌'}")
        return
    
    print(f"✓ Config loaded - formkey: {formkey[:10]}...")
    
    # Initialize client with tokens dict
    try:
        tokens = {
            'p_b': p_b,
            'p_lat': p_lat,
            'formkey': formkey
        }
        client = PoeApi(tokens=tokens)
        print("✓ PoeApi client created")
    except Exception as e:
        print(f"❌ Failed to create client: {e}")
        return
    
    # Test available bots
    print("\n--- Testing get_available_bots ---")
    try:
        bots = client.get_available_bots()
        print(f"Result type: {type(bots)}")
        
        if isinstance(bots, dict):
            print(f"Number of bots: {len(bots)}")
            bot_names = list(bots.keys())[:10]
            print(f"First 10 bots: {bot_names}")
            
            # Try to get chat history for each bot
            print(f"\n--- Testing chat history ---")
            total_conversations = 0
            
            for i, bot_name in enumerate(bot_names):
                print(f"\nTesting bot {i+1}/10: {bot_name}")
                try:
                    history = client.get_chat_history(bot_name, count=50)
                    print(f"  History type: {type(history)}")
                    
                    if isinstance(history, dict) and 'data' in history:
                        bot_conversations = history['data'].get(bot_name, [])
                        conv_count = len(bot_conversations)
                        total_conversations += conv_count
                        print(f"  Conversations: {conv_count}")
                        
                        if conv_count > 0:
                            # Show sample conversation
                            sample = bot_conversations[0]
                            print(f"  Sample: {json.dumps(sample, indent=2)[:200]}...")
                    else:
                        print(f"  Unexpected format: {str(history)[:100]}")
                        
                except Exception as e:
                    print(f"  Error: {e}")
            
            print(f"\n🎯 TOTAL CONVERSATIONS FOUND: {total_conversations}")
            
            if total_conversations > 0:
                print("🎉 SUCCESS: API is working and found conversations!")
                return True
            else:
                print("⚠️  API works but no conversations found")
        else:
            print(f"Unexpected bots format: {bots}")
            
    except Exception as e:
        print(f"❌ get_available_bots failed: {e}")
    
    # Try alternative methods
    print(f"\n--- Testing alternative methods ---")
    
    methods = [
        'get_settings',
        'get_user_bots', 
        'get_threadData',
    ]
    
    for method_name in methods:
        try:
            method = getattr(client, method_name)
            result = method()
            print(f"{method_name}: {type(result)} - {str(result)[:100]}...")
        except Exception as e:
            print(f"{method_name}: Failed - {e}")
    
    return False

if __name__ == "__main__":
    success = main()
    if not success:
        print(f"\n💭 Possible issues:")
        print("1. Account has no conversations")
        print("2. Conversations are private/hidden") 
        print("3. API tokens need refresh")
        print("4. Poe.com changed their API")
