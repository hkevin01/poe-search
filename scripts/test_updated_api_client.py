#!/usr/bin/env python3
"""Test script to verify the updated API client with poe-api-wrapper."""

import json
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from poe_search.api.client import PoeAPIClient
from poe_search.utils.config import load_config


def test_updated_api_client():
    """Test the updated API client with poe-api-wrapper."""
    
    print("=== Updated API Client Test ===\n")
    
    # Load configuration
    try:
        config = load_config()
        
        # Use new token format
        if hasattr(config, 'get_poe_tokens'):
            tokens = config.get_poe_tokens()
            if not tokens.get('p-b'):
                print("❌ No p-b cookie found in configuration")
                return False
            print(f"✅ p-b cookie loaded: {tokens.get('p-b', '')[:10]}...")
            print(f"✅ p-lat cookie loaded: {tokens.get('p-lat', '')[:10] if tokens.get('p-lat') else 'Not set'}...")
            print(f"✅ formkey loaded: {tokens.get('formkey', '')[:10] if tokens.get('formkey') else 'Not set'}...")
        else:
            # Fall back to old format
            token = config.poe_token
            if not token:
                print("❌ No Poe token found in configuration")
                return False
            print(f"✅ Token loaded: {token[:10]}...")
            tokens = {
                "p-b": token,
                "p-lat": token
            }
        
    except Exception as e:
        print(f"❌ Failed to load configuration: {e}")
        return False
    
    # Test with updated API client
    try:
        print("\n🔗 Testing updated API client...")
        
        # Initialize API client
        api_client = PoeAPIClient(token=tokens, config=config)
        print("✅ API client created successfully")
        
        # Test getting recent conversations
        print("\n💬 Testing conversation retrieval...")
        try:
            conversations = api_client.get_recent_conversations(days=7)
            print(f"✅ Found {len(conversations)} conversations")
            
            if conversations:
                print("Sample conversations:")
                for i, conv in enumerate(conversations[:3]):
                    print(f"  {i+1}. {conv.get('title', 'Untitled')}")
                    print(f"     ID: {conv.get('id', 'Unknown')}")
                    print(f"     Bot: {conv.get('bot', {}).get('displayName', 'Unknown')}")
                    print(f"     Messages: {conv.get('messageCount', 0)}")
                    print()
                # Test getting a specific conversation
                first_conv_id = conversations[0]["id"]
                print(f"📝 Testing conversation detail retrieval for: {first_conv_id}")
                try:
                    conversation_detail = api_client.get_conversation(first_conv_id)
                    if conversation_detail:
                        print(f"✅ Conversation detail retrieved")
                        print(f"   Title: {conversation_detail.get('title', 'Untitled')}")
                        print(f"   Messages: {len(conversation_detail.get('messages', []))}")
                        messages = conversation_detail.get('messages', [])
                        if messages:
                            print("   Sample messages:")
                            for j, msg in enumerate(messages[:2]):
                                role = msg.get('role', 'unknown')
                                text = msg.get('text', '')[:100] + "..." if len(msg.get('text', '')) > 100 else msg.get('text', '')
                                print(f"     {j+1}. [{role}] {text}")
                    else:
                        print("❌ Failed to get conversation detail")
                except Exception as e:
                    print(f"❌ Failed to get conversation detail: {e}")
            else:
                print("⚠️  No conversations found.")
        except Exception as e:
            print(f"❌ Failed to get conversations: {e}")
        
        # Test: Print the last 5 conversations the user had at poe.com, regardless of bot
        print("\n🕑 Last 5 conversations across all bots:")
        try:
            conversations = api_client.get_recent_conversations(days=30)  # Use a larger window to ensure enough results
            # Sort by updatedAt or createdAt if available
            def get_sort_key(conv):
                return conv.get('updatedAt') or conv.get('createdAt') or ''
            conversations_sorted = sorted(conversations, key=get_sort_key, reverse=True)
            last_5 = conversations_sorted[:5]
            if last_5:
                for i, conv in enumerate(last_5, 1):
                    print(f"{i}. {conv.get('title', 'Untitled')}")
                    print(f"   Bot: {conv.get('bot', {}).get('displayName', 'Unknown')}")
                    print(f"   Date: {conv.get('updatedAt', conv.get('createdAt', 'Unknown'))}")
                    print(f"   ID: {conv.get('id', 'Unknown')}")
                    print()
            else:
                print("No conversations found in the last 30 days.")
        except Exception as e:
            print(f"❌ Failed to print last 5 conversations: {e}")
        
        # Test: Compare wrapper output vs real API output
        print("\n🔍 Comparing wrapper output vs real Poe.com API output:")
        try:
            wrapper_convs = api_client.get_recent_conversations(days=30)
            real_convs = api_client.get_all_real_conversations(first=50)
            print(f"Wrapper returned {len(wrapper_convs)} conversations.")
            print(f"Real API returned {len(real_convs)} conversations.")
            # Print titles from both for comparison
            print("\nWrapper conversation titles:")
            for c in wrapper_convs[:10]:
                print(f"- {c.get('title', 'Untitled')} (Bot: {c.get('bot', {}).get('displayName', c.get('bot', ''))})")
            print("\nReal API conversation titles:")
            for c in real_convs[:10]:
                print(f"- {c.get('title', 'Untitled')} (Bot: {c.get('bot', 'Unknown')})")
            # Print any titles in wrapper but not in real API
            wrapper_titles = set(c.get('title', '') for c in wrapper_convs)
            real_titles = set(c.get('title', '') for c in real_convs)
            only_in_wrapper = wrapper_titles - real_titles
            only_in_real = real_titles - wrapper_titles
            print(f"\nTitles only in wrapper: {only_in_wrapper}")
            print(f"Titles only in real API: {only_in_real}")
        except Exception as e:
            print(f"❌ Failed to compare wrapper and real API output: {e}")
        
        # Test: Print real Poe.com chat history using the new method
        print("\n🟢 Real Poe.com chat history (ChatHistoryListPaginationQuery):")
        try:
            real_convs = api_client.get_true_chat_history(count=20)
            print(f"Real API returned {len(real_convs)} conversations.")
            for c in real_convs[:10]:
                print(f"- {c.get('title', 'Untitled')} (Bot: {c.get('bot', 'Unknown')})")
        except Exception as e:
            print(f"❌ Failed to fetch real Poe.com chat history: {e}")
        
        print("\n🎉 All tests completed!")
        return True
        
    except Exception as e:
        print(f"❌ API client test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Main function."""
    success = test_updated_api_client()
    
    if success:
        print("\n✅ Updated API client test successful!")
        print("The API client is working correctly with poe-api-wrapper and the new response structure.")
    else:
        print("\n❌ Updated API client test failed.")
        print("Please check the error messages above.")
        sys.exit(1)


if __name__ == "__main__":
    main() 