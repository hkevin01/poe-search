#!/usr/bin/env python3
"""
Simple test to check if bot discovery fix works
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
    print("🔍 Testing bot discovery fix")
    
    # Use corrected token format
    tokens = {
        "p-b": "AG58MLIXFnbOh98QAv4YHA==",
        "p-lat": "87OepyV2QcF9TkiuqhaFyWZgROH+Vp00g0QZLwZEMg==",
        "formkey": "c25281d6b4dfb3f76fb03c597e3e61aa"
    }
    
    try:
        client = PoeApi(tokens)
        print("✓ PoeApi client created successfully!")
        
        # Test get_available_bots
        print("\n🧪 Testing get_available_bots()")
        try:
            bots = client.get_available_bots()
            print(f"✓ get_available_bots() returned: {type(bots)}")
            
            if isinstance(bots, dict):
                bot_ids = list(bots.keys())
                print(f"  Found {len(bot_ids)} bots (dict format)")
                if len(bot_ids) > 0:
                    print(f"  First few bots: {bot_ids[:5]}")
            elif isinstance(bots, list):
                print(f"  Found {len(bots)} bots (list format)")
                if len(bots) > 0:
                    print(f"  First few bots: {bots[:5]}")
            else:
                print(f"  Unexpected format: {bots}")
                
            return len(bot_ids) > 0 if isinstance(bots, dict) else len(bots) > 0
            
        except Exception as e:
            print(f"❌ get_available_bots() failed: {e}")
            return False
            
    except Exception as e:
        print(f"❌ Failed to create client: {e}")
        return False


if __name__ == "__main__":
    success = main()
    if success:
        print("\n✅ Bot discovery is working!")
    else:
        print("\n❌ Bot discovery failed")
