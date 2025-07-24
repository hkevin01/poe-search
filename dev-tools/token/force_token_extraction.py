#!/usr/bin/env python3
"""
Force proper Poe.com token extraction including formkey
"""
import sys
from pathlib import Path

# Add the src directory to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def force_token_extraction():
    """Force a fresh token extraction using Playwright"""
    
    print("🔄 Forcing fresh token extraction from Poe.com...")
    
    try:
        from poe_search.utils.browser_tokens import get_browser_tokens
        
        # Force Playwright extraction (non-headless so user can see what's happening)
        print("   📱 Launching browser for token extraction...")
        tokens = get_browser_tokens(headless=False, use_google_auth=True)
        
        if tokens:
            print("   ✅ Token extraction successful!")
            print(f"      formkey: {tokens.get('formkey', 'None')[:20]}...")
            print(f"      p-b: {tokens.get('p-b', 'None')[:20]}...")
            print(f"      p-lat: {tokens.get('p-lat', 'None')[:20]}...")
            
            # Test the tokens
            print("\n🧪 Testing extracted tokens...")
            from poe_search.api.direct_client import DirectPoeClient
            
            if tokens.get('formkey') and tokens.get('p-b'):
                client = DirectPoeClient(
                    formkey=tokens['formkey'],
                    token=tokens['p-b']
                )
                
                if client.test_connection():
                    print("   ✅ Connection test successful!")
                    
                    # Try to get conversations
                    conversations = client.get_conversations(limit=5)
                    print(f"   ✅ Retrieved {len(conversations)} conversations")
                    
                    if conversations:
                        print("   📋 Sample conversations:")
                        for i, conv in enumerate(conversations[:3]):
                            print(f"      {i+1}. {conv.get('title', 'No title')}")
                    
                else:
                    print("   ❌ Connection test failed")
            else:
                print("   ❌ Missing required tokens")
                
        else:
            print("   ❌ Token extraction failed")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    force_token_extraction()
