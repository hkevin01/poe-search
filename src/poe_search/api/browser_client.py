#!/usr/bin/env python3
"""
Poe Browser Client - Selenium-based Poe.com API Client

This module provides a browser automation client for interacting with Poe.com
using Selenium WebDriver. It handles authentication via cookies and extracts
conversations and messages from the Poe.com web interface.

Author: Kevin Hildebrand
Created: 2025-01-25
License: MIT
Version: 1.1.0

Dependencies:
    - selenium
    - webdriver-manager
    - typing

Usage:
    from poe_search.api.browser_client import PoeApiClient
    
    # Initialize with authentication token
    client = PoeApiClient(token="your_p-b_token_here")
    
    # Get conversations
    conversations = client.get_conversations(limit=20)
    
    # Get messages from specific conversation
    messages = client.get_conversation_messages(conversation_id="abc123")
    
    # Clean up
    client.close()

Note:
    This client requires valid Poe.com authentication tokens (p-b cookie).
    Tokens can be obtained from browser dev tools when logged into Poe.com.
"""

import time
import logging
import re
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any, Callable
from pathlib import Path

# Selenium imports
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import (
    TimeoutException, 
    NoSuchElementException, 
    WebDriverException,
    ElementClickInterceptedException
)

# WebDriver manager for automatic driver downloads
try:
    from webdriver_manager.chrome import ChromeDriverManager
    WEBDRIVER_MANAGER_AVAILABLE = True
except ImportError:
    WEBDRIVER_MANAGER_AVAILABLE = False
    logging.warning("webdriver-manager not available. Please ensure chromedriver is in PATH.")

# Configure logging
logger = logging.getLogger(__name__)


