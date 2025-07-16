#!/usr/bin/env python3
"""Simple test to check Poe API conversation fetching."""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from poe_api_wrapper import PoeApi
from poe_search.utils.config import load_config

def test_basic_connection():
    """Test basic Poe API connection and conversation fetching."""
    print("=== Basic Poe API Connection Test ===")
    
    try:
        # Load config
        config = load_config()
        print("✓ Configuration loaded")
        
        # Initialize client
        formkey = config.get('formkey')
        p_b = config.get('p_b')
        
        if not formkey or not p_b:
            print("❌ Missing formkey or p_b cookie")
            return False
        
        client = PoeApi(cookie=p_b, formkey=formkey)
        print("✓ PoeApi client initialized")
        
        # Test 1: Get available bots
        print("\n--- Test 1: Available Bots ---")
        bots = client.get_available_bots()
        print(f"Available bots type: {type(bots)}")
        print(f"Available bots count: {len(bots) if isinstance(bots, (dict, list)) else 'N/A'}")
        
        if isinstance(bots, dict) and len(bots) > 0:
            first_5_bots = list(bots.keys())[:5]
            print(f"First 5 bots: {first_5_bots}")
            
            # Test 2: Try to get chat history for first bot
            print(f"\n--- Test 2: Chat History for {first_5_bots[0]} ---")
            try:
                history = client.get_chat_history(first_5_bots[0], count=100)
                print(f"Chat history type: {type(history)}")
                print(f"Chat history: {history}")
                
                if isinstance(history, dict) and 'data' in history:
                    bot_data = history['data'].get(first_5_bots[0], [])
                    print(f"Conversations for {first_5_bots[0]}: {len(bot_data)}")
                    if bot_data:
                        print(f"Sample conversation: {bot_data[0]}")
                        return True
                
            except Exception as e:
                print(f"Chat history failed: {e}")
        
        # Test 3: Try other methods
        print(f"\n--- Test 3: Other Methods ---")
        try:
            settings = client.get_settings()
            print(f"Settings: {type(settings)} - {str(settings)[:200]}...")
        except Exception as e:
            print(f"get_settings failed: {e}")
            
        try:
            user_bots = client.get_user_bots()
            print(f"User bots: {type(user_bots)} - {len(user_bots) if isinstance(user_bots, (list, dict)) else 'N/A'}")
        except Exception as e:
            print(f"get_user_bots failed: {e}")
            
        return False
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

if __name__ == "__main__":
    success = test_basic_connection()
    if success:
        print("\n🎉 SUCCESS: Found conversations!")
    else:
        print("\n💥 FAILURE: No conversations found")
