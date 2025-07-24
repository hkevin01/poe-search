#!/usr/bin/env python3
"""Test script to retrieve and display conversation history from Poe.com."""

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
from poe_search.api.official_client import OfficialPoeAPIClient
from poe_search.storage.database import Database
from poe_search.utils.config import load_config

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ConversationHistoryTester:
    """Test class for retrieving and analyzing conversation history."""
    
    def __init__(self):
        """Initialize the tester."""
        self.config = None
        self.wrapper_client = None
        self.official_client = None
        self.database = None
        self.test_results = {
            'wrapper_tests': {},
            'official_tests': {},
            'database_tests': {},
            'conversation_analysis': {}
        }
    
    def setup(self):
        """Set up the test environment."""
        print("🔧 Setting up conversation history tester...")
        
        try:
            # Load configuration
            self.config = load_config()
            print("✅ Configuration loaded")
            
            # Initialize database
            self.database = Database("sqlite:///test_conversations.db")
            print("✅ Database initialized")
            
            # Initialize wrapper client if tokens available
            if self.config.has_valid_tokens():
                tokens = self.config.get_poe_tokens()
                self.wrapper_client = PoeAPIClient(token=tokens, config=self.config)
                print("✅ Wrapper client initialized")
            else:
                print("⚠️  No valid tokens for wrapper client")
            
            # Initialize official client if API key available
            api_key = getattr(self.config, 'poe_api_key', '')
            if api_key:
                self.official_client = OfficialPoeAPIClient(api_key=api_key, config=self.config)
                print("✅ Official client initialized")
            else:
                print("⚠️  No API key for official client")
            
            return True
            
        except Exception as e:
            print(f"❌ Setup failed: {e}")
            return False
    
    def test_wrapper_conversation_history(self, limit: int = 50) -> Dict[str, Any]:
        """Test retrieving conversation history using wrapper client."""
        print(f"\n📋 Testing wrapper client conversation history (limit: {limit})...")
        
        if not self.wrapper_client:
            print("❌ Wrapper client not available")
            return {'success': False, 'error': 'Client not available'}
        
        try:
            start_time = time.time()
            
            # Get recent conversations
            conversations = self.wrapper_client.get_recent_conversations(days=30)
            
            if not conversations:
                print("⚠️  No conversations found")
                return {'success': False, 'error': 'No conversations found'}
            
            print(f"📊 Found {len(conversations)} conversations")
            
            # Limit to requested number
            conversations = conversations[:limit]
            
            # Get full conversation details with messages
            detailed_conversations = []
            for i, conv in enumerate(conversations):
                print(f"📖 Loading conversation {i+1}/{len(conversations)}: {conv.get('title', 'Untitled')}")
                
                try:
                    conversation_id = conv.get('id', '')
                    if conversation_id:
                        detailed_conv = self.wrapper_client.get_conversation(conversation_id)
                        if detailed_conv:
                            detailed_conversations.append(detailed_conv)
                            print(f"   ✅ Loaded {len(detailed_conv.get('messages', []))} messages")
                        else:
                            print(f"   ⚠️  Failed to load conversation {conversation_id}")
                    
                    # Add small delay to avoid rate limiting
                    time.sleep(0.5)
                    
                except Exception as e:
                    print(f"   ❌ Error loading conversation: {e}")
                    continue
            
            end_time = time.time()
            duration = end_time - start_time
            
            # Analyze conversations
            analysis = self._analyze_conversations(detailed_conversations)
            
            result = {
                'success': True,
                'total_conversations': len(detailed_conversations),
                'duration_seconds': duration,
                'analysis': analysis,
                'sample_conversations': detailed_conversations[:3]  # First 3 for preview
            }
            
            print(f"✅ Wrapper test completed: {len(detailed_conversations)} conversations in {duration:.1f}s")
            return result
            
        except Exception as e:
            print(f"❌ Wrapper test failed: {e}")
            return {'success': False, 'error': str(e)}
    
    def test_official_api(self) -> Dict[str, Any]:
        """Test the official API client."""
        print(f"\n🔗 Testing official API client...")
        
        if not self.official_client:
            print("❌ Official client not available")
            return {'success': False, 'error': 'Client not available'}
        
        try:
            # Test connection
            connection_test = self.official_client.test_connection()
            
            if not connection_test.get('success'):
                print(f"❌ Connection test failed: {connection_test.get('error')}")
                return connection_test
            
            print("✅ Connection test passed")
            
            # Test getting available bots
            bots = self.official_client.get_available_bots()
            print(f"✅ Found {len(bots)} available bots")
            
            # Test a simple response
            test_message = "Hello! This is a test message from Poe Search."
            response = self.official_client.get_bot_response(test_message, "GPT-3.5-Turbo")
            
            result = {
                'success': True,
                'connection_test': connection_test,
                'available_bots': len(bots),
                'test_response_length': len(response),
                'test_response_preview': response[:200] + "..." if len(response) > 200 else response
            }
            
            print(f"✅ Official API test completed")
            return result
            
        except Exception as e:
            print(f"❌ Official API test failed: {e}")
            return {'success': False, 'error': str(e)}
    
    def test_database_storage(self, conversations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Test storing conversations in the database."""
        print(f"\n💾 Testing database storage...")
        
        if not self.database:
            print("❌ Database not available")
            return {'success': False, 'error': 'Database not available'}
        
        try:
            # Clear existing test data
            self.database.clear_conversations()
            print("🗑️  Cleared existing test data")
            
            # Store conversations
            stored_count = 0
            for conv in conversations:
                try:
                    self.database.store_conversation(conv)
                    stored_count += 1
                except Exception as e:
                    print(f"⚠️  Failed to store conversation {conv.get('id', 'unknown')}: {e}")
                    continue
            
            # Retrieve stored conversations
            retrieved_conversations = self.database.get_all_conversations()
            
            # Test search functionality
            search_results = self.database.search_messages("test", limit=10)
            
            result = {
                'success': True,
                'stored_count': stored_count,
                'retrieved_count': len(retrieved_conversations),
                'search_results_count': len(search_results)
            }
            
            print(f"✅ Database test completed: {stored_count} stored, {len(retrieved_conversations)} retrieved")
            return result
            
        except Exception as e:
            print(f"❌ Database test failed: {e}")
            return {'success': False, 'error': str(e)}
    
    def _analyze_conversations(self, conversations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze conversation data."""
        if not conversations:
            return {}
        
        total_messages = 0
        total_chars = 0
        bot_usage = {}
        date_distribution = {}
        
        for conv in conversations:
            # Count messages
            messages = conv.get('messages', [])
            total_messages += len(messages)
            
            # Count characters
            for msg in messages:
                text = msg.get('text', '')
                total_chars += len(text)
            
            # Bot usage
            bot_name = conv.get('bot', {}).get('displayName', 'Unknown')
            bot_usage[bot_name] = bot_usage.get(bot_name, 0) + 1
            
            # Date distribution
            created_at = conv.get('createdAt', '')
            if created_at:
                try:
                    date = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                    date_str = date.strftime('%Y-%m-%d')
                    date_distribution[date_str] = date_distribution.get(date_str, 0) + 1
                except:
                    pass
        
        return {
            'total_conversations': len(conversations),
            'total_messages': total_messages,
            'total_characters': total_chars,
            'avg_messages_per_conversation': total_messages / len(conversations) if conversations else 0,
            'avg_chars_per_message': total_chars / total_messages if total_messages > 0 else 0,
            'bot_usage': bot_usage,
            'date_distribution': dict(sorted(date_distribution.items(), reverse=True)[:10])  # Top 10 dates
        }
    
    def display_conversation_preview(self, conversation: Dict[str, Any], max_messages: int = 5):
        """Display a preview of a conversation."""
        print(f"\n{'='*80}")
        print(f"📝 Conversation: {conversation.get('title', 'Untitled')}")
        print(f"🤖 Bot: {conversation.get('bot', {}).get('displayName', 'Unknown')}")
        print(f"📅 Created: {conversation.get('createdAt', 'Unknown')}")
        print(f"💬 Messages: {len(conversation.get('messages', []))}")
        print(f"{'='*80}")
        
        messages = conversation.get('messages', [])[:max_messages]
        for i, msg in enumerate(messages):
            role = msg.get('role', 'unknown')
            text = msg.get('text', '')
            timestamp = msg.get('timestamp', '')
            
            print(f"\n[{i+1}] {role.upper()} ({timestamp}):")
            print(f"    {text[:200]}{'...' if len(text) > 200 else ''}")
        
        if len(conversation.get('messages', [])) > max_messages:
            print(f"\n... and {len(conversation.get('messages', [])) - max_messages} more messages")
    
    def run_comprehensive_test(self, limit: int = 50):
        """Run comprehensive conversation history test."""
        print("🚀 Starting comprehensive conversation history test")
        print(f"📊 Target: {limit} conversations")
        
        if not self.setup():
            print("❌ Setup failed, aborting test")
            return
        
        # Test wrapper client
        if self.wrapper_client:
            wrapper_result = self.test_wrapper_conversation_history(limit)
            self.test_results['wrapper_tests'] = wrapper_result
            
            if wrapper_result.get('success'):
                conversations = wrapper_result.get('sample_conversations', [])
                
                # Test database storage
                db_result = self.test_database_storage(conversations)
                self.test_results['database_tests'] = db_result
                
                # Display conversation previews
                print(f"\n📖 Displaying conversation previews:")
                for conv in conversations[:3]:  # Show first 3
                    self.display_conversation_preview(conv)
        
        # Test official API
        if self.official_client:
            official_result = self.test_official_api()
            self.test_results['official_tests'] = official_result
        
        # Display summary
        self.display_test_summary()
        
        # Save results
        self.save_test_results()
    
    def display_test_summary(self):
        """Display a summary of test results."""
        print(f"\n{'='*80}")
        print("📊 TEST SUMMARY")
        print(f"{'='*80}")
        
        # Wrapper tests
        wrapper_result = self.test_results.get('wrapper_tests', {})
        if wrapper_result.get('success'):
            analysis = wrapper_result.get('analysis', {})
            print(f"\n✅ Wrapper Client Results:")
            print(f"   📝 Conversations: {analysis.get('total_conversations', 0)}")
            print(f"   💬 Total Messages: {analysis.get('total_messages', 0)}")
            print(f"   📊 Avg Messages/Conv: {analysis.get('avg_messages_per_conversation', 0):.1f}")
            print(f"   🤖 Most Used Bot: {max(analysis.get('bot_usage', {}).items(), key=lambda x: x[1])[0] if analysis.get('bot_usage') else 'N/A'}")
        else:
            print(f"\n❌ Wrapper Client: {wrapper_result.get('error', 'Failed')}")
        
        # Official API tests
        official_result = self.test_results.get('official_tests', {})
        if official_result.get('success'):
            print(f"\n✅ Official API Results:")
            print(f"   🔗 Connection: Working")
            print(f"   🤖 Available Bots: {official_result.get('available_bots', 0)}")
            print(f"   📝 Test Response: {official_result.get('test_response_length', 0)} chars")
        else:
            print(f"\n❌ Official API: {official_result.get('error', 'Failed')}")
        
        # Database tests
        db_result = self.test_results.get('database_tests', {})
        if db_result.get('success'):
            print(f"\n✅ Database Results:")
            print(f"   💾 Stored: {db_result.get('stored_count', 0)} conversations")
            print(f"   📖 Retrieved: {db_result.get('retrieved_count', 0)} conversations")
            print(f"   🔍 Search Results: {db_result.get('search_results_count', 0)}")
        else:
            print(f"\n❌ Database: {db_result.get('error', 'Failed')}")
    
    def save_test_results(self):
        """Save test results to file."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"conversation_test_results_{timestamp}.json"
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.test_results, f, indent=2, default=str)
            print(f"\n💾 Test results saved to: {filename}")
        except Exception as e:
            print(f"\n❌ Failed to save test results: {e}")


def main():
    """Main function."""
    print("🎯 Poe Search - Conversation History Tester")
    print("=" * 50)
    
    # Parse command line arguments
    limit = 50
    if len(sys.argv) > 1:
        try:
            limit = int(sys.argv[1])
        except ValueError:
            print(f"⚠️  Invalid limit '{sys.argv[1]}', using default: {limit}")
    
    # Run the test
    tester = ConversationHistoryTester()
    tester.run_comprehensive_test(limit)


if __name__ == "__main__":
    main() 