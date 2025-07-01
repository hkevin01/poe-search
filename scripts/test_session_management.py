#!/usr/bin/env python3
"""Test script for session management functionality."""

import json
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from poe_search.utils.browser_tokens import (
    load_session, save_session, is_session_valid, 
    clear_session, force_relogin, refresh_tokens_if_needed
)


def test_session_management():
    """Test session management functionality."""
    
    print("=== Session Management Test ===\n")
    
    # Test 1: Check if session exists
    print("1. Checking for existing session...")
    session = load_session()
    if session:
        print(f"   ✅ Session found: {session.get('username', 'Unknown')}")
        print(f"   ✅ Expires: {session.get('expires_at', 'Unknown')}")
        print(f"   ✅ Valid: {is_session_valid(session)}")
    else:
        print("   ❌ No session found")
    
    # Test 2: Test token refresh
    print("\n2. Testing token refresh...")
    try:
        tokens = refresh_tokens_if_needed()
        if tokens and tokens.get('p-b'):
            print(f"   ✅ Tokens obtained: {tokens.get('p-b', '')[:10]}...")
        else:
            print("   ❌ Failed to obtain tokens")
    except Exception as e:
        print(f"   ❌ Token refresh failed: {e}")
    
    # Test 3: Check session again
    print("\n3. Checking session after refresh...")
    session = load_session()
    if session:
        print(f"   ✅ Session updated: {session.get('username', 'Unknown')}")
        print(f"   ✅ Valid: {is_session_valid(session)}")
    else:
        print("   ❌ No session found after refresh")
    
    print("\n=== Session Management Test Complete ===")
    print("\nAvailable commands:")
    print("- 'clear' to clear session data")
    print("- 'relogin' to force re-login")
    print("- 'quit' to exit")
    
    while True:
        command = input("\nEnter command: ").strip().lower()
        
        if command == 'clear':
            print("Clearing session data...")
            clear_session()
            print("✅ Session data cleared")
            
        elif command == 'relogin':
            print("Forcing re-login...")
            try:
                tokens = force_relogin()
                if tokens and tokens.get('p-b'):
                    print("✅ Re-login successful")
                else:
                    print("❌ Re-login failed")
            except Exception as e:
                print(f"❌ Re-login error: {e}")
                
        elif command == 'quit':
            print("Goodbye!")
            break
            
        else:
            print("Unknown command. Use 'clear', 'relogin', or 'quit'")


if __name__ == "__main__":
    test_session_management() 