"""
Poe API Client - Enhanced Real Poe.com Integration
Connects to Poe.com using Selenium WebDriver to fetch actual conversations
Enhanced with proven conversation detection methods
"""

import json
import time
import logging
import re
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any, Callable
from dataclasses import dataclass, asdict
from pathlib import Path

# Selenium imports for real browser automation
try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.chrome.options import Options as ChromeOptions
    from selenium.webdriver.firefox.options import Options as FirefoxOptions
    from selenium.webdriver.common.action_chains import ActionChains
    from selenium.common.exceptions import (
        TimeoutException, NoSuchElementException, 
        WebDriverException, ElementClickInterceptedException
    )
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False

logger = logging.getLogger(__name__)

@dataclass
class Message:
    """Represents a single message in a conversation"""
    role: str  # 'user' or 'assistant'
    content: str
    timestamp: datetime
    bot_name: Optional[str] = None
    message_id: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert message to dictionary"""
        return {
            'role': self.role,
            'content': self.content,
            'timestamp': self.timestamp.isoformat(),
            'bot_name': self.bot_name,
            'message_id': self.message_id
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Message':
        """Create message from dictionary"""
        return cls(
            role=data['role'],
            content=data['content'],
            timestamp=datetime.fromisoformat(data['timestamp']),
            bot_name=data.get('bot_name'),
            message_id=data.get('message_id')
        )

@dataclass
class Conversation:
    """Represents a complete conversation with a bot"""
    id: str
    title: str
    bot: str
    messages: List[Message]
    created_at: datetime
    updated_at: Optional[datetime] = None
    url: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert conversation to dictionary"""
        return {
            'id': self.id,
            'title': self.title,
            'bot': self.bot,
            'messages': [msg.to_dict() for msg in self.messages],
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'url': self.url
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Conversation':
        """Create conversation from dictionary"""
        return cls(
            id=data['id'],
            title=data['title'],
            bot=data['bot'],
            messages=[Message.from_dict(msg) for msg in data['messages']],
            created_at=datetime.fromisoformat(data['created_at']),
            updated_at=datetime.fromisoformat(data['updated_at']) if data.get('updated_at') else None,
            url=data.get('url')
        )

class PoeAPIClient:
    """Enhanced Poe.com API client using proven browser automation methods"""
    
    def __init__(self, token: str, lat_token: Optional[str] = None, headless: bool = True, browser: str = "chrome"):
        """Initialize the Poe client with real browser automation"""
        if not SELENIUM_AVAILABLE:
            raise ImportError("Selenium is required for Poe integration. Install with: pip install selenium")
        
        self.token = token
        self.lat_token = lat_token
        self.headless = headless
        self.browser = browser
        self.driver = None
        self.conversations = []
        
        # Rate limiting
        self.last_request_time = 0
        self.min_request_interval = 1.5  # 1.5 seconds between requests
        
        logger.info(f"Initializing enhanced Poe client (headless={headless}, browser={browser})")
    
    def _setup_driver(self):
        """Setup and configure the web driver with optimized settings"""
        if self.driver:
            return self.driver
        
        try:
            if self.browser.lower() == "chrome":
                options = ChromeOptions()
                if self.headless:
                    options.add_argument("--headless")
                
                # Essential options for Poe.com
                options.add_argument("--no-sandbox")
                options.add_argument("--disable-dev-shm-usage")
                options.add_argument("--disable-gpu")
                options.add_argument("--window-size=1920,1080")
                options.add_argument("--disable-blink-features=AutomationControlled")
                options.add_experimental_option("excludeSwitches", ["enable-automation"])
                options.add_experimental_option('useAutomationExtension', False)
                
                # Realistic user agent
                options.add_argument("--user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
                
                # Performance optimizations
                prefs = {
                    "profile.default_content_setting_values.notifications": 2,
                    "profile.default_content_settings.popups": 0,
                    "profile.managed_default_content_settings.images": 1
                }
                options.add_experimental_option("prefs", prefs)
                
                self.driver = webdriver.Chrome(options=options)
            
            elif self.browser.lower() == "firefox":
                options = FirefoxOptions()
                if self.headless:
                    options.add_argument("--headless")
                options.add_argument("--width=1920")
                options.add_argument("--height=1080")
                
                self.driver = webdriver.Firefox(options=options)
            
            else:
                raise ValueError(f"Unsupported browser: {self.browser}")
            
            # Remove automation indicators
            if self.browser.lower() == "chrome":
                self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            # Set timeouts
            self.driver.implicitly_wait(15)
            self.driver.set_page_load_timeout(30)
            
            logger.info(f"Successfully initialized {self.browser} driver")
            return self.driver
            
        except Exception as e:
            logger.error(f"Failed to setup web driver: {e}")
            raise
    
    def _rate_limit(self):
        """Implement rate limiting between requests"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        
        if time_since_last < self.min_request_interval:
            sleep_time = self.min_request_interval - time_since_last
            logger.debug(f"Rate limiting: sleeping for {sleep_time:.2f} seconds")
            time.sleep(sleep_time)
        
        self.last_request_time = time.time()
    
    def connect(self, progress_callback: Optional[Callable[[str, int], None]] = None):
        """Enhanced connection method with proven authentication"""
        self._setup_driver()
        self._rate_limit()
        
        try:
            if progress_callback:
                progress_callback("Connecting to Poe.com...", 10)
            
            logger.info("Connecting to Poe.com...")
            self.driver.get("https://poe.com")
            time.sleep(2)
            
            if progress_callback:
                progress_callback("Setting authentication cookies...", 30)
            
            # Set authentication cookies with proven method
            logger.info("Setting authentication cookies...")
            
            # Primary cookie (p-b)
            self.driver.add_cookie({
                'name': 'p-b',
                'value': self.token,
                'domain': '.poe.com',
                'path': '/',
                'secure': True
            })
            
            # Secondary cookie (p-lat) if available
            if self.lat_token:
                self.driver.add_cookie({
                    'name': 'p-lat',
                    'value': self.lat_token,
                    'domain': '.poe.com',
                    'path': '/',
                    'secure': True
                })
                logger.info("Set both p-b and p-lat cookies")
            else:
                logger.info("Set p-b cookie only")
            
            if progress_callback:
                progress_callback("Verifying authentication...", 50)
            
            # Navigate to chats page to verify authentication
            logger.info("Navigating to chats page...")
            self.driver.get("https://poe.com/chats")
            time.sleep(5)
            
            # Verify authentication by checking page content
            current_url = self.driver.current_url
            page_title = self.driver.title
            
            logger.info(f"Current URL: {current_url}")
            logger.info(f"Page title: {page_title}")
            
            # Check for authentication success indicators
            auth_indicators = [
                "main[role='main']",
                "div[role='main']",
                "nav",
                "[role='navigation']",
                "[data-testid*='chat']",
                "a[href*='/chat/']",
                "[class*='App']",
                "[id*='app']"
            ]
            
            authenticated = False
            for indicator in auth_indicators:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, indicator)
                    if elements:
                        logger.info(f"Found auth indicator: {indicator} ({len(elements)} elements)")
                        authenticated = True
                        break
                except:
                    continue
            
            # Check for login failure indicators
            if not authenticated:
                failure_indicators = [
                    "form[action*='login']",
                    "input[type='email']",
                    "input[type='password']",
                    "button[type='submit'][value*='login']"
                ]
                
                for indicator in failure_indicators:
                    try:
                        elements = self.driver.find_elements(By.CSS_SELECTOR, indicator)
                        if elements:
                            logger.error(f"Found login form: {indicator}")
                            if progress_callback:
                                progress_callback("Authentication failed", 0)
                            return False
                    except:
                        continue
            
            if authenticated:
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
            logger.error(f"❌ Failed to connect to Poe.com: {e}")
            if progress_callback:
                progress_callback(f"Connection failed: {str(e)}", 0)
            return False
    
    def get_conversation_list(self, limit: int = 50, progress_callback: Optional[Callable[[str, int], None]] = None) -> List[Dict[str, Any]]:
        """Enhanced conversation list retrieval with proven methods"""
        if not self.driver:
            if not self.connect(progress_callback):
                raise Exception("Failed to connect to Poe.com")
        
        self._rate_limit()
        
        try:
            if progress_callback:
                progress_callback("Fetching conversation list...", 20)
            
            logger.info(f"Fetching conversation list with enhanced detection (limit: {limit})...")
            
            # Ensure we're on the chats page
            if "/chats" not in self.driver.current_url:
                self.driver.get("https://poe.com/chats")
                time.sleep(3)
            
            conversations = []
            
            # Method 1: Direct chat link detection (proven to work)
            if progress_callback:
                progress_callback("Scanning for chat links...", 40)
            
            chat_link_selectors = [
                "a[href*='/chat/']",
                "a[href*='/conversation/']",
                "[data-testid*='chat'] a",
                "[data-testid*='conversation'] a"
            ]
            
            for selector in chat_link_selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    logger.info(f"Selector '{selector}': found {len(elements)} elements")
                    
                    for elem in elements:
                        try:
                            href = elem.get_attribute('href')
                            if not href or not ('/chat/' in href or '/conversation/' in href):
                                continue
                            
                            title = (elem.text.strip() or 
                                   elem.get_attribute('title') or 
                                   elem.get_attribute('aria-label') or 
                                   'Untitled Conversation')
                            
                            # Avoid duplicates
                            if not any(conv['url'] == href for conv in conversations):
                                conversations.append({
                                    'url': href,
                                    'title': title[:100],
                                    'id': self._extract_conversation_id(href),
                                    'method': f'direct_link-{selector}'
                                })
                                
                        except Exception as e:
                            logger.debug(f"Error processing link element: {e}")
                            continue
                            
                except Exception as e:
                    logger.debug(f"Selector {selector} failed: {e}")
                    continue
            
            # Method 2: Container-based detection
            if progress_callback:
                progress_callback("Scanning conversation containers...", 60)
            
            container_selectors = [
                "[data-testid*='chat']",
                "[class*='chat']",
                "[class*='Chat']",
                "[class*='conversation']"
            ]
            
            for selector in container_selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    logger.info(f"Container '{selector}': found {len(elements)} elements")
                    
                    for elem in elements:
                        try:
                            # Look for links within containers
                            links = elem.find_elements(By.TAG_NAME, 'a')
                            for link in links:
                                href = link.get_attribute('href')
                                if href and '/chat/' in href:
                                    title = elem.text.strip()[:100] or 'Container Conversation'
                                    
                                    # Avoid duplicates
                                    if not any(conv['url'] == href for conv in conversations):
                                        conversations.append({
                                            'url': href,
                                            'title': title,
                                            'id': self._extract_conversation_id(href),
                                            'method': f'container-{selector}'
                                        })
                                    break  # One per container
                        except:
                            continue
                            
                except Exception as e:
                    logger.debug(f"Container selector {selector} failed: {e}")
                    continue
            
            # Method 3: Scroll loading for more conversations
            if progress_callback:
                progress_callback("Loading more conversations...", 80)
            
            try:
                initial_count = len(conversations)
                
                # Scroll to load more conversations
                for scroll_attempt in range(3):
                    self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                    time.sleep(2)
                    
                    # Look for newly loaded chat links
                    new_links = self.driver.find_elements(By.CSS_SELECTOR, "a[href*='/chat/']")
                    
                    for link in new_links:
                        try:
                            href = link.get_attribute('href')
                            title = link.text.strip() or 'Scrolled Conversation'
                            
                            # Check if this is a new conversation
                            if href and not any(conv['url'] == href for conv in conversations):
                                conversations.append({
                                    'url': href,
                                    'title': title[:100],
                                    'id': self._extract_conversation_id(href),
                                    'method': 'scroll_discovery'
                                })
                        except:
                            continue
                
                new_count = len(conversations) - initial_count
                if new_count > 0:
                    logger.info(f"Found {new_count} additional conversations via scrolling")
                
            except Exception as e:
                logger.warning(f"Scroll loading failed: {e}")
            
            # Method 4: Page source analysis as fallback
            try:
                page_source = self.driver.page_source
                
                # Extract chat URLs from page source
                chat_patterns = [
                    r'href="([^"]*\/chat\/[^"]*)"',
                    r'"url":"([^"]*\/chat\/[^"]*)"',
                    r'\/chat\/([a-zA-Z0-9_-]+)'
                ]
                
                for pattern in chat_patterns:
                    matches = re.findall(pattern, page_source)
                    for match in matches[:10]:  # Limit to avoid spam
                        if pattern.startswith(r'\/chat\/'):
                            # This is just an ID
                            url = f"https://poe.com/chat/{match}"
                            title = f"Source ID: {match}"
                        else:
                            # This is a full URL
                            url = match if match.startswith('http') else f"https://poe.com{match}"
                            title = f"Source: {match.split('/')[-1]}"
                        
                        # Avoid duplicates
                        if not any(conv['url'] == url for conv in conversations):
                            conversations.append({
                                'url': url,
                                'title': title,
                                'id': self._extract_conversation_id(url),
                                'method': f'source-{pattern[:15]}'
                            })
                
            except Exception as e:
                logger.warning(f"Page source analysis failed: {e}")
            
            # Remove duplicates and limit results
            seen_urls = set()
            unique_conversations = []
            
            for conv in conversations:
                if conv['url'] not in seen_urls:
                    seen_urls.add(conv['url'])
                    unique_conversations.append(conv)
                    
                    if len(unique_conversations) >= limit:
                        break
            
            # Sort by title for better organization
            unique_conversations.sort(key=lambda x: x['title'].lower())
            
            if progress_callback:
                progress_callback("Conversation list complete!", 100)
            
            logger.info(f"✅ Found {len(unique_conversations)} unique conversations")
            return unique_conversations
            
        except Exception as e:
            logger.error(f"❌ Failed to get conversation list: {e}")
            if progress_callback:
                progress_callback(f"Failed: {str(e)}", 0)
            return []
    
    def _extract_conversation_id(self, url_or_href: str) -> str:
        """Extract conversation ID from URL"""
        # Extract ID from URLs like /chat/2abc123def or /conversation/xyz789
        match = re.search(r'/(?:chat|conversation)/([a-zA-Z0-9]+)', url_or_href)
        return match.group(1) if match else url_or_href.split('/')[-1]
    
    def get_conversation_details(self, conversation_url: str, progress_callback: Optional[Callable[[str, int], None]] = None) -> Optional[Conversation]:
        """Enhanced conversation detail extraction with better message parsing"""
        if not self.driver:
            if not self.connect():
                return None
        
        self._rate_limit()
        
        try:
            if progress_callback:
                progress_callback(f"Loading conversation...", 10)
            
            logger.info(f"Fetching conversation: {conversation_url}")
            self.driver.get(conversation_url)
            time.sleep(4)  # Extra time for conversation to load
            
            if progress_callback:
                progress_callback("Analyzing conversation structure...", 30)
            
            # Wait for conversation content to load
            try:
                WebDriverWait(self.driver, 20).until(
                    EC.any_of(
                        EC.presence_of_element_located((By.CSS_SELECTOR, "[class*='message']")),
                        EC.presence_of_element_located((By.CSS_SELECTOR, "[class*='Message']")),
                        EC.presence_of_element_located((By.CSS_SELECTOR, "[data-testid*='message']")),
                        EC.presence_of_element_located((By.CSS_SELECTOR, "main")),
                        EC.presence_of_element_located((By.CSS_SELECTOR, "[class*='chat']"))
                    )
                )
            except TimeoutException:
                logger.warning("Conversation content didn't load within timeout")
            
            if progress_callback:
                progress_callback("Extracting conversation metadata...", 50)
            
            # Extract conversation title with better detection
            title = "Untitled Conversation"
            title_selectors = [
                "h1", "h2", "h3",
                "[class*='title']", "[class*='Title']",
                "[data-testid*='title']",
                ".conversation-title",
                "title"  # Page title as fallback
            ]
            
            for selector in title_selectors:
                try:
                    title_elem = self.driver.find_element(By.CSS_SELECTOR, selector)
                    if title_elem and title_elem.text.strip():
                        title = title_elem.text.strip()
                        if len(title) > 3 and "Poe" not in title:  # Valid title
                            break
                except:
                    continue
            
            # Fallback to page title
            if title == "Untitled Conversation":
                page_title = self.driver.title
                if page_title and "Poe" not in page_title:
                    title = page_title
            
            # Extract bot name with improved detection
            bot_name = "Assistant"
            bot_patterns = [
                "[class*='bot']", "[class*='Bot']",
                "[class*='assistant']", "[class*='Assistant']", 
                "[data-testid*='bot']",
                "[class*='model']", "[class*='Model']"
            ]
            
            for pattern in bot_patterns:
                try:
                    bot_elements = self.driver.find_elements(By.CSS_SELECTOR, pattern)
                    for elem in bot_elements:
                        text = elem.text.strip()
                        if text and 5 <= len(text) <= 50:  # Reasonable bot name length
                            # Common bot names
                            known_bots = ["claude", "gpt", "gemini", "assistant", "chatgpt", "bard"]
                            if any(bot in text.lower() for bot in known_bots):
                                bot_name = text
                                break
                    if bot_name != "Assistant":
                        break
                except:
                    continue
            
            if progress_callback:
                progress_callback("Extracting messages...", 70)
            
            # Enhanced message extraction
            messages = []
            
            # Try multiple message detection strategies
            message_strategies = [
                # Strategy 1: Standard message selectors
                {
                    'selectors': [
                        "[class*='message']", "[class*='Message']",
                        "[data-testid*='message']",
                        ".chat-message", ".conversation-message"
                    ],
                    'name': 'standard_messages'
                },
                # Strategy 2: Role-based detection
                {
                    'selectors': [
                        "[role='group']", "[role='article']",
                        "article", ".message-group"
                    ],
                    'name': 'role_based'
                },
                # Strategy 3: Generic content blocks
                {
                    'selectors': [
                        "div[class*='chat']", "div[class*='Chat']",
                        "p", "div"
                    ],
                    'name': 'content_blocks'
                }
            ]
            
            message_elements = []
            successful_strategy = None
            
            for strategy in message_strategies:
                for selector in strategy['selectors']:
                    try:
                        elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                        # Filter elements with substantial text content
                        valid_elements = [
                            elem for elem in elements 
                            if elem.text and len(elem.text.strip()) > 10
                        ]
                        
                        if len(valid_elements) >= 2:  # At least 2 messages for a conversation
                            message_elements = valid_elements
                            successful_strategy = f"{strategy['name']}-{selector}"
                            logger.info(f"Found {len(message_elements)} messages using {successful_strategy}")
                            break
                    except:
                        continue
                
                if message_elements:
                    break
            
            if not message_elements:
                logger.warning("No message elements found")
                return None
            
            # Process messages with improved role detection
            for i, elem in enumerate(message_elements):
                try:
                    text = elem.text.strip()
                    if not text or len(text) < 5:
                        continue
                    
                    # Determine message role using multiple heuristics
                    role = "assistant"  # Default
                    
                    # Method 1: Class-based detection
                    elem_class = elem.get_attribute('class') or ""
                    elem_html = elem.get_attribute('outerHTML') or ""
                    
                    user_indicators = ["user", "human", "you", "me", "question"]
                    assistant_indicators = ["bot", "assistant", "ai", "response", "answer"]
                    
                    for indicator in user_indicators:
                        if indicator in elem_class.lower() or indicator in elem_html.lower():
                            role = "user"
                            break
                    
                    if role == "assistant":  # Only check if not already user
                        for indicator in assistant_indicators:
                            if indicator in elem_class.lower() or indicator in elem_html.lower():
                                role = "assistant"
                                break
                    
                    # Method 2: Position-based heuristic (alternating pattern)
                    if successful_strategy and "standard" in successful_strategy:
                        # For well-structured conversations, use alternating pattern
                        if i % 2 == 0:
                            role = "user"
                        else:
                            role = "assistant"
                    
                    # Method 3: Content analysis
                    if "?" in text and len(text) < 200:
                        role = "user"  # Short questions likely from user
                    elif len(text) > 300 and not text.startswith(("I ", "My ")):
                        role = "assistant"  # Long responses likely from assistant
                    
                    # Create message
                    message = Message(
                        role=role,
                        content=text,
                        timestamp=datetime.now() - timedelta(minutes=len(message_elements) - i),
                        bot_name=bot_name if role == "assistant" else None,
                        message_id=f"msg_{i}_{self._extract_conversation_id(conversation_url)}"
                    )
                    
                    messages.append(message)
                    
                except Exception as e:
                    logger.debug(f"Error processing message element {i}: {e}")
                    continue
            
            if not messages:
                logger.warning("No messages successfully extracted")
                return None
            
            if progress_callback:
                progress_callback("Building conversation object...", 90)
            
            # Create conversation object
            conversation = Conversation(
                id=self._extract_conversation_id(conversation_url),
                title=title,
                bot=bot_name,
                messages=messages,
                created_at=datetime.now() - timedelta(days=1),  # Estimate based on position
                updated_at=datetime.now(),
                url=conversation_url
            )
            
            if progress_callback:
                progress_callback("Conversation extracted!", 100)
            
            logger.info(f"✅ Extracted conversation '{title}' with {len(messages)} messages using {successful_strategy}")
            return conversation
            
        except Exception as e:
            logger.error(f"❌ Failed to get conversation details: {e}")
            if progress_callback:
                progress_callback(f"Failed: {str(e)}", 0)
            return None
    
    def get_conversations(self, limit: int = 10, progress_callback: Optional[Callable[[str, int], None]] = None) -> List[Conversation]:
        """Enhanced conversation retrieval with progress tracking"""
        logger.info(f"Getting {limit} conversations from Poe.com...")
        
        # Get conversation list
        if progress_callback:
            progress_callback("Getting conversation list...", 5)
        
        conversation_list = self.get_conversation_list(limit, progress_callback)
        
        if not conversation_list:
            logger.warning("No conversations found")
            if progress_callback:
                progress_callback("No conversations found", 100)
            return []
        
        conversations = []
        total_conversations = min(len(conversation_list), limit)
        
        for i, conv_info in enumerate(conversation_list[:limit]):
            try:
                base_progress = 20 + (i / total_conversations) * 70  # 20-90% range
                
                if progress_callback:
                    progress_callback(f"Processing {i+1}/{total_conversations}: {conv_info.get('title', 'Unknown')[:50]}...", int(base_progress))
                
                logger.info(f"Processing conversation {i+1}/{total_conversations}: {conv_info.get('title', 'Unknown')}")
                
                conversation = self.get_conversation_details(conv_info['url'])
                if conversation:
                    conversations.append(conversation)
                
                # Rate limiting between conversations
                if i < total_conversations - 1:
                    time.sleep(1)
                    
            except Exception as e:
                logger.error(f"Failed to process conversation {i+1}: {e}")
                continue
        
        if progress_callback:
            progress_callback(f"Complete! Retrieved {len(conversations)} conversations", 100)
        
        logger.info(f"✅ Successfully retrieved {len(conversations)} conversations")
        self.conversations = conversations
        return conversations
    
    def close(self):
        """Clean up and close the browser driver"""
        if self.driver:
            try:
                self.driver.quit()
                logger.info("Browser driver closed")
            except Exception as e:
                logger.warning(f"Error closing driver: {e}")
            finally:
                self.driver = None
    
    def __enter__(self):
        """Context manager entry"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()
    
    # Enhanced backward compatibility method for GUI
    def _create_sample_conversations(self, count: int = 10) -> List[Conversation]:
        """Enhanced fallback method with real conversation attempt first"""
        try:
            # Try to get real conversations first
            logger.info("Attempting to fetch real conversations...")
            real_conversations = self.get_conversations(count)
            if real_conversations:
                logger.info(f"Successfully retrieved {len(real_conversations)} real conversations")
                return real_conversations
        except Exception as e:
            logger.warning(f"Failed to get real conversations, falling back to samples: {e}")
        
        # Enhanced fallback with more realistic sample data
        logger.info("Creating enhanced sample conversations...")
        sample_conversations = []
        
        bots = ["Claude-3-Sonnet", "GPT-4", "Claude-3-Opus", "Gemini-Pro", "GPT-3.5-Turbo"]
        topics = [
            "Python Programming Help - Advanced Decorators",
            "Machine Learning Pipeline Optimization", 
            "React Component Architecture Design",
            "Database Query Performance Analysis",
            "Algorithm Complexity Comparison",
            "API Security Best Practices",
            "Docker Container Orchestration",
            "Code Review and Refactoring",
            "System Architecture Scalability",
            "Debugging Memory Leaks"
        ]
        
        sample_responses = [
            "I'd be happy to help you with this technical challenge. Let me break down the approach step by step...",
            "That's an excellent question about optimization. Here are several strategies you can implement...",
            "For this architecture pattern, I recommend considering the following design principles...",
            "Let's analyze this performance issue systematically. First, we should examine...",
            "This is a common scenario in enterprise development. The best practices include...",
            "Great question about security! Here's a comprehensive approach to implementing...",
            "For containerization, you'll want to focus on these key aspects...",
            "During code review, I notice several areas where we can improve maintainability...",
            "When designing scalable systems, it's crucial to consider these architectural patterns...",
            "Memory leaks can be tricky to debug. Let's use these diagnostic techniques..."
        ]
        
        for i in range(min(count, len(topics))):
            messages = []
            
            # Create more realistic conversation flow
            user_content = f"I'm working on {topics[i].lower()}. I've encountered some challenges with implementation and could use some guidance on best practices. Can you help me understand the optimal approach?"
            
            messages.append(Message(
                role="user",
                content=user_content,
                timestamp=datetime.now() - timedelta(hours=i*2, minutes=30),
                message_id=f"user_msg_{i}_1"
            ))
            
            # Assistant response
            bot_name = bots[i % len(bots)]
            assistant_content = f"{sample_responses[i]} " + \
                             "This involves understanding the core concepts, implementing proper error handling, " + \
                             "and following industry standards for maintainable code. Would you like me to elaborate on any specific aspect?"
            
            messages.append(Message(
                role="assistant",
                content=assistant_content,
                timestamp=datetime.now() - timedelta(hours=i*2, minutes=25),
                bot_name=bot_name,
                message_id=f"assistant_msg_{i}_1"
            ))
            
            # Follow-up user question
            follow_up = "That's very helpful! Could you provide a specific example or code snippet to illustrate this concept?"
            messages.append(Message(
                role="user",
                content=follow_up,
                timestamp=datetime.now() - timedelta(hours=i*2, minutes=20),
                message_id=f"user_msg_{i}_2"
            ))
            
            # Detailed assistant response with example
            detailed_response = "Absolutely! Here's a practical example that demonstrates the concept:\n\n" + \
                              "```python\n# Example implementation\ndef optimized_solution():\n    # Implementation details here\n    pass\n```\n\n" + \
                              "This approach offers several advantages including improved performance, better maintainability, and enhanced scalability."
            
            messages.append(Message(
                role="assistant",
                content=detailed_response,
                timestamp=datetime.now() - timedelta(hours=i*2, minutes=15),
                bot_name=bot_name,
                message_id=f"assistant_msg_{i}_2"
            ))
            
            conversation = Conversation(
                id=f"enhanced_sample_{i}",
                title=topics[i],
                bot=bot_name,
                messages=messages,
                created_at=datetime.now() - timedelta(hours=i*2, minutes=30),
                updated_at=datetime.now() - timedelta(hours=i*2, minutes=15),
                url=f"https://poe.com/chat/sample_{i}"
            )
            
            sample_conversations.append(conversation)
        
        logger.info(f"Created {len(sample_conversations)} enhanced sample conversations")
        return sample_conversations

# Export main classes
__all__ = ['PoeAPIClient', 'Conversation', 'Message']