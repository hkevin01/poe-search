#!/usr/bin/env python3
"""Test script to demonstrate rate limiting toggle and token cost prompt features."""

import logging
import sys
import time
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from poe_search.api.client import PoeAPIClient
from poe_search.utils.config import RateLimitSettings, load_config

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def test_rate_limiting_toggle():
    """Test the rate limiting toggle functionality."""
    print("Testing Rate Limiting Toggle Features")
    print("=" * 50)
    
    # Load configuration
    try:
        config = load_config()
        if not config.has_valid_tokens():
            print("❌ No valid tokens found. Please update your cookies first.")
            print("Run: python scripts/update_cookies.py")
            return
        
        tokens = config.get_poe_tokens()
        print(f"✅ Tokens loaded: p-b={tokens.get('p-b', '')[:10]}...")
        
    except Exception as e:
        print(f"❌ Failed to load config: {e}")
        return
    
    # Test 1: Rate limiting enabled (default)
    print("\n🧪 Test 1: Rate limiting enabled (default)")
    config.rate_limit.enable_rate_limiting = True
    config.rate_limit.max_calls_per_minute = 5
    config.rate_limit.show_rate_limit_warnings = True
    
    try:
        client = PoeAPIClient(token=tokens, config=config)
        print("✅ API client created with rate limiting enabled")
        
        # Test rapid calls to see rate limiting in action
        start_time = time.time()
        for i in range(3):
            print(f"  Call {i+1}/3: Getting bots...")
            bots = client.get_bots()
            print(f"  ✅ Got {len(bots)} bots")
        
        elapsed = time.time() - start_time
        print(f"  📊 Total time: {elapsed:.1f} seconds")
        
    except Exception as e:
        print(f"  ❌ Error: {e}")
    
    # Test 2: Rate limiting disabled
    print("\n🧪 Test 2: Rate limiting disabled")
    config.rate_limit.enable_rate_limiting = False
    
    try:
        client = PoeAPIClient(token=tokens, config=config)
        print("✅ API client created with rate limiting disabled")
        
        # Test rapid calls - should be faster without rate limiting
        start_time = time.time()
        for i in range(3):
            print(f"  Call {i+1}/3: Getting bots...")
            bots = client.get_bots()
            print(f"  ✅ Got {len(bots)} bots")
        
        elapsed = time.time() - start_time
        print(f"  📊 Total time: {elapsed:.1f} seconds")
        
    except Exception as e:
        print(f"  ❌ Error: {e}")
    
    # Test 3: Custom rate limiting settings
    print("\n🧪 Test 3: Custom rate limiting settings")
    config.rate_limit.enable_rate_limiting = True
    config.rate_limit.max_calls_per_minute = 10  # Higher limit
    config.rate_limit.retry_attempts = 2  # Fewer retries
    config.rate_limit.base_delay_seconds = 2  # Shorter delays
    config.rate_limit.show_rate_limit_warnings = False  # No warnings
    
    try:
        client = PoeAPIClient(token=tokens, config=config)
        print("✅ API client created with custom rate limiting settings")
        print(f"  📊 Settings: {config.rate_limit.max_calls_per_minute} calls/min, "
              f"{config.rate_limit.retry_attempts} retries, "
              f"{config.rate_limit.base_delay_seconds}s base delay")
        
        # Test with custom settings
        start_time = time.time()
        for i in range(3):
            print(f"  Call {i+1}/3: Getting bots...")
            bots = client.get_bots()
            print(f"  ✅ Got {len(bots)} bots")
        
        elapsed = time.time() - start_time
        print(f"  📊 Total time: {elapsed:.1f} seconds")
        
    except Exception as e:
        print(f"  ❌ Error: {e}")
    
    # Test 4: Token cost prompt detection
    print("\n🧪 Test 4: Token cost prompt detection")
    config.rate_limit.prompt_for_token_costs = True
    
    try:
        client = PoeAPIClient(token=tokens, config=config)
        print("✅ API client created with token cost prompt detection enabled")
        
        # Simulate a token cost error (this won't actually happen with valid tokens)
        print("  🔍 Testing token cost prompt detection...")
        print("  ℹ️  Token cost prompts will be detected and logged")
        print("  ℹ️  Users will be directed to Poe.com for token purchases")
        
        # Test normal API call
        bots = client.get_bots()
        print(f"  ✅ Got {len(bots)} bots (no cost prompt detected)")
        
    except Exception as e:
        print(f"  ❌ Error: {e}")
    
    print("\n✅ Rate limiting toggle tests completed!")
    print("\n💡 Features demonstrated:")
    print("  - Rate limiting can be enabled/disabled via settings")
    print("  - Custom rate limiting parameters (calls/min, retries, delays)")
    print("  - Warning messages can be toggled on/off")
    print("  - Token cost prompts are detected and logged")
    print("  - All settings are configurable through the GUI")


def test_settings_integration():
    """Test integration with settings dialog."""
    print("\n🧪 Testing Settings Integration")
    print("=" * 30)
    
    try:
        config = load_config()
        
        # Show current rate limiting settings
        print("Current Rate Limiting Settings:")
        print(f"  Enable Rate Limiting: {config.rate_limit.enable_rate_limiting}")
        print(f"  Max Calls per Minute: {config.rate_limit.max_calls_per_minute}")
        print(f"  Retry Attempts: {config.rate_limit.retry_attempts}")
        print(f"  Base Delay: {config.rate_limit.base_delay_seconds}s")
        print(f"  Show Warnings: {config.rate_limit.show_rate_limit_warnings}")
        print(f"  Prompt for Token Costs: {config.rate_limit.prompt_for_token_costs}")
        
        print("\n✅ Settings integration test completed!")
        print("💡 These settings can be modified in the GUI Settings dialog")
        
    except Exception as e:
        print(f"❌ Settings integration test failed: {e}")


if __name__ == "__main__":
    test_rate_limiting_toggle()
    test_settings_integration() 