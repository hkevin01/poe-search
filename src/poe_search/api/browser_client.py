#!/usr/bin/env python3
"""
Poe Browser Client - Selenium-based Poe.com API Client

This module provides a browser automation client for interacting with Poe.com
using Selenium WebDriver. It handles authentication via cookies and extracts
conversations and messages from the Poe.com web interface.

Author: Kevin Hildebrand
Created: 2025-01-25
License: MIT
Version: 1.0.0

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
        Extract conversation list from Poe.com using multiple detection methods.
        
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
                - preview (str): Message preview if available
                - extracted_at (str): Timestamp of extraction
        
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
                progress_callback("Loading conversations page...", 10)
            
            logger.info(f"🔍 Fetching conversation list (limit: {limit})")
            
            # Ensure we're on the chats page
            self.driver.get("https://poe.com/chats")
            time.sleep(3)
            
            conversations = []
            
            # Method 1: Standard chat list items (Poe's expected structure)
            if progress_callback:
                progress_callback("Scanning for chat list items...", 30)
            
            try:
                # Wait for conversation list to load
                WebDriverWait(self.driver, 15).until(
                    EC.any_of(
                        EC.presence_of_element_located((By.CSS_SELECTOR, '[data-testid="chat-list-item"]')),
                        EC.presence_of_element_located((By.CSS_SELECTOR, '[data-testid*="chat"]')),
                        EC.presence_of_element_located((By.CSS_SELECTOR, 'a[href*="/chat/"]'))
                    )
                )
                
                # Try official chat list items first
                chat_items = self.driver.find_elements(By.CSS_SELECTOR, '[data-testid="chat-list-item"]')
                logger.info(f"Found {len(chat_items)} official chat list items")
                
                for item in chat_items[:limit]:
                    try:
                        # Extract conversation data from structured elements
                        title_elem = item.find_element(By.CSS_SELECTOR, '[data-testid="chat-title"]') if \
                                   item.find_elements(By.CSS_SELECTOR, '[data-testid="chat-title"]') else item
                        
                        title = title_elem.text.split('\n')[0] if title_elem.text else "Untitled"
                        
                        # Extract conversation ID from href
                        href = item.get_attribute('href')
                        if not href:
                            # Look for nested links
                            links = item.find_elements(By.TAG_NAME, 'a')
                            href = links[0].get_attribute('href') if links else None
                        
                        conv_id = self._extract_conversation_id(href) if href else None
                        
                        # Extract bot name
                        bot_text = item.text
                        bot = self._extract_bot_name(bot_text)
                        
                        if conv_id and title:
                            conversations.append({
                                'id': conv_id,
                                'title': title,
                                'bot': bot,
                                'url': href,
                                'preview': bot_text,
                                'method': 'official_chat_list',
                                'extracted_at': datetime.now().isoformat()
                            })
                            
                    except Exception as e:
                        logger.debug(f"Error processing chat list item: {e}")
                        continue
                        
            except TimeoutException:
                logger.warning("Official chat list items not found, trying alternative methods")
            
            # Method 2: Direct link detection (fallback)
            if len(conversations) < limit:
                if progress_callback:
                    progress_callback("Scanning for chat links...", 50)
                
                link_selectors = [
                    "a[href*='/chat/']",
                    "a[href*='/conversation/']",
                    "[data-testid*='chat'] a",
                    "[data-testid*='conversation'] a"
                ]
                
                for selector in link_selectors:
                    try:
                        elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                        logger.info(f"Selector '{selector}': found {len(elements)} elements")
                        
                        for elem in elements:
                            if len(conversations) >= limit:
                                break
                                
                            try:
                                href = elem.get_attribute('href')
                                if not href or not ('/chat/' in href or '/conversation/' in href):
                                    continue
                                
                                conv_id = self._extract_conversation_id(href)
                                
                                # Avoid duplicates
                                if any(conv['id'] == conv_id for conv in conversations):
                                    continue
                                
                                title = (elem.text.strip() or 
                                       elem.get_attribute('title') or 
                                       elem.get_attribute('aria-label') or 
                                       'Untitled Conversation')[:100]
                                
                                # Try to find bot name from parent elements
                                parent = elem.find_element(By.XPATH, '..')
                                bot = self._extract_bot_name(parent.text if parent else elem.text)
                                
                                conversations.append({
                                    'id': conv_id,
                                    'title': title,
                                    'bot': bot,
                                    'url': href,
                                    'preview': title,
                                    'method': f'direct_link-{selector}',
                                    'extracted_at': datetime.now().isoformat()
                                })
                                
                            except Exception as e:
                                logger.debug(f"Error processing link element: {e}")
                                continue
                                
                    except Exception as e:
                        logger.debug(f"Selector {selector} failed: {e}")
                        continue
            
            # Method 3: Scroll loading for more conversations
            if len(conversations) < limit:
                if progress_callback:
                    progress_callback("Loading more conversations...", 70)
                
                try:
                    initial_count = len(conversations)
                    
                    # Scroll to load more
                    for scroll_attempt in range(3):
                        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                        time.sleep(2)
                        
                        # Look for newly loaded links
                        new_links = self.driver.find_elements(By.CSS_SELECTOR, "a[href*='/chat/']")
                        
                        for link in new_links:
                            if len(conversations) >= limit:
                                break
                                
                            try:
                                href = link.get_attribute('href')
                                conv_id = self._extract_conversation_id(href)
                                
                                # Check for duplicates
                                if any(conv['id'] == conv_id for conv in conversations):
                                    continue
                                
                                title = link.text.strip() or 'Scrolled Conversation'
                                bot = self._extract_bot_name(link.text)
                                
                                conversations.append({
                                    'id': conv_id,
                                    'title': title[:100],
                                    'bot': bot,
                                    'url': href,
                                    'preview': title,
                                    'method': 'scroll_discovery',
                                    'extracted_at': datetime.now().isoformat()
                                })
                                
                            except Exception as e:
                                logger.debug(f"Error processing scrolled link: {e}")
                                continue
                    
                    new_count = len(conversations) - initial_count
                    if new_count > 0:
                        logger.info(f"Found {new_count} additional conversations via scrolling")
                        
                except Exception as e:
                    logger.warning(f"Scroll loading failed: {e}")
            
            if progress_callback:
                progress_callback("Processing complete!", 100)
            
            # Remove duplicates and limit results
            seen_ids = set()
            unique_conversations = []
            
            for conv in conversations:
                if conv['id'] not in seen_ids:
                    seen_ids.add(conv['id'])
                    unique_conversations.append(conv)
                    
                    if len(unique_conversations) >= limit:
                        break
            
            logger.info(f"✅ Successfully extracted {len(unique_conversations)} conversations")
            return unique_conversations
            
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
        Extract conversation ID from Poe.com URL.
        
        Args:
            url (str): Full URL or path containing conversation ID
            
        Returns:
            str: Extracted conversation ID
        """
        if not url:
            return ""
        
        # Extract from URLs like /chat/abc123 or https://poe.com/chat/xyz789
        match = re.search(r'/(?:chat|conversation)/([a-zA-Z0-9_-]+)', url)
        return match.group(1) if match else url.split('/')[-1]

    def _extract_bot_name(self, text: str) -> str:
        """
        Extract bot name from conversation text using pattern matching.
        
        Args:
            text (str): Text content to analyze
            
        Returns:
            str: Detected bot name or 'Assistant' as fallback
        """
        if not text:
            return "Assistant"
        
        # Common bot name patterns
        bot_patterns = [
            r'\b(Claude[^:\n]*)',
            r'\b(GPT[^:\n]*)',
            r'\b(Gemini[^:\n]*)',
            r'\b(Assistant[^:\n]*)',
            r'\b(ChatGPT[^:\n]*)',
            r'\b([A-Z][a-z]+-\d+[^:\n]*)'  # Pattern like Claude-3, GPT-4
        ]
        
        for pattern in bot_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                bot_name = match.group(1).strip()
                if 5 <= len(bot_name) <= 50:  # Reasonable length
                    return bot_name
        
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
            # Get conversations
            print("Fetching conversations...")
            conversations = client.get_conversations(limit=5)
            
            print(f"Found {len(conversations)} conversations:")
            for conv in conversations:
                print(f"- {conv['title']} ({conv['bot']})")
            
            # Get messages from first conversation
            if conversations:
                conv_id = conversations[0]['id']
                print(f"\nFetching messages from: {conversations[0]['title']}")
                
                messages = client.get_conversation_messages(conv_id)
                print(f"Found {len(messages)} messages:")
                
                for msg in messages[:3]:  # Show first 3 messages
                    print(f"{msg['role']}: {msg['content'][:100]}...")
            
        except Exception as e:
            print(f"❌ Error: {e}")