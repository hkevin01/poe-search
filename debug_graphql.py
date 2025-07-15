#!/usr/bin/env python3
"""
Enhanced debug script to test GraphQL queries against Poe.com API
"""
import asyncio
import json
import httpx
from pathlib import Path
import sys
import logging
import json
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from poe_search.utils.config import load_config

# Set up logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def test_poe_graphql():
    """Test different GraphQL queries with Poe.com"""
    
    # Load config and get tokens
    config = load_config()
    tokens = config.get_poe_tokens()
    
    if not tokens.get('formkey') or not tokens.get('p-b'):
        logger.error("Missing required tokens")
        return
        
    logger.info("Testing Poe.com GraphQL API...")
    logger.info(f"Formkey: {tokens['formkey'][:10]}...")
    logger.info(f"P-B token: {tokens['p-b'][:10]}...")
    
    # Create session with proper headers
    session = httpx.Client(
        headers={
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Cookie": f"p-b={tokens['p-b']}",
            "Poe-Formkey": tokens['formkey'],
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Origin": "https://poe.com",
            "Referer": "https://poe.com/",
            "X-Requested-With": "XMLHttpRequest",
        },
        timeout=30.0
    )
    
    # Test queries in order of complexity
    queries = [
        {
            "name": "Simple viewer query",
            "query": {
                "query": "query { viewer { id } }",
                "variables": {}
            }
        },
        {
            "name": "User info query", 
            "query": {
                "query": """
                query {
                  viewer {
                    id
                    handle
                    displayName
                  }
                }
                """,
                "variables": {}
            }
        },
        {
            "name": "Chat list query (simplified)",
            "query": {
                "query": """
                query {
                  chats(first: 5) {
                    edges {
                      node {
                        id
                        title
                      }
                    }
                  }
                }
                """,
                "variables": {}
            }
        },
        {
            "name": "Chat list query (full)",
            "query": {
                "query": """
                query ChatListPaginationQuery($count: Int!) {
                  chats(first: $count) {
                    edges {
                      node {
                        id
                        title
                        creationTime
                        lastMessageTime
                        bot {
                          displayName
                          nickname
                        }
                      }
                    }
                  }
                }
                """,
                "variables": {"count": 10}
            }
        }
    ]
    
    for test in queries:
        logger.info(f"\n=== Testing: {test['name']} ===")
        
        try:
            response = session.post(
                "https://poe.com/api/gql_POST",
                json=test['query']
            )
            
            logger.info(f"Status: {response.status_code}")
            logger.info(f"Headers: {dict(response.headers)}")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    logger.info(f"Success! Response: {json.dumps(data, indent=2)}")
                    
                    # If this is the chat list query, count conversations
                    if "chats" in str(data):
                        if "data" in data and "chats" in data["data"]:
                            count = len(data["data"]["chats"]["edges"])
                            logger.info(f"Found {count} conversations!")
                        
                except json.JSONDecodeError as e:
                    logger.error(f"JSON decode error: {e}")
                    logger.error(f"Raw response: {response.text[:500]}")
            else:
                logger.error(f"Failed with status {response.status_code}")
                logger.error(f"Response: {response.text[:500]}")
                
        except Exception as e:
            logger.error(f"Request failed: {e}")
    
    session.close()
    
    # Also test the main page to see if we're logged in
    logger.info("\n=== Testing main page access ===")
    try:
        session2 = httpx.Client(
            headers={
                "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Cookie": f"p-b={tokens['p-b']}",
            },
            timeout=30.0
        )
        
        response = session2.get("https://poe.com/", follow_redirects=True)
        logger.info(f"Main page status: {response.status_code}")
        logger.info(f"Final URL: {response.url}")
        
        # Check if we're redirected to login
        if "login" in str(response.url):
            logger.warning("Redirected to login - may not be properly authenticated")
        else:
            logger.info("Successfully accessed main page - likely authenticated")
            
        session2.close()
        
    except Exception as e:
        logger.error(f"Main page test failed: {e}")


if __name__ == "__main__":
    test_poe_graphql()
