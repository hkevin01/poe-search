#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, '/home/kevin/Projects/poe-search/src')

print("Testing basic API client import and creation...")

try:
    from poe_search.api.client import PoeAPIClient
    print("✅ Successfully imported PoeAPIClient")
    
    # Test with your actual token
    with open('/home/kevin/Projects/poe-search/config/poe_tokens.json') as f:
        import json
        tokens = json.load(f)
    
    print("✅ Loaded tokens from config")
    
    # Create client
    client = PoeAPIClient(token=tokens['p-b'])
    print("✅ Successfully created PoeAPIClient")
    
    # Check what attributes it has
    print("Client attributes:", [attr for attr in dir(client) if not attr.startswith('_')])
    
    # Test connection
    print("Testing connection...")
    result = client.test_connection()
    print(f"Connection test result: {result}")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()