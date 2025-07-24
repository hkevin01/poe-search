#!/usr/bin/env python3
"""
Focused GraphQL debug script for Poe.com API
"""
import json
import sys
from pathlib import Path

# Add the src directory to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from poe_search.api.direct_client import DirectPoeClient

def test_poe_graphql():
    """Test GraphQL queries step by step"""
    
    print("🔍 Starting Poe GraphQL Debug...")
    
    # Get tokens first
    print("\n0️⃣ Getting Poe tokens...")
    try:
        from poe_search.utils.browser_tokens import refresh_tokens_if_needed
        tokens = refresh_tokens_if_needed()
        
        if not tokens:
            print("   ❌ Failed to get tokens")
            return
            
        print(f"   ✅ Got tokens: formkey={tokens.get('formkey', 'None')[:15]}...")
        print(f"              p-b={tokens.get('p-b', 'None')[:15]}...")
        
    except Exception as e:
        print(f"   ❌ Token extraction failed: {e}")
        return
    
    # Initialize client with tokens
    print("\n1️⃣ Initializing DirectPoeClient...")
    try:
        client = DirectPoeClient(
            formkey=tokens['formkey'],
            token=tokens['p-b']
        )
        print("   ✅ Client initialized")
    except Exception as e:
        print(f"   ❌ Client initialization failed: {e}")
        return
    
    # Test 2: Basic connection
    print("\n2️⃣ Testing basic connection...")
    try:
        result = client.test_connection()
        print(f"   ✅ Result: {result}")
        if not result:
            print("   ❌ Connection failed, stopping")
            return
    except Exception as e:
        print(f"   ❌ Exception: {e}")
        return
    
    # Test 3: Get conversations
    print("\n3️⃣ Testing conversation retrieval...")
    try:
        conversations = client.get_conversations(limit=5)
        print(f"   ✅ Retrieved {len(conversations)} conversations")
        
        if conversations:
            print("   📋 Sample conversations:")
            for i, conv in enumerate(conversations[:3]):
                print(f"      {i+1}. {conv.get('title', 'No title')}")
        else:
            print("   ⚠️ No conversations found")
            
    except Exception as e:
        print(f"   ❌ Exception: {e}")
        import traceback
        traceback.print_exc()
    
    # Test 4: Manual GraphQL call with debugging
    print("\n4️⃣ Manual GraphQL debugging...")
    
    # Get credentials for manual test
    credentials = {'formkey': tokens['formkey'], 'p-b': tokens['p-b']}
    print(f"   📋 Credentials: formkey={credentials.get('formkey', 'None')[:15]}...")
    
    # Simple GraphQL query
    import httpx
    
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Origin": "https://poe.com",
        "Referer": "https://poe.com/",
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36",
        "Cookie": f"formkey={credentials.get('formkey')}; p-b={credentials.get('p-b')}",
        "poe-formkey": credentials.get('formkey', ''),
    }
    
    # Try a simple viewer query first
    simple_query = {
        "query": "query { viewer { id handle } }",
        "variables": {}
    }
    
    with httpx.Client(http2=True, verify=False) as http_client:
        try:
            print("   📤 Sending simple viewer query...")
            response = http_client.post(
                "https://poe.com/api/gql_POST",
                json=simple_query,
                headers=headers,
                timeout=30.0
            )
            
            print(f"   📥 Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"   📥 Response: {json.dumps(data, indent=4)}")
            else:
                print(f"   ❌ Error response: {response.text[:500]}")
                
        except Exception as e:
            print(f"   ❌ Manual GraphQL failed: {e}")


if __name__ == "__main__":
    test_poe_graphql()
