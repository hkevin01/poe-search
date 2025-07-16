#!/usr/bin/env python3
"""Direct API test without complex token management."""

import json
import sys
from pathlib import Path

# Set Python path
sys.path.insert(0, '/home/kevin/Projects/poe-search/src')

try:
    from poe_api_wrapper import PoeApi
    print("✓ PoeApi imported successfully")
except ImportError as e:
    print(f"❌ Failed to import PoeApi: {e}")
    sys.exit(1)

def main():
    print("=== Direct Poe API Test (Simple) ===")
    
    # Load tokens directly from file
    config_file = '/home/kevin/Projects/poe-search/config/poe_tokens.json'
    try:
        with open(config_file, 'r') as f:
            config = json.load(f)
        print("✓ Config loaded directly")
    except Exception as e:
        print(f"❌ Failed to load config: {e}")
        return
    
    # Extract tokens with multiple key variants
    p_b = config.get('p_b') or config.get('p-b')
    p_lat = config.get('p_lat') or config.get('p-lat') 
    formkey = config.get('formkey')
    
    print(f"Tokens found:")
    print(f"  p_b: {'✓' if p_b else '❌'} ({p_b[:10] if p_b else 'None'}...)")
    print(f"  p_lat: {'✓' if p_lat else '❌'} ({p_lat[:10] if p_lat else 'None'}...)")
    print(f"  formkey: {'✓' if formkey else '❌'} ({formkey[:10] if formkey else 'None'}...)")
    
    if not all([p_b, p_lat, formkey]):
        print("❌ Missing required tokens")
        return
    
    # Try creating client
    try:
        tokens = {
            'p_b': p_b,
            'p_lat': p_lat,
            'formkey': formkey
        }
        print("Creating PoeApi client...")
        client = PoeApi(tokens=tokens)
        print("✓ PoeApi client created successfully")
    except Exception as e:
        print(f"❌ Failed to create client: {e}")
        return
    
    # Quick test: get available bots
    try:
        print("\n--- Testing get_available_bots ---")
        bots = client.get_available_bots()
        print(f"Result: {type(bots)} with {len(bots) if isinstance(bots, (dict, list)) else 'unknown'} items")
        
        if isinstance(bots, dict) and len(bots) > 0:
            print("✓ Successfully got bots list")
            bot_names = list(bots.keys())[:3]  # First 3 bots
            print(f"Sample bots: {bot_names}")
            
            # Try chat history for first bot
            print(f"\n--- Testing chat history for {bot_names[0]} ---")
            try:
                history = client.get_chat_history(bot_names[0], count=20)
                print(f"History result: {type(history)}")
                
                if isinstance(history, dict) and 'data' in history:
                    bot_data = history['data'].get(bot_names[0], [])
                    print(f"Conversations: {len(bot_data)}")
                    
                    if len(bot_data) > 0:
                        print("🎉 SUCCESS: Found conversations!")
                        print(f"Sample conversation keys: {list(bot_data[0].keys()) if bot_data[0] else 'None'}")
                        return True
                    else:
                        print("⚠️ No conversations found for this bot")
                else:
                    print(f"Unexpected history format: {history}")
                    
            except Exception as e:
                print(f"Chat history failed: {e}")
        else:
            print("⚠️ No bots returned or unexpected format")
            
    except Exception as e:
        print(f"❌ get_available_bots failed: {e}")
    
    return False

if __name__ == "__main__":
    success = main()
    if success:
        print("\n🎯 RESULT: API is working and conversations were found!")
    else:
        print("\n❌ RESULT: Could not retrieve conversations")
