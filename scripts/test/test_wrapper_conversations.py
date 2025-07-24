#!/usr/bin/env python3
"""Detailed test script for wrapper API conversation retrieval."""

import json
import logging
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from poe_search.api.client import PoeAPIClient
from poe_search.utils.config import load_config

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class WrapperConversationTester:
    """Test class for wrapper API conversation retrieval."""
    
    def __init__(self):
        """Initialize the tester."""
        self.config = None
        self.client = None
    
    def setup(self):
        """Set up the test environment."""
        print("🔧 Setting up wrapper conversation tester...")
        
        try:
            # Load configuration
            self.config = load_config()
            print("✅ Configuration loaded")
            
            # Initialize wrapper client
            if self.config.has_valid_tokens():
                tokens = self.config.get_poe_tokens()
                self.client = PoeAPIClient(token=tokens, config=self.config)
                print("✅ Wrapper client initialized")
                return True
            else:
                print("❌ No valid tokens for wrapper client")
                return False
                
        except Exception as e:
            print(f"❌ Setup failed: {e}")
            return False
    
    def test_direct_api_calls(self):
        """Test direct API calls to understand what's available."""
        print(f"\n🔍 Testing direct API calls...")
        
        if not self.client or not self.client.client:
            print("❌ Client not available")
            return
        
        try:
            # Test 1: Get user settings
            print("\n1. Testing user settings...")
            try:
                settings = self.client.client.get_settings()
                print(f"   ✅ Settings retrieved: {type(settings)}")
                if isinstance(settings, dict):
                    print(f"   📊 Settings keys: {list(settings.keys())}")
            except Exception as e:
                print(f"   ❌ Settings failed: {e}")
            
            # Test 2: Get available bots (different method)
            print("\n2. Testing available bots...")
            try:
                # Try different bot retrieval methods
                bots = self.client.client.get_available_bots()
                print(f"   ✅ Bots retrieved: {len(bots) if bots else 0}")
                if bots:
                    print(f"   📊 Sample bots: {bots[:3]}")
            except Exception as e:
                print(f"   ❌ Bots failed: {e}")
            
            # Test 3: Try to get chat history for specific bots
            print("\n3. Testing chat history for specific bots...")
            
            # Common bot IDs to try
            common_bots = [
                "chinchilla",  # ChatGPT
                "a2",          # Claude
                "capybara",    # Sage
                "beaver",      # GPT-4
                "acouchy",     # Claude+
                "agouti",      # ChatGPT
                "llama_2_70b", # Llama
                "gemini_pro",  # Gemini
            ]
            
            for bot_id in common_bots:
                try:
                    print(f"   🔍 Trying bot: {bot_id}")
                    history = self.client.client.get_chat_history(bot_id, count=5)
                    
                    if history:
                        print(f"   ✅ Found {len(history)} conversations for {bot_id}")
                        if isinstance(history, list) and history:
                            print(f"   📝 Sample conversation: {history[0].get('title', 'Untitled')}")
                            break
                    else:
                        print(f"   ⚠️  No conversations for {bot_id}")
                        
                except Exception as e:
                    print(f"   ❌ Failed for {bot_id}: {str(e)[:100]}...")
                    continue
            
            # Test 4: Try to get all conversations using GraphQL
            print("\n4. Testing GraphQL conversation retrieval...")
            try:
                # Try the method that gets all conversations
                all_conversations = self.client.get_all_real_conversations(first=20)
                print(f"   ✅ GraphQL method: {len(all_conversations)} conversations")
                if all_conversations:
                    print(f"   📝 Sample: {all_conversations[0].get('title', 'Untitled')}")
            except Exception as e:
                print(f"   ❌ GraphQL method failed: {e}")
            
        except Exception as e:
            print(f"❌ Direct API test failed: {e}")
    
    def test_conversation_retrieval_methods(self):
        """Test different methods to retrieve conversations."""
        print(f"\n📋 Testing conversation retrieval methods...")
        
        if not self.client:
            print("❌ Client not available")
            return
        
        try:
            # Method 1: get_recent_conversations with different time periods
            print("\n1. Testing get_recent_conversations with different periods...")
            
            for days in [1, 7, 30, 90]:
                try:
                    conversations = self.client.get_recent_conversations(days=days)
                    print(f"   📅 {days} days: {len(conversations)} conversations")
                    if conversations:
                        print(f"   📝 Sample: {conversations[0].get('title', 'Untitled')}")
                        break
                except Exception as e:
                    print(f"   ❌ {days} days failed: {str(e)[:50]}...")
            
            # Method 2: Try getting conversation IDs first
            print("\n2. Testing get_conversation_ids...")
            try:
                conversation_ids = self.client.get_conversation_ids(days=30)
                print(f"   📋 Found {len(conversation_ids)} conversation IDs")
                if conversation_ids:
                    print(f"   🔍 Sample IDs: {conversation_ids[:3]}")
                    
                    # Try to get details for first conversation
                    if conversation_ids:
                        conv_id = conversation_ids[0]
                        print(f"   📖 Getting details for conversation: {conv_id}")
                        conv_details = self.client.get_conversation(conv_id)
                        if conv_details:
                            print(f"   ✅ Conversation details retrieved")
                            print(f"   📝 Title: {conv_details.get('title', 'Untitled')}")
                            print(f"   💬 Messages: {len(conv_details.get('messages', []))}")
                        else:
                            print(f"   ❌ Failed to get conversation details")
            except Exception as e:
                print(f"   ❌ get_conversation_ids failed: {e}")
            
            # Method 3: Try different bot-specific approaches
            print("\n3. Testing bot-specific conversation retrieval...")
            
            # Try to get conversations from specific bots
            test_bots = ["chinchilla", "a2", "capybara"]
            
            for bot_id in test_bots:
                try:
                    print(f"   🤖 Testing bot: {bot_id}")
                    
                    # Try to get chat history for this bot
                    response = self.client.client.get_chat_history(bot_id, count=10)
                    
                    if response and isinstance(response, dict) and 'data' in response:
                        bot_data = response['data'].get(bot_id, [])
                        if bot_data:
                            print(f"   ✅ Found {len(bot_data)} conversations for {bot_id}")
                            for conv in bot_data[:2]:  # Show first 2
                                print(f"   📝 - {conv.get('title', 'Untitled')} (ID: {conv.get('chatId', 'Unknown')})")
                            break
                        else:
                            print(f"   ⚠️  No conversations for {bot_id}")
                    else:
                        print(f"   ⚠️  No data for {bot_id}")
                        
                except Exception as e:
                    print(f"   ❌ Failed for {bot_id}: {str(e)[:50]}...")
                    continue
            
        except Exception as e:
            print(f"❌ Conversation retrieval test failed: {e}")
    
    def test_user_info_and_bots(self):
        """Test user info and bot retrieval."""
        print(f"\n👤 Testing user info and bot retrieval...")
        
        if not self.client:
            print("❌ Client not available")
            return
        
        try:
            # Get user info
            print("\n1. Getting user information...")
            user_info = self.client.get_user_info()
            print(f"   ✅ User info retrieved: {type(user_info)}")
            if isinstance(user_info, dict):
                print(f"   📊 User info keys: {list(user_info.keys())}")
                
                # Check for subscription info
                if 'subscription' in user_info:
                    sub = user_info['subscription']
                    print(f"   💳 Subscription: {sub}")
                
                # Check for message points
                if 'message_points' in user_info:
                    points = user_info['message_points']
                    print(f"   🎯 Message points: {points}")
            
            # Get bots
            print("\n2. Getting available bots...")
            bots = self.client.get_bots()
            print(f"   ✅ Bots retrieved: {len(bots) if bots else 0}")
            if bots:
                print(f"   📊 Bot count: {len(bots)}")
                # Show first few bots
                for i, (bot_id, bot_info) in enumerate(list(bots.items())[:5]):
                    print(f"   🤖 {i+1}. {bot_info.get('displayName', 'Unknown')} ({bot_id})")
            
        except Exception as e:
            print(f"❌ User info and bots test failed: {e}")
    
    def run_comprehensive_test(self):
        """Run comprehensive wrapper API test."""
        print("🚀 Starting comprehensive wrapper API test")
        
        if not self.setup():
            print("❌ Setup failed, aborting test")
            return
        
        # Run all tests
        self.test_direct_api_calls()
        self.test_conversation_retrieval_methods()
        self.test_user_info_and_bots()
        
        print(f"\n{'='*80}")
        print("📊 WRAPPER API TEST SUMMARY")
        print(f"{'='*80}")
        print("✅ Tests completed")
        print("💡 If no conversations found, you may need to:")
        print("   1. Have recent conversations in your Poe account")
        print("   2. Update the poe-api-wrapper library")
        print("   3. Check if Poe.com has changed their API endpoints")
        print("   4. Try the official API for new message sending")


def main():
    """Main function."""
    print("🎯 Poe Search - Wrapper API Conversation Tester")
    print("=" * 50)
    
    # Run the test
    tester = WrapperConversationTester()
    tester.run_comprehensive_test()


if __name__ == "__main__":
    main() 