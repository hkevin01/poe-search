#!/usr/bin/env python3
"""
Test specific API methods with timeouts
"""

import sys
import os
import signal
import time
from threading import Thread

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

try:
    from poe_api_wrapper import PoeApi
    print("✓ PoeApi imported successfully")
except ImportError as e:
    print(f"❌ Failed to import PoeApi: {e}")
    sys.exit(1)


def timeout_handler(signum, frame):
    raise TimeoutError("Function call timed out")


def test_method_with_timeout(client, method_name, timeout_seconds=15):
    """Test a client method with a timeout."""
    print(f"  Testing {method_name}() with {timeout_seconds}s timeout...")
    
    # Set up timeout
    signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(timeout_seconds)
    
    try:
        method = getattr(client, method_name)
        result = method()
        signal.alarm(0)  # Cancel timeout
        print(f"    ✓ {method_name}() succeeded: {type(result)}")
        
        if hasattr(result, '__len__'):
            print(f"      Length: {len(result)}")
            
        return True, result
        
    except TimeoutError:
        signal.alarm(0)  # Cancel timeout
        print(f"    ⏰ {method_name}() timed out after {timeout_seconds}s")
        return False, None
        
    except Exception as e:
        signal.alarm(0)  # Cancel timeout  
        print(f"    ❌ {method_name}() failed: {e}")
        return False, None


def main():
    print("🔍 Testing specific API methods")
    
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
        
        # Test various methods
        methods_to_test = [
            ('get_settings', 10),
            ('get_available_bots', 15),
            ('get_chat_history', 20),  # This might need a bot parameter
        ]
        
        results = {}
        for method_name, timeout in methods_to_test:
            success, result = test_method_with_timeout(client, method_name, timeout)
            results[method_name] = (success, result)
        
        print(f"\n📊 Summary:")
        for method_name, (success, result) in results.items():
            status = "✓" if success else "❌"
            print(f"  {status} {method_name}")
            
        # If get_available_bots worked, try to use it for get_chat_history
        if results['get_available_bots'][0]:
            bots = results['get_available_bots'][1]
            if isinstance(bots, dict) and len(bots) > 0:
                first_bot = list(bots.keys())[0]
                print(f"\n🧪 Testing get_chat_history with bot: {first_bot}")
                
                try:
                    signal.signal(signal.SIGALRM, timeout_handler)
                    signal.alarm(20)
                    history = client.get_chat_history(first_bot)
                    signal.alarm(0)
                    print(f"  ✓ get_chat_history({first_bot}) succeeded: {type(history)}")
                    if hasattr(history, '__len__'):
                        print(f"    Found {len(history)} items")
                except TimeoutError:
                    signal.alarm(0)
                    print(f"  ⏰ get_chat_history({first_bot}) timed out")
                except Exception as e:
                    signal.alarm(0)
                    print(f"  ❌ get_chat_history({first_bot}) failed: {e}")
        
        return True
            
    except Exception as e:
        print(f"❌ Client creation failed: {e}")
        return False


if __name__ == "__main__":
    success = main()
    if success:
        print("\n✅ Method testing completed")
    else:
        print("\n❌ Testing failed")
