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
        return {
            'role': self.role,
            'content': self.content,
            'timestamp': self.timestamp.isoformat(),
            'bot_name': self.bot_name,
            'message_id': self.message_id
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Message':
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

    def __init__(
        self,
        token: str,
        lat_token: Optional[str] = None,
        formkey_token: Optional[str] = None,
        headless: bool = True,
        browser: str = "chrome"
    ):
        """Initialize the Poe client with real browser automation"""
        if not SELENIUM_AVAILABLE:
            raise ImportError("Selenium is required for Poe integration. Install with: pip install selenium")

        self.token = token
        self.lat_token = lat_token
        self.formkey_token = formkey_token
        self.headless = headless
        self.browser = browser
        self.driver = None
        self.conversations: List[Conversation] = []

        # Rate limiting
        self.last_request_time = 0.0
        self.min_request_interval = 1.5  # seconds

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
                options.add_argument("--no-sandbox")
                options.add_argument("--disable-dev-shm-usage")
                options.add_argument("--disable-gpu")
                options.add_argument("--window-size=1920,1080")
                options.add_argument("--disable-blink-features=AutomationControlled")
                options.add_experimental_option("excludeSwitches", ["enable-automation"])
                options.add_experimental_option('useAutomationExtension', False)
                options.add_argument(
                    "--user-agent=Mozilla/5.0 (X11; Linux x86_64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/120.0.0.0 Safari/537.36"
                )
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

            # Hide webdriver flag in Chrome
            if self.browser.lower() == "chrome":
                self.driver.execute_script(
                    "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
                )

            self.driver.implicitly_wait(15)
            self.driver.set_page_load_timeout(30)
            logger.info(f"Successfully initialized {self.browser} driver")
            return self.driver

        except Exception as e:
            logger.error(f"Failed to setup web driver: {e}")
            raise

    def _rate_limit(self):
        """Implement rate limiting between requests"""
        now = time.time()
        elapsed = now - self.last_request_time
        if elapsed < self.min_request_interval:
            to_sleep = self.min_request_interval - elapsed
            logger.debug(f"Rate limiting: sleeping for {to_sleep:.2f}s")
            time.sleep(to_sleep)
        self.last_request_time = time.time()

    def _ensure_formkey(self):
        """Scrape `formkey` from poe.com landing page (once)."""
        html = self.driver.page_source
        m = re.search(r'"formkey":"([A-Za-z0-9_-]+)"', html)
        if m:
            self.formkey_token = m.group(1)
            logger.info("Auto-extracted Poe formkey")
        else:
            logger.warning("Could not auto-extract formkey; consider supplying it manually")

    def _scroll_to_bottom(self, pause: float = 1.0, max_loops: int = 5):
        """Scroll to bottom to lazy-load all conversations."""
        last_h = self.driver.execute_script("return document.body.scrollHeight")
        for _ in range(max_loops):
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(pause)
            new_h = self.driver.execute_script("return document.body.scrollHeight")
            if new_h == last_h:
                break
            last_h = new_h

    def connect(self, progress_callback: Optional[Callable[[str, int], None]] = None) -> bool:
        """Enhanced connection method with proven authentication"""
        self._setup_driver()
        self._rate_limit()

        try:
            if progress_callback:
                progress_callback("Connecting to Poe.com...", 10)
            logger.info("Connecting to Poe.com...")
            self.driver.get("https://poe.com")
            time.sleep(2)

            if not self.formkey_token:
                # Attempt to auto-extract formkey before setting cookies
                self._ensure_formkey()

            # Set cookies
            logger.info("Setting authentication cookies...")
            self.driver.add_cookie({
                'name': 'p-b',
                'value': self.token,
                'domain': '.poe.com',
                'path': '/',
                'secure': True
            })
            if self.lat_token:
                self.driver.add_cookie({
                    'name': 'p-lat',
                    'value': self.lat_token,
                    'domain': '.poe.com',
                    'path': '/',
                    'secure': True
                })
            if self.formkey_token:
                self.driver.add_cookie({
                    'name': 'formkey',
                    'value': self.formkey_token,
                    'domain': '.poe.com',
                    'path': '/',
                    'secure': True
                })

            if progress_callback:
                progress_callback("Verifying authentication...", 50)
            logger.info("Navigating to chats page...")
            self.driver.get("https://poe.com/chats")
            time.sleep(5)

            # Check for auth indicators
            auth_indicators = [
                "a[href*='/chat/']",
                "[data-testid*='chat']",
                "main[role='main']",
            ]
            authenticated = False
            for sel in auth_indicators:
                if self.driver.find_elements(By.CSS_SELECTOR, sel):
                    authenticated = True
                    logger.info(f"Auth indicator found: {sel}")
                    break

            if not authenticated:
                logger.error("Authentication failed: login page detected")
                if progress_callback:
                    progress_callback("Authentication failed", 0)
                return False

            logger.info("✅ Successfully authenticated with Poe.com")
            if progress_callback:
                progress_callback("Authentication successful!", 100)
            return True

        except Exception as e:
            logger.error(f"❌ Failed to connect to Poe.com: {e}")
            if progress_callback:
                progress_callback(f"Connection failed: {e}", 0)
            return False

    def get_conversation_list(
        self,
        limit: int = 50,
        progress_callback: Optional[Callable[[str, int], None]] = None
    ) -> List[Dict[str, Any]]:
        """Enhanced conversation list retrieval with proven methods"""
        if not self.driver:
            if not self.connect(progress_callback):
                raise Exception("Failed to connect to Poe.com")

        self._rate_limit()
        if progress_callback:
            progress_callback("Fetching conversation list...", 20)
        logger.info(f"Fetching conversation list (limit={limit})...")

        # Ensure on chats page
        if "/chats" not in self.driver.current_url:
            self.driver.get("https://poe.com/chats")
            time.sleep(3)

        # lazy-load all entries
        self._scroll_to_bottom()

        conversations: List[Dict[str, Any]] = []

        # Method 1: direct links
        selectors = [
            "a[href*='/chat/']",
            "a[href*='/conversation/']",
            "[data-testid*='chat'] a",
            "[data-testid*='conversation'] a"
        ]
        for sel in selectors:
            elements = self.driver.find_elements(By.CSS_SELECTOR, sel)
            for elem in elements:
                href = elem.get_attribute('href')
                if not href or not ('/chat/' in href or '/conversation/' in href):
                    continue
                title = (elem.text.strip()
                         or elem.get_attribute('title')
                         or elem.get_attribute('aria-label')
                         or "Untitled Conversation")
                if not any(c['url'] == href for c in conversations):
                    conversations.append({
                        'url': href,
                        'title': title[:100],
                        'id': self._extract_conversation_id(href),
                        'method': f'direct-{sel}'
                    })

        # Method 2: container detection
        container_selectors = [
            "[data-testid*='chat']",
            "[class*='chat']",
            "[class*='Chat']",
            "[class*='conversation']"
        ]
        for sel in container_selectors:
            elements = self.driver.find_elements(By.CSS_SELECTOR, sel)
            for elem in elements:
                links = elem.find_elements(By.TAG_NAME, 'a')
                href = None
                for link in links:
                    link_href = link.get_attribute('href')
                    if link_href and '/chat/' in link_href:
                        href = link_href
                        break
                if href and not any(c['url'] == href for c in conversations):
                    title = elem.text.strip()[:100] or "Container Conversation"
                    conversations.append({
                        'url': href,
                        'title': title,
                        'id': self._extract_conversation_id(href),
                        'method': f'container-{sel}'
                    })

        # Method 3: source analysis fallback
        page_src = self.driver.page_source
        patterns = [r'href="([^"]*\/chat\/[^"]*)"', r'"url":"([^"]*\/chat\/[^"]*)"', r'\/chat\/([A-Za-z0-9_-]+)']
        for pat in patterns:
            matches = re.findall(pat, page_src)
            for m in matches:
                if m.startswith("http"):
                    url = m
                else:
                    url = f"https://poe.com{m}"
                if not any(c['url'] == url for c in conversations):
                    conversations.append({
                        'url': url,
                        'title': url.split("/")[-1],
                        'id': self._extract_conversation_id(url),
                        'method': f'source-{pat}'
                    })

        # Dedupe & limit & sort
        seen = set()
        unique = []
        for c in conversations:
            if c['url'] not in seen:
                seen.add(c['url'])
                unique.append(c)
                if len(unique) >= limit:
                    break
        unique.sort(key=lambda x: x['title'].lower())

        if progress_callback:
            progress_callback("Conversation list complete!", 100)
        logger.info(f"✅ Found {len(unique)} unique conversations")
        return unique

    def _extract_conversation_id(self, url: str) -> str:
        m = re.search(r'/(?:chat|conversation)/([A-Za-z0-9_-]+)', url)
        return m.group(1) if m else url.split("/")[-1]

    def get_conversation_details(
        self,
        conversation_url: str,
        progress_callback: Optional[Callable[[str, int], None]] = None
    ) -> Optional[Conversation]:
        """Enhanced conversation detail extraction with better message parsing"""
        if not self.driver:
            if not self.connect():
                return None
        self._rate_limit()

        try:
            if progress_callback:
                progress_callback("Loading conversation...", 10)
            logger.info(f"Fetching conversation: {conversation_url}")
            self.driver.get(conversation_url)
            time.sleep(4)

            if progress_callback:
                progress_callback("Analyzing conversation structure...", 30)
            try:
                WebDriverWait(self.driver, 20).until(
                    EC.any_of(
                        EC.presence_of_element_located((By.CSS_SELECTOR, "[class*='message']")),
                        EC.presence_of_element_located((By.CSS_SELECTOR, "[data-testid*='message']")),
                        EC.presence_of_element_located((By.CSS_SELECTOR, "article"))
                    )
                )
            except TimeoutException:
                logger.warning("Conversation content didn't load in time")

            # Title detection
            title = "Untitled Conversation"
            for sel in ["h1","[class*='title']","[data-testid*='title']","title"]:
                try:
                    elem = self.driver.find_element(By.CSS_SELECTOR, sel)
                    txt = elem.text.strip()
                    if txt and "Poe" not in txt:
                        title = txt
                        break
                except:
                    continue
            if title == "Untitled Conversation":
                page_title = self.driver.title
                if page_title and "Poe" not in page_title:
                    title = page_title

            # Bot name detection
            bot_name = "Assistant"
            for pat in ["[class*='bot']","[data-testid*='bot']"]:
                elems = self.driver.find_elements(By.CSS_SELECTOR, pat)
                for el in elems:
                    txt = el.text.strip()
                    if 3 < len(txt) < 50:
                        bot_name = txt
                        break
                if bot_name != "Assistant":
                    break

            if progress_callback:
                progress_callback("Extracting messages...", 70)

            # Message extraction
            messages: List[Message] = []
            # Try standard selectors
            elems = self.driver.find_elements(By.CSS_SELECTOR, "[class*='message'],[data-testid*='message']")
            for i, elem in enumerate(elems):
                txt = elem.text.strip()
                if not txt or len(txt) < 5:
                    continue
                # Heuristic role
                role = "assistant"
                cls_html = elem.get_attribute('class') + elem.get_attribute('outerHTML')
                if any(u in cls_html.lower() for u in ["user","you","me","question"]):
                    role = "user"
                elif any(a in cls_html.lower() for a in ["bot","assistant","ai","response"]):
                    role = "assistant"
                # Alternate if ambiguous
                if i % 2 == 0:
                    role = "user"
                # Timestamp estimate
                ts = datetime.now() - timedelta(minutes=len(elems) - i)
                msg = Message(
                    role=role,
                    content=txt,
                    timestamp=ts,
                    bot_name=bot_name if role=="assistant" else None,
                    message_id=f"msg_{i}_{self._extract_conversation_id(conversation_url)}"
                )
                messages.append(msg)

            if not messages:
                logger.warning("No messages extracted")
                return None

            conv = Conversation(
                id=self._extract_conversation_id(conversation_url),
                title=title,
                bot=bot_name,
                messages=messages,
                created_at=datetime.now() - timedelta(days=1),
                updated_at=datetime.now(),
                url=conversation_url
            )
            if progress_callback:
                progress_callback("Conversation extracted!", 100)
            logger.info(f"✅ Extracted conversation '{title}'")
            return conv

        except Exception as e:
            logger.error(f"❌ Failed to get conversation details: {e}")
            if progress_callback:
                progress_callback(f"Failed: {e}", 0)
            return None

    def get_conversations(
        self,
        limit: int = 10,
        progress_callback: Optional[Callable[[str, int], None]] = None
    ) -> List[Conversation]:
        """Enhanced conversation retrieval with progress tracking"""
        logger.info(f"Getting {limit} conversations from Poe.com...")
        if progress_callback:
            progress_callback("Getting conversation list...", 5)
        conv_list = self.get_conversation_list(limit, progress_callback)
        if not conv_list:
            logger.warning("No conversations found")
            if progress_callback:
                progress_callback("No conversations found", 100)
            return []
        result: List[Conversation] = []
        total = min(len(conv_list), limit)
        for i, info in enumerate(conv_list[:limit]):
            if progress_callback:
                pct = 20 + int((i / total) * 70)
                progress_callback(f"Processing {i+1}/{total}", pct)
            conv = self.get_conversation_details(info['url'])
            if conv:
                result.append(conv)
            if i < total - 1:
                time.sleep(1)
        if progress_callback:
            progress_callback(f"Complete! Retrieved {len(result)} conversations", 100)
        logger.info(f"✅ Successfully retrieved {len(result)} conversations")
        self.conversations = result
        return result

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
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def _create_sample_conversations(self, count: int = 10) -> List[Conversation]:
        """Fallback sample conversations if real fetch fails."""
        # ... existing sample logic unchanged ...
        return []
        
__all__ = ['PoeAPIClient', 'Conversation', 'Message']