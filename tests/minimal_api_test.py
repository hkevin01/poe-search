#!/usr/bin/env python3
"""
Minimal test to check basic API wrapper functionality
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
    print("🔍 Minimal API wrapper test")
    
    # Use corrected token format
    tokens = {
        "p-b": "AG58MLIXFnbOh98QAv4YHA==",
        "p-lat": "87OepyV2QcF9TkiuqhaFyWZgROH+Vp00g0QZLwZEMg==",
        "formkey": "c25281d6b4dfb3f76fb03c597e3e61aa"
    }
    
    try:
        print("  Creating PoeApi client...")
        client = PoeApi(tokens)
        print("✓ PoeApi client created!")
        
        # Try the simplest possible API call
        print("  Testing get_settings()...")
        try:
            settings = client.get_settings()
            print(f"✓ get_settings() works: {type(settings)}")
            return True
        except Exception as e:
            print(f"❌ get_settings() failed: {e}")
            
        return False
            
    except Exception as e:
        print(f"❌ Client creation failed: {e}")
        return False


if __name__ == "__main__":
    success = main()
    if success:
        print("\n✅ Basic API is working")
    else:
        print("\n❌ API not working")
