#!/usr/bin/env python3
"""
Test script to check if we can sync conversations using the working wrapper client.
"""

import logging
import sys
import os

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from poe_search.client import PoeSearchClient
from poe_search.storage.database import Database

def test_wrapper_sync():
    """Test syncing conversations using the wrapper client."""
    
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    logger = logging.getLogger(__name__)
    
    logger.info("🧪 Testing wrapper client conversation sync...")
    
    try:
        # Initialize database and client
        db = Database()
        client = PoeSearchClient()
        
        # First, test if we can connect using the main client
        logger.info("🔌 Testing basic connection...")
        if hasattr(client, 'api_client') and client.api_client:
            # Get API client type
            api_client = client.api_client
            client_type = type(api_client).__name__
            logger.info(f"✅ Found API client: {client_type}")
            
            # Test getting conversation history via the main client
            logger.info("📚 Testing conversation history fetch...")
            conversations = client.get_conversation_history(days=30, limit=20)
            
            if conversations:
                logger.info(f"✅ Found {len(conversations)} conversations!")
                
                # Show some details
                for i, conv in enumerate(conversations[:3]):
                    conv_id = conv.get('id', 'Unknown')
                    title = conv.get('title', 'Untitled')[:50]
                    logger.info(f"  {i+1}. ID: {conv_id}, Title: {title}")
                    
                # Test database storage
                logger.info("💾 Testing database storage...")
                for conversation in conversations[:5]:
                    try:
                        # Save conversation to database
                        db.save_conversation(conversation)
                        logger.info(f"  ✅ Saved conversation: {conversation.get('id', 'Unknown')}")
                    except Exception as e:
                        logger.error(f"  ❌ Failed to save conversation: {e}")
                        
                # Check what we stored
                stored_conversations = db.get_conversations()
                logger.info(f"✅ Database now contains {len(stored_conversations)} conversations")
                
                return True
            else:
                logger.warning("⚠️ No conversations found")
                # Check if it's an empty result or an error
                try:
                    user_info = api_client.get_user_info() if hasattr(api_client, 'get_user_info') else None
                    if user_info:
                        logger.info(f"✅ User info accessible: {user_info.get('username', 'Unknown')}")
                        logger.info("   This suggests authentication is working but no conversations exist")
                    else:
                        logger.warning("⚠️ Cannot get user info")
                except Exception as e:
                    logger.error(f"❌ Error getting user info: {e}")
                return False
        else:
            logger.error("❌ No API client available")
            return False
            
    except Exception as e:
        logger.error(f"❌ Test failed: {e}", exc_info=True)
        return False

if __name__ == "__main__":
    success = test_wrapper_sync()
    if success:
        print("\n🎉 Wrapper sync test completed successfully!")
        sys.exit(0)
    else:
        print("\n💥 Wrapper sync test failed!")
        sys.exit(1)
