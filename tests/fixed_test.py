#!/usr/bin/env python3
"""Test with properly decoded tokens from GUI logs."""

import sys
import urllib.parse

# Set Python path
sys.path.insert(0, '/home/kevin/Projects/poe-search/src')

try:
    from poe_api_wrapper import PoeApi
    print("✓ PoeApi imported successfully")
except ImportError as e:
    print(f"❌ Failed to import PoeApi: {e}")
    sys.exit(1)

def main():
    print("=== Fixed Token Test ===")
    
    # Extract tokens from GUI logs (URL encoded values)
    p_b_encoded = "AG58MLIXFnbOh98QAv4YHA%3D%3D"
    p_lat_encoded = "87OepyV2QcF9TkiuqhaFyWZgROH%2BVp00g0QZLwZEMg%3D%3D"
    formkey = "c25281d6b4dfb3f76fb03c597e3e61aa"
    
    # URL decode the cookies
    p_b = urllib.parse.unquote(p_b_encoded)
    p_lat = urllib.parse.unquote(p_lat_encoded)
    
    print(f"Decoded tokens:")
    print(f"  p_b: {p_b}")
    print(f"  p_lat: {p_lat}")
    print(f"  formkey: {formkey}")
    
    # Create client with properly decoded tokens
    try:
        tokens = {
            'p_b': p_b,
            'p_lat': p_lat,
            'formkey': formkey
        }
        print("\nCreating PoeApi client...")
        client = PoeApi(tokens=tokens)
        print("✓ PoeApi client created successfully")
    except Exception as e:
        print(f"❌ Failed to create client: {e}")
        return
    
    # Test get_available_bots
    try:
        print("\n--- Testing get_available_bots ---")
        bots = client.get_available_bots()
        print(f"Bots result: {type(bots)}")
        
        if isinstance(bots, dict) and len(bots) > 0:
            print(f"✓ Found {len(bots)} bots")
            bot_names = list(bots.keys())[:5]
            print(f"First 5 bots: {bot_names}")
            
            # Test chat history for first few bots
            print(f"\n--- Testing chat history ---")
            total_conversations = 0
            
            for i, bot_name in enumerate(bot_names[:3]):  # Test first 3 bots
                print(f"\nBot {i+1}: {bot_name}")
                try:
                    history = client.get_chat_history(bot_name, count=100)
                    print(f"  History type: {type(history)}")
                    
                    if isinstance(history, dict) and 'data' in history:
                        bot_conversations = history['data'].get(bot_name, [])
                        conv_count = len(bot_conversations)
                        total_conversations += conv_count
                        print(f"  Conversations: {conv_count}")
                        
                        if conv_count > 0:
                            sample = bot_conversations[0]
                            print(f"  Sample keys: {list(sample.keys())}")
                            print(f"  Sample title: {sample.get('title', 'No title')}")
                    else:
                        print(f"  Unexpected format: {str(history)[:100]}")
                        
                except Exception as e:
                    print(f"  Error: {e}")
            
            print(f"\n🎯 TOTAL CONVERSATIONS FOUND: {total_conversations}")
            
            if total_conversations > 0:
                print("🎉 SUCCESS: Found real conversations!")
                
                # Now test our sync worker approach
                print(f"\n--- Testing sync worker approach ---")
                try:
                    from poe_search.client import PoeSearchClient
                    from poe_search.utils.config import load_config
                    
                    config = load_config()
                    search_client = PoeSearchClient(config)
                    
                    # Test with very long time period
                    conversations = search_client.get_conversation_history(days=3650, limit=1000)
                    print(f"PoeSearchClient found: {len(conversations)} conversations")
                    
                    if len(conversations) > 0:
                        print("✓ PoeSearchClient approach works too!")
                    else:
                        print("⚠️ PoeSearchClient approach found 0 conversations - needs investigation")
                        
                except Exception as e:
                    print(f"PoeSearchClient test failed: {e}")
                
                return True
            else:
                print("⚠️ API works but no conversations found")
        else:
            print(f"Unexpected bots format: {bots}")
            
    except Exception as e:
        print(f"❌ get_available_bots failed: {e}")
    
    return False

if __name__ == "__main__":
    success = main()
    if success:
        print(f"\n🎯 CONCLUSION: API is working and can fetch conversations!")
        print("The issue was URL-encoded tokens and possibly date filtering.")
    else:
        print(f"\n❌ CONCLUSION: Still unable to fetch conversations")
