import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from typing import List

class PoeApiClient:
    def __init__(self, token: str = None):
        self.token = token
        self.driver = None
        self._setup_browser()

    def _setup_browser(self):
        chrome_options = Options()
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_experimental_option('excludeSwitches', ['enable-automation'])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        self.driver = webdriver.Chrome(
            service=webdriver.chrome.service.Service(ChromeDriverManager().install()),
            options=chrome_options
        )
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        self.driver.get("https://poe.com")
        # User must log in manually if not already
        time.sleep(5)

    def get_conversations(self, limit: int = 50) -> List[dict]:
        """
        Use Selenium to extract conversation list from Poe.com UI.
        Returns a list of dicts with id, title, bot, and last message preview.
        """
        self.driver.get("https://poe.com")
        time.sleep(2)
        conversations = []
        try:
            # Wait for conversation list to load
            WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, '[data-testid="chat-list-item"]'))
            )
            chat_items = self.driver.find_elements(By.CSS_SELECTOR, '[data-testid="chat-list-item"]')
            for item in chat_items[:limit]:
                try:
                    title = item.text.split('\n')[0]
                    conv_id = item.get_attribute('href').split('/')[-1] if item.get_attribute('href') else None
                    bot = item.text.split('\n')[1] if '\n' in item.text else "Unknown"
                    conversations.append({
                        'id': conv_id,
                        'title': title,
                        'bot': bot,
                        'preview': item.text
                    })
                except Exception:
                    continue
        except Exception as e:
            print(f"❌ Failed to extract conversations: {e}")
        return conversations

    def get_conversation_messages(self, conversation_id: str) -> List[dict]:
        """
        Use Selenium to extract all messages from a given conversation.
        Returns a list of dicts with role, content, and timestamp if available.
        """
        url = f"https://poe.com/chat/{conversation_id}"
        self.driver.get(url)
        time.sleep(2)
        messages = []
        try:
            WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, '[data-testid*="message"]'))
            )
            msg_elems = self.driver.find_elements(By.CSS_SELECTOR, '[data-testid*="message"]')
            for elem in msg_elems:
                try:
                    role = "assistant" if "bot" in elem.get_attribute("class").lower() else "user"
                    content = elem.text
                    messages.append({
                        'role': role,
                        'content': content
                    })
                except Exception:
                    continue
        except Exception as e:
            print(f"❌ Failed to extract messages: {e}")
        return messages

    def close(self):
        if self.driver:
            self.driver.quit()
