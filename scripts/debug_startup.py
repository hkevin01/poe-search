#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, '/home/kevin/Projects/poe-search/src')

print("=== Debug: Testing token loading and API client creation ===")

try:
    # Test 1: Load config
    print("1. Testing config loading...")
    from poe_search.config import load_config
    config = load_config()
    print("✅ Config loaded successfully")
    
    # Test 2: Load tokens
    print("2. Testing token loading...")
    tokens = config.get_poe_tokens() if hasattr(config, 'get_poe_tokens') else None
    print(f"✅ Tokens loaded: {bool(tokens)}")
    
    # Test 3: Create main client
    print("3. Testing main client creation...")
    from poe_search.client import PoeSearchClient
    main_client = PoeSearchClient()
    print("✅ Main client created")
    
    # Test 4: Test API connection (this is where the error likely occurs)
    print("4. Testing API connection...")
    result = main_client.test_api_connection()
    print(f"✅ API connection test result: {result}")
    
except Exception as e:
    print(f"❌ Error at step: {e}")
    import traceback
    traceback.print_exc()