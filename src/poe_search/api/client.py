"""API client for Poe.com using poe-api-wrapper."""

import logging
import random
import time
from datetime import datetime, timedelta
from functools import wraps
from typing import Any, Dict, List, Optional

import requests
from poe_api_wrapper import PoeApi

from poe_search.utils.config import load_poe_tokens_from_file

logger = logging.getLogger(__name__)


def rate_limited(max_calls: int = 10, time_window: int = 60,
                retry_attempts: int = 3, base_delay: int = 5,
                max_delay: int = 60, jitter_range: float = 0.5,
                show_warnings: bool = True, 
                prompt_token_costs: bool = True):
    """Decorator to implement rate limiting and retry logic.
    
    Args:
        max_calls: Maximum number of calls allowed in time window
        time_window: Time window in seconds
        retry_attempts: Number of retry attempts for failed calls
        base_delay: Base delay for exponential backoff
        max_delay: Maximum delay cap
        jitter_range: Jitter range for delays
        show_warnings: Whether to show rate limit warnings
        prompt_token_costs: Whether to prompt for token costs
    """
    def decorator(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            # Check if rate limiting is disabled
            if (hasattr(self, 'rate_limit_config') and 
                    not self.rate_limit_config.get('enabled', True)):
                return func(self, *args, **kwargs)
            
            # Initialize rate limiting state if not exists
            if not hasattr(self, '_rate_limit_state'):
                self._rate_limit_state = {
                    'calls': [],
                    'last_call_time': 0
                }
            
            # Check rate limiting
            current_time = time.time()
            state = self._rate_limit_state
            
            # Remove old calls outside the time window
            state['calls'] = [
                call_time for call_time in state['calls']
                if current_time - call_time < time_window
            ]
            
            # Check if we're at the rate limit
            if len(state['calls']) >= max_calls:
                wait_time = time_window - (current_time - state['calls'][0])
                if wait_time > 0:
                    if show_warnings:
                        logger.warning(
                            f"Rate limit reached. Waiting {wait_time:.1f} seconds..."
                        )
                    time.sleep(wait_time)
                    current_time = time.time()
            
            # Add jitter to avoid thundering herd
            jitter = random.uniform(0.1, jitter_range)
            time.sleep(jitter)
            
            # Retry logic with exponential backoff
            last_exception = None
            for attempt in range(retry_attempts + 1):
                try:
                    # Record the call
                    state['calls'].append(time.time())
                    state['last_call_time'] = time.time()
                    
                    # Make the API call
                    result = func(self, *args, **kwargs)
                    
                    # If successful, return immediately
                    return result
                    
                except Exception as e:
                    last_exception = e
                    error_msg = str(e).lower()
                    
                    # Check if it's a rate limit error
                    rate_limit_keywords = [
                        'rate limit', '429', 'too many requests', 'quota'
                    ]
                    if any(keyword in error_msg for keyword in rate_limit_keywords):
                        if attempt < retry_attempts:
                            # Exponential backoff: 2^attempt * base_delay
                            delay = min(base_delay * (2 ** attempt), max_delay)
                            jitter = random.uniform(0.5, 1.5)
                            total_delay = delay * jitter
                            
                            if show_warnings:
                                logger.warning(
                                    f"Rate limit hit (attempt {attempt + 1}/"
                                    f"{retry_attempts + 1}). "
                                    f"Waiting {total_delay:.1f} seconds before retry..."
                                )
                            time.sleep(total_delay)
                            continue
                        else:
                            if show_warnings:
                                logger.error(
                                    f"Rate limit exceeded after {retry_attempts + 1} "
                                    "attempts"
                                )
                            raise
                    
                    # Check for token cost prompts
                    elif (prompt_token_costs and 
                          any(keyword in error_msg for keyword in 
                              ['token', 'cost', 'payment', 'subscription'])):
                        if hasattr(self, 'handle_token_cost_prompt'):
                            self.handle_token_cost_prompt(error_msg)
                        else:
                            logger.warning(
                                f"Token cost prompt detected: {error_msg}"
                            )
                    
                    # For other errors, retry with shorter delays
                    elif attempt < retry_attempts:
                        delay = min(2 ** attempt, 10)  # Shorter delays
                        if show_warnings:
                            logger.warning(
                                f"API call failed (attempt {attempt + 1}/"
                                f"{retry_attempts + 1}): {e}. "
                                f"Retrying in {delay} seconds..."
                            )
                        time.sleep(delay)
                        continue
                    else:
                        if show_warnings:
                            logger.error(
                                f"API call failed after {retry_attempts + 1} "
                                f"attempts: {e}"
                            )
                        raise
            
            # If we get here, all retries failed
            if last_exception:
                raise last_exception
            
        return wrapper
    return decorator


class PoeAPIClient:
    """Client for interacting with Poe.com API using poe-api-wrapper."""
    
    def __init__(self, token: str, proxy: Optional[str] = None, config=None):
        """Initialize the Poe API client.
        
        Args:
            token: Poe authentication token (p-b cookie) or dict of tokens
            proxy: Optional proxy URL
            config: Configuration object for rate limiting settings
        """
        self.token = token
        self.proxy = proxy
        self.config = config
        
        # Rate limiting configuration - use config if available, otherwise defaults
        if config and hasattr(config, 'rate_limit'):
            self.rate_limit_config = {
                'max_calls': config.rate_limit.max_calls_per_minute,
                'time_window': 60,  # 1 minute window
                'retry_attempts': config.rate_limit.retry_attempts,
                'base_delay': config.rate_limit.base_delay_seconds,
                'max_delay': config.rate_limit.max_delay_seconds,
                'jitter_range': config.rate_limit.jitter_range,
                'show_warnings': config.rate_limit.show_rate_limit_warnings,
                'prompt_token_costs': config.rate_limit.prompt_for_token_costs,
            }
        else:
            # Default rate limiting configuration
            self.rate_limit_config = {
                'max_calls': 8,  # Conservative limit
                'time_window': 60,  # 1 minute window
                'retry_attempts': 3,
                'base_delay': 5,
                'max_delay': 60,
                'jitter_range': 0.5,
                'show_warnings': True,
                'prompt_token_costs': True,
            }
        
        # Handle both string token and dict of tokens
        if isinstance(token, str):
            # Legacy format - use p-b token as both cookies
            tokens = {
                "p-b": token,
                "p-lat": token  # Using same token for both cookies
            }
        elif isinstance(token, dict):
            # New format - use provided tokens
            tokens = token
        else:
            raise ValueError("Token must be string or dict")
        
        try:
            self.client = PoeApi(tokens)
            logger.info("PoeApi client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize PoeApi client: {e}")
            self.client = None
    
    def handle_token_cost_prompt(self, error_msg: str):
        """Handle token cost prompts from Poe.com.
        
        Args:
            error_msg: Error message containing token cost information
        """
        logger.warning(f"Token cost prompt detected: {error_msg}")
        
        # Extract cost information if available
        cost_info = "Token cost information"
        if "cost" in error_msg.lower():
            cost_info = "Poe.com is requesting payment for additional tokens"
        elif "subscription" in error_msg.lower():
            cost_info = "Poe.com is requesting a subscription upgrade"
        elif "payment" in error_msg.lower():
            cost_info = "Poe.com is requesting payment"
        
        # Log the prompt for user awareness
        logger.info(f"Token cost prompt: {cost_info}")
        logger.info("Please visit https://poe.com to purchase additional tokens")
        
        # Could integrate with GUI to show a dialog here
        if hasattr(self, 'config') and self.config:
            logger.info("Token cost prompt logged - check Poe.com for details")
    
    @rate_limited(max_calls=5, time_window=60, retry_attempts=3)
    def get_user_info(self) -> Dict[str, Any]:
        """Get user information from Poe.
        
        Returns:
            Dictionary of user information
        """
        logger.info("Fetching user information")
        
        if not self.client:
            logger.error("PoeApi client not initialized")
            return {}
        
        try:
            # Try to get user settings
            settings = self.client.get_settings()
            
            user_info = {
                "settings": settings if isinstance(settings, dict) else {},
                "subscription": {},
                "message_points": {}
            }
            
            # Extract subscription info from settings if available
            if isinstance(settings, dict):
                if "subscription" in settings:
                    user_info["subscription"] = settings["subscription"]
                if "messagePointInfo" in settings:
                    user_info["message_points"] = settings["messagePointInfo"]
            
            logger.info("User information fetched successfully")
            return user_info
            
        except Exception as e:
            logger.error(f"Failed to fetch user info: {e}")
            return {}
    
    @rate_limited(max_calls=5, time_window=60, retry_attempts=3)
    def get_bots(self) -> Dict[str, Any]:
        """Get available bots from Poe.
        
        Returns:
            Dictionary of bot information
        """
        logger.info("Fetching available bots")
        
        if not self.client:
            logger.error("PoeApi client not initialized")
            return self._get_mock_bots()
        
        try:
            # Try to get bots with a simple timeout approach
            bots = self.client.get_available_bots()
            
            if not bots:
                logger.warning("No bots returned from API, using mock data")
                return self._get_mock_bots()
            
            logger.info(f"Fetched {len(bots)} bots")
            
            # Convert to expected format
            bot_dict = {}
            for bot in bots:
                bot_id = bot.get("id", "")
                bot_dict[bot_id] = {
                    "displayName": bot.get("displayName", ""),
                    "id": bot_id
                }
            
            return bot_dict
            
        except Exception as e:
            logger.error(f"Failed to fetch bots: {e}")
            # Return a mock response for testing
            return self._get_mock_bots()
    
    def _get_mock_bots(self) -> Dict[str, Any]:
        """Get mock bot data for testing."""
        return {
            "claude-3-5-sonnet": {
                "displayName": "Claude 3.5 Sonnet", 
                "id": "claude-3-5-sonnet"
            },
            "gpt4": {
                "displayName": "GPT-4", 
                "id": "gpt4"
            },
            "gemini": {
                "displayName": "Gemini", 
                "id": "gemini"
            }
        }
    
    @rate_limited(max_calls=8, time_window=60, retry_attempts=3)
    def get_recent_conversations(self, days: int = 7) -> List[Dict[str, Any]]:
        """Get recent conversations from Poe.
        
        Args:
            days: Number of days to look back
            
        Returns:
            List of conversation data
        """
        logger.info(f"Fetching conversations from last {days} days")
        
        if not self.client:
            logger.error("PoeApi client not initialized")
            return self._get_mock_conversations(days)
        
        try:
            all_conversations = []
            bot_ids = []
            for bot_id in bot_ids:
                try:
                    if bot_id != bot_ids[0]:
                        time.sleep(random.uniform(1, 3))
                    response = self.client.get_chat_history(bot_id, count=20)
                    conversations = []
                    if (
                        isinstance(response, dict)
                        and 'data' in response
                        and isinstance(response['data'], dict)
                        and bot_id in response['data']
                        and isinstance(response['data'][bot_id], list)
                    ):
                        conversations = response['data'][bot_id]
                    else:
                        logger.warning(f"No conversations found for bot {bot_id} in response: {response}")
                        continue
                    for conv in conversations:
                        if not isinstance(conv, dict):
                            logger.warning(f"Conversation is not a dict: {type(conv)} - {conv}")
                            continue
                        conversation = {
                            "id": str(conv.get("chatId", "")),
                            "title": conv.get("title", f"Conversation with {bot_id}"),
                            "createdAt": conv.get("createdAt", datetime.now().isoformat()),
                            "updatedAt": conv.get("updatedAt", datetime.now().isoformat()),
                            "messageCount": conv.get("messageCount", 0),
                            "bot": {
                                "id": bot_id,
                                "displayName": self._get_bot_name(bot_id)
                            }
                        }
                        all_conversations.append(conversation)
                except Exception as e:
                    logger.warning(f"Failed to get conversations for bot {bot_id}: {e}")
                    time.sleep(random.uniform(2, 5))
                    continue
            logger.info(f"Fetched {len(all_conversations)} conversations")
            return all_conversations
        except Exception as e:
            logger.error(f"Failed to fetch conversations: {e}")
            logger.info("Falling back to mock data for testing")
            return self._get_mock_conversations(days)
    
    def get_conversation_ids(self, days: int = 7) -> List[str]:
        """Get list of conversation IDs from Poe.
        
        Args:
            days: Number of days to look back
            
        Returns:
            List of conversation IDs
        """
        logger.info(f"Fetching conversation IDs from last {days} days")
        
        try:
            conversations = self.get_recent_conversations(days)
            conv_ids = [conv["id"] for conv in conversations if conv.get("id")]
            logger.info(f"Found {len(conv_ids)} conversation IDs")
            return conv_ids
        except Exception as e:
            logger.error(f"Failed to get conversation IDs: {e}")
            # Return some mock IDs for testing
            return ["mock_conv_1", "mock_conv_2", "mock_conv_3"]
    
    def get_recent_conversation_ids(self, days: int = 7) -> List[str]:
        """Get recent conversation IDs (alias for get_conversation_ids).
        
        Args:
            days: Number of days to look back
            
        Returns:
            List of conversation IDs
        """
        return self.get_conversation_ids(days)
    
    @rate_limited(max_calls=10, time_window=60, retry_attempts=3)
    def get_conversation(self, conversation_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific conversation with its messages.
        
        Args:
            conversation_id: Conversation ID
            
        Returns:
            Conversation data with messages, or None if not found
        """
        logger.info(f"Fetching conversation: {conversation_id}")
        
        if not self.client:
            logger.error("PoeApi client not initialized")
            return self._get_mock_conversation(conversation_id)
        
        try:
            bot_ids = []
            for bot_id in bot_ids:
                try:
                    response = self.client.get_chat_history(bot_id, count=50)
                    conversations = []
                    if (
                        isinstance(response, dict)
                        and 'data' in response
                        and isinstance(response['data'], dict)
                        and bot_id in response['data']
                        and isinstance(response['data'][bot_id], list)
                    ):
                        conversations = response['data'][bot_id]
                    else:
                        continue
                    for conv in conversations:
                        if not isinstance(conv, dict):
                            logger.warning(f"Conversation is not a dict: {type(conv)} - {conv}")
                            continue
                        if str(conv.get("chatId", "")) == conversation_id:
                            try:
                                messages = self.client.get_message_history(bot_id, conversation_id, count=100)
                                formatted_messages = []
                                if hasattr(messages, '__iter__') and not isinstance(messages, (str, bytes)):
                                    messages = list(messages)
                                    for msg in messages:
                                        if not isinstance(msg, dict):
                                            logger.warning(f"Message is not a dict: {type(msg)} - {msg}")
                                            continue
                                        formatted_message = {
                                            "id": str(msg.get("id", "")),
                                            "text": msg.get("text", ""),
                                            "role": msg.get("role", "unknown"),
                                            "timestamp": msg.get("timestamp", datetime.now().isoformat()),
                                            "author": msg.get("author", "unknown")
                                        }
                                        formatted_messages.append(formatted_message)
                                return {
                                    "id": conversation_id,
                                    "title": conv.get("title", f"Conversation with {bot_id}"),
                                    "createdAt": conv.get("createdAt", datetime.now().isoformat()),
                                    "updatedAt": conv.get("updatedAt", datetime.now().isoformat()),
                                    "messageCount": len(formatted_messages),
                                    "bot": {
                                        "id": bot_id,
                                        "displayName": self._get_bot_name(bot_id)
                                    },
                                    "messages": formatted_messages
                                }
                            except Exception as e:
                                logger.warning(f"Failed to get messages for conversation {conversation_id}: {e}")
                                return {
                                    "id": conversation_id,
                                    "title": conv.get("title", f"Conversation with {bot_id}"),
                                    "createdAt": conv.get("createdAt", datetime.now().isoformat()),
                                    "updatedAt": conv.get("updatedAt", datetime.now().isoformat()),
                                    "messageCount": conv.get("messageCount", 0),
                                    "bot": {
                                        "id": bot_id,
                                        "displayName": self._get_bot_name(bot_id)
                                    },
                                    "messages": []
                                }
                except Exception as e:
                    logger.warning(f"Failed to search conversations for bot {bot_id}: {e}")
                    continue
            logger.warning(f"Conversation {conversation_id} not found in any bot's history")
            return self._get_mock_conversation(conversation_id)
        except Exception as e:
            logger.error(f"Failed to fetch conversation {conversation_id}: {e}")
            return self._get_mock_conversation(conversation_id)
    
    def _get_bot_name(self, bot_id: str) -> str:
        """Get bot display name by ID.
        
        Args:
            bot_id: Bot ID
            
        Returns:
            Bot display name
        """
        # Known bot mappings
        bot_names = {}
        
        return bot_names.get(bot_id, bot_id)
    
    def _get_mock_conversations(self, days: int = 7) -> List[Dict[str, Any]]:
        """Get mock conversation data for testing (only enabled in test/dev mode)."""
        import os
        if not os.getenv('POE_DEV_MODE', '').lower() in ('1', 'true', 'yes'):
            logger.warning("Mock data is disabled in production mode.")
            return []
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
        
        mock_bots = []
        bot_names = []
        
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
    
    def _get_mock_conversation(self, conversation_id: str) -> Optional[Dict[str, Any]]:
        """Get mock conversation data for testing.
        
        Args:
            conversation_id: Conversation ID
            
        Returns:
            Mock conversation data or None if not found
        """
        # Try to find in existing mock conversations
        mock_conversations = self._get_mock_conversations(7)
        for conv in mock_conversations:
            if conv["id"] == conversation_id:
                return conv
        
        # If not found, create a new mock conversation
        logger.info(f"Creating mock conversation for {conversation_id}")
        
        mock_titles = [
            "Python programming help",
            "Machine learning discussion", 
            "Web development questions",
            "Data analysis project",
            "Code review assistance"
        ]
        
        mock_bots = []
        bot_names = []
        
        # Extract index from conversation ID
        try:
            index = int(conversation_id.replace("conv_", ""))
        except ValueError:
            index = 0
        
        bot_id = mock_bots[index % len(mock_bots)]
        bot_name = bot_names[index % len(bot_names)]
        
        return {
            "id": conversation_id,
            "title": mock_titles[index % len(mock_titles)],
            "createdAt": datetime.now().isoformat(),
            "updatedAt": datetime.now().isoformat(),
            "messageCount": 10 + index * 2,
            "bot": {
                "id": bot_id,
                "displayName": bot_name
            },
            "messages": [
                {
                    "id": f"msg_{conversation_id}_{i:03d}",
                    "role": "user" if i % 2 == 0 else "bot",
                    "content": f"This is message {i+1} in conversation {conversation_id}. It contains sample content for testing.",
                    "createdAt": (datetime.now() - timedelta(minutes=i*5)).isoformat(),
                }
                for i in range(6)  # 6 messages per conversation
            ],
        }

    def get_all_real_conversations(self, first: int = 50) -> list:
        """Fetch all real Poe.com conversations using the ChatListPaginationQuery GraphQL endpoint."""
        logger.info("Fetching all real conversations from Poe.com API (ChatListPaginationQuery)")
        tokens = self.token if isinstance(self.token, dict) else {"p-b": self.token}
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
            "Cookie": f"p-b={tokens.get('p-b','')}; p-lat={tokens.get('p-lat','')}; formkey={tokens.get('formkey','')}"
        }
        url = "https://poe.com/api/gql_POST"
        query = {
            "operationName": "ChatListPaginationQuery",
            "variables": {"first": first},
            "query": "query ChatListPaginationQuery($first: Int) { chatList(first: $first) { edges { node { chatId title lastMessage { text } bot { id displayName } createdAt updatedAt } } } }"
        }
        try:
            response = requests.post(url, headers=headers, json=query)
            response.raise_for_status()
            data = response.json()
            chats = data.get('data', {}).get('chatList', {}).get('edges', [])
            conversations = []
            for edge in chats:
                node = edge.get('node', {})
                conversations.append({
                    "id": str(node.get('chatId', '')),
                    "title": node.get('title', 'Untitled'),
                    "bot": node.get('bot', {}).get('displayName', 'Unknown'),
                    "bot_id": node.get('bot', {}).get('id', ''),
                    "last_message": node.get('lastMessage', {}).get('text', ''),
                    "createdAt": node.get('createdAt', ''),
                    "updatedAt": node.get('updatedAt', ''),
                })
            logger.info(f"Fetched {len(conversations)} real conversations from Poe.com API")
            return conversations
        except Exception as e:
            logger.error(f"Failed to fetch real conversations: {e}")
            return []

    def _get_fresh_tokens(self):
        # Use secrets.json cookies if available
        tokens = load_poe_tokens_from_file()
        if tokens.get('p-b') and tokens.get('p-lat') and tokens.get('formkey'):
            return tokens
        # Otherwise, run browser automation
        from poe_search.utils.browser_tokens import get_browser_tokens
        return get_browser_tokens(headless=True)

    def get_true_chat_history(self, count: int = 20, cursor: str = None) -> list:
        """Fetch real Poe.com chat history using the exact browser GraphQL request (ChatHistoryListPaginationQuery), always with fresh tokens."""
        logger.info("Fetching true chat history from Poe.com API (ChatHistoryListPaginationQuery) with fresh tokens")
        tokens = self._get_fresh_tokens()
        # Compose headers as seen in browser
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:140.0) Gecko/20100101 Firefox/140.0",
            "Accept": "*/*",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Referer": "https://poe.com/chats",
            "poegraphql": "1",
            "poe-queryname": "ChatHistoryListPaginationQuery",
            "poe-formkey": tokens.get('formkey', ''),
            # TODO: Optionally extract poe-tchannel and poe-tag-id from browser if needed
            "Origin": "https://poe.com",
            "Cookie": f"p-b={tokens.get('p-b','')}; p-lat={tokens.get('p-lat','')}; formkey={tokens.get('formkey','')}; cf_clearance={tokens.get('cf_clearance','')}"
        }
        url = "https://poe.com/api/gql_POST"
        payload = {
            "queryName": "ChatHistoryListPaginationQuery",
            "variables": {"count": count},
            "extensions": {"hash": "99961eff898a3aaa4be55b026af876ffd60d8447c08e22ec9f0d29000073198f"}
        }
        if cursor is not None:
            payload["variables"]["cursor"] = str(cursor)
        try:
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()
            chats = data.get('data', {}).get('chatHistoryList', {}).get('edges', [])
            conversations = []
            for edge in chats:
                node = edge.get('node', {})
                conversations.append({
                    "id": str(node.get('chatId', '')),
                    "title": node.get('title', 'Untitled'),
                    "bot": node.get('bot', {}).get('displayName', 'Unknown'),
                    "bot_id": node.get('bot', {}).get('id', ''),
                    "last_message": node.get('lastMessage', {}).get('text', ''),
                    "createdAt": node.get('createdAt', ''),
                    "updatedAt": node.get('updatedAt', ''),
                })
            logger.info(f"Fetched {len(conversations)} true conversations from Poe.com API")
            return conversations
        except Exception as e:
            logger.error(f"Failed to fetch true chat history: {e}")
            return []
