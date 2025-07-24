#!/usr/bin/env python3
"""
Test using the exact same approach as the successful GUI.
"""

import logging
import sys
import os
from pathlib import Path

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_gui_approach():
    """Test using the same approach as the working GUI."""
    
    # Set up logging to match GUI
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    logger = logging.getLogger(__name__)
    
    try:
        from poe_search.utils.config import load_config
        from poe_search.client import PoeSearchClient
        from poe_search.storage.database import Database
        
        logger.info("🔧 Using GUI approach to test conversation sync...")
        
        # Load config like GUI does
        config = load_config()
        logger.info("✅ Configuration loaded")
        
        # Set up database path like GUI does
        db_path = Path(__file__).parent / "data" / "poe_search.db"
        
        # Initialize client like GUI does
        client = PoeSearchClient(config=config, database_url=f"sqlite:///{db_path}")
        logger.info("✅ PoeSearchClient created")
        
        # Get the underlying API client like GUI does
        api_client = client.api_client
        client_type = type(api_client).__name__
        logger.info(f"✅ Got API client: {client_type}")
        
        # Test connection like GUI does
        try:
            user_info = api_client.get_user_info()
            if user_info:
                username = user_info.get('username', 'Unknown')
                logger.info(f"✅ Connected to Poe.com as: {username}")
                
                # Test conversation history using the client method that works
                logger.info("📚 Testing conversation history...")
                conversations = client.get_conversation_history(days=30, limit=50)
                
                if conversations:
                    logger.info(f"🎉 Found {len(conversations)} conversations!")
                    return True
                else:
                    logger.info("ℹ️ No conversations found (but connection works)")
                    return True  # Connection works, just no conversations
            else:
                logger.error("❌ Could not get user info")
                return False
                
        except Exception as e:
            logger.error(f"❌ Connection test failed: {e}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Test failed: {e}", exc_info=True)
        return False

if __name__ == "__main__":
    success = test_gui_approach()
    if success:
        print("\n🎉 GUI approach test successful!")
        sys.exit(0)
    else:
        print("\n💥 GUI approach test failed!")
        sys.exit(1)
