#!/usr/bin/env python3
"""Debug script for official Poe API to understand empty responses."""

import asyncio
import logging
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import fastapi_poe as fp

from poe_search.utils.config import get_poe_api_key

# Set up logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def test_async_api():
    """Test the async version of the API."""
    print("🔄 Testing async API...")
    
    api_key = get_poe_api_key()
    if not api_key:
        print("❌ No API key found")
        return
    
    try:
        message = fp.ProtocolMessage(role="user", content="Hello! Please respond with a simple greeting.")
        
        print(f"📤 Sending message to GPT-3.5-Turbo...")
        response_parts = []
        
        async for partial in fp.get_bot_response(
            messages=[message], 
            bot_name="GPT-3.5-Turbo", 
            api_key=api_key
        ):
            print(f"📥 Partial response: {partial}")
            if hasattr(partial, 'text') and partial.text:
                response_parts.append(partial.text)
                print(f"   Content: {partial.text}")
            else:
                print(f"   No content in partial: {type(partial)}")
        
        response = ''.join(response_parts)
        print(f"✅ Final response: {response}")
        print(f"📊 Response length: {len(response)}")
        
    except Exception as e:
        print(f"❌ Async API test failed: {e}")
        import traceback
        traceback.print_exc()


def test_sync_api():
    """Test the sync version of the API."""
    print("🔄 Testing sync API...")
    
    api_key = get_poe_api_key()
    if not api_key:
        print("❌ No API key found")
        return
    
    try:
        message = fp.ProtocolMessage(role="user", content="Hello! Please respond with a simple greeting.")
        
        print(f"📤 Sending message to GPT-3.5-Turbo...")
        response_parts = []
        
        for partial in fp.get_bot_response_sync(
            messages=[message], 
            bot_name="GPT-3.5-Turbo", 
            api_key=api_key
        ):
            print(f"📥 Partial response: {partial}")
            if hasattr(partial, 'text') and partial.text:
                response_parts.append(partial.text)
                print(f"   Content: {partial.text}")
            else:
                print(f"   No content in partial: {type(partial)}")
        
        response = ''.join(response_parts)
        print(f"✅ Final response: {response}")
        print(f"📊 Response length: {len(response)}")
        
    except Exception as e:
        print(f"❌ Sync API test failed: {e}")
        import traceback
        traceback.print_exc()


def test_different_messages():
    """Test with different message formats."""
    print("🔄 Testing different message formats...")
    
    api_key = get_poe_api_key()
    if not api_key:
        print("❌ No API key found")
        return
    
    test_messages = [
        "Hi",
        "Hello, how are you?",
        "What is 2+2?",
        "Please explain quantum computing in simple terms.",
        "Write a short poem about programming."
    ]
    
    for i, msg in enumerate(test_messages, 1):
        print(f"\n--- Test {i}: {msg[:30]}... ---")
        try:
            message = fp.ProtocolMessage(role="user", content=msg)
            response_parts = []
            
            for partial in fp.get_bot_response_sync(
                messages=[message], 
                bot_name="GPT-3.5-Turbo", 
                api_key=api_key
            ):
                if hasattr(partial, 'text') and partial.text:
                    response_parts.append(partial.text)
            
            response = ''.join(response_parts)
            print(f"Response length: {len(response)}")
            if response:
                print(f"Response: {response[:100]}...")
            else:
                print("Empty response")
                
        except Exception as e:
            print(f"Error: {e}")


def test_different_bots():
    """Test with different bots."""
    print("🔄 Testing different bots...")
    
    api_key = get_poe_api_key()
    if not api_key:
        print("❌ No API key found")
        return
    
    test_bots = ["GPT-3.5-Turbo", "GPT-4", "Claude-3-Haiku"]
    
    for bot in test_bots:
        print(f"\n--- Testing {bot} ---")
        try:
            message = fp.ProtocolMessage(role="user", content="Say hello!")
            response_parts = []
            
            for partial in fp.get_bot_response_sync(
                messages=[message], 
                bot_name=bot, 
                api_key=api_key
            ):
                if hasattr(partial, 'text') and partial.text:
                    response_parts.append(partial.text)
            
            response = ''.join(response_parts)
            print(f"Response length: {len(response)}")
            if response:
                print(f"Response: {response[:100]}...")
            else:
                print("Empty response")
                
        except Exception as e:
            print(f"Error: {e}")


def main():
    """Main function."""
    print("🔍 Poe Search - Official API Debug")
    print("=" * 50)
    
    # Test 1: Sync API
    test_sync_api()
    
    print("\n" + "="*50)
    
    # Test 2: Different messages
    test_different_messages()
    
    print("\n" + "="*50)
    
    # Test 3: Different bots
    test_different_bots()
    
    print("\n" + "="*50)
    
    # Test 4: Async API (if needed)
    print("Testing async API...")
    asyncio.run(test_async_api())


if __name__ == "__main__":
    main() 