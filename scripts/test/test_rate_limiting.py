#!/usr/bin/env python3
"""Test script to demonstrate rate limiting functionality."""

import logging
import sys
import time
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from poe_search.api.client import PoeAPIClient
from poe_search.utils.config import load_config

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def test_rate_limiting():
    """Test the rate limiting functionality."""
    print("Testing Poe API Rate Limiting")
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
    
    # Create API client
    try:
        client = PoeAPIClient(token=tokens)  # type: ignore
        print("✅ API client created successfully")
    except Exception as e:
        print(f"❌ Failed to create API client: {e}")
        return
    
    # Test 1: Get bots (should be rate limited)
    print("\n🧪 Test 1: Getting bots (rate limited to 5 calls per minute)")
    start_time = time.time()
    
    for i in range(3):
        try:
            print(f"  Call {i+1}/3: Getting bots...")
            bots = client.get_bots()
            print(f"  ✅ Got {len(bots)} bots")
        except Exception as e:
            print(f"  ❌ Error: {e}")
        
        if i < 2:  # Don't sleep after last call
            print("  ⏳ Waiting 2 seconds between calls...")
            time.sleep(2)
    
    elapsed = time.time() - start_time
    print(f"  📊 Total time: {elapsed:.1f} seconds")
    
    # Test 2: Get conversations (should be rate limited)
    print("\n🧪 Test 2: Getting conversations (rate limited to 8 calls per minute)")
    start_time = time.time()
    
    for i in range(3):
        try:
            print(f"  Call {i+1}/3: Getting conversations...")
            conversations = client.get_recent_conversations(days=1)
            print(f"  ✅ Got {len(conversations)} conversations")
        except Exception as e:
            print(f"  ❌ Error: {e}")
        
        if i < 2:  # Don't sleep after last call
            print("  ⏳ Waiting 3 seconds between calls...")
            time.sleep(3)
    
    elapsed = time.time() - start_time
    print(f"  📊 Total time: {elapsed:.1f} seconds")
    
    # Test 3: Simulate rapid calls to trigger rate limiting
    print("\n🧪 Test 3: Rapid calls to trigger rate limiting")
    start_time = time.time()
    
    for i in range(5):
        try:
            print(f"  Call {i+1}/5: Getting bots...")
            bots = client.get_bots()
            print(f"  ✅ Got {len(bots)} bots")
        except Exception as e:
            print(f"  ❌ Error: {e}")
        
        # No manual delay - let rate limiting handle it
        print("  ⚡ No manual delay - rate limiting should handle timing")
    
    elapsed = time.time() - start_time
    print(f"  📊 Total time: {elapsed:.1f} seconds")
    
    print("\n✅ Rate limiting tests completed!")
    print("\n💡 Tips for avoiding rate limits:")
    print("  - The app now automatically handles rate limiting")
    print("  - Delays are added between API calls")
    print("  - Exponential backoff is used for retries")
    print("  - Rate limits are conservative (8 calls per minute)")
    print("  - If you hit rate limits, wait 10-30 minutes before retrying")


if __name__ == "__main__":
    test_rate_limiting() 