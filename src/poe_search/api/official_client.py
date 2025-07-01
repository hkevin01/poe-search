"""Official Poe API client using fastapi_poe library."""

import logging
import time
from datetime import datetime, timedelta
from functools import wraps
from typing import Any, Dict, List, Optional

import fastapi_poe as fp
from fastapi_poe import ProtocolMessage

from poe_search.utils.config import RateLimitSettings

logger = logging.getLogger(__name__)


def rate_limited(max_calls: int = 10, time_window: int = 60,
                retry_attempts: int = 3, base_delay: int = 5,
                max_delay: int = 60, jitter_range: float = 0.5,
                show_warnings: bool = True):
    """Decorator to implement rate limiting and retry logic for official API.
    
    Args:
        max_calls: Maximum number of calls allowed in time window
        time_window: Time window in seconds
        retry_attempts: Number of retry attempts for failed calls
        base_delay: Base delay for exponential backoff
        max_delay: Maximum delay cap
        jitter_range: Jitter range for delays
        show_warnings: Whether to show rate limit warnings
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
            import random
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


class OfficialPoeAPIClient:
    """Official Poe API client using fastapi_poe library."""
    
    def __init__(self, api_key: str, config: Optional[Any] = None):
        """Initialize the official Poe API client.
        
        Args:
            api_key: Poe API key from poe.com/api_key
            config: Configuration object for rate limiting settings
        """
        self.api_key = api_key
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
                'enabled': config.rate_limit.enable_rate_limiting,
            }
        else:
            # Default rate limiting configuration (more conservative for official API)
            self.rate_limit_config = {
                'max_calls': 8,  # Conservative limit (official API allows 500/min)
                'time_window': 60,  # 1 minute window
                'retry_attempts': 3,
                'base_delay': 5,
                'max_delay': 60,
                'jitter_range': 0.5,
                'show_warnings': True,
                'enabled': True,
            }
        
        # Validate API key
        if not api_key or len(api_key.strip()) == 0:
            raise ValueError("API key is required for official Poe API")
        
        logger.info("Official Poe API client initialized")
    
    @rate_limited(max_calls=5, time_window=60, retry_attempts=3)
    def get_bot_response(self, message: str, bot_name: str = "GPT-3.5-Turbo") -> str:
        """Get a response from a Poe bot using the official API.
        
        Args:
            message: User message to send
            bot_name: Name of the bot to query
            
        Returns:
            Bot response as string
        """
        logger.info(f"Getting response from {bot_name}")
        
        try:
            message_obj = ProtocolMessage(role="user", content=message)
            response_parts = []
            
            for partial in fp.get_bot_response_sync(
                messages=[message_obj], 
                bot_name=bot_name, 
                api_key=self.api_key
            ):
                # The PartialResponse has a 'text' attribute, not 'content'
                if hasattr(partial, 'text') and partial.text:
                    response_parts.append(partial.text)
            
            response = ''.join(response_parts)
            logger.info(f"Received response from {bot_name} ({len(response)} chars)")
            return response
            
        except Exception as e:
            logger.error(f"Failed to get response from {bot_name}: {e}")
            raise
    
    @rate_limited(max_calls=3, time_window=60, retry_attempts=2)
    def get_available_bots(self) -> List[Dict[str, Any]]:
        """Get list of available bots (limited functionality with official API).
        
        Returns:
            List of available bots
        """
        logger.info("Getting available bots")
        
        # Note: Official API doesn't provide direct bot listing
        # Return common bot names that users can try
        common_bots = [
            {"id": "gpt-3.5-turbo", "displayName": "GPT-3.5-Turbo"},
            {"id": "gpt-4", "displayName": "GPT-4"},
            {"id": "claude-3-opus", "displayName": "Claude 3 Opus"},
            {"id": "claude-3-sonnet", "displayName": "Claude 3 Sonnet"},
            {"id": "claude-3-haiku", "displayName": "Claude 3 Haiku"},
            {"id": "gemini-pro", "displayName": "Gemini Pro"},
            {"id": "llama-2-70b", "displayName": "Llama 2 70B"},
            {"id": "mixtral-8x7b", "displayName": "Mixtral 8x7B"},
        ]
        
        logger.info(f"Returning {len(common_bots)} common bot names")
        return common_bots
    
    def test_connection(self) -> Dict[str, Any]:
        """Test the API connection and key validity.
        
        Returns:
            Dictionary with test results
        """
        logger.info("Testing official API connection")
        
        try:
            # Try a simple query to test the connection
            test_message = "Hello, this is a test message."
            response = self.get_bot_response(test_message, "GPT-3.5-Turbo")
            
            return {
                "success": True,
                "api_key_valid": True,
                "response_length": len(response),
                "test_message": test_message,
                "response_preview": response[:100] + "..." if len(response) > 100 else response
            }
            
        except Exception as e:
            logger.error(f"API connection test failed: {e}")
            return {
                "success": False,
                "api_key_valid": False,
                "error": str(e)
            }
    
    def get_user_info(self) -> Dict[str, Any]:
        """Get user information (limited with official API).
        
        Returns:
            Dictionary of user information
        """
        logger.info("Getting user information from official API")
        
        # Note: Official API doesn't provide user info directly
        # Return basic info that we can infer
        return {
            "api_type": "official",
            "rate_limit": "500 requests per minute",
            "point_system": "Uses account points",
            "available_features": ["bot responses", "file uploads"],
            "limitations": ["No conversation history", "No user settings"]
        }
    
    def upload_file(self, file_path: str) -> Optional[str]:
        """Upload a file using the official API.
        
        Args:
            file_path: Path to the file to upload
            
        Returns:
            File attachment object or None if failed
        """
        logger.info(f"Uploading file: {file_path}")
        
        try:
            with open(file_path, 'rb') as f:
                attachment = fp.upload_file_sync(f, api_key=self.api_key)
                logger.info(f"File uploaded successfully: {file_path}")
                return attachment
                
        except Exception as e:
            logger.error(f"Failed to upload file {file_path}: {e}")
            return None
    
    def get_bot_response_with_file(self, message: str, file_path: str, 
                                 bot_name: str = "GPT-3.5-Turbo") -> str:
        """Get a bot response with a file attachment.
        
        Args:
            message: User message
            file_path: Path to file to attach
            bot_name: Name of the bot to query
            
        Returns:
            Bot response as string
        """
        logger.info(f"Getting response from {bot_name} with file attachment")
        
        try:
            # Upload the file first
            attachment = self.upload_file(file_path)
            if not attachment:
                raise ValueError(f"Failed to upload file: {file_path}")
            
            # Create message with attachment
            message_obj = ProtocolMessage(
                role="user", 
                content=message, 
                attachments=[attachment]
            )
            
            response_parts = []
            for partial in fp.get_bot_response_sync(
                messages=[message_obj], 
                bot_name=bot_name, 
                api_key=self.api_key
            ):
                # The PartialResponse has a 'text' attribute, not 'content'
                if hasattr(partial, 'text') and partial.text:
                    response_parts.append(partial.text)
            
            response = ''.join(response_parts)
            logger.info(f"Received response with file from {bot_name}")
            return response
            
        except Exception as e:
            logger.error(f"Failed to get response with file from {bot_name}: {e}")
            raise 