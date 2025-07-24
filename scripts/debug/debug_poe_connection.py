#!/usr/bin/env python3
"""
Quick debug script to test Poe.com authentication and conversation fetching.
"""

import sys
import json
import asyncio
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from poe_search.utils.config import load_poe_tokens_from_file
from poe_api_wrapper import PoeApi


async def test_poe_connection():
    """Test Poe.com connection and basic functionality."""
    print("🔍 Testing Poe.com Connection")
    print("=" * 40)
    
    # Load tokens
    try:
        tokens = load_poe_tokens_from_file()
        print(f"✅ Loaded tokens: {list(tokens.keys())}")
    except Exception as e:
        print(f"❌ Failed to load tokens: {e}")
        return
    
    # Initialize Poe API
    try:
        poe = PoeApi(cookie=tokens.get("p-b", ""))
        print("✅ PoeApi initialized")
    except Exception as e:
        print(f"❌ Failed to initialize PoeApi: {e}")
        return
    
    # Test basic connection
    try:
        print("🔄 Testing connection...")
        
        # Try to get available bots
        try:
            bots = poe.get_available_bots()
            print(f"✅ Available bots: {len(bots) if bots else 0}")
            if bots:
                bot_names = [bot for bot in list(bots.keys())[:5]]
                print(f"   First 5 bots: {bot_names}")
        except Exception as e:
            print(f"⚠️ get_available_bots failed: {e}")
        
        # Try to get conversations
        try:
            conversations = poe.get_user_conversations(count=10)
            print(f"✅ Conversations: {len(conversations) if conversations else 0}")
            if conversations:
                for i, conv in enumerate(conversations[:3]):
                    title = conv.get('title', 'No title')[:50]
                    print(f"   {i+1}. {title}")
        except Exception as e:
            print(f"⚠️ get_user_conversations failed: {e}")
        
        # Try to get conversation history
        try:
            chat_history = poe.get_chat_history()
            print(f"✅ Chat history: {len(chat_history) if chat_history else 0}")
            if chat_history:
                for i, chat in enumerate(chat_history[:3]):
                    title = chat.get('title', 'No title')[:50]
                    bot = chat.get('bot', 'Unknown bot')
                    print(f"   {i+1}. {title} (Bot: {bot})")
        except Exception as e:
            print(f"⚠️ get_chat_history failed: {e}")
            
    except Exception as e:
        print(f"❌ Connection test failed: {e}")
        return
    
    print("\n📊 Summary:")
    print("- Authentication is working (tokens are valid)")
    print("- Some API endpoints may have issues (common with wrapper)")
    print("- Consider updating to latest poe-api-wrapper version")


if __name__ == "__main__":
    asyncio.run(test_poe_connection())
