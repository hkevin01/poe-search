#!/usr/bin/env python3
"""
Test the get_chat_history method
"""

import sys
import os

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

try:
    from poe_api_wrapper import PoeApi
    print("✓ PoeApi imported successfully")
except ImportError as e:
    print(f"❌ Failed to import PoeApi: {e}")
    sys.exit(1)


def main():
    print("🔍 Testing get_chat_history method")
    
    # Use corrected token format
    tokens = {
        "p-b": "AG58MLIXFnbOh98QAv4YHA==",
        "p-lat": "87OepyV2QcF9TkiuqhaFyWZgROH+Vp00g0QZLwZEMg==",
        "formkey": "c25281d6b4dfb3f76fb03c597e3e61aa"
    }
    
    try:
        client = PoeApi(tokens)
        print("✓ PoeApi client created successfully!")
        
        # Test get_chat_history method
        print("\n🧪 Testing get_chat_history()")
        try:
            # Try with no parameters first
            history = client.get_chat_history()
            print(f"✓ get_chat_history() returned: {type(history)}")
            
            if hasattr(history, '__len__'):
                print(f"  Length: {len(history)}")
                
            if hasattr(history, '__iter__') and len(history) > 0:
                print(f"  First item type: {type(history[0])}")
                print(f"  First item: {str(history[0])[:100]}...")
                
            return len(history) > 0
            
        except TypeError as e:
            if "missing" in str(e):
                print(f"⚠️  Method requires parameters: {e}")
                
                # Try with a chat/bot parameter
                print("\n🧪 Trying get_chat_history with bot parameter")
                try:
                    # Get available bots first
                    bots = client.get_available_bots()
                    if bots:
                        first_bot = list(bots.keys())[0] if isinstance(bots, dict) else bots[0]
                        print(f"  Using bot: {first_bot}")
                        
                        history = client.get_chat_history(first_bot)
                        print(f"✓ get_chat_history(bot) returned: {type(history)}")
                        
                        if hasattr(history, '__len__'):
                            print(f"  Length: {len(history)}")
                            
                        return len(history) > 0
                    else:
                        print("  No bots available")
                        
                except Exception as e2:
                    print(f"  Error with bot parameter: {e2}")
                    
                return False
            else:
                print(f"❌ Error calling get_chat_history(): {e}")
                return False
                
        except Exception as e:
            print(f"❌ Error calling get_chat_history(): {e}")
            return False
            
    except Exception as e:
        print(f"❌ Failed to create client: {e}")
        return False


if __name__ == "__main__":
    success = main()
    if success:
        print("\n✅ SUCCESS: Found a working method to get chat data!")
    else:
        print("\n❌ Still need to find the right method/parameters")
