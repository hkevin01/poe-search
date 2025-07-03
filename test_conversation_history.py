"""Test script specifically for retrieving prior conversations from Poe.com."""

import json
import sys
from datetime import datetime, timedelta
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from poe_search.api.client import PoeAPIClient
from poe_search.utils.config import load_poe_tokens_from_file


def test_conversation_history():
    """Test retrieving conversation history with different parameters."""
    print("="*60)
    print("TESTING CONVERSATION HISTORY RETRIEVAL")
    print("="*60)
    
    # Load tokens
    print("1. Loading tokens...")
    try:
        tokens = load_poe_tokens_from_file()
        print(f"   ✅ Tokens loaded: p-b={bool(tokens.get('p-b'))}, "
              f"p-lat={bool(tokens.get('p-lat'))}, formkey={bool(tokens.get('formkey'))}")
    except Exception as e:
        print(f"   ❌ Failed to load tokens: {e}")
        return False
    
    # Initialize client
    print("\n2. Initializing API client...")
    try:
        client = PoeAPIClient(token=tokens)
        if client.client:
            print("   ✅ API client initialized successfully")
        else:
            print("   ⚠️  API client initialized but underlying client is None")
    except Exception as e:
        print(f"   ❌ Failed to initialize client: {e}")
        return False
    
    # Test bot retrieval
    print("\n3. Testing bot retrieval...")
    try:
        bots = client.get_bots()
        print(f"   ✅ Retrieved {len(bots)} bots")
        
        # Show available bots
        print("   Available bots:")
        for i, (bot_id, bot_info) in enumerate(list(bots.items())[:10]):
            print(f"     {i+1}. {bot_id}: {bot_info.get('displayName', 'No name')}")
        
        if len(bots) > 10:
            print(f"     ... and {len(bots) - 10} more")
            
    except Exception as e:
        print(f"   ❌ Failed to get bots: {e}")
        return False
    
    # Test conversation ID retrieval with different time ranges
    print("\n4. Testing conversation ID retrieval...")
    time_ranges = [1, 7, 30, 90]
    
    for days in time_ranges:
        try:
            conv_ids = client.get_conversation_ids(days=days)
            print(f"   📅 Last {days} days: {len(conv_ids)} conversation IDs")
            
            if conv_ids:
                print(f"     Sample IDs: {conv_ids[:3]}")
                
        except Exception as e:
            print(f"   ❌ Failed to get IDs for {days} days: {e}")
    
    # Test detailed conversation retrieval
    print("\n5. Testing detailed conversation retrieval...")
    try:
        conversations = client.get_recent_conversations(days=7)
        print(f"   ✅ Retrieved {len(conversations)} detailed conversations")
        
        # Show conversation details
        for i, conv in enumerate(conversations[:5]):
            title = conv.get('title', 'No title')
            created = conv.get('createdAt', 'Unknown date')
            bot = conv.get('bot', 'Unknown bot')
            
            print(f"     {i+1}. {conv['id']}")
            print(f"        Title: {title}")
            print(f"        Bot: {bot}")
            print(f"        Created: {created}")
            print()
            
    except Exception as e:
        print(f"   ❌ Failed to get detailed conversations: {e}")
    
    # Test individual conversation fetching
    print("\n6. Testing individual conversation fetching...")
    try:
        conv_ids = client.get_conversation_ids(days=7)
        if conv_ids:
            test_id = conv_ids[0]
            print(f"   Testing with conversation ID: {test_id}")
            
            conversation = client.get_conversation(test_id)
            if conversation:
                print("   ✅ Successfully retrieved conversation details")
                print(f"     Title: {conversation.get('title', 'No title')}")
                print(f"     Messages: {len(conversation.get('messages', []))}")
                print(f"     Bot: {conversation.get('bot', 'Unknown')}")
                
                # Show first few messages if available
                messages = conversation.get('messages', [])
                if messages:
                    print("     First few messages:")
                    for i, msg in enumerate(messages[:3]):
                        author = msg.get('author', 'Unknown')
                        content = msg.get('content', 'No content')
                        content_preview = content[:100] + "..." if len(content) > 100 else content
                        print(f"       {i+1}. {author}: {content_preview}")
            else:
                print("   ⚠️  Could not retrieve conversation details")
        else:
            print("   ⚠️  No conversation IDs available for testing")
            
    except Exception as e:
        print(f"   ❌ Failed to test individual conversation: {e}")
    
    # Save test results
    print("\n7. Saving test results...")
    try:
        results = {
            "test_timestamp": datetime.now().isoformat(),
            "tokens_loaded": bool(tokens.get('p-b')),
            "client_initialized": client.client is not None,
            "bots_count": len(bots) if 'bots' in locals() else 0,
            "conversation_counts": {}
        }
        
        # Add conversation counts for different time ranges
        for days in time_ranges:
            try:
                conv_ids = client.get_conversation_ids(days=days)
                results["conversation_counts"][f"last_{days}_days"] = len(conv_ids)
            except:
                results["conversation_counts"][f"last_{days}_days"] = 0
        
        # Save to file
        results_file = Path("config/conversation_test_results.json")
        with open(results_file, 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"   ✅ Test results saved to {results_file}")
        
    except Exception as e:
        print(f"   ❌ Failed to save test results: {e}")
    
    print("\n" + "="*60)
    print("CONVERSATION HISTORY TEST COMPLETE")
    print("="*60)
    
    return True


def analyze_token_requirements():
    """Analyze when tokens need to be refreshed."""
    print("\n" + "="*60)
    print("TOKEN REFRESH ANALYSIS")
    print("="*60)
    
    # Check current token file
    token_path = Path("config/poe_tokens.json")
    if token_path.exists():
        stat = token_path.stat()
        modified_time = datetime.fromtimestamp(stat.st_mtime)
        age_hours = (datetime.now() - modified_time).total_seconds() / 3600
        
        print(f"Token file age: {age_hours:.1f} hours")
        
        if age_hours < 24:
            print("   ✅ Tokens are relatively fresh (< 24 hours)")
        elif age_hours < 48:
            print("   ⚠️  Tokens are getting old (24-48 hours)")
        else:
            print("   ❌ Tokens are likely expired (> 48 hours)")
            
        print(f"Last modified: {modified_time}")
        
        # Recommendations
        print("\nRecommendations:")
        if age_hours > 24:
            print("   - Consider refreshing tokens")
            print("   - Run: python scripts/refresh_tokens.py")
        else:
            print("   - Tokens should still be valid")
            print("   - If getting auth errors, refresh anyway")
            
    else:
        print("❌ No token file found!")
        print("   Run: python scripts/refresh_tokens.py")


if __name__ == "__main__":
    print("Poe.com Conversation History Test")
    print("This script tests conversation retrieval functionality")
    print()
    
    success = test_conversation_history()
    analyze_token_requirements()
    
    if success:
        print("\n✅ Test completed successfully!")
    else:
        print("\n❌ Test completed with errors!")
        print("   Check token validity and network connection")
        
    print("\nNext steps:")
    print("1. If tokens are expired, run: python scripts/refresh_tokens.py")
    print("2. Run full test suite: pytest tests/api/test_conversation_retrieval.py -v")
    print("3. Try the GUI: python -m poe_search.gui")
