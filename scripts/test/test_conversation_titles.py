#!/usr/bin/env python3
"""Test script to fetch and display the last 5 conversation titles from Poe.com."""

import json
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from poe_search.api.client import PoeAPIClient
from poe_search.utils.config import load_config

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def test_conversation_titles():
    """Test fetching and displaying the last 5 conversation titles."""
    
    print("🔍 Fetching Last 5 Poe.com Conversations")
    print("=" * 50)
    
    try:
        # Load configuration
        print("📋 Loading configuration...")
        config = load_config()
        
        if not config.has_valid_tokens():
            print("❌ No valid Poe tokens found in configuration")
            print("Please ensure your tokens are properly configured.")
            return False
        
        tokens = config.get_poe_tokens()
        print(f"✅ Configuration loaded with tokens (p-b: {tokens.get('p-b', '')[:10]}...)")
        
        # Initialize API client
        print("🔗 Initializing Poe API client...")
        client = PoeAPIClient(token=tokens, config=config)
        
        if not client.client:
            print("❌ Failed to initialize Poe API client")
            return False
        
        print("✅ Poe API client initialized successfully")
        
        # Try direct API calls to debug the response format
        print("\n🔍 Debugging API responses...")
        
        # Test 1: Try to get chat history directly from the poe-api-wrapper
        try:
            print("Testing direct API call to get chat history...")
            
            # Try with a popular bot
            bot_id = "chinchilla"  # ChatGPT
            print(f"Getting chat history for bot: {bot_id}")
            
            # Call the API directly to see the raw response
            raw_response = client.client.get_chat_history(bot_id, count=5)
            
            print("\n===== FULL RAW RESPONSE FROM API =====")
            import pprint
            pprint.pprint(raw_response)
            print("===== END RAW RESPONSE =====\n")
            
            print(f"Raw response type: {type(raw_response)}")
            print(f"Raw response length: {len(raw_response) if hasattr(raw_response, '__len__') else 'N/A'}")
            
            if raw_response:
                if isinstance(raw_response, dict):
                    print(f"Raw response keys: {list(raw_response.keys())}")
                elif hasattr(raw_response, '__len__') and len(raw_response) > 0:
                    print(f"First item type: {type(raw_response[0])}")
                    print(f"First item: {raw_response[0]}")
            
            # Try to process the response manually
            if isinstance(raw_response, list) and len(raw_response) > 0:
                print(f"\n📋 Found {len(raw_response)} conversations:")
                print("-" * 50)
                
                for i, conv in enumerate(raw_response[:5], 1):
                    if isinstance(conv, dict):
                        title = conv.get('title', 'Untitled')
                        conv_id = conv.get('chatId', 'Unknown ID')
                        bot_name = conv.get('bot', {}).get('displayName', bot_id)
                        message_count = conv.get('messageCount', 0)
                        
                        print(f"{i}. {title}")
                        print(f"   🤖 Bot: {bot_name}")
                        print(f"   💬 Messages: {message_count}")
                        print(f"   🆔 ID: {conv_id}")
                        print()
                    else:
                        print(f"{i}. Raw conversation data: {conv}")
                        print()
                
                return True
            else:
                print("No conversations found or unexpected response format")
                
        except Exception as e:
            print(f"Direct API call failed: {e}")
            logger.exception("Detailed error for direct API call:")
        
        # Test 2: Try the wrapper method with better error handling
        print("\n🔄 Trying wrapper method with better error handling...")
        try:
            conversations = client.get_recent_conversations(days=7)
            
            if conversations and len(conversations) > 0:
                print(f"✅ Found {len(conversations)} conversations via wrapper")
                
                # Sort conversations by updated date (most recent first)
                sorted_conversations = sorted(
                    conversations, 
                    key=lambda x: x.get('updatedAt', ''), 
                    reverse=True
                )
                
                # Get the last 5 conversations
                last_5_conversations = sorted_conversations[:5]
                
                print(f"\n📋 Last 5 Conversations:")
                print("-" * 50)
                
                for i, conv in enumerate(last_5_conversations, 1):
                    title = conv.get('title', 'Untitled')
                    conv_id = conv.get('id', 'Unknown ID')
                    updated_at = conv.get('updatedAt', 'Unknown date')
                    bot_name = conv.get('bot', {}).get('displayName', 'Unknown bot')
                    message_count = conv.get('messageCount', 0)
                    
                    # Try to parse and format the date
                    try:
                        if updated_at and updated_at != 'Unknown date':
                            # Handle different date formats
                            if 'T' in updated_at:
                                dt = datetime.fromisoformat(updated_at.replace('Z', '+00:00'))
                            else:
                                dt = datetime.fromisoformat(updated_at)
                            formatted_date = dt.strftime('%Y-%m-%d %H:%M')
                        else:
                            formatted_date = 'Unknown date'
                    except:
                        formatted_date = updated_at
                    
                    print(f"{i}. {title}")
                    print(f"   🤖 Bot: {bot_name}")
                    print(f"   📅 Updated: {formatted_date}")
                    print(f"   💬 Messages: {message_count}")
                    print(f"   🆔 ID: {conv_id}")
                    print()
                
                return True
            else:
                print("⚠️  No conversations found via wrapper method")
                
        except Exception as e:
            print(f"Wrapper method failed: {e}")
            logger.exception("Detailed error for wrapper method:")
        
        # Test 3: Try to get user info to verify connection
        print("\n👤 Testing user info retrieval...")
        try:
            # Try to get user settings or info
            user_info = client.client.get_user_info()
            if user_info:
                print(f"✅ User info retrieved: {user_info}")
            else:
                print("⚠️  No user info available")
        except Exception as e:
            print(f"User info retrieval failed: {e}")
        
        print("\n💡 Summary:")
        print("The API connection is working, but there may be issues with:")
        print("1. Response format changes in poe-api-wrapper")
        print("2. API endpoint changes on Poe.com")
        print("3. Token permissions or rate limiting")
        
        return False
        
    except Exception as e:
        print(f"❌ Error during test: {e}")
        logger.exception("Detailed error information:")
        return False


def main():
    """Main function to run the conversation titles test."""
    success = test_conversation_titles()
    
    if success:
        print("\n✅ Test completed successfully!")
        return 0
    else:
        print("\n❌ Test completed with issues - check the output above for details")
        return 1


if __name__ == "__main__":
    sys.exit(main()) 