class PoeApiClient:
    """
    Selenium-based client for interacting with Poe.com web interface.
    
    This client uses browser automation to extract conversations and messages
    from Poe.com, providing a programmatic interface to the web UI.
    
    Attributes:
        token (str): Primary authentication token (p-b cookie)
        lat_token (str, optional): Secondary authentication token (p-lat cookie)
        headless (bool): Whether to run browser in headless mode
        driver: Selenium WebDriver instance
        
    Example:
        >>> client = PoeApiClient(token="AG58MLIXFnbOh98QAv4YHA==")
        >>> conversations = client.get_conversations(limit=10)
        >>> for conv in conversations:
        ...     print(f"Title: {conv['title']}, Bot: {conv['bot']}")
    """
    
    def __init__(self, token: str = None, lat_token: str = None, headless: bool = True):
        """
        Initialize the Poe API client.
        
        Args:
            token (str, optional): Primary authentication token (p-b cookie).
                                 If None, manual login will be required.
            lat_token (str, optional): Secondary authentication token (p-lat cookie).
                                     Improves authentication reliability.
            headless (bool): Run browser in headless mode. Defaults to True.
                           Set to False for debugging or manual intervention.
        
        Raises:
            WebDriverException: If browser setup fails
            ImportError: If required dependencies are missing
        """
        self.token = token
        self.lat_token = lat_token
        self.headless = headless
        self.driver = None
        self.authenticated = False
        
        # Rate limiting
        self.last_request_time = 0
        self.min_request_interval = 1.5  # seconds between requests
        
        logger.info(f"Initializing PoeApiClient (headless={headless})")
        self._setup_browser()

    def _setup_browser(self) -> None:
        """
        Set up and configure the Chrome browser with optimal settings for Poe.com.
        
        Configures Chrome with stealth options to avoid detection and
        optimize performance for web scraping.
        
        Raises:
            WebDriverException: If browser initialization fails
        """
        try:
            chrome_options = Options()
            
            # Basic browser options
            if self.headless:
                chrome_options.add_argument('--headless')
            
            # Essential options for stability and stealth
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--window-size=1920,1080')
            
            # Anti-detection measures
            chrome_options.add_argument('--disable-blink-features=AutomationControlled')
            chrome_options.add_experimental_option('excludeSwitches', ['enable-automation'])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            
            # Realistic user agent
            chrome_options.add_argument(
                '--user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 '
                '(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            )
            
            # Performance optimizations
            prefs = {
                "profile.default_content_setting_values.notifications": 2,
                "profile.default_content_settings.popups": 0,
                "profile.managed_default_content_settings.images": 1
            }
            chrome_options.add_experimental_option("prefs", prefs)
            
            # Initialize driver
            if WEBDRIVER_MANAGER_AVAILABLE:
                service = webdriver.chrome.service.Service(ChromeDriverManager().install())
                self.driver = webdriver.Chrome(service=service, options=chrome_options)
            else:
                # Fallback to system chromedriver
                self.driver = webdriver.Chrome(options=chrome_options)
            
            # Remove automation indicators
            self.driver.execute_script(
                "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
            )
            
            # Set timeouts
            self.driver.implicitly_wait(10)
            self.driver.set_page_load_timeout(30)
            
            logger.info("✅ Browser setup completed successfully")
            
        except Exception as e:
            logger.error(f"❌ Failed to setup browser: {e}")
            raise WebDriverException(f"Browser setup failed: {e}")

    def _rate_limit(self) -> None:
        """
        Implement rate limiting to avoid overwhelming Poe.com servers.
        
        Ensures minimum time interval between requests to be respectful
        to the service and avoid potential blocking.
        """
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        
        if time_since_last < self.min_request_interval:
            sleep_time = self.min_request_interval - time_since_last
            logger.debug(f"Rate limiting: sleeping for {sleep_time:.2f} seconds")
            time.sleep(sleep_time)
        
        self.last_request_time = time.time()

    def authenticate(self, progress_callback: Optional[Callable[[str, int], None]] = None) -> bool:
        """
        Authenticate with Poe.com using provided tokens.
        
        Sets authentication cookies and verifies successful login by
        checking for authenticated user interface elements.
        
        Args:
            progress_callback: Optional callback function for progress updates.
                             Should accept (message: str, percentage: int).
        
        Returns:
            bool: True if authentication successful, False otherwise
            
        Example:
            >>> client = PoeApiClient(token="your_token")
            >>> if client.authenticate():
            ...     print("Successfully authenticated!")
            ... else:
            ...     print("Authentication failed")
        """
        if not self.driver:
            logger.error("Browser not initialized")
            return False
        
        try:
            if progress_callback:
                progress_callback("Connecting to Poe.com...", 10)
            
            logger.info("🌐 Navigating to Poe.com...")
            self.driver.get("https://poe.com")
            time.sleep(2)
            
            if self.token:
                if progress_callback:
                    progress_callback("Setting authentication cookies...", 30)
                
                logger.info("🔑 Setting authentication cookies...")
                
                # Set primary authentication cookie
                self.driver.add_cookie({
                    'name': 'p-b',
                    'value': self.token,
                    'domain': '.poe.com',
                    'path': '/',
                    'secure': True
                })
                
                # Set secondary cookie if available
                if self.lat_token:
                    self.driver.add_cookie({
                        'name': 'p-lat',
                        'value': self.lat_token,
                        'domain': '.poe.com',
                        'path': '/',
                        'secure': True
                    })
                    logger.info("✅ Set both p-b and p-lat cookies")
                else:
                    logger.info("✅ Set p-b cookie")
                
                # Refresh to apply authentication
                if progress_callback:
                    progress_callback("Verifying authentication...", 60)
                
                self.driver.refresh()
                time.sleep(3)
            
            else:
                # Manual login required
                if progress_callback:
                    progress_callback("Manual login required...", 50)
                
                logger.info("⚠️  No token provided - manual login required")
                time.sleep(5)  # Give user time to log in manually
            
            # Verify authentication
            if progress_callback:
                progress_callback("Checking authentication status...", 80)
            
            # Navigate to chats page to verify access
            self.driver.get("https://poe.com/chats")
            time.sleep(3)
            
            # Check for authentication indicators
            auth_indicators = [
                "main[role='main']",
                "[data-testid*='chat']",
                "a[href*='/chat/']",
                "nav",
                "[class*='App']"
            ]
            
            authenticated = False
            for indicator in auth_indicators:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, indicator)
                    if elements:
                        logger.info(f"✅ Found auth indicator: {indicator}")
                        authenticated = True
                        break
                except:
                    continue
            
            # Check for login failure indicators
            if not authenticated:
                failure_indicators = [
                    "form[action*='login']",
                    "input[type='email']",
                    "input[type='password']"
                ]
                
                for indicator in failure_indicators:
                    try:
                        elements = self.driver.find_elements(By.CSS_SELECTOR, indicator)
                        if elements:
                            logger.warning(f"❌ Found login form: {indicator}")
                            if progress_callback:
                                progress_callback("Authentication failed", 0)
                            return False
                    except:
                        continue
            
            if authenticated:
                self.authenticated = True
                logger.info("✅ Successfully authenticated with Poe.com")
                if progress_callback:
                    progress_callback("Authentication successful!", 100)
                return True
            else:
                logger.error("❌ Authentication verification failed")
                if progress_callback:
                    progress_callback("Authentication failed", 0)
                return False
                
        except Exception as e:
            logger.error(f"❌ Authentication failed: {e}")
            if progress_callback:
                progress_callback(f"Authentication error: {str(e)}", 0)
            return False

    def get_conversations(self, limit: int = 50, progress_callback: Optional[Callable[[str, int], None]] = None) -> List[Dict[str, Any]]:
        """
        Extract conversation list using the EXACT same method as the working standalone script.
        
        Uses proven strategies to find and extract conversation metadata
        including titles, bot names, and URLs.
        
        Args:
            limit (int): Maximum number of conversations to retrieve. Defaults to 50.
            progress_callback: Optional callback for progress updates.
        
        Returns:
            List[Dict[str, Any]]: List of conversation dictionaries containing:
                - id (str): Conversation ID
                - title (str): Conversation title
                - bot (str): Bot name used in conversation
                - url (str): Full URL to conversation
                - method (str): Extraction method used
                - extracted_at (str): Timestamp of extraction
                - messages (list): Empty list (populated separately if needed)
        
        Example:
            >>> conversations = client.get_conversations(limit=10)
            >>> for conv in conversations:
            ...     print(f"{conv['title']} - {conv['bot']}")
        
        Raises:
            RuntimeError: If not authenticated or browser not available
        """
        if not self.authenticated:
            if not self.authenticate(progress_callback):
                raise RuntimeError("Authentication required before fetching conversations")
        
        self._rate_limit()
        
        try:
            if progress_callback:
                progress_callback("Loading conversations page...", 20)
            
            logger.info(f"🔍 Fetching conversation list (limit: {limit})")
            
            # Navigate to chats page (EXACT same as working script)
            self.driver.get("https://poe.com/chats")
            time.sleep(5)  # Increased wait time like working script
            
            conversations = []
            
            # Method 1: Direct chat links (EXACT same as working script)
            if progress_callback:
                progress_callback("Extracting chat links...", 40)
            
            chat_links = self.driver.find_elements(By.CSS_SELECTOR, "a[href*='/chat/']")
            logger.info(f"Found {len(chat_links)} chat links")
            
            for i, link in enumerate(chat_links):
                if len(conversations) >= limit:
                    break
                    
                try:
                    href = link.get_attribute('href')
                    text = link.text.strip()
                    
                    if href and text:
                        conversations.append({
                            'id': self._extract_conversation_id(href),
                            'title': text[:100],
                            'url': href,
                            'bot': self._extract_bot_name(text),  # Try to extract from text
                            'method': 'direct_link',
                            'extracted_at': datetime.now().isoformat(),
                            'messages': []  # Empty for now, will be populated if needed
                        })
                        
                except Exception as e:
                    logger.debug(f"Error processing chat link {i}: {e}")
                    continue
            
            # Method 2: Chat containers (EXACT same as working script)
            if progress_callback:
                progress_callback("Extracting chat containers...", 60)
            
            chat_containers = self.driver.find_elements(By.CSS_SELECTOR, "[data-testid*='chat']")
            logger.info(f"Found {len(chat_containers)} chat containers")
            
            for container in chat_containers:
                if len(conversations) >= limit:
                    break
                    
                try:
                    text = container.text.strip()
                    
                    # Look for a link within this container
                    links = container.find_elements(By.TAG_NAME, 'a')
                    href = None
                    for link in links:
                        link_href = link.get_attribute('href')
                        if link_href and '/chat/' in link_href:
                            href = link_href
                            break
                    
                    if text and 5 < len(text) < 200:
                        # Check if we already have this conversation
                        conv_id = self._extract_conversation_id(href) if href else f"container_{len(conversations)}"
                        exists = any(conv['id'] == conv_id for conv in conversations)
                        
                        if not exists:
                            conversations.append({
                                'id': conv_id,
                                'title': text[:100],
                                'url': href or 'No direct URL',
                                'bot': self._extract_bot_name(text),
                                'method': 'container_text',
                                'extracted_at': datetime.now().isoformat(),
                                'messages': []
                            })
                            
                except Exception as e:
                    logger.debug(f"Error processing chat container: {e}")
                    continue
            
            if progress_callback:
                progress_callback("Removing duplicates...", 80)
            
            # Remove duplicates by URL (EXACT same as working script)
            seen_urls = set()
            unique_conversations = []
            
            for conv in conversations:
                if conv['url'] not in seen_urls:
                    seen_urls.add(conv['url'])
                    unique_conversations.append(conv)
            
            # Limit results
            final_conversations = unique_conversations[:limit]
            
            if progress_callback:
                progress_callback("Extraction complete!", 100)
            
            logger.info(f"✅ Successfully extracted {len(final_conversations)} conversations")
            return final_conversations
            
        except Exception as e:
            logger.error(f"❌ Failed to extract conversations: {e}")
            if progress_callback:
                progress_callback(f"Failed: {str(e)}", 0)
            return []

    def get_conversation_messages(self, conversation_id: str, progress_callback: Optional[Callable[[str, int], None]] = None) -> List[Dict[str, Any]]:
        """
        Extract all messages from a specific conversation.
        
        Navigates to the conversation URL and extracts all messages with
        role detection (user vs assistant) and content parsing.
        
        Args:
            conversation_id (str): The conversation ID to extract messages from
            progress_callback: Optional callback for progress updates
        
        Returns:
            List[Dict[str, Any]]: List of message dictionaries containing:
                - role (str): 'user' or 'assistant'
                - content (str): Message content
                - timestamp (str): Estimated timestamp
                - bot_name (str): Bot name for assistant messages
                - message_id (str): Unique message identifier
        
        Example:
            >>> messages = client.get_conversation_messages("abc123def")
            >>> for msg in messages:
            ...     print(f"{msg['role']}: {msg['content'][:50]}...")
        
        Raises:
            ValueError: If conversation_id is invalid
            RuntimeError: If not authenticated
        """
        if not conversation_id:
            raise ValueError("conversation_id cannot be empty")
        
        if not self.authenticated:
            if not self.authenticate():
                raise RuntimeError("Authentication required before fetching messages")
        
        self._rate_limit()
        
        try:
            if progress_callback:
                progress_callback("Loading conversation...", 10)
            
            url = f"https://poe.com/chat/{conversation_id}"
            logger.info(f"🔍 Extracting messages from: {url}")
            
            self.driver.get(url)
            time.sleep(3)
            
            if progress_callback:
                progress_callback("Waiting for messages to load...", 30)
            
            # Wait for conversation messages to load
            try:
                WebDriverWait(self.driver, 15).until(
                    EC.any_of(
                        EC.presence_of_element_located((By.CSS_SELECTOR, '[data-testid*="message"]')),
                        EC.presence_of_element_located((By.CSS_SELECTOR, '[class*="message"]')),
                        EC.presence_of_element_located((By.CSS_SELECTOR, '[class*="Message"]')),
                        EC.presence_of_element_located((By.CSS_SELECTOR, 'main'))
                    )
                )
            except TimeoutException:
                logger.warning("Messages didn't load within timeout, proceeding anyway")
            
            if progress_callback:
                progress_callback("Extracting messages...", 50)
            
            messages = []
            
            # Multiple strategies for message detection
            message_strategies = [
                # Strategy 1: Official message elements
                {
                    'selectors': [
                        '[data-testid*="message"]',
                        '[data-testid="message"]',
                        '[class*="Message_"]'
                    ],
                    'name': 'official_messages'
                },
                # Strategy 2: Generic message classes
                {
                    'selectors': [
                        '[class*="message"]',
                        '[class*="Message"]',
                        '.chat-message'
                    ],
                    'name': 'generic_messages'
                },
                # Strategy 3: Role-based detection
                {
                    'selectors': [
                        '[role="group"]',
                        '[role="article"]',
                        'article'
                    ],
                    'name': 'role_based'
                }
            ]
            
            message_elements = []
            successful_strategy = None
            
            for strategy in message_strategies:
                for selector in strategy['selectors']:
                    try:
                        elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                        # Filter for elements with substantial content
                        valid_elements = [
                            elem for elem in elements 
                            if elem.text and len(elem.text.strip()) > 5
                        ]
                        
                        if len(valid_elements) >= 1:
                            message_elements = valid_elements
                            successful_strategy = f"{strategy['name']}-{selector}"
                            logger.info(f"Found {len(message_elements)} messages using {successful_strategy}")
                            break
                    except Exception as e:
                        logger.debug(f"Strategy {selector} failed: {e}")
                        continue
                
                if message_elements:
                    break
            
            if not message_elements:
                logger.warning("No message elements found")
                return []
            
            if progress_callback:
                progress_callback("Processing messages...", 80)
            
            # Extract bot name for the conversation
            bot_name = self._extract_conversation_bot_name()
            
            # Process each message
            for i, elem in enumerate(message_elements):
                try:
                    content = elem.text.strip()
                    if not content or len(content) < 3:
                        continue
                    
                    # Determine message role using multiple heuristics
                    role = self._determine_message_role(elem, i, successful_strategy)
                    
                    # Create message object
                    message = {
                        'role': role,
                        'content': content,
                        'timestamp': (datetime.now() - timedelta(minutes=len(message_elements) - i)).isoformat(),
                        'bot_name': bot_name if role == 'assistant' else None,
                        'message_id': f"msg_{i}_{conversation_id}",
                        'extraction_method': successful_strategy
                    }
                    
                    messages.append(message)
                    
                except Exception as e:
                    logger.debug(f"Error processing message {i}: {e}")
                    continue
            
            if progress_callback:
                progress_callback("Messages extracted!", 100)
            
            logger.info(f"✅ Extracted {len(messages)} messages using {successful_strategy}")
            return messages
            
        except Exception as e:
            logger.error(f"❌ Failed to extract messages: {e}")
            if progress_callback:
                progress_callback(f"Failed: {str(e)}", 0)
            return []

    def _extract_conversation_id(self, url: str) -> str:
        """
        Extract conversation ID from Poe.com URL with better error handling.
        
        Args:
            url (str): Full URL or path containing conversation ID
            
        Returns:
            str: Extracted conversation ID
        """
        if not url:
            return f"unknown_{int(time.time())}"
        
        try:
            # Extract from URLs like /chat/abc123 or https://poe.com/chat/xyz789
            match = re.search(r'/(?:chat|conversation)/([a-zA-Z0-9_-]+)', url)
            if match:
                return match.group(1)
            
            # Fallback: use last part of URL
            parts = url.rstrip('/').split('/')
            if len(parts) >= 2:
                return parts[-1]
            
            # Final fallback: generate unique ID
            return f"extracted_{int(time.time() * 1000)}"
            
        except Exception as e:
            logger.debug(f"Error extracting conversation ID from {url}: {e}")
            return f"error_{int(time.time())}"

    def _extract_bot_name(self, text: str) -> str:
        """
        Extract bot name from conversation text with improved patterns.
        
        Args:
            text (str): Text content to analyze
            
        Returns:
            str: Detected bot name or 'Assistant' as fallback
        """
        if not text:
            return "Assistant"
        
        # Clean the text
        text = text.strip()
        
        # Known bot patterns (more comprehensive)
        bot_patterns = [
            r'\b(Claude[^:\n\r]*)',
            r'\b(GPT[^:\n\r]*)',
            r'\b(ChatGPT[^:\n\r]*)',
            r'\b(Gemini[^:\n\r]*)',
            r'\b(Assistant[^:\n\r]*)',
            r'\b(Anthropic[^:\n\r]*)',
            r'\b(OpenAI[^:\n\r]*)',
            r'\b([A-Z][a-z]+-\d+[^:\n\r]*)',  # Pattern like Claude-3, GPT-4
            r'\b([A-Z][a-zA-Z]*Bot[^:\n\r]*)',  # Pattern like ChatBot
        ]
        
        for pattern in bot_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                bot_name = match.group(1).strip()
                # Clean up the bot name
                bot_name = re.sub(r'[^\w\s-]', '', bot_name)  # Remove special chars
                if 3 <= len(bot_name) <= 30:  # Reasonable length
                    return bot_name
        
        # Try to extract from first few words if they look like a bot name
        words = text.split()[:3]  # First 3 words
        for word in words:
            if len(word) > 3 and word[0].isupper():
                # Check if it's a likely bot name
                if any(indicator in word.lower() for indicator in ['claude', 'gpt', 'gemini', 'assistant', 'ai']):
                    return word
        
        return "Assistant"

    def _extract_conversation_bot_name(self) -> str:
        """
        Extract bot name from current conversation page.
        
        Returns:
            str: Bot name or 'Assistant' as fallback
        """
        try:
            # Look for bot name indicators on the page
            bot_selectors = [
                '[data-testid*="bot"]',
                '[class*="bot"]',
                '[class*="Bot"]',
                '[class*="assistant"]',
                '[class*="model"]'
            ]
            
            for selector in bot_selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for elem in elements:
                        text = elem.text.strip()
                        if text and 3 <= len(text) <= 50:
                            return text
                except:
                    continue
            
            # Fallback: extract from page title
            title = self.driver.title
            bot_name = self._extract_bot_name(title)
            return bot_name if bot_name != "Assistant" else "Assistant"
            
        except Exception as e:
            logger.debug(f"Error extracting bot name: {e}")
            return "Assistant"

    def _determine_message_role(self, element, index: int, strategy: str) -> str:
        """
        Determine if a message is from user or assistant using multiple heuristics.
        
        Args:
            element: Selenium WebElement containing the message
            index (int): Position of message in conversation
            strategy (str): Detection strategy used to find messages
            
        Returns:
            str: 'user' or 'assistant'
        """
        try:
            # Method 1: Class-based detection
            elem_class = element.get_attribute('class') or ""
            elem_html = element.get_attribute('outerHTML') or ""
            
            user_indicators = ["user", "human", "you", "me", "question"]
            assistant_indicators = ["bot", "assistant", "ai", "response", "answer"]
            
            # Check for explicit role indicators
            for indicator in user_indicators:
                if indicator in elem_class.lower() or indicator in elem_html.lower():
                    return "user"
            
            for indicator in assistant_indicators:
                if indicator in elem_class.lower() or indicator in elem_html.lower():
                    return "assistant"
            
            # Method 2: Content analysis
            text = element.text.strip()
            
            # Short questions are likely from users
            if "?" in text and len(text) < 200:
                return "user"
            
            # Long responses are likely from assistants
            if len(text) > 300 and not text.startswith(("I ", "My ", "Can you")):
                return "assistant"
            
            # Method 3: Alternating pattern heuristic
            if "official" in strategy or "generic" in strategy:
                # For well-structured conversations, assume alternating pattern
                return "user" if index % 2 == 0 else "assistant"
            
            # Default fallback
            return "assistant"
            
        except Exception as e:
            logger.debug(f"Error determining message role: {e}")
            return "assistant"

    def debug_conversation_extraction(self):
        """Debug helper to check what elements are found."""
        self.driver.get("https://poe.com/chats")
        time.sleep(5)
        
        # Check what we can find
        chat_links = self.driver.find_elements(By.CSS_SELECTOR, "a[href*='/chat/']")
        print(f"🔗 Direct chat links: {len(chat_links)}")
        
        chat_containers = self.driver.find_elements(By.CSS_SELECTOR, "[data-testid*='chat']")
        print(f"📦 Chat containers: {len(chat_containers)}")
        
        # Print first few for inspection
        for i, link in enumerate(chat_links[:3]):
            href = link.get_attribute('href')
            text = link.text[:50].replace('\n', ' ')
            print(f"  Link {i+1}: href={href}, text='{text}'")
        
        for i, container in enumerate(chat_containers[:3]):
            text = container.text[:50].replace('\n', ' ')
            print(f"  Container {i+1}: text='{text}'")

    def close(self) -> None:
        """
        Clean up resources and close the browser driver.
        
        Should be called when done with the client to free up system resources.
        Can also be used in a context manager (with statement).
        """
        if self.driver:
            try:
                self.driver.quit()
                logger.info("✅ Browser driver closed successfully")
            except Exception as e:
                logger.warning(f"⚠️  Error closing driver: {e}")
            finally:
                self.driver = None
                self.authenticated = False

    def __enter__(self):
        """Context manager entry - enables 'with' statement usage."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - automatically closes browser."""
        self.close()

    def __del__(self):
        """Destructor - ensure browser is closed when object is garbage collected."""
        if hasattr(self, 'driver') and self.driver:
            self.close()


