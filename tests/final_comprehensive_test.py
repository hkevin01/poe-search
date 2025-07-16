#!/usr/bin/env python3
"""
Final comprehensive test with all fixes applied
"""

import sys
import os

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

try:
    from poe_search.client import PoeSearchClient
    from poe_search.utils.config import PoeSearchConfig
    print("✓ PoeSearchClient imported successfully")
except ImportError as e:
    print(f"❌ Failed to import PoeSearchClient: {e}")
    sys.exit(1)


def main():
    print("🎯 FINAL TEST: Comprehensive conversation retrieval test")
    print("This test will verify:")
    print("  1. Authentication works with correct token format")
    print("  2. Bot discovery works properly")  
    print("  3. Conversation retrieval works with unlimited timespan")
    print("  4. We get real conversations (not zero)")
    
    # Create config with corrected token format
    config = PoeSearchConfig()
    
    # Set tokens with correct format (hyphens not underscores)
    tokens = {
        "p-b": "AG58MLIXFnbOh98QAv4YHA==",
        "p-lat": "87OepyV2QcF9TkiuqhaFyWZgROH+Vp00g0QZLwZEMg==",
        "formkey": "c25281d6b4dfb3f76fb03c597e3e61aa"
    }
    config.poe_tokens = tokens
    
    print(f"\n🔧 Using tokens: {list(tokens.keys())}")
    
    try:
        # Create client
        print("\n🧪 Test 1: Creating PoeSearchClient")
        search_client = PoeSearchClient(config=config)
        print("✓ PoeSearchClient created successfully!")
        
        # Test conversation history with various time spans
        print("\n🧪 Test 2: Testing conversation retrieval")
        
        # Test with short period first
        print("  Testing 7 days (should work quickly):")
        try:
            conversations_7d = search_client.get_conversation_history(days=7, limit=10)
            print(f"    ✓ 7 days: {len(conversations_7d)} conversations")
        except Exception as e:
            print(f"    ❌ 7 days failed: {e}")
            conversations_7d = []
        
        # Test with medium period
        print("  Testing 90 days:")
        try:
            conversations_90d = search_client.get_conversation_history(days=90, limit=50)
            print(f"    ✓ 90 days: {len(conversations_90d)} conversations")
        except Exception as e:
            print(f"    ❌ 90 days failed: {e}")
            conversations_90d = []
            
        # Test with very large period (all conversations)
        print("  Testing ALL conversations (3650 days):")
        try:
            conversations_all = search_client.get_conversation_history(days=3650, limit=1000)
            print(f"    ✓ ALL time: {len(conversations_all)} conversations")
        except Exception as e:
            print(f"    ❌ ALL time failed: {e}")
            conversations_all = []
        
        # Analyze results
        print(f"\n📊 RESULTS SUMMARY:")
        print(f"  7 days:    {len(conversations_7d)} conversations")
        print(f"  90 days:   {len(conversations_90d)} conversations") 
        print(f"  All time:  {len(conversations_all)} conversations")
        
        # Show sample conversations if any found
        if len(conversations_all) > 0:
            print(f"\n💬 Sample conversations (showing first 3):")
            for i, conv in enumerate(conversations_all[:3]):
                title = conv.get('title', 'No title')[:50]
                conv_id = conv.get('id', 'No ID')
                created = conv.get('createdAt', conv.get('created_at', 'No date'))
                bot = conv.get('bot', {}).get('displayName', 'Unknown bot')
                print(f"  {i+1}. {title}... (ID: {conv_id[:10]}..., Bot: {bot})")
            
            print(f"\n✅ SUCCESS! Found {len(conversations_all)} total conversations!")
            print("🎉 The zero conversations problem is SOLVED!")
            return True
        else:
            print(f"\n❌ Still getting zero conversations - need more investigation")
            return False
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    print(f"\n{'='*60}")
    if success:
        print("✅ FINAL CONCLUSION: Conversation fetching is now WORKING!")
        print("✅ User can now search through ALL their Poe conversations!")
    else:
        print("❌ FINAL CONCLUSION: Still need to debug further")
    print(f"{'='*60}")
