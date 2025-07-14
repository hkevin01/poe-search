"""
Direct Poe API client that bypasses problematic wrappers
"""
import logging
import httpx
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

class DirectPoeClient:
    """Direct implementation of Poe API client"""
    
    def __init__(self, formkey: str, token: str):
        self.formkey = formkey
        self.token = token
        self.session = httpx.Client(
            headers={
                "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36",
                "Cookie": f"p-b={token}",
                "Poe-Formkey": formkey,
                "Content-Type": "application/json",
            },
            timeout=30.0
        )
    
    def test_connection(self) -> bool:
        """Test if we can connect to Poe.com"""
        try:
            response = self.session.get("https://poe.com")
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Connection test failed: {e}")
            return False
    
    def get_conversations(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get conversations from Poe using GraphQL"""
        query = {
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
            "variables": {"count": limit}
        }
        
        try:
            logger.info(f"Fetching conversations from Poe (limit: {limit})")
            response = self.session.post("https://poe.com/api/gql_POST", json=query)
            
            if response.status_code == 200:
                data = response.json()
                conversations = []
                
                if "data" in data and "chats" in data["data"]:
                    for edge in data["data"]["chats"]["edges"]:
                        node = edge["node"]
                        conversations.append({
                            "id": node["id"],
                            "title": node["title"],
                            "created_at": node["creationTime"],
                            "last_message_time": node.get("lastMessageTime"),
                            "bot": node["bot"]["nickname"] if node.get("bot") else "unknown",
                            "message_count": 0  # Will be updated when we fetch messages
                        })
                
                logger.info(f"Successfully fetched {len(conversations)} conversations")
                return conversations
            else:
                logger.error(f"GraphQL query failed: {response.status_code} - {response.text[:200]}")
                return []
                
        except Exception as e:
            logger.error(f"Failed to get conversations: {e}")
            return []
    
    def close(self):
        """Close the HTTP session"""
        if self.session:
            self.session.close()