# Example usage and testing
if __name__ == "__main__":
    """
    Example usage of the PoeApiClient.
    
    This section demonstrates how to use the client for basic operations.
    """
    import os
    import json
    
    # Configure logging for example
    logging.basicConfig(level=logging.INFO)
    
    # Example: Load token from environment or config file
    token = os.getenv('POE_TOKEN')
    
    if not token:
        # Try loading from config file
        config_path = Path(__file__).parent.parent.parent.parent / "config" / "poe_tokens.json"
        if config_path.exists():
            with open(config_path) as f:
                config = json.load(f)
                token = config.get('p-b')
        else:
            print("❌ No token found. Set POE_TOKEN environment variable or create config file.")
            exit(1)
    
    # Use client with context manager for automatic cleanup
    with PoeApiClient(token=token, headless=False) as client:
        try:
            # Debug what we can extract
            print("🧪 Running debug extraction...")
            client.debug_conversation_extraction()
            
            # Get conversations
            print("\n📋 Fetching conversations...")
            conversations = client.get_conversations(limit=5)
            
            print(f"✅ Found {len(conversations)} conversations:")
            for i, conv in enumerate(conversations):
                print(f"  {i+1}. {conv['title']} ({conv['bot']}) - {conv['method']}")
            
            # Get messages from first conversation if available
            if conversations:
                conv_id = conversations[0]['id']
                print(f"\n💬 Fetching messages from: {conversations[0]['title']}")
                
                messages = client.get_conversation_messages(conv_id)
                print(f"✅ Found {len(messages)} messages:")
                
                for i, msg in enumerate(messages[:3]):  # Show first 3 messages
                    content_preview = msg['content'][:100].replace('\n', ' ')
                    print(f"  {i+1}. {msg['role']}: {content_preview}...")
            
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()