#!/usr/bin/env python3
"""
Check if we can access the authenticated Poe.com homepage.
"""

import sys
import logging
import httpx
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from poe_search.utils.config import load_config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_authentication():
    """Test if our tokens allow access to authenticated pages."""
    
    config = load_config()
    tokens = config.get_poe_tokens()
    
    if not tokens.get('formkey') or not tokens.get('p-b'):
        logger.error("Missing tokens")
        return False
        
    logger.info("Testing authentication with full cookie set...")
    
    # Create session with all cookies, not just p-b
    session = httpx.Client(
        headers={
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
        },
        timeout=30.0,
        follow_redirects=True
    )
    
    # Set cookies properly
    cookie_header = f"p-b={tokens['p-b']}"
    if tokens.get('p-lat'):
        cookie_header += f"; p-lat={tokens['p-lat']}"
    
    session.headers["Cookie"] = cookie_header
    
    try:
        # Try to access main page
        logger.info("Accessing https://poe.com/...")
        response = session.get("https://poe.com/")
        
        logger.info(f"Status: {response.status_code}")
        logger.info(f"Final URL: {response.url}")
        
        # Check if we're logged in by looking for login indicators
        content = response.text.lower()
        
        if "login" in str(response.url):
            logger.error("❌ Redirected to login page - not authenticated")
            return False
        elif "sign in" in content or "log in" in content:
            logger.error("❌ Login prompts found in content - not authenticated")
            return False
        elif "chat" in content or "conversation" in content:
            logger.info("✅ Authenticated! Found chat/conversation content")
            return True
        else:
            logger.warning("⚠️ Authentication status unclear")
            logger.info(f"Content preview: {content[:200]}...")
            return False
            
    except Exception as e:
        logger.error(f"Request failed: {e}")
        return False
    finally:
        session.close()

if __name__ == "__main__":
    if test_authentication():
        print("✅ Authentication working!")
        exit(0)
    else:
        print("❌ Authentication failed!")
        exit(1)
