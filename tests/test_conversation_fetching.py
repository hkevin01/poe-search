#!/usr/bin/env python3
"""
Comprehensive test suite for Poe API conversation fetching.
Tests all available methods to ensure we can retrieve real conversations.
"""

import json
import logging
import sys
import time
from pathlib import Path

from poe_api_wrapper import PoeApi

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from poe_search.utils.config import load_config
from poe_search.client import PoeSearchClient

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class PoeConversationTester:
    """Comprehensive tester for Poe conversation fetching."""
    
    def __init__(self):
        self.config = None
        self.poe_client = None
        self.search_client = None
        self.results = {}
        
    def setup(self):
        """Setup test environment and clients."""
        logger.info("=== Setting up Poe API Test Environment ===")
        
        try:
            # Load configuration
            self.config = load_config()
            logger.info("✓ Configuration loaded successfully")
            
            # Initialize raw PoeApi client
            formkey = self.config.get('formkey')
            p_b_cookie = self.config.get('p_b')
            
            if not formkey or not p_b_cookie:
                raise ValueError("Missing formkey or p_b cookie in config")
                
            self.poe_client = PoeApi(cookie=p_b_cookie, formkey=formkey)
            logger.info("✓ Raw PoeApi client initialized")
            
            # Initialize search client
            self.search_client = PoeSearchClient(self.config)
            logger.info("✓ PoeSearchClient initialized")
            
            return True
            
        except Exception as e:
            logger.error(f"✗ Setup failed: {e}")
            return False
    
    def test_available_bots(self):
        """Test 1: Get available bots."""
        logger.info("\n=== Test 1: Available Bots ===")
        try:
            bots = self.poe_client.get_available_bots()
            self.results['available_bots'] = {
                'success': True,
                'count': len(bots) if isinstance(bots, (list, dict)) else 0,
                'data': bots
            }
            logger.info(f"✓ Found {len(bots) if isinstance(bots, (list, dict)) else 0} available bots")
            if isinstance(bots, dict):
                logger.info(f"  Bot names: {list(bots.keys())[:10]}...")  # Show first 10
            return True
        except Exception as e:
            self.results['available_bots'] = {'success': False, 'error': str(e)}
            logger.error(f"✗ Failed to get available bots: {e}")
            return False
    
    def test_chat_history_methods(self):
        """Test 2: Try different chat history methods."""
        logger.info("\n=== Test 2: Chat History Methods ===")
        
        # First get available bots to use in tests
        try:
            bots = self.poe_client.get_available_bots()
            if not bots:
                logger.warning("No bots available for chat history tests")
                return False
                
            # Get some bot IDs to test with
            bot_ids = []
            if isinstance(bots, dict):
                bot_ids = list(bots.keys())[:5]  # Test first 5 bots
            elif isinstance(bots, list):
                bot_ids = [bot.get('id', bot.get('name', str(bot))) for bot in bots[:5]]
            
            logger.info(f"Testing chat history with bots: {bot_ids}")
            
            all_conversations = []
            
            for bot_id in bot_ids:
                try:
                    logger.info(f"  Testing bot: {bot_id}")
                    
                    # Method 1: get_chat_history with different parameters
                    for count in [10, 50, 100]:
                        try:
                            history = self.poe_client.get_chat_history(bot_id, count=count)
                            logger.info(f"    get_chat_history(count={count}): {type(history)} - {len(history) if isinstance(history, (list, dict)) else 'N/A'}")
                            
                            if history and isinstance(history, dict):
                                if 'data' in history and bot_id in history['data']:
                                    conversations = history['data'][bot_id]
                                    if conversations:
                                        all_conversations.extend(conversations)
                                        logger.info(f"    ✓ Found {len(conversations)} conversations for {bot_id}")
                                        break  # Found conversations, no need to try other counts
                            
                        except Exception as e:
                            logger.warning(f"    get_chat_history(count={count}) failed: {e}")
                    
                    # Method 2: get_previous_messages
                    try:
                        prev_msgs = self.poe_client.get_previous_messages(bot_id, count=20)
                        logger.info(f"    get_previous_messages: {type(prev_msgs)} - {len(prev_msgs) if isinstance(prev_msgs, (list, dict)) else 'N/A'}")
                    except Exception as e:
                        logger.warning(f"    get_previous_messages failed: {e}")
                    
                    time.sleep(0.5)  # Rate limiting
                    
                except Exception as e:
                    logger.warning(f"  Bot {bot_id} failed: {e}")
                    continue
            
            self.results['chat_history'] = {
                'success': True,
                'total_conversations': len(all_conversations),
                'conversations': all_conversations[:10]  # Store sample
            }
            
            logger.info(f"✓ Total conversations found: {len(all_conversations)}")
            return len(all_conversations) > 0
            
        except Exception as e:
            self.results['chat_history'] = {'success': False, 'error': str(e)}
            logger.error(f"✗ Chat history test failed: {e}")
            return False
    
    def test_alternative_methods(self):
        """Test 3: Alternative conversation discovery methods."""
        logger.info("\n=== Test 3: Alternative Methods ===")
        
        methods_to_test = [
            ('get_threadData', lambda: self.poe_client.get_threadData()),
            ('get_user_bots', lambda: self.poe_client.get_user_bots()),
            ('get_settings', lambda: self.poe_client.get_settings()),
        ]
        
        for method_name, method_func in methods_to_test:
            try:
                logger.info(f"  Testing {method_name}...")
                result = method_func()
                logger.info(f"    ✓ {method_name}: {type(result)} - {len(result) if isinstance(result, (list, dict)) else 'N/A'}")
                self.results[method_name] = {'success': True, 'data': result}
            except Exception as e:
                logger.warning(f"    ✗ {method_name} failed: {e}")
                self.results[method_name] = {'success': False, 'error': str(e)}
    
    def test_search_client_methods(self):
        """Test 4: Test PoeSearchClient conversation methods."""
        logger.info("\n=== Test 4: PoeSearchClient Methods ===")
        
        try:
            # Test with very long time period to get all conversations
            logger.info("  Testing get_conversation_history with extended time periods...")
            
            for days in [365, 1000, 3650]:  # 1 year, ~3 years, 10 years
                try:
                    conversations = self.search_client.get_conversation_history(days=days, limit=1000)
                    logger.info(f"    get_conversation_history(days={days}): Found {len(conversations)} conversations")
                    
                    if conversations:
                        self.results['search_client_extended'] = {
                            'success': True,
                            'days': days,
                            'count': len(conversations),
                            'sample': conversations[:3]
                        }
                        logger.info(f"✓ Success with {days} days: {len(conversations)} conversations")
                        return True
                        
                except Exception as e:
                    logger.warning(f"    get_conversation_history(days={days}) failed: {e}")
            
            self.results['search_client_extended'] = {'success': False, 'error': 'No conversations found with any time period'}
            return False
            
        except Exception as e:
            self.results['search_client_extended'] = {'success': False, 'error': str(e)}
            logger.error(f"✗ PoeSearchClient test failed: {e}")
            return False
    
    def test_direct_api_exploration(self):
        """Test 5: Direct API exploration to find conversation endpoints."""
        logger.info("\n=== Test 5: Direct API Exploration ===")
        
        try:
            # Try to explore different API endpoints that might have conversations
            endpoints_to_try = [
                'get_available_groups',
                'get_most_mentioned', 
                'explore',
                'load_group_history',
            ]
            
            for endpoint in endpoints_to_try:
                try:
                    if hasattr(self.poe_client, endpoint):
                        logger.info(f"  Testing {endpoint}...")
                        method = getattr(self.poe_client, endpoint)
                        result = method()
                        logger.info(f"    ✓ {endpoint}: {type(result)} - {len(result) if isinstance(result, (list, dict)) else str(result)[:100]}")
                        self.results[f'direct_{endpoint}'] = {'success': True, 'data': result}
                    else:
                        logger.warning(f"    Method {endpoint} not available")
                        
                except Exception as e:
                    logger.warning(f"    ✗ {endpoint} failed: {e}")
                    self.results[f'direct_{endpoint}'] = {'success': False, 'error': str(e)}
                    
        except Exception as e:
            logger.error(f"✗ Direct API exploration failed: {e}")
    
    def generate_report(self):
        """Generate comprehensive test report."""
        logger.info("\n" + "="*60)
        logger.info("=== COMPREHENSIVE TEST REPORT ===")
        logger.info("="*60)
        
        total_conversations = 0
        successful_methods = []
        
        for test_name, result in self.results.items():
            if result.get('success'):
                if 'count' in result:
                    total_conversations += result['count']
                if 'total_conversations' in result:
                    total_conversations += result['total_conversations']
                successful_methods.append(test_name)
        
        logger.info(f"📊 SUMMARY:")
        logger.info(f"   Total conversations found: {total_conversations}")
        logger.info(f"   Successful methods: {len(successful_methods)}")
        logger.info(f"   Failed methods: {len(self.results) - len(successful_methods)}")
        
        logger.info(f"\n✅ WORKING METHODS:")
        for method in successful_methods:
            result = self.results[method]
            count = result.get('count', result.get('total_conversations', 0))
            logger.info(f"   - {method}: {count} conversations")
        
        logger.info(f"\n❌ FAILED METHODS:")
        for test_name, result in self.results.items():
            if not result.get('success'):
                error = result.get('error', 'Unknown error')
                logger.info(f"   - {test_name}: {error}")
        
        # Save detailed results to file
        results_file = Path(__file__).parent / 'conversation_test_results.json'
        with open(results_file, 'w') as f:
            json.dump(self.results, f, indent=2, default=str)
        logger.info(f"\n📄 Detailed results saved to: {results_file}")
        
        return total_conversations > 0
    
    def run_all_tests(self):
        """Run all tests in sequence."""
        logger.info("🚀 Starting comprehensive Poe conversation fetching tests...")
        
        if not self.setup():
            logger.error("❌ Setup failed, cannot continue")
            return False
        
        # Run all tests
        tests = [
            self.test_available_bots,
            self.test_chat_history_methods,
            self.test_alternative_methods,
            self.test_search_client_methods,
            self.test_direct_api_exploration,
        ]
        
        for i, test in enumerate(tests, 1):
            logger.info(f"\n⏳ Running test {i}/{len(tests)}...")
            try:
                test()
            except Exception as e:
                logger.error(f"Test {i} crashed: {e}")
        
        # Generate final report
        success = self.generate_report()
        
        if success:
            logger.info("\n🎉 SUCCESS: Found conversations! The API is working.")
        else:
            logger.error("\n💥 FAILURE: No conversations found. Need to investigate API issues.")
        
        return success


def main():
    """Main test execution."""
    tester = PoeConversationTester()
    success = tester.run_all_tests()
    
    if not success:
        logger.error("\n🔧 NEXT STEPS:")
        logger.error("1. Check if your Poe account actually has conversations")
        logger.error("2. Verify authentication tokens are valid and not expired")
        logger.error("3. Check if Poe.com API has changed its endpoints")
        logger.error("4. Try logging into Poe.com manually to see conversations")
        
    return 0 if success else 1


if __name__ == "__main__":
    exit(main())
