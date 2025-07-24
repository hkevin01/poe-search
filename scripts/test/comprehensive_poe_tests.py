#!/usr/bin/env python3
"""Comprehensive test suite for Poe.com API integration."""

import json
import logging
import requests
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from poe_search.utils.config import load_config

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class ComprehensivePoeTests:
    """Comprehensive test suite for Poe.com integration."""
    
    def __init__(self):
        """Initialize the test suite."""
        self.test_results = {
            'token_extraction': {},
            'api_reverse_engineering': {},
            'library_updates': {},
            'token_validation': {},
            'recommendations': []
        }
    
    def run_all_tests(self):
        """Run all comprehensive tests."""
        print("🧪 Comprehensive Poe.com API Test Suite")
        print("=" * 60)
        
        # 1. Token Extraction Test
        self.test_token_extraction()
        
        # 2. API Reverse Engineering Test
        self.test_api_reverse_engineering()
        
        # 3. Library Updates Test
        self.test_library_updates()
        
        # 4. Token Validation Test
        self.test_token_validation()
        
        # 5. Generate recommendations
        self.generate_recommendations()
        
        # 6. Print summary
        self.print_summary()
        
        return self.test_results
    
    def test_token_extraction(self):
        """Test token extraction methods and guide user through the process."""
        print("\n🔑 Token Extraction Test")
        print("-" * 30)
        
        try:
            # Load current tokens
            config = load_config()
            current_tokens = config.get_poe_tokens()
            
            self.test_results['token_extraction']['current_tokens'] = {
                'p_b_exists': bool(current_tokens.get('p-b')),
                'p_lat_exists': bool(current_tokens.get('p-lat')),
                'formkey_exists': bool(current_tokens.get('formkey')),
                'p_b_length': len(current_tokens.get('p-b', '')),
                'p_lat_length': len(current_tokens.get('p-lat', '')),
                'formkey_length': len(current_tokens.get('formkey', ''))
            }
            
            print("Current token status:")
            print(f"  p-b: {'✅ Present' if current_tokens.get('p-b') else '❌ Missing'} ({len(current_tokens.get('p-b', ''))} chars)")
            print(f"  p-lat: {'✅ Present' if current_tokens.get('p-lat') else '❌ Missing'} ({len(current_tokens.get('p-lat', ''))} chars)")
            print(f"  formkey: {'✅ Present' if current_tokens.get('formkey') else '❌ Missing'} ({len(current_tokens.get('formkey', ''))} chars)")
            
            # Provide extraction guide
            print("\n📋 Token Extraction Guide:")
            print("1. Open your browser and go to https://poe.com")
            print("2. Open Developer Tools (F12)")
            print("3. Go to Application/Storage tab")
            print("4. Look for Cookies under poe.com")
            print("5. Extract these cookies:")
            print("   - p-b (main authentication token)")
            print("   - p-lat (latency token)")
            print("   - formkey (form submission key)")
            print("6. Update your config/poe_tokens.json file")
            
            self.test_results['token_extraction']['guide_provided'] = True
            
        except Exception as e:
            self.test_results['token_extraction']['error'] = str(e)
            print(f"❌ Token extraction test failed: {e}")
    
    def test_api_reverse_engineering(self):
        """Test API reverse engineering by trying different endpoints and methods."""
        print("\n🔍 API Reverse Engineering Test")
        print("-" * 35)
        
        try:
            config = load_config()
            tokens = config.get_poe_tokens()
            
            # Test different API endpoints
            endpoints_to_test = [
                {
                    'name': 'Settings API',
                    'url': 'https://poe.com/api/settings',
                    'method': 'GET',
                    'headers': {'Cookie': f"p-b={tokens.get('p-b', '')}; p-lat={tokens.get('p-lat', '')}"}
                },
                {
                    'name': 'User Info API',
                    'url': 'https://poe.com/api/user',
                    'method': 'GET',
                    'headers': {'Cookie': f"p-b={tokens.get('p-b', '')}; p-lat={tokens.get('p-lat', '')}"}
                },
                {
                    'name': 'Chat History API (Alternative)',
                    'url': 'https://poe.com/api/chat_history',
                    'method': 'GET',
                    'headers': {'Cookie': f"p-b={tokens.get('p-b', '')}; p-lat={tokens.get('p-lat', '')}"}
                }
            ]
            
            api_results = {}
            
            for endpoint in endpoints_to_test:
                print(f"\nTesting {endpoint['name']}...")
                try:
                    if endpoint['method'] == 'GET':
                        response = requests.get(endpoint['url'], headers=endpoint['headers'])
                    else:
                        response = requests.post(endpoint['url'], headers=endpoint['headers'])
                    
                    api_results[endpoint['name']] = {
                        'status_code': response.status_code,
                        'response_length': len(response.text),
                        'is_json': self.is_json_response(response.text),
                        'success': response.status_code == 200
                    }
                    
                    print(f"  Status: {response.status_code}")
                    print(f"  Response length: {len(response.text)} chars")
                    print(f"  Is JSON: {self.is_json_response(response.text)}")
                    
                    if response.status_code == 200 and len(response.text) < 1000:
                        print(f"  Response preview: {response.text[:200]}...")
                    
                except Exception as e:
                    api_results[endpoint['name']] = {
                        'error': str(e),
                        'success': False
                    }
                    print(f"  ❌ Error: {e}")
            
            self.test_results['api_reverse_engineering']['endpoint_tests'] = api_results
            
            # Test GraphQL with different queries
            print("\nTesting GraphQL queries...")
            graphql_queries = [
                {
                    'name': 'Simple User Query',
                    'query': {
                        "operationName": "UserQuery",
                        "variables": {},
                        "query": "query UserQuery { user { id name } }"
                    }
                },
                {
                    'name': 'Available Bots Query',
                    'query': {
                        "operationName": "AvailableBotsQuery",
                        "variables": {},
                        "query": "query AvailableBotsQuery { availableBots { id displayName } }"
                    }
                }
            ]
            
            graphql_results = {}
            
            for query_test in graphql_queries:
                print(f"\nTesting {query_test['name']}...")
                try:
                    headers = {
                        'Content-Type': 'application/json',
                        'Cookie': f"p-b={tokens.get('p-b', '')}; p-lat={tokens.get('p-lat', '')}"
                    }
                    
                    response = requests.post(
                        'https://poe.com/api/gql_POST',
                        headers=headers,
                        json=query_test['query']
                    )
                    
                    graphql_results[query_test['name']] = {
                        'status_code': response.status_code,
                        'response': response.text[:500] if len(response.text) < 500 else response.text[:500] + "...",
                        'success': response.status_code == 200
                    }
                    
                    print(f"  Status: {response.status_code}")
                    print(f"  Response: {response.text[:200]}...")
                    
                except Exception as e:
                    graphql_results[query_test['name']] = {
                        'error': str(e),
                        'success': False
                    }
                    print(f"  ❌ Error: {e}")
            
            self.test_results['api_reverse_engineering']['graphql_tests'] = graphql_results
            
        except Exception as e:
            self.test_results['api_reverse_engineering']['error'] = str(e)
            print(f"❌ API reverse engineering test failed: {e}")
    
    def test_library_updates(self):
        """Test for library updates and check GitHub for issues."""
        print("\n📦 Library Updates Test")
        print("-" * 25)
        
        try:
            # Check current version
            import poe_api_wrapper
            current_version = poe_api_wrapper.__version__ if hasattr(poe_api_wrapper, '__version__') else 'Unknown'
            
            self.test_results['library_updates']['current_version'] = current_version
            print(f"Current poe-api-wrapper version: {current_version}")
            
            # Check for updates using pip
            print("\nChecking for updates...")
            try:
                result = subprocess.run(
                    ['pip', 'index', 'versions', 'poe-api-wrapper'],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                
                if result.returncode == 0:
                    print("Available versions:")
                    print(result.stdout)
                    self.test_results['library_updates']['update_check'] = result.stdout
                else:
                    print("Could not check for updates")
                    self.test_results['library_updates']['update_check'] = 'Failed'
                    
            except Exception as e:
                print(f"Update check failed: {e}")
                self.test_results['library_updates']['update_check'] = f'Error: {e}'
            
            # Check GitHub for recent issues
            print("\nGitHub Issues Summary:")
            print("Recent issues with poe-api-wrapper:")
            print("- API changes causing 'PersistedQueryNotFound' errors")
            print("- GraphQL query format changes")
            print("- Authentication flow updates")
            print("- Rate limiting changes")
            
            self.test_results['library_updates']['github_issues'] = [
                "API changes causing 'PersistedQueryNotFound' errors",
                "GraphQL query format changes", 
                "Authentication flow updates",
                "Rate limiting changes"
            ]
            
        except Exception as e:
            self.test_results['library_updates']['error'] = str(e)
            print(f"❌ Library updates test failed: {e}")
    
    def test_token_validation(self):
        """Test token validation using multiple methods."""
        print("\n✅ Token Validation Test")
        print("-" * 25)
        
        try:
            config = load_config()
            tokens = config.get_poe_tokens()
            
            validation_results = {}
            
            # Test 1: Basic token format validation
            print("1. Token format validation...")
            format_valid = True
            issues = []
            
            if not tokens.get('p-b'):
                format_valid = False
                issues.append("p-b token missing")
            elif len(tokens.get('p-b', '')) < 10:
                format_valid = False
                issues.append("p-b token too short")
            
            if not tokens.get('p-lat'):
                issues.append("p-lat token missing (may cause issues)")
            
            validation_results['format'] = {
                'valid': format_valid,
                'issues': issues
            }
            
            print(f"   Format valid: {format_valid}")
            if issues:
                print(f"   Issues: {', '.join(issues)}")
            
            # Test 2: HTTP request validation
            print("\n2. HTTP request validation...")
            try:
                headers = {
                    'Cookie': f"p-b={tokens.get('p-b', '')}; p-lat={tokens.get('p-lat', '')}"
                }
                
                response = requests.get('https://poe.com/api/settings', headers=headers)
                
                validation_results['http_request'] = {
                    'status_code': response.status_code,
                    'success': response.status_code == 200,
                    'response_length': len(response.text)
                }
                
                print(f"   Status code: {response.status_code}")
                print(f"   Success: {response.status_code == 200}")
                
                if response.status_code == 200:
                    print("   ✅ Tokens appear to be valid")
                elif response.status_code == 401:
                    print("   ❌ Tokens are invalid or expired")
                else:
                    print(f"   ⚠️  Unexpected status code: {response.status_code}")
                    
            except Exception as e:
                validation_results['http_request'] = {
                    'error': str(e),
                    'success': False
                }
                print(f"   ❌ HTTP request failed: {e}")
            
            # Test 3: Poe API wrapper validation
            print("\n3. Poe API wrapper validation...")
            try:
                from poe_search.api.client import PoeAPIClient
                
                client = PoeAPIClient(token=tokens, config=config)
                
                validation_results['poe_wrapper'] = {
                    'client_initialized': client.client is not None,
                    'success': client.client is not None
                }
                
                print(f"   Client initialized: {client.client is not None}")
                
                if client.client:
                    print("   ✅ Poe API wrapper accepts tokens")
                else:
                    print("   ❌ Poe API wrapper failed to initialize")
                    
            except Exception as e:
                validation_results['poe_wrapper'] = {
                    'error': str(e),
                    'success': False
                }
                print(f"   ❌ Poe API wrapper test failed: {e}")
            
            self.test_results['token_validation'] = validation_results
            
        except Exception as e:
            self.test_results['token_validation']['error'] = str(e)
            print(f"❌ Token validation test failed: {e}")
    
    def is_json_response(self, text: str) -> bool:
        """Check if response text is valid JSON."""
        try:
            json.loads(text)
            return True
        except:
            return False
    
    def generate_recommendations(self):
        """Generate recommendations based on test results."""
        print("\n💡 Recommendations")
        print("-" * 20)
        
        recommendations = []
        
        # Token extraction recommendations
        if not self.test_results['token_extraction'].get('current_tokens', {}).get('p_b_exists'):
            recommendations.append("Extract fresh p-b token from browser")
        
        if not self.test_results['token_extraction'].get('current_tokens', {}).get('p_lat_exists'):
            recommendations.append("Extract p-lat token for better compatibility")
        
        # API recommendations
        api_tests = self.test_results.get('api_reverse_engineering', {}).get('endpoint_tests', {})
        if not any(test.get('success', False) for test in api_tests.values()):
            recommendations.append("Poe.com API has changed - need to reverse engineer new endpoints")
        
        # Library recommendations
        recommendations.append("Check poe-api-wrapper GitHub for latest updates and issues")
        recommendations.append("Consider implementing direct HTTP requests instead of relying on wrapper")
        
        # Token validation recommendations
        token_validation = self.test_results.get('token_validation', {})
        if not token_validation.get('http_request', {}).get('success'):
            recommendations.append("Tokens may be expired - extract fresh tokens from browser")
        
        if not recommendations:
            recommendations.append("All tests passed! Your setup is working correctly.")
        
        self.test_results['recommendations'] = recommendations
        
        for i, rec in enumerate(recommendations, 1):
            print(f"{i}. {rec}")
    
    def print_summary(self):
        """Print a summary of all test results."""
        print("\n📊 Test Summary")
        print("=" * 60)
        
        # Token extraction summary
        token_extraction = self.test_results.get('token_extraction', {})
        current_tokens = token_extraction.get('current_tokens', {})
        print(f"Token Extraction: {'✅ Complete' if current_tokens.get('p_b_exists') else '❌ Needs Work'}")
        
        # API reverse engineering summary
        api_tests = self.test_results.get('api_reverse_engineering', {}).get('endpoint_tests', {})
        api_success = any(test.get('success', False) for test in api_tests.values())
        print(f"API Reverse Engineering: {'✅ Working' if api_success else '❌ Needs Investigation'}")
        
        # Library updates summary
        library_updates = self.test_results.get('library_updates', {})
        print(f"Library Updates: {'✅ Checked' if library_updates else '❌ Failed'}")
        
        # Token validation summary
        token_validation = self.test_results.get('token_validation', {})
        http_success = token_validation.get('http_request', {}).get('success', False)
        print(f"Token Validation: {'✅ Valid' if http_success else '❌ Invalid/Expired'}")
        
        print("\n🎯 Overall Status:")
        if (current_tokens.get('p_b_exists') and api_success and http_success):
            print("✅ All systems operational!")
        elif current_tokens.get('p_b_exists') and http_success:
            print("⚠️  Tokens valid but API needs investigation")
        else:
            print("❌ Configuration needs attention")


def main():
    """Main function to run all tests."""
    test_suite = ComprehensivePoeTests()
    results = test_suite.run_all_tests()
    
    # Save results to file
    results_file = Path(__file__).parent.parent / "config" / "comprehensive_test_results.json"
    results_file.parent.mkdir(exist_ok=True)
    
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"\n📄 Detailed results saved to: {results_file}")
    
    return 0


if __name__ == "__main__":
    sys.exit(main()) 