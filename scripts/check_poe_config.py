#!/usr/bin/env python3
"""Comprehensive Poe Assistant Configuration Checker."""

import json
import logging
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from poe_search.api.client import PoeAPIClient
from poe_search.utils.config import ConfigManager, load_config

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class PoeConfigChecker:
    """Comprehensive configuration checker for Poe Search."""
    
    def __init__(self):
        """Initialize the configuration checker."""
        self.config = None
        self.config_manager = None
        self.api_client = None
        self.check_results = {
            'configuration': {},
            'api_connection': {},
            'tokens': {},
            'dependencies': {},
            'recommendations': []
        }
    
    def run_full_check(self) -> Dict[str, Any]:
        """Run a complete configuration check.
        
        Returns:
            Dictionary with check results and recommendations
        """
        print("🔍 Poe Assistant Configuration Check")
        print("=" * 50)
        
        # 1. Check configuration loading
        self._check_configuration()
        
        # 2. Check tokens
        self._check_tokens()
        
        # 3. Check dependencies
        self._check_dependencies()
        
        # 4. Check API connection
        self._check_api_connection()
        
        # 5. Generate recommendations
        self._generate_recommendations()
        
        # 6. Print summary
        self._print_summary()
        
        return self.check_results
    
    def _check_configuration(self):
        """Check configuration loading and settings."""
        print("\n📋 Configuration Check:")
        
        try:
            # Load configuration
            self.config_manager = ConfigManager()
            self.config = self.config_manager.get_config()
            
            self.check_results['configuration']['loaded'] = True
            self.check_results['configuration']['config_path'] = str(self.config_manager.config_path)
            self.check_results['configuration']['secrets_path'] = str(self.config_manager.config_path.parent / 'secrets.json')
            
            print(f"  ✅ Configuration loaded from: {self.config_manager.config_path}")
            
            # Check configuration settings
            settings = {
                'database_url': self.config.database_url,
                'log_level': self.config.log_level,
                'enable_debug_mode': self.config.enable_debug_mode,
                'rate_limiting_enabled': self.config.rate_limit.enable_rate_limiting,
                'max_calls_per_minute': self.config.rate_limit.max_calls_per_minute,
                'sync_interval': self.config.sync.sync_interval,
                'auto_sync': self.config.sync.auto_sync_on_startup,
            }
            
            self.check_results['configuration']['settings'] = settings
            
            for key, value in settings.items():
                print(f"  📊 {key}: {value}")
                
        except Exception as e:
            self.check_results['configuration']['loaded'] = False
            self.check_results['configuration']['error'] = str(e)
            print(f"  ❌ Configuration loading failed: {e}")
    
    def _check_tokens(self):
        """Check Poe tokens and authentication."""
        print("\n🔑 Token Check:")
        
        if not self.config:
            print("  ❌ No configuration available")
            return
        
        try:
            tokens = self.config.get_poe_tokens()
            
            self.check_results['tokens']['has_tokens'] = bool(tokens.get('p-b'))
            self.check_results['tokens']['p_b_length'] = len(tokens.get('p-b', ''))
            self.check_results['tokens']['p_lat_length'] = len(tokens.get('p-lat', ''))
            self.check_results['tokens']['formkey_length'] = len(tokens.get('formkey', ''))
            
            if tokens.get('p-b'):
                print(f"  ✅ p-b token found (length: {len(tokens['p-b'])})")
                print(f"     Preview: {tokens['p-b'][:20]}...")
            else:
                print("  ❌ p-b token missing")
            
            if tokens.get('p-lat'):
                print(f"  ✅ p-lat token found (length: {len(tokens['p-lat'])})")
                print(f"     Preview: {tokens['p-lat'][:20]}...")
            else:
                print("  ⚠️  p-lat token missing (may cause issues)")
            
            if tokens.get('formkey'):
                print(f"  ✅ formkey found (length: {len(tokens['formkey'])})")
                print(f"     Preview: {tokens['formkey'][:20]}...")
            else:
                print("  ⚠️  formkey missing (may cause API issues)")
            
            # Check token validity
            if self.config.has_valid_tokens():
                print("  ✅ Token validation passed")
                self.check_results['tokens']['valid'] = True
            else:
                print("  ❌ Token validation failed")
                self.check_results['tokens']['valid'] = False
                
        except Exception as e:
            self.check_results['tokens']['error'] = str(e)
            print(f"  ❌ Token check failed: {e}")
    
    def _check_dependencies(self):
        """Check required dependencies."""
        print("\n📦 Dependencies Check:")
        
        dependencies = [
            ('poe_api_wrapper', 'Poe API Wrapper'),
            ('PyQt6', 'PyQt6 GUI Framework'),
            ('sqlalchemy', 'SQLAlchemy Database ORM'),
            ('requests', 'HTTP Requests Library'),
            ('httpx', 'HTTPX Async HTTP Client'),
        ]
        
        for module_name, display_name in dependencies:
            try:
                __import__(module_name)
                print(f"  ✅ {display_name} available")
                self.check_results['dependencies'][module_name] = True
            except ImportError:
                print(f"  ❌ {display_name} not available")
                self.check_results['dependencies'][module_name] = False
    
    def _check_api_connection(self):
        """Check API connection and functionality."""
        print("\n🌐 API Connection Check:")
        
        if not self.config or not self.config.has_valid_tokens():
            print("  ❌ No valid tokens available for API test")
            self.check_results['api_connection']['tested'] = False
            return
        
        try:
            # Initialize API client
            tokens = self.config.get_poe_tokens()
            self.api_client = PoeAPIClient(token=tokens, config=self.config)
            
            self.check_results['api_connection']['client_initialized'] = self.api_client.client is not None
            
            if not self.api_client.client:
                print("  ❌ API client failed to initialize")
                return
            
            print("  ✅ API client initialized successfully")
            
            # Test basic functionality
            print("  🔄 Testing API endpoints...")
            
            # Test 1: Get bots (may fail due to API changes)
            try:
                bots = self.api_client.get_bots()
                bot_count = len(bots) if isinstance(bots, dict) else 0
                print(f"  📊 Bots endpoint: {bot_count} bots found")
                self.check_results['api_connection']['bots_working'] = bot_count > 0
            except Exception as e:
                print(f"  ⚠️  Bots endpoint failed: {str(e)[:100]}...")
                self.check_results['api_connection']['bots_working'] = False
            
            # Test 2: Get conversations (may fail due to API changes)
            try:
                conversations = self.api_client.get_recent_conversations(days=1)
                conv_count = len(conversations) if isinstance(conversations, list) else 0
                print(f"  📊 Conversations endpoint: {conv_count} conversations found")
                self.check_results['api_connection']['conversations_working'] = conv_count >= 0
            except Exception as e:
                print(f"  ⚠️  Conversations endpoint failed: {str(e)[:100]}...")
                self.check_results['api_connection']['conversations_working'] = False
            
            self.check_results['api_connection']['tested'] = True
            
        except Exception as e:
            self.check_results['api_connection']['tested'] = False
            self.check_results['api_connection']['error'] = str(e)
            print(f"  ❌ API connection test failed: {e}")
    
    def _generate_recommendations(self):
        """Generate recommendations based on check results."""
        print("\n💡 Recommendations:")
        
        recommendations = []
        
        # Check configuration
        if not self.check_results['configuration'].get('loaded'):
            recommendations.append("Fix configuration loading issues")
        
        # Check tokens
        if not self.check_results['tokens'].get('valid'):
            recommendations.append("Update Poe tokens - current tokens may be invalid or expired")
        
        if not self.check_results['tokens'].get('p_lat_length'):
            recommendations.append("Add p-lat token for better API compatibility")
        
        if not self.check_results['tokens'].get('formkey_length'):
            recommendations.append("Add formkey for full API functionality")
        
        # Check dependencies
        if not self.check_results['dependencies'].get('poe_api_wrapper'):
            recommendations.append("Install poe-api-wrapper: pip install poe-api-wrapper")
        
        if not self.check_results['dependencies'].get('PyQt6'):
            recommendations.append("Install PyQt6 for GUI: pip install PyQt6")
        
        # Check API connection
        if not self.check_results['api_connection'].get('tested'):
            recommendations.append("Fix API connection issues")
        
        if not self.check_results['api_connection'].get('bots_working'):
            recommendations.append("API endpoints may have changed - consider updating poe-api-wrapper")
        
        # Add specific recommendations
        if not recommendations:
            recommendations.append("Configuration looks good! You can proceed with development.")
        
        self.check_results['recommendations'] = recommendations
        
        for i, rec in enumerate(recommendations, 1):
            print(f"  {i}. {rec}")
    
    def _print_summary(self):
        """Print a summary of the check results."""
        print("\n📊 Summary:")
        print("=" * 50)
        
        # Configuration status
        config_ok = self.check_results['configuration'].get('loaded', False)
        print(f"Configuration: {'✅ OK' if config_ok else '❌ Issues'}")
        
        # Token status
        tokens_ok = self.check_results['tokens'].get('valid', False)
        print(f"Tokens: {'✅ Valid' if tokens_ok else '❌ Invalid/Missing'}")
        
        # Dependencies status
        deps_ok = all(self.check_results['dependencies'].values())
        print(f"Dependencies: {'✅ All Available' if deps_ok else '❌ Missing'}")
        
        # API status
        api_tested = self.check_results['api_connection'].get('tested', False)
        api_working = self.check_results['api_connection'].get('bots_working', False) or self.check_results['api_connection'].get('conversations_working', False)
        print(f"API Connection: {'✅ Working' if api_tested and api_working else '⚠️  Issues' if api_tested else '❌ Not Tested'}")
        
        print("\n🎯 Overall Status:")
        if config_ok and tokens_ok and deps_ok and api_working:
            print("✅ Poe Assistant is properly configured and ready to use!")
        elif config_ok and tokens_ok and deps_ok:
            print("⚠️  Configuration is good but API has some issues (may be temporary)")
        else:
            print("❌ Configuration needs attention - see recommendations above")


def main():
    """Main function to run the configuration check."""
    checker = PoeConfigChecker()
    results = checker.run_full_check()
    
    # Save results to file
    results_file = Path(__file__).parent.parent / "config" / "check_results.json"
    results_file.parent.mkdir(exist_ok=True)
    
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"\n📄 Results saved to: {results_file}")
    
    return 0 if results['configuration'].get('loaded') and results['tokens'].get('valid') else 1


if __name__ == "__main__":
    sys.exit(main()) 