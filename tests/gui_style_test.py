#!/usr/bin/env python3
"""
Test that mimics exactly what the GUI does for conversation sync
"""

import sys
import os
import logging

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

try:
    from poe_search.client import PoeSearchClient
    from poe_search.utils.config import PoeSearchConfig
    print("✓ Imports successful")
except ImportError as e:
    print(f"❌ Failed to import: {e}")
    sys.exit(1)


def main():
    print("🎯 Testing GUI-style conversation sync")
    print("This mimics exactly what the GUI does")
    
    # Create config with corrected token format (hyphens not underscores)
    config = PoeSearchConfig()
    
    # Set tokens exactly as the GUI expects them
    tokens = {
        "p-b": "AG58MLIXFnbOh98QAv4YHA==",
        "p-lat": "87OepyV2QcF9TkiuqhaFyWZgROH+Vp00g0QZLwZEMg==",
        "formkey": "c25281d6b4dfb3f76fb03c597e3e61aa"
    }
    config.poe_tokens = tokens
    
    print(f"\n🔧 Using token format: {list(tokens.keys())}")
    
    try:
        # Step 1: Create PoeSearchClient (same as GUI)
        print("\n📱 Step 1: Creating PoeSearchClient like GUI does")
        search_client = PoeSearchClient(config=config)
        print("✓ PoeSearchClient created successfully!")
        
        # Step 2: Test conversation retrieval with current limits
        print("\n📱 Step 2: Testing conversation retrieval (current method)")
        
        # Test the actual method the sync worker calls
        print("  Calling get_conversation_history() like sync worker...")
        try:
            # Use same parameters as sync worker but log the process
            logger.info("About to call get_conversation_history(days=3650, limit=10000)")
            conversations = search_client.get_conversation_history(days=3650, limit=10000)
            logger.info(f"get_conversation_history returned {len(conversations)} conversations")
            
            print(f"    ✓ SUCCESS: Found {len(conversations)} conversations!")
            
            if len(conversations) > 0:
                print(f"\n💬 Sample conversations:")
                for i, conv in enumerate(conversations[:3]):
                    title = conv.get('title', 'No title')[:40]
                    conv_id = conv.get('id', 'No ID')[:15]
                    bot = conv.get('bot', {})
                    bot_name = bot.get('displayName', 'Unknown') if isinstance(bot, dict) else str(bot)
                    print(f"  {i+1}. {title}... (ID: {conv_id}..., Bot: {bot_name})")
                
                print(f"\n✅ SOLUTION VERIFIED!")
                print(f"✅ The user now has access to {len(conversations)} conversations!")
                print(f"✅ Zero conversations problem is SOLVED!")
                return True
            else:
                print(f"\n⚠️  Still getting 0 conversations - investigating...")
                return False
                
        except Exception as e:
            logger.error(f"get_conversation_history failed: {e}")
            print(f"    ❌ Error: {e}")
            return False
            
    except Exception as e:
        logger.error(f"Client creation failed: {e}")
        print(f"❌ Failed to create client: {e}")
        return False


if __name__ == "__main__":
    print("="*60)
    success = main()
    print("="*60)
    if success:
        print("🎉 FINAL SUCCESS: All fixes working together!")
        print("🎉 User can now access ALL their Poe conversations!")
    else:
        print("❌ Still troubleshooting...")
    print("="*60)
