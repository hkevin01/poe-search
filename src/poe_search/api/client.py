# src/poe_search/api/client.py
import asyncio
import json
import time
import tempfile
from typing import List, Optional, Dict, Any, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
import logging

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from webdriver_manager.chrome import ChromeDriverManager

logger = logging.getLogger(__name__)

@dataclass
class Message:
    """Represents a single message in a conversation"""
    id: str
    role: str  # 'user' or 'assistant'
    content: str
    timestamp: datetime
    bot_name: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'role': self.role,
            'content': self.content,
            'timestamp': self.timestamp.isoformat(),
            'bot_name': self.bot_name
        }

@dataclass
class Conversation:
    """Represents a complete conversation"""
    id: str
    title: str
    bot: str
    messages: List[Message]
    created_at: datetime
    updated_at: datetime
    category: Optional[str] = None
    tags: List[str] = None
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = []
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'title': self.title,
            'bot': self.bot,
            'messages': [msg.to_dict() for msg in self.messages],
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'category': self.category,
            'tags': self.tags
        }

class PoeApiClient:
    """Enhanced Poe API client using browser automation"""
    
    def __init__(self, token: str, headless: bool = False, rate_limit: float = 2.0):
        self.token = token
        self.headless = headless
        self.rate_limit = rate_limit
        self.driver = None
        self.is_connected = False
        self.conversations_cache = []
        
    async def connect(self) -> bool:
        """Initialize browser connection to Poe with enhanced reliability"""
        try:
            logger.info("🔄 Initializing enhanced Poe browser connection...")
            
            # Enhanced Chrome options for better reliability
            chrome_options = Options()
            temp_dir = tempfile.mkdtemp()
            chrome_options.add_argument(f"--user-data-dir={temp_dir}")
            
            if self.headless:
                chrome_options.add_argument("--headless=new")  # Use new headless mode
            
            # Enhanced browser options
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-blink-features=AutomationControlled")
            chrome_options.add_argument("--disable-web-security")
            chrome_options.add_argument("--disable-features=VizDisplayCompositor")
            chrome_options.add_argument("--window-size=1920,1080")
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            
            # Additional options for stability
            chrome_options.add_argument("--disable-extensions")
            chrome_options.add_argument("--disable-plugins")
            chrome_options.add_argument("--disable-images")  # Speed up loading
            
            # Initialize driver with enhanced settings
            service = webdriver.chrome.service.Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            
            # Enhanced stealth mode
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            self.driver.execute_cdp_cmd('Network.setUserAgentOverride', {
                "userAgent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            })
            
            # Navigate to Poe with retry logic
            for attempt in range(3):
                try:
                    logger.info(f"🌐 Opening Poe.com (attempt {attempt + 1})...")
                    self.driver.get("https://poe.com")
                    await asyncio.sleep(3)
                    
                    # Set authentication cookie if provided
                    if self.token:
                        logger.info("🔑 Setting authentication cookie...")
                        self.driver.add_cookie({
                            'name': 'p-b',
                            'value': self.token,
                            'domain': '.poe.com',
                            'path': '/',
                            'secure': True
                        })
                        
                        # Refresh to apply authentication
                        self.driver.refresh()
                        await asyncio.sleep(5)
                    
                    # Enhanced login detection
                    login_indicators = [
                        "textarea[placeholder*='Talk']",
                        "textarea[placeholder*='Message']",
                        "[data-testid*='textInput']",
                        "textarea",
                        "[contenteditable='true']"
                    ]
                    
                    for indicator in login_indicators:
                        try:
                            element = WebDriverWait(self.driver, 10).until(
                                EC.presence_of_element_located((By.CSS_SELECTOR, indicator))
                            )
                            if element:
                                self.is_connected = True
                                logger.info("✅ Successfully connected to Poe!")
                                return True
                        except:
                            continue
                    
                    if attempt == 2:
                        logger.warning("⚠️ Could not detect login. Manual login may be required.")
                        return False
                        
                except Exception as e:
                    logger.warning(f"⚠️ Attempt {attempt + 1} failed: {e}")
                    if attempt == 2:
                        raise e
                    await asyncio.sleep(2)
            
            return False
                
        except Exception as e:
            logger.error(f"❌ Failed to connect to Poe: {e}")
            return False
    
    async def get_conversations(self, limit: int = 100) -> List[Conversation]:
        """Enhanced conversation fetching with multiple strategies"""
        if not self.is_connected:
            logger.error("❌ Not connected to Poe. Call connect() first.")
            return []
        
        try:
            logger.info(f"📥 Fetching up to {limit} conversations...")
            conversations = []
            
            # Strategy 1: Try to navigate to chat history page
            chat_urls = [
                "https://poe.com",
                "https://poe.com/chats",
                "https://poe.com/chat"
            ]
            
            for url in chat_urls:
                try:
                    self.driver.get(url)
                    await asyncio.sleep(3)
                    
                    # Enhanced conversation detection
                    conversation_selectors = [
                        # New Poe interface selectors
                        "[data-testid*='chat']",
                        "[data-testid*='conversation']",
                        "a[href*='/chat/']",
                        "div[class*='ChatListItem']",
                        "div[class*='ConversationItem']",
                        # Generic selectors
                        "[role='button'][class*='chat']",
                        "button[class*='conversation']",
                        ".chat-item",
                        ".conversation-item"
                    ]
                    
                    found_conversations = False
                    for selector in conversation_selectors:
                        try:
                            elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                            if len(elements) > 5:  # Likely found conversation list
                                logger.info(f"Found {len(elements)} conversation elements with selector: {selector}")
                                conversations = await self._extract_conversations_from_elements(elements[:limit])
                                found_conversations = True
                                break
                        except Exception as e:
                            logger.debug(f"Selector {selector} failed: {e}")
                            continue
                    
                    if found_conversations:
                        break
                        
                except Exception as e:
                    logger.warning(f"Failed to load {url}: {e}")
                    continue
            
            # Strategy 2: If no conversations found, try scrolling and dynamic loading
            if not conversations:
                logger.info("🔄 Trying dynamic conversation loading...")
                conversations = await self._dynamic_conversation_discovery(limit)
            
            # Strategy 3: Manual extraction fallback
            if not conversations:
                logger.info("🔄 Trying manual conversation extraction...")
                conversations = await self._manual_conversation_extraction(limit)
            
            # Cache results
            self.conversations_cache = conversations
            
            logger.info(f"✅ Successfully fetched {len(conversations)} conversations")
            return conversations
            
        except Exception as e:
            logger.error(f"❌ Failed to fetch conversations: {e}")
            return []
    
    async def _extract_conversations_from_elements(self, elements) -> List[Conversation]:
        """Extract conversation data from DOM elements"""
        conversations = []
        
        for i, element in enumerate(elements):
            try:
                # Extract conversation title
                title_selectors = [
                    ".conversation-title",
                    "[data-testid*='title']",
                    "h3", "h4", "h5",
                    ".title",
                    "span[class*='title']"
                ]
                
                title = "Untitled Conversation"
                for selector in title_selectors:
                    try:
                        title_elem = element.find_element(By.CSS_SELECTOR, selector)
                        if title_elem.text.strip():
                            title = title_elem.text.strip()
                            break
                    except:
                        continue
                
                # Extract conversation ID from href or data attributes
                conv_id = f"conv_{i+1}"
                try:
                    href = element.get_attribute('href')
                    if href and '/chat/' in href:
                        conv_id = href.split('/chat/')[-1].split('?')[0]
                except:
                    pass
                
                # Extract bot information
                bot_selectors = [
                    "[class*='bot']",
                    "[data-testid*='bot']",
                    ".model-name",
                    "span[class*='model']"
                ]
                
                bot = "Assistant"
                for selector in bot_selectors:
                    try:
                        bot_elem = element.find_element(By.CSS_SELECTOR, selector)
                        if bot_elem.text.strip():
                            bot = bot_elem.text.strip()
                            break
                    except:
                        continue
                
                # Create conversation object
                conversation = Conversation(
                    id=conv_id,
                    title=title[:100],  # Limit title length
                    bot=bot,
                    messages=[],  # Will be populated separately
                    created_at=datetime.now() - timedelta(days=i),  # Estimated
                    updated_at=datetime.now() - timedelta(hours=i)
                )
                
                conversations.append(conversation)
                
                # Rate limiting
                await asyncio.sleep(self.rate_limit / 10)
                
            except Exception as e:
                logger.warning(f"⚠️ Failed to extract conversation {i}: {e}")
                continue
        
        return conversations
    
    async def _dynamic_conversation_discovery(self, limit: int) -> List[Conversation]:
        """Try to discover conversations through scrolling and dynamic loading"""
        conversations = []
        
        try:
            # Scroll to load more conversations
            last_height = self.driver.execute_script("return document.body.scrollHeight")
            
            for scroll_attempt in range(5):  # Try scrolling 5 times
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                await asyncio.sleep(2)
                
                new_height = self.driver.execute_script("return document.body.scrollHeight")
                if new_height == last_height:
                    break  # No more content to load
                last_height = new_height
            
            # Look for any clickable elements that might be conversations
            clickable_elements = self.driver.find_elements(By.CSS_SELECTOR, "a, button, [role='button']")
            
            potential_conversations = []
            for element in clickable_elements:
                try:
                    text = element.text.strip()
                    href = element.get_attribute('href') or ""
                    
                    # Filter for conversation-like elements
                    if (len(text) > 10 and len(text) < 200 and 
                        ('chat' in href.lower() or 'conversation' in href.lower() or
                         any(keyword in text.lower() for keyword in ['chat', 'conversation', 'talk', 'ask']))):
                        potential_conversations.append(element)
                        
                        if len(potential_conversations) >= limit:
                            break
                except:
                    continue
            
            conversations = await self._extract_conversations_from_elements(potential_conversations)
            
        except Exception as e:
            logger.warning(f"Dynamic discovery failed: {e}")
        
        return conversations
    
    async def _manual_conversation_extraction(self, limit: int) -> List[Conversation]:
        """Manual fallback extraction method"""
        conversations = []
        
        try:
            # Get all text content and try to find conversation patterns
            page_source = self.driver.page_source
            
            # Simple pattern matching for conversation titles
            import re
            
            # Look for common conversation patterns
            patterns = [
                r'"title":"([^"]{10,100})"',
                r'data-title="([^"]{10,100})"',
                r'aria-label="([^"]{10,100})"'
            ]
            
            found_titles = set()
            for pattern in patterns:
                matches = re.findall(pattern, page_source)
                for match in matches:
                    if len(match) > 10 and match not in found_titles:
                        found_titles.add(match)
                        
                        conv = Conversation(
                            id=f"manual_{len(conversations)}",
                            title=match,
                            bot="Unknown",
                            messages=[],
                            created_at=datetime.now() - timedelta(days=len(conversations)),
                            updated_at=datetime.now()
                        )
                        conversations.append(conv)
                        
                        if len(conversations) >= limit:
                            break
                
                if len(conversations) >= limit:
                    break
            
        except Exception as e:
            logger.warning(f"Manual extraction failed: {e}")
        
        return conversations
    
    async def get_conversation_messages(self, conversation_id: str) -> List[Message]:
        """Enhanced message extraction for a specific conversation"""
        if not self.is_connected:
            return []
        
        try:
            logger.info(f"📬 Fetching messages for conversation: {conversation_id}")
            
            # Navigate to conversation
            chat_url = f"https://poe.com/chat/{conversation_id}"
            self.driver.get(chat_url)
            await asyncio.sleep(3)
            
            # Wait for messages to load
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # Enhanced message detection
            message_selectors = [
                "[data-testid*='message']",
                "[class*='Message']",
                "[class*='message']",
                ".prose",
                "div[dir='auto']",
                "[role='text']",
                ".chat-message",
                ".conversation-message"
            ]
            
            all_message_elements = []
            for selector in message_selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if elements:
                        all_message_elements.extend(elements)
                except:
                    continue
            
            # Remove duplicates while preserving order
            seen = set()
            unique_elements = []
            for elem in all_message_elements:
                elem_id = id(elem)
                if elem_id not in seen:
                    seen.add(elem_id)
                    unique_elements.append(elem)
            
            messages = []
            for i, element in enumerate(unique_elements):
                try:
                    content = element.text.strip()
                    
                    # Filter out empty or very short messages
                    if not content or len(content) < 3:
                        continue
                    
                    # Determine message role
                    role = "assistant"  # Default
                    element_classes = element.get_attribute("class") or ""
                    element_html = element.get_attribute("outerHTML") or ""
                    
                    # Look for user indicators
                    user_indicators = ["user", "human", "you", "input"]
                    if any(indicator in element_classes.lower() for indicator in user_indicators):
                        role = "user"
                    elif any(indicator in element_html.lower() for indicator in user_indicators):
                        role = "user"
                    
                    # Try to extract bot name
                    bot_name = "Assistant"
                    bot_indicators = element.find_elements(By.CSS_SELECTOR, "[class*='bot'], [class*='model'], .assistant-name")
                    if bot_indicators:
                        bot_name = bot_indicators[0].text.strip() or "Assistant"
                    
                    message = Message(
                        id=f"msg_{conversation_id}_{i}",
                        role=role,
                        content=content,
                        timestamp=datetime.now() - timedelta(minutes=len(messages) * 2),
                        bot_name=bot_name
                    )
                    
                    messages.append(message)
                    
                except Exception as e:
                    logger.debug(f"Failed to extract message {i}: {e}")
                    continue
            
            logger.info(f"✅ Extracted {len(messages)} messages from conversation {conversation_id}")
            return messages
            
        except Exception as e:
            logger.error(f"❌ Failed to fetch messages for {conversation_id}: {e}")
            return []
    
    async def search_conversations(self, query: str, limit: int = 50) -> List[Conversation]:
        """Search conversations by content"""
        # Use cached conversations for local search
        if not self.conversations_cache:
            await self.get_conversations(limit)
        
        matching = []
        query_lower = query.lower()
        
        for conv in self.conversations_cache:
            # Search in title
            if query_lower in conv.title.lower():
                matching.append(conv)
                continue
            
            # Search in messages if loaded
            for message in conv.messages:
                if query_lower in message.content.lower():
                    matching.append(conv)
                    break
        
        return matching[:limit]
    
    def disconnect(self):
        """Clean disconnect"""
        if self.driver:
            try:
                self.driver.quit()
            except:
                pass
            self.driver = None
            self.is_connected = False
            logger.info("🔌 Disconnected from Poe")
    
    def __del__(self):
        """Cleanup on destruction"""
        self.disconnect()

# Factory function
def create_poe_client(token: str, headless: bool = False, rate_limit: float = 2.0) -> PoeApiClient:
    """Create a configured Poe API client"""
    return PoeApiClient(token=token, headless=headless, rate_limit=rate_limit)