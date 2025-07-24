"""
Poe API Client - Real Poe.com Integration
Connects to Poe.com using Selenium WebDriver to fetch actual conversations
"""

import json
import time
import logging
import re
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
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
    """Real Poe.com API client using browser automation"""
    
    def __init__(self, token: str, headless: bool = True, browser: str = "chrome"):
        """Initialize the Poe client with real browser automation"""
        if not SELENIUM_AVAILABLE:
            raise ImportError("Selenium is required for Poe integration. Install with: pip install selenium")
        
        self.token = token
        self.headless = headless
        self.browser = browser
        self.driver = None
        self.conversations = []
        
        # Rate limiting
        self.last_request_time = 0
        self.min_request_interval = 2.0  # 2 seconds between requests
        
        logger.info(f"Initializing Poe client (headless={headless}, browser={browser})")
    
    def _setup_driver(self):
        """Setup and configure the web driver"""
        if self.driver:
            return self.driver
        
        try:
            if self.browser.lower() == "chrome":
                options = ChromeOptions()
                if self.headless:
                    options.add_argument("--headless")
                options.add_argument("--no-sandbox")
                options.add_argument("--disable-dev-shm-usage")
                options.add_argument("--disable-gpu")
                options.add_argument("--window-size=1920,1080")
                options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
                
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
            
            # Set timeouts
            self.driver.implicitly_wait(10)
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
    
    def connect(self):
        """Connect to Poe.com and authenticate"""
        self._setup_driver()
        self._rate_limit()
        
        try:
            logger.info("Connecting to Poe.com...")
            self.driver.get("https://poe.com")
            
            # Add the authentication cookie
            logger.info("Setting authentication cookie...")
            self.driver.add_cookie({
                'name': 'p-b',
                'value': self.token,
                'domain': '.poe.com',
                'path': '/',
                'secure': True,
                'httpOnly': True
            })
            
            # Refresh to apply authentication
            self.driver.refresh()
            time.sleep(3)
            
            # Verify we're logged in by checking for user-specific elements
            try:
                # Look for conversation list or chat interface
                WebDriverWait(self.driver, 15).until(
                    EC.any_of(
                        EC.presence_of_element_located((By.CSS_SELECTOR, "[class*='ChatPage']")),
                        EC.presence_of_element_located((By.CSS_SELECTOR, "[class*='conversation']")),
                        EC.presence_of_element_located((By.CSS_SELECTOR, "[data-testid*='chat']")),
                        EC.presence_of_element_located((By.CSS_SELECTOR, "main"))
                    )
                )
                logger.info("✅ Successfully authenticated with Poe.com")
                return True
                
            except TimeoutException:
                logger.error("❌ Authentication failed - couldn't find chat interface")
                return False
                
        except Exception as e:
            logger.error(f"❌ Failed to connect to Poe.com: {e}")
            return False
    
    def get_conversation_list(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get list of conversations from Poe.com"""
        if not self.driver:
            if not self.connect():
                raise Exception("Failed to connect to Poe.com")
        
        self._rate_limit()
        
        try:
            logger.info(f"Fetching conversation list (limit: {limit})...")
            
            # Navigate to conversations/history page
            # Poe.com structure may vary, try multiple approaches
            conversation_links = []
            
            # Method 1: Look for conversation links in sidebar
            try:
                sidebar_conversations = self.driver.find_elements(
                    By.CSS_SELECTOR, 
                    "a[href*='/chat/'], a[href*='/conversation/'], [class*='conversation'] a, [class*='ChatPage'] a"
                )
                
                for link in sidebar_conversations[:limit]:
                    href = link.get_attribute('href')
                    title = link.text.strip() or link.get_attribute('title') or "Untitled"
                    
                    if href and ('/chat/' in href or '/conversation/' in href):
                        conversation_links.append({
                            'url': href,
                            'title': title,
                            'id': self._extract_conversation_id(href)
                        })
                        
            except Exception as e:
                logger.warning(f"Method 1 failed: {e}")
            
            # Method 2: Look for conversation history via navigation
            if not conversation_links:
                try:
                    # Try to navigate to history/conversations page
                    history_urls = [
                        "https://poe.com/chats",
                        "https://poe.com/conversations", 
                        "https://poe.com/history"
                    ]
                    
                    for url in history_urls:
                        try:
                            self.driver.get(url)
                            time.sleep(2)
                            
                            conversation_elements = self.driver.find_elements(
                                By.CSS_SELECTOR,
                                "a[href*='/chat/'], [data-testid*='conversation'], [class*='conversation']"
                            )
                            
                            if conversation_elements:
                                for elem in conversation_elements[:limit]:
                                    link = elem.find_element(By.TAG_NAME, 'a') if elem.tag_name != 'a' else elem
                                    href = link.get_attribute('href')
                                    title = elem.text.strip() or "Untitled"
                                    
                                    if href and '/chat/' in href:
                                        conversation_links.append({
                                            'url': href,
                                            'title': title,
                                            'id': self._extract_conversation_id(href)
                                        })
                                break
                                
                        except Exception as e:
                            logger.debug(f"History URL {url} failed: {e}")
                            continue
                            
                except Exception as e:
                    logger.warning(f"Method 2 failed: {e}")
            
            # Method 3: Extract from current page JavaScript/DOM
            if not conversation_links:
                try:
                    # Try to extract conversation data from page scripts or DOM
                    scripts = self.driver.find_elements(By.TAG_NAME, 'script')
                    for script in scripts:
                        content = script.get_attribute('innerHTML')
                        if content and ('chat' in content.lower() or 'conversation' in content.lower()):
                            # Look for conversation IDs or URLs in script content
                            chat_matches = re.findall(r'["\']([^"\']*chat[^"\']*)["\']', content)
                            for match in chat_matches[:limit]:
                                if 'chat/' in match or 'conversation/' in match:
                                    conversation_links.append({
                                        'url': f"https://poe.com{match}" if match.startswith('/') else match,
                                        'title': 'Extracted Conversation',
                                        'id': self._extract_conversation_id(match)
                                    })
                except Exception as e:
                    logger.warning(f"Method 3 failed: {e}")
            
            logger.info(f"✅ Found {len(conversation_links)} conversations")
            return conversation_links
            
        except Exception as e:
            logger.error(f"❌ Failed to get conversation list: {e}")
            return []
    
    def _extract_conversation_id(self, url_or_href: str) -> str:
        """Extract conversation ID from URL"""
        # Extract ID from URLs like /chat/2abc123def or /conversation/xyz789
        match = re.search(r'/(?:chat|conversation)/([a-zA-Z0-9]+)', url_or_href)
        return match.group(1) if match else url_or_href.split('/')[-1]
    
    def get_conversation_details(self, conversation_url: str) -> Optional[Conversation]:
        """Get full conversation details from a specific conversation URL"""
        if not self.driver:
            if not self.connect():
                return None
        
        self._rate_limit()
        
        try:
            logger.info(f"Fetching conversation: {conversation_url}")
            self.driver.get(conversation_url)
            time.sleep(3)
            
            # Wait for conversation to load
            WebDriverWait(self.driver, 15).until(
                EC.any_of(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "[class*='message']")),
                    EC.presence_of_element_located((By.CSS_SELECTOR, "[class*='Message']")),
                    EC.presence_of_element_located((By.CSS_SELECTOR, "[data-testid*='message']")),
                    EC.presence_of_element_located((By.CSS_SELECTOR, ".conversation"))
                )
            )
            
            # Extract conversation title
            title = "Untitled Conversation"
            try:
                title_selectors = [
                    "h1", "h2", ".title", "[class*='title']", 
                    "[data-testid*='title']", ".conversation-title"
                ]
                for selector in title_selectors:
                    title_elem = self.driver.find_element(By.CSS_SELECTOR, selector)
                    if title_elem and title_elem.text.strip():
                        title = title_elem.text.strip()
                        break
            except:
                # If no title found, use page title or generate from first message
                title = self.driver.title or "Untitled Conversation"
            
            # Extract bot name
            bot_name = "Assistant"
            try:
                # Look for bot indicators in the page
                bot_indicators = self.driver.find_elements(
                    By.CSS_SELECTOR, 
                    "[class*='bot'], [class*='assistant'], [data-testid*='bot']"
                )
                for indicator in bot_indicators:
                    text = indicator.text.strip()
                    if text and len(text) < 50:  # Reasonable bot name length
                        bot_name = text
                        break
            except:
                pass
            
            # Extract messages
            messages = []
            message_selectors = [
                "[class*='message']", "[class*='Message']", 
                "[data-testid*='message']", ".conversation-message",
                "[role='group']", ".chat-message"
            ]
            
            message_elements = []
            for selector in message_selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if elements:
                        message_elements = elements
                        break
                except:
                    continue
            
            if not message_elements:
                logger.warning("No message elements found, trying fallback methods")
                # Fallback: look for any elements that might contain conversation text
                message_elements = self.driver.find_elements(By.CSS_SELECTOR, "div, p, span")
                message_elements = [elem for elem in message_elements if elem.text and len(elem.text.strip()) > 10]
            
            for i, elem in enumerate(message_elements):
                try:
                    text = elem.text.strip()
                    if not text or len(text) < 3:
                        continue
                    
                    # Determine message role (user vs assistant)
                    role = "assistant"  # Default to assistant
                    
                    # Look for user indicators
                    user_indicators = [
                        "user", "you", "human", "me", "my",
                        "[class*='user']", "[class*='human']"
                    ]
                    
                    elem_class = elem.get_attribute('class') or ""
                    elem_html = elem.get_attribute('outerHTML') or ""
                    
                    for indicator in user_indicators:
                        if indicator in elem_class.lower() or indicator in elem_html.lower():
                            role = "user"
                            break
                    
                    # Alternating pattern heuristic (often user, assistant, user, assistant...)
                    if i % 2 == 0:
                        role = "user"
                    else:
                        role = "assistant"
                    
                    # Create message
                    message = Message(
                        role=role,
                        content=text,
                        timestamp=datetime.now() - timedelta(minutes=len(message_elements) - i),
                        bot_name=bot_name if role == "assistant" else None,
                        message_id=f"msg_{i}"
                    )
                    
                    messages.append(message)
                    
                except Exception as e:
                    logger.debug(f"Error processing message element {i}: {e}")
                    continue
            
            if not messages:
                logger.warning("No messages extracted from conversation")
                return None
            
            # Create conversation object
            conversation = Conversation(
                id=self._extract_conversation_id(conversation_url),
                title=title,
                bot=bot_name,
                messages=messages,
                created_at=datetime.now() - timedelta(days=1),  # Estimate
                url=conversation_url
            )
            
            logger.info(f"✅ Extracted conversation '{title}' with {len(messages)} messages")
            return conversation
            
        except Exception as e:
            logger.error(f"❌ Failed to get conversation details: {e}")
            return None
    
    def get_conversations(self, limit: int = 10) -> List[Conversation]:
        """Get multiple conversations from Poe.com"""
        logger.info(f"Getting {limit} conversations from Poe.com...")
        
        # Get conversation list
        conversation_list = self.get_conversation_list(limit)
        
        if not conversation_list:
            logger.warning("No conversations found")
            return []
        
        conversations = []
        
        for i, conv_info in enumerate(conversation_list[:limit]):
            try:
                logger.info(f"Processing conversation {i+1}/{len(conversation_list)}: {conv_info.get('title', 'Unknown')}")
                
                conversation = self.get_conversation_details(conv_info['url'])
                if conversation:
                    conversations.append(conversation)
                
                # Rate limiting between conversations
                if i < len(conversation_list) - 1:
                    time.sleep(1)
                    
            except Exception as e:
                logger.error(f"Failed to process conversation {i+1}: {e}")
                continue
        
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
    
    # Backward compatibility method for GUI
    def _create_sample_conversations(self, count: int = 10) -> List[Conversation]:
        """Fallback method that returns real conversations or creates samples"""
        try:
            # Try to get real conversations first
            real_conversations = self.get_conversations(count)
            if real_conversations:
                return real_conversations
        except Exception as e:
            logger.warning(f"Failed to get real conversations, falling back to samples: {e}")
        
        # Fallback to sample data if real fetching fails
        logger.info("Creating sample conversations as fallback...")
        sample_conversations = []
        
        bots = ["Claude-3", "GPT-4", "Gemini-Pro", "Claude-Instant", "GPT-3.5"]
        topics = [
            "Python Programming Help",
            "Machine Learning Concepts", 
            "Web Development Tips",
            "Data Analysis Project",
            "Algorithm Optimization",
            "Database Design Question",
            "API Integration Help",
            "Code Review Session",
            "Technical Architecture",
            "Debugging Session"
        ]
        
        for i in range(min(count, len(topics))):
            messages = []
            
            # User question
            user_content = f"I need help with {topics[i].lower()}. Can you provide some guidance?"
            messages.append(Message(
                role="user",
                content=user_content,
                timestamp=datetime.now() - timedelta(hours=i),
                message_id=f"user_msg_{i}"
            ))
            
            # Assistant response
            bot_name = bots[i % len(bots)]
            assistant_content = f"I'd be happy to help you with {topics[i].lower()}! Here's a comprehensive approach..."
            messages.append(Message(
                role="assistant", 
                content=assistant_content,
                timestamp=datetime.now() - timedelta(hours=i, minutes=5),
                bot_name=bot_name,
                message_id=f"assistant_msg_{i}"
            ))
            
            conversation = Conversation(
                id=f"sample_conv_{i}",
                title=topics[i],
                bot=bot_name,
                messages=messages,
                created_at=datetime.now() - timedelta(hours=i),
                url=f"https://poe.com/chat/sample_{i}"
            )
            
            sample_conversations.append(conversation)
        
        return sample_conversations

# Export main classes
__all__ = ['PoeAPIClient', 'Conversation', 'Message']