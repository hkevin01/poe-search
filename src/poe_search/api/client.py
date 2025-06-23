"""API client for Poe.com."""

import logging
import time
from typing import Any, Dict, List, Optional
from datetime import datetime, timedelta

import httpx
import websocket
from websocket import WebSocketApp

logger = logging.getLogger(__name__)


class PoeAPIClient:
    """Client for interacting with Poe.com API."""
    
    def __init__(self, token: str, proxy: Optional[str] = None):
        """Initialize the Poe API client.
        
        Args:
            token: Poe authentication token (p-b cookie)
            proxy: Optional proxy URL
        """
        self.token = token
        self.proxy = proxy
        self.session = self._setup_session()
        self.base_url = "https://poe.com"
        self.gql_url = f"{self.base_url}/api/gql_POST"
        
        # Rate limiting
        self.last_request_time = 0
        self.min_request_interval = 1.0  # Minimum seconds between requests
        
        # Bot information cache
        self._bots = {}
        self._bot_names = {}
    
    def _setup_session(self) -> httpx.Client:
        """Set up HTTP session with authentication."""
        headers = {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
        }
        
        client = httpx.Client(headers=headers, timeout=30.0)
        
        if self.proxy:
            client = httpx.Client(
                headers=headers,
                timeout=30.0,
                proxies=self.proxy,
            )
        
        # Set authentication cookie
        client.cookies.set("p-b", self.token, domain="poe.com")
        
        return client
    
    def _rate_limit(self):
        """Implement rate limiting."""
        elapsed = time.time() - self.last_request_time
        if elapsed < self.min_request_interval:
            time.sleep(self.min_request_interval - elapsed)
        self.last_request_time = time.time()
    
    def _make_request(self, method: str, url: str, **kwargs) -> httpx.Response:
        """Make HTTP request with rate limiting and error handling."""
        self._rate_limit()
        
        try:
            response = self.session.request(method, url, **kwargs)
            response.raise_for_status()
            return response
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error {e.response.status_code}: {e.response.text}")
            raise
        except httpx.RequestError as e:
            logger.error(f"Request error: {e}")
            raise
    
    def get_bots(self) -> Dict[str, Any]:
        """Get available bots from Poe.
        
        Returns:
            Dictionary of bot information
        """
        logger.info("Fetching available bots")
        
        try:
            response = self._make_request("GET", f"{self.base_url}/")
            # Parse bot information from response
            # This is a simplified implementation
            # In a real implementation, you'd parse the HTML/JS to extract bot data
            
            # Mock data for now
            self._bots = {
                "chinchilla": {"displayName": "ChatGPT", "id": "chinchilla"},
                "a2": {"displayName": "Claude-instant", "id": "a2"},
                "capybara": {"displayName": "Assistant", "id": "capybara"},
                "beaver": {"displayName": "GPT-4", "id": "beaver"},
                "a2_2": {"displayName": "Claude-2-100k", "id": "a2_2"},
                "llama_2_7b_chat": {"displayName": "Llama-2-7b", "id": "llama_2_7b_chat"},
            }
            
            self._bot_names = {
                bot_id: bot_data["displayName"] 
                for bot_id, bot_data in self._bots.items()
            }
            
            return self._bots
            
        except Exception as e:
            logger.error(f"Failed to fetch bots: {e}")
            return {}
    
    def get_recent_conversations(self, days: int = 7) -> List[Dict[str, Any]]:
        """Get recent conversations from Poe.
        
        Args:
            days: Number of days to look back
            
        Returns:
            List of conversation data
        """
        logger.info(f"Fetching conversations from last {days} days")
        
        # In a real implementation, this would make actual API calls to Poe
        # For now, return mock data
        
        conversations = []
        start_date = datetime.now() - timedelta(days=days)
        
        # Mock conversation data
        for i in range(5):  # Mock 5 conversations
            conversation = {
                "id": f"conv_{i}",
                "bot": list(self._bots.keys())[i % len(self._bots)] if self._bots else "chinchilla",
                "title": f"Conversation {i+1}",
                "created_at": (start_date + timedelta(days=i)).isoformat(),
                "updated_at": (start_date + timedelta(days=i, hours=1)).isoformat(),
                "message_count": 10 + i * 2,
                "messages": [
                    {
                        "id": f"msg_{i}_{j}",
                        "role": "user" if j % 2 == 0 else "bot",
                        "content": f"Message {j+1} in conversation {i+1}",
                        "timestamp": (start_date + timedelta(days=i, minutes=j*5)).isoformat(),
                    }
                    for j in range(4)  # 4 messages per conversation
                ],
            }
            conversations.append(conversation)
        
        return conversations
    
    def get_conversation_history(
        self,
        bot: str,
        count: int = 25,
        cursor: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Get conversation history for a specific bot.
        
        Args:
            bot: Bot identifier
            count: Number of messages to retrieve
            cursor: Pagination cursor
            
        Returns:
            List of message data
        """
        logger.info(f"Fetching conversation history for {bot}")
        
        # In a real implementation, this would make GraphQL queries to Poe
        # For now, return mock data
        
        messages = []
        for i in range(min(count, 10)):  # Mock up to 10 messages
            message = {
                "id": f"msg_hist_{i}",
                "conversation_id": f"conv_{bot}",
                "role": "user" if i % 2 == 0 else "bot",
                "content": f"Historical message {i+1} for {bot}",
                "timestamp": (datetime.now() - timedelta(hours=i)).isoformat(),
                "bot": bot,
            }
            messages.append(message)
        
        return messages
    
    def send_message(
        self,
        bot: str,
        message: str,
        conversation_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Send a message to a bot.
        
        Args:
            bot: Bot identifier
            message: Message content
            conversation_id: Optional conversation ID
            
        Returns:
            Response data
        """
        logger.info(f"Sending message to {bot}")
        
        # In a real implementation, this would send the message via websocket/API
        # For now, return mock response
        
        response = {
            "id": f"response_{int(time.time())}",
            "conversation_id": conversation_id or f"new_conv_{int(time.time())}",
            "content": f"Mock response from {bot} to: {message}",
            "timestamp": datetime.now().isoformat(),
            "bot": bot,
        }
        
        return response
    
    def delete_conversation(self, conversation_id: str) -> bool:
        """Delete a conversation.
        
        Args:
            conversation_id: ID of conversation to delete
            
        Returns:
            Success status
        """
        logger.info(f"Deleting conversation {conversation_id}")
        
        # In a real implementation, this would call the delete API
        # For now, return success
        
        return True
    
    def clear_conversation(self, bot: str) -> bool:
        """Clear conversation history with a bot.
        
        Args:
            bot: Bot identifier
            
        Returns:
            Success status
        """
        logger.info(f"Clearing conversation with {bot}")
        
        # In a real implementation, this would call the clear API
        # For now, return success
        
        return True
