#!/bin/bash
cd ~/Projects/poe-search
source venv/bin/activate
python << 'EOF'
import sys
import os
sys.path.insert(0, '/home/kevin/Projects/poe-search/src')

print("=== Debug: Testing with venv activated ===")

try:
    # Test 1: Load config
    print("1. Testing config loading...")
    from poe_search.config import load_config
    config = load_config()
    print("✅ Config loaded successfully")
    
    # Test 2: Create main client
    print("2. Testing main client creation...")
    from poe_search.client import PoeSearchClient
    main_client = PoeSearchClient()
    print("✅ Main client created")
    
    # Test 3: Test API connection (this is where the error likely occurs)
    print("3. Testing API connection...")
    result = main_client.test_api_connection()
    print(f"✅ API connection test result: {result}")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
EOF