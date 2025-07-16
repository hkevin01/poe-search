#!/usr/bin/env python3
"""
Test to discover available methods on PoeApi object
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
    print("🔍 Discovering PoeApi methods")
    
    # Use corrected token format
    tokens = {
        "p-b": "AG58MLIXFnbOh98QAv4YHA==",
        "p-lat": "87OepyV2QcF9TkiuqhaFyWZgROH+Vp00g0QZLwZEMg==", 
        "formkey": "c25281d6b4dfb3f76fb03c597e3e61aa"
    }
    
    try:
        client = PoeApi(tokens)
        print("✓ PoeApi client created successfully!")
        
        # Get all methods and attributes
        methods = [method for method in dir(client) if not method.startswith('_')]
        print(f"\n📋 Available methods and attributes ({len(methods)}):")
        
        for method in sorted(methods):
            attr = getattr(client, method)
            if callable(attr):
                print(f"  🔧 {method}() - method")
            else:
                print(f"  📄 {method} - attribute")
        
        # Look specifically for conversation-related methods
        conv_methods = [m for m in methods if 'conv' in m.lower()]
        if conv_methods:
            print(f"\n💬 Conversation-related methods:")
            for method in conv_methods:
                print(f"  {method}")
        
        # Look for history/chat related methods
        history_methods = [m for m in methods if any(word in m.lower() for word in ['history', 'chat', 'message', 'get_'])]
        if history_methods:
            print(f"\n📜 History/chat related methods:")
            for method in history_methods:
                print(f"  {method}")
                
        # Test some promising methods
        test_methods = ['get_conversations', 'get_chat_history', 'get_chats', 'conversations']
        print(f"\n🧪 Testing common method names:")
        for method_name in test_methods:
            if hasattr(client, method_name):
                method = getattr(client, method_name)
                if callable(method):
                    print(f"  ✓ {method_name}() exists - trying to call it")
                    try:
                        result = method()
                        print(f"    → Result type: {type(result)}")
                        if hasattr(result, '__len__'):
                            print(f"    → Length: {len(result)}")
                    except Exception as e:
                        print(f"    → Error: {e}")
                else:
                    print(f"  📄 {method_name} exists but is not callable")
            else:
                print(f"  ❌ {method_name} does not exist")
                
    except Exception as e:
        print(f"❌ Failed to create client: {e}")
        return False


if __name__ == "__main__":
    main()
