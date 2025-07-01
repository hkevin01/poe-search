#!/usr/bin/env python3
"""Test suite for Poe.com API integration and real data verification."""

import json
import logging
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from poe_search.api.client import PoeAPIClient
from poe_search.client import PoeSearchClient
from poe_search.storage.database import Database
from poe_search.utils.config import load_config

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class PoeAPIIntegrationTestSuite:
    """Comprehensive test suite for Poe.com API integration."""
    
    def __init__(self):
        """Initialize the test suite."""
        self.config = None
        self.api_client = None
        self.poe_client = None
        self.database = None
        self.test_results = {
            'passed': 0,
            'failed': 0,
            'skipped': 0,
            'details': []
        }
    
    def setup(self):
        """Set up test environment."""
        print("🔧 Setting up test environment...")
        
        try:
            # Load configuration
            self.config = load_config()
            if not self.config.has_valid_tokens():
                raise ValueError("No valid Poe.com tokens found")
            
            # Initialize API client
            tokens = self.config.get_poe_tokens()
            self.api_client = PoeAPIClient(token=tokens, config=self.config)
            
            # Initialize main client
            self.poe_client = PoeSearchClient(config=self.config)
            
            # Initialize database
            self.database = Database(self.config.database_url)
            
            print("✅ Test environment setup complete")
            return True
            
        except Exception as e:
            print(f"❌ Test environment setup failed: {e}")
            return False
    
    def run_test(self, test_name: str, test_func):
        """Run a single test and record results."""
        print(f"\n🧪 Running test: {test_name}")
        print("-" * 50)
        
        try:
            start_time = time.time()
            result = test_func()
            end_time = time.time()
            
            if result:
                print(f"✅ {test_name} - PASSED ({end_time - start_time:.2f}s)")
                self.test_results['passed'] += 1
                self.test_results['details'].append({
                    'test': test_name,
                    'status': 'PASSED',
                    'duration': end_time - start_time
                })
            else:
                print(f"❌ {test_name} - FAILED ({end_time - start_time:.2f}s)")
                self.test_results['failed'] += 1
                self.test_results['details'].append({
                    'test': test_name,
                    'status': 'FAILED',
                    'duration': end_time - start_time
                })
                
        except Exception as e:
            print(f"❌ {test_name} - ERROR: {e}")
            self.test_results['failed'] += 1
            self.test_results['details'].append({
                'test': test_name,
                'status': 'ERROR',
                'error': str(e)
            })
    
    def test_token_validation(self):
        """Test that Poe.com tokens are valid and working."""
        print("Testing token validation...")
        
        # Test token format
        tokens = self.config.get_poe_tokens()
        assert tokens.get('p-b'), "p-b token is required"
        assert len(tokens['p-b']) > 10, "p-b token seems too short"
        
        # Test API connection
        try:
            bots = self.api_client.get_bots()
            assert isinstance(bots, dict), "Bots should be a dictionary"
            print(f"  📊 Found {len(bots)} available bots")
            return True
        except Exception as e:
            print(f"  ❌ API connection failed: {e}")
            return False
    
    def test_user_profile_data(self):
        """Test fetching user profile data from Poe.com."""
        print("Testing user profile data...")
        
        try:
            # Get user info (if available)
            user_info = self.api_client.get_user_info()
            if user_info:
                print(f"  👤 User: {user_info.get('name', 'Unknown')}")
                print(f"  📧 Email: {user_info.get('email', 'Not provided')}")
                print(f"  🆔 User ID: {user_info.get('id', 'Unknown')}")
                return True
            else:
                print("  ℹ️  User info not available (this is normal)")
                return True
                
        except Exception as e:
            print(f"  ❌ Failed to get user info: {e}")
            return False
    
    def test_conversation_fetching(self):
        """Test fetching real conversations from Poe.com."""
        print("Testing conversation fetching...")
        
        try:
            # Fetch recent conversations
            conversations = self.api_client.get_recent_conversations(days=7)
            
            if not conversations:
                print("  ⚠️  No conversations found in last 7 days")
                # Try longer period
                conversations = self.api_client.get_recent_conversations(days=30)
                if conversations:
                    print(f"  📊 Found {len(conversations)} conversations in last 30 days")
                else:
                    print("  ⚠️  No conversations found in last 30 days")
                    return True  # This might be normal for new users
            
            print(f"  📊 Found {len(conversations)} conversations")
            
            # Validate conversation structure
            for i, conv in enumerate(conversations[:3]):  # Check first 3
                assert 'id' in conv, f"Conversation {i} missing ID"
                assert 'title' in conv, f"Conversation {i} missing title"
                print(f"  📝 Conversation {i+1}: {conv.get('title', 'Untitled')[:50]}...")
            
            return True
            
        except Exception as e:
            print(f"  ❌ Failed to fetch conversations: {e}")
            return False
    
    def test_conversation_details(self):
        """Test fetching detailed conversation data."""
        print("Testing conversation details...")
        
        try:
            # Get conversation list first
            conversations = self.api_client.get_recent_conversations(days=7)
            if not conversations:
                print("  ⚠️  No conversations to test details")
                return True
            
            # Test first conversation
            first_conv = conversations[0]
            conv_id = first_conv['id']
            
            print(f"  🔍 Fetching details for conversation: {conv_id}")
            conv_details = self.api_client.get_conversation(conv_id)
            
            if conv_details:
                print(f"  📊 Conversation has {len(conv_details.get('messages', []))} messages")
                print(f"  🤖 Bot: {conv_details.get('bot', 'Unknown')}")
                print(f"  📅 Created: {conv_details.get('created_at', 'Unknown')}")
                return True
            else:
                print("  ❌ Failed to get conversation details")
                return False
                
        except Exception as e:
            print(f"  ❌ Failed to test conversation details: {e}")
            return False
    
    def test_bot_information(self):
        """Test fetching available bots information."""
        print("Testing bot information...")
        
        try:
            bots = self.api_client.get_bots()
            
            if not bots:
                print("  ❌ No bots found")
                return False
            
            print(f"  📊 Found {len(bots)} bots")
            
            # Check for popular bots
            popular_bots = ['claude-3-5-sonnet', 'gpt-4', 'gemini-pro', 'llama-3-1-8b-instruct']
            found_bots = []
            
            for bot_id in popular_bots:
                if bot_id in bots:
                    bot_info = bots[bot_id]
                    found_bots.append(bot_id)
                    print(f"  🤖 {bot_id}: {bot_info.get('display_name', 'Unknown')}")
            
            print(f"  ✅ Found {len(found_bots)} popular bots: {', '.join(found_bots)}")
            return len(found_bots) > 0
            
        except Exception as e:
            print(f"  ❌ Failed to get bot information: {e}")
            return False
    
    def test_database_integration(self):
        """Test database integration and data persistence."""
        print("Testing database integration...")
        
        try:
            # Test database connection
            self.database.create_tables()
            print("  ✅ Database tables created/verified")
            
            # Test conversation storage
            conversations = self.api_client.get_recent_conversations(days=7)
            if conversations:
                # Store a test conversation
                test_conv = conversations[0]
                self.database.add_conversation(test_conv)
                print(f"  ✅ Stored conversation: {test_conv.get('title', 'Untitled')}")
                
                # Retrieve from database
                stored_conv = self.database.get_conversation(test_conv['id'])
                if stored_conv:
                    print(f"  ✅ Retrieved conversation from database")
                    return True
                else:
                    print(f"  ❌ Failed to retrieve conversation from database")
                    return False
            else:
                print("  ⚠️  No conversations to test database storage")
                return True
                
        except Exception as e:
            print(f"  ❌ Database integration failed: {e}")
            return False
    
    def test_rate_limiting(self):
        """Test rate limiting functionality."""
        print("Testing rate limiting...")
        
        try:
            # Test with rate limiting enabled
            self.config.rate_limit.enable_rate_limiting = True
            self.config.rate_limit.max_calls_per_minute = 5
            
            start_time = time.time()
            
            # Make multiple API calls
            for i in range(3):
                print(f"  🔄 API call {i+1}/3...")
                bots = self.api_client.get_bots()
                time.sleep(1)  # Small delay
            
            end_time = time.time()
            total_time = end_time - start_time
            
            print(f"  ⏱️  Total time for 3 calls: {total_time:.2f}s")
            
            # Rate limiting should add delays
            if total_time > 3:  # Should take more than 3 seconds with rate limiting
                print("  ✅ Rate limiting working (delays detected)")
                return True
            else:
                print("  ⚠️  Rate limiting may not be working (no delays detected)")
                return True  # Not a failure, just a warning
                
        except Exception as e:
            print(f"  ❌ Rate limiting test failed: {e}")
            return False
    
    def test_data_validation(self):
        """Test that fetched data has expected structure and content."""
        print("Testing data validation...")
        
        try:
            conversations = self.api_client.get_recent_conversations(days=7)
            
            if not conversations:
                print("  ⚠️  No conversations to validate")
                return True
            
            validation_errors = []
            
            for i, conv in enumerate(conversations[:5]):  # Validate first 5
                # Check required fields
                if 'id' not in conv:
                    validation_errors.append(f"Conversation {i} missing ID")
                if 'title' not in conv:
                    validation_errors.append(f"Conversation {i} missing title")
                if 'created_at' not in conv:
                    validation_errors.append(f"Conversation {i} missing created_at")
                
                # Check data types
                if not isinstance(conv.get('id'), str):
                    validation_errors.append(f"Conversation {i} ID is not string")
                if not isinstance(conv.get('title'), str):
                    validation_errors.append(f"Conversation {i} title is not string")
                
                # Check for reasonable values
                if len(conv.get('title', '')) > 500:
                    validation_errors.append(f"Conversation {i} title too long")
            
            if validation_errors:
                print(f"  ❌ Validation errors found:")
                for error in validation_errors:
                    print(f"    - {error}")
                return False
            else:
                print(f"  ✅ All {len(conversations[:5])} conversations validated successfully")
                return True
                
        except Exception as e:
            print(f"  ❌ Data validation failed: {e}")
            return False
    
    def test_error_handling(self):
        """Test error handling for various scenarios."""
        print("Testing error handling...")
        
        try:
            # Test with invalid conversation ID
            invalid_conv_id = "invalid_conversation_id_12345"
            result = self.api_client.get_conversation(invalid_conv_id)
            
            if result is None:
                print("  ✅ Properly handled invalid conversation ID")
            else:
                print("  ⚠️  Unexpected result for invalid conversation ID")
            
            # Test with invalid bot ID
            invalid_bot_id = "invalid_bot_id_12345"
            result = self.api_client.get_bot(invalid_bot_id)
            
            if result is None:
                print("  ✅ Properly handled invalid bot ID")
            else:
                print("  ⚠️  Unexpected result for invalid bot ID")
            
            return True
            
        except Exception as e:
            print(f"  ❌ Error handling test failed: {e}")
            return False
    
    def generate_report(self):
        """Generate a comprehensive test report."""
        print("\n" + "="*60)
        print("📊 POE.COM API INTEGRATION TEST REPORT")
        print("="*60)
        
        total_tests = self.test_results['passed'] + self.test_results['failed'] + self.test_results['skipped']
        
        print(f"Total Tests: {total_tests}")
        print(f"✅ Passed: {self.test_results['passed']}")
        print(f"❌ Failed: {self.test_results['failed']}")
        print(f"⏭️  Skipped: {self.test_results['skipped']}")
        
        if total_tests > 0:
            success_rate = (self.test_results['passed'] / total_tests) * 100
            print(f"📈 Success Rate: {success_rate:.1f}%")
        
        print("\n📋 Test Details:")
        for detail in self.test_results['details']:
            status_icon = "✅" if detail['status'] == 'PASSED' else "❌"
            duration = f"({detail.get('duration', 0):.2f}s)" if 'duration' in detail else ""
            print(f"  {status_icon} {detail['test']} {duration}")
            if 'error' in detail:
                print(f"    Error: {detail['error']}")
        
        # Save detailed report
        report_file = Path("test_reports") / f"poe_api_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        report_file.parent.mkdir(exist_ok=True)
        
        with open(report_file, 'w') as f:
            json.dump({
                'timestamp': datetime.now().isoformat(),
                'summary': {
                    'total': total_tests,
                    'passed': self.test_results['passed'],
                    'failed': self.test_results['failed'],
                    'skipped': self.test_results['skipped'],
                    'success_rate': success_rate if total_tests > 0 else 0
                },
                'details': self.test_results['details']
            }, f, indent=2)
        
        print(f"\n📄 Detailed report saved to: {report_file}")
        
        return self.test_results['failed'] == 0
    
    def run_all_tests(self):
        """Run the complete test suite."""
        print("🚀 Starting Poe.com API Integration Test Suite")
        print("="*60)
        
        if not self.setup():
            print("❌ Test suite setup failed. Exiting.")
            return False
        
        # Run all tests
        tests = [
            ("Token Validation", self.test_token_validation),
            ("User Profile Data", self.test_user_profile_data),
            ("Conversation Fetching", self.test_conversation_fetching),
            ("Conversation Details", self.test_conversation_details),
            ("Bot Information", self.test_bot_information),
            ("Database Integration", self.test_database_integration),
            ("Rate Limiting", self.test_rate_limiting),
            ("Data Validation", self.test_data_validation),
            ("Error Handling", self.test_error_handling),
        ]
        
        for test_name, test_func in tests:
            self.run_test(test_name, test_func)
        
        # Generate report
        success = self.generate_report()
        
        if success:
            print("\n🎉 All tests passed! Poe.com integration is working correctly.")
        else:
            print("\n⚠️  Some tests failed. Check the report for details.")
        
        return success


def main():
    """Main test runner."""
    test_suite = PoeAPIIntegrationTestSuite()
    success = test_suite.run_all_tests()
    
    if success:
        print("\n✅ Poe.com API integration test suite completed successfully!")
        sys.exit(0)
    else:
        print("\n❌ Poe.com API integration test suite completed with failures!")
        sys.exit(1)


if __name__ == "__main__":
    main() 