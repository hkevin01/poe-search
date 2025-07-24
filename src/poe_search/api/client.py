# src/poe_search/api/client.py
import asyncio
import tempfile
import time
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from dataclasses import dataclass

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager

from ..models.conversation import Conversation, Message
from ..utils.logger import get_logger

logger = get_logger(__name__)

@dataclass
class PoeApiConfig:
    token: str
    rate_limit_delay: float = 2.0
    max_retries: int = 3
    headless: bool = False

class PoeApiClient:
    """Working Poe API client using browser automation"""
    
    def __init__(self, config: PoeApiConfig):
        self.config = config
        self.driver = None
        self.is_connected = False
        
    async def connect(self) -> bool:
        """Initialize browser connection to Poe"""
        try:
            logger.info("🔄 Initializing Poe browser connection...")
            
            # Set up Chrome options
            chrome_options = Options()
            temp_dir = tempfile.mkdtemp()
            chrome_options.add_argument(f"--user-data-dir={temp_dir}")
            
            if self.config.headless:
                chrome_options.add_argument("--headless")
            
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-blink-features=AutomationControlled")
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            
            # Initialize driver
            self.driver = webdriver.Chrome(
                service=webdriver.chrome.service.Service(ChromeDriverManager().install()),
                options=chrome_options
            )
            
            # Remove automation detection
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            # Navigate to Poe
            logger.info("🌐 Opening Poe.com...")
            self.driver.get("https://poe.com")
            
            # Set token cookie if provided
            if self.config.token:
                self.driver.add_cookie({
                    'name': 'p-b',
                    'value': self.config.token,
                    'domain': '.poe.com'
                })
                self.driver.refresh()
            
            # Wait for page load
            await asyncio.sleep(3)
            
            # Check if logged in
            try:
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "textarea, [contenteditable='true']"))
                )
                self.is_connected = True
                logger.info("✅ Successfully connected to Poe!")
                return True
            except:
                logger.warning("⚠️ Not logged in. Manual login required.")
                return False
                
        except Exception as e:
            logger.error(f"❌ Failed to connect to Poe: {e}")
            return False
    
    async def get_conversations(self, limit: int = 50) -> List[Conversation]:
        """Fetch conversations from Poe"""
        if not self.is_connected:
            logger.error("❌ Not connected to Poe. Call connect() first.")
            return []
        
        try:
            logger.info(f"📥 Fetching {limit} conversations...")
            
            # Navigate to chat history (adjust URL as needed)
            self.driver.get("https://poe.com")
            await asyncio.sleep(2)
            
            conversations = []
            
            # Look for conversation list elements
            conversation_selectors = [
                "[data-testid*='conversation']",
                "[class*='conversation']",
                "[class*='chat-item']",
                "a[href*='/chat/']"
            ]
            
            conversation_elements = []
            for selector in conversation_selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if elements:
                        conversation_elements = elements[:limit]
                        break
                except:
                    continue
            
            if not conversation_elements:
                logger.warning("⚠️ No conversation elements found. Manual navigation may be required.")
                return []
            
            # Extract conversation data
            for i, element in enumerate(conversation_elements):
                try:
                    # Extract basic info
                    title = element.text.strip() or f"Conversation {i+1}"
                    href = element.get_attribute('href') if element.tag_name == 'a' else ""
                    conv_id = self._extract_conversation_id(href) or f"conv_{i+1}"
                    
                    # Create conversation object
                    conversation = Conversation(
                        id=conv_id,
                        title=title,
                        bot="Unknown",  # Will be updated when fetching messages
                        messages=[],
                        created_at=datetime.now() - timedelta(days=i),  # Placeholder
                        updated_at=datetime.now() - timedelta(days=i)
                    )
                    
                    conversations.append(conversation)
                    
                    # Rate limiting
                    await asyncio.sleep(self.config.rate_limit_delay)
                    
                except Exception as e:
                    logger.warning(f"⚠️ Failed to extract conversation {i}: {e}")
                    continue
            
            logger.info(f"✅ Successfully fetched {len(conversations)} conversations")
            return conversations
            
        except Exception as e:
            logger.error(f"❌ Failed to fetch conversations: {e}")
            return []
    
    async def get_conversation_messages(self, conversation_id: str) -> List[Message]:
        """Fetch messages for a specific conversation"""
        if not self.is_connected:
            return []
        
        try:
            # Navigate to specific conversation
            self.driver.get(f"https://poe.com/chat/{conversation_id}")
            await asyncio.sleep(3)
            
            messages = []
            
            # Look for message elements
            message_selectors = [
                "[data-testid*='message']",
                "[class*='message']",
                ".prose",
                "div[dir='auto']"
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
            
            # Extract messages
            for i, element in enumerate(message_elements):
                try:
                    content = element.text.strip()
                    if content and len(content) > 5:  # Filter out empty/short elements
                        
                        # Determine role (user/assistant) based on element properties
                        role = "assistant"  # Default assumption
                        if "user" in element.get_attribute("class").lower():
                            role = "user"
                        
                        message = Message(
                            id=f"msg_{i}",
                            role=role,
                            content=content,
                            timestamp=datetime.now() - timedelta(minutes=i*5),
                            bot_name="Assistant"
                        )
                        
                        messages.append(message)
                        
                except Exception as e:
                    logger.warning(f"⚠️ Failed to extract message {i}: {e}")
                    continue
            
            logger.info(f"✅ Extracted {len(messages)} messages from conversation {conversation_id}")
            return messages
            
        except Exception as e:
            logger.error(f"❌ Failed to fetch messages for {conversation_id}: {e}")
            return []
    
    def _extract_conversation_id(self, href: str) -> Optional[str]:
        """Extract conversation ID from URL"""
        if not href:
            return None
        
        # Extract from various URL patterns
        patterns = [
            r'/chat/([^/\?]+)',
            r'chatId=([^&]+)',
            r'conversation[_-]([^&]+)'
        ]
        
        import re
        for pattern in patterns:
            match = re.search(pattern, href)
            if match:
                return match.group(1)
        
        return None
    
    async def search_conversations(self, query: str, filters: Optional[Dict] = None) -> List[Conversation]:
        """Search conversations (placeholder - implement based on Poe's search functionality)"""
        # For now, get all conversations and filter locally
        all_conversations = await self.get_conversations(limit=100)
        
        # Simple text search
        matching = []
        for conv in all_conversations:
            if query.lower() in conv.title.lower():
                matching.append(conv)
        
        return matching
    
    def disconnect(self):
        """Close browser connection"""
        if self.driver:
            self.driver.quit()
            self.driver = None
            self.is_connected = False
            logger.info("🔌 Disconnected from Poe")

# Factory function for easy instantiation
def create_poe_client(token: str, headless: bool = False) -> PoeApiClient:
    """Create a configured Poe API client"""
    config = PoeApiConfig(