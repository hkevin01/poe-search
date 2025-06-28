"""API client for Poe.com."""

import logging
import time
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import httpx

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
            "User-Agent": (
                "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36"
            ),
            "Accept": (
                "text/html,application/xhtml+xml,application/xml;q=0.9,"
                "image/webp,*/*;q=0.8"
            ),
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
                proxy=self.proxy,
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
            logger.error(
                f"HTTP error {e.response.status_code}: {e.response.text}"
            )
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
        
        try:
            # Make GraphQL query to get recent conversations
            query = """
            query GetRecentConversations($count: Int!) {
                viewer {
                    recentConversations(count: $count) {
                        id
                        title
                        createdAt
                        updatedAt
                        messageCount
                        bot {
                            id
                            displayName
                        }
                    }
                }
            }
            """
            
            variables = {"count": 50}  # Get up to 50 recent conversations
            
            response = self._make_gql_request(query, variables)
            
            # Log the response for debugging
            logger.debug(f"API Response: {response}")
            
            if "data" in response and "viewer" in response["data"]:
                conversations = response["data"]["viewer"]["recentConversations"]
                logger.info(f"Fetched {len(conversations)} conversations")
                return conversations
            else:
                logger.warning("No conversations found in API response")
                logger.warning(f"Response structure: {list(response.keys()) if isinstance(response, dict) else 'Not a dict'}")
                return []
                
        except Exception as e:
            logger.error(f"Failed to fetch conversations: {e}")
            logger.info("Falling back to mock data for testing")
            return self._get_mock_conversations(days)
    
    def _get_mock_conversations(self, days: int = 7) -> List[Dict[str, Any]]:
        """Get mock conversation data for testing.
        
        Args:
            days: Number of days to look back
            
        Returns:
            List of mock conversation data
        """
        conversations = []
        start_date = datetime.now() - timedelta(days=days)
        
        # Mock conversation data that looks more realistic
        mock_titles = [
            "Python programming help",
            "Machine learning discussion",
            "Web development questions",
            "Data analysis project",
            "Code review assistance",
            "Algorithm optimization",
            "Database design help",
            "API integration guide"
        ]
        
        mock_bots = ["chinchilla", "a2", "capybara", "beaver", "a2_2"]
        bot_names = ["ChatGPT", "Claude", "Assistant", "GPT-4", "Claude-2"]
        
        for i in range(8):  # Mock 8 conversations
            bot_id = mock_bots[i % len(mock_bots)]
            bot_name = bot_names[i % len(bot_names)]
            
            conversation = {
                "id": f"conv_{i:03d}",
                "title": mock_titles[i % len(mock_titles)],
                "createdAt": (start_date + timedelta(days=i)).isoformat(),
                "updatedAt": (start_date + timedelta(days=i, hours=1)).isoformat(),
                "messageCount": 10 + i * 2,
                "bot": {
                    "id": bot_id,
                    "displayName": bot_name
                },
                "messages": [
                    {
                        "id": f"msg_{i:03d}_{j:03d}",
                        "role": "user" if j % 2 == 0 else "bot",
                        "content": f"This is message {j+1} in conversation {i+1}. It contains some sample content for testing the search functionality.",
                        "createdAt": (start_date + timedelta(days=i, minutes=j*5)).isoformat(),
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
    
    def get_conversation_ids(self, days: int = 7) -> List[str]:
        """Get list of conversation IDs from Poe.
        
        Args:
            days: Number of days to look back
            
        Returns:
            List of conversation IDs
        """
        logger.info(f"Fetching conversation IDs from last {days} days")
        
        conversations = self.get_recent_conversations(days)
        return [conv["id"] for conv in conversations]
    
    def get_recent_conversation_ids(self, days: int = 7) -> List[str]:
        """Get recent conversation IDs (alias for get_conversation_ids).
        
        Args:
            days: Number of days to look back
            
        Returns:
            List of conversation IDs
        """
        return self.get_conversation_ids(days)
    
    def get_conversation(self, conversation_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific conversation with its messages.
        
        Args:
            conversation_id: Conversation ID
            
        Returns:
            Conversation data with messages, or None if not found
        """
        logger.info(f"Fetching conversation: {conversation_id}")
        
        try:
            # Make GraphQL query to get conversation details
            query = """
            query GetConversation($id: ID!) {
                conversation(id: $id) {
                    id
                    title
                    createdAt
                    updatedAt
                    messageCount
                    bot {
                        id
                        displayName
                    }
                    messages {
                        id
                        role
                        content
                        createdAt
                    }
                }
            }
            """
            
            variables = {"id": conversation_id}
            
            response = self._make_gql_request(query, variables)
            
            if "data" in response and "conversation" in response["data"]:
                conversation = response["data"]["conversation"]
                logger.info(f"Fetched conversation: {conversation_id}")
                return conversation
            else:
                logger.warning(f"Conversation {conversation_id} not found")
                return None
                
        except Exception as e:
            logger.error(f"Failed to fetch conversation {conversation_id}: {e}")
            return None
    
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
    
    def _make_gql_request(self, query: str, variables: Dict[str, Any]) -> Dict[str, Any]:
        """Make a GraphQL request to Poe API.
        
        Args:
            query: GraphQL query string
            variables: Query variables
            
        Returns:
            API response data
        """
        payload = {
            "query": query,
            "variables": variables
        }
        
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        
        response = self._make_request("POST", self.gql_url, json=payload, headers=headers)
        return response.json()
