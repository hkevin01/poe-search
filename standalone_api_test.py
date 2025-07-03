#!/usr/bin/env python3
"""Standalone test script for Poe API connectivity."""

import os
import sys
import threading
import time

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from poe_search.api.client import PoeAPIClient
from poe_search.utils.config import load_poe_tokens_from_file


def test_with_timeout(timeout_seconds=30):
    """Run API test with timeout."""
    result = {"success": False, "error": None}
    
    def run_test():
        try:
            print("Loading tokens...")
            tokens = load_poe_tokens_from_file()
            
            print("Creating API client...")
            client = PoeAPIClient(token=tokens)
            
            print("Testing get_bots()...")
            bots = client.get_bots()
            
            print(f"✓ get_bots() returned {len(bots)} bots")
            
            print("Testing get_conversation_ids()...")
            conv_ids = client.get_conversation_ids()
            
            print(f"✓ get_conversation_ids() returned {len(conv_ids)} IDs")
            
            if conv_ids:
                print("Testing get_conversation()...")
                conversation = client.get_conversation(conv_ids[0])
                print(f"✓ get_conversation() returned: {type(conversation)}")
            
            result["success"] = True
            
        except Exception as e:
            result["error"] = str(e)
            print(f"✗ Error: {e}")
    
    # Run test in thread with timeout
    test_thread = threading.Thread(target=run_test)
    test_thread.daemon = True
    test_thread.start()
    test_thread.join(timeout=timeout_seconds)
    
    if test_thread.is_alive():
        print(f"✗ Test timed out after {timeout_seconds} seconds")
        return False
    
    return result["success"]


if __name__ == "__main__":
    print("=== Poe API Connectivity Test ===")
    success = test_with_timeout(30)
    
    if success:
        print("\n✓ All tests PASSED!")
        sys.exit(0)
    else:
        print("\n✗ Tests FAILED!")
        sys.exit(1)
