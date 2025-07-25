#!/usr/bin/env python3
"""
Poe.com Conversation Lister - Updated for /chats endpoint
Loads token from config and lists conversations from https://poe.com/chats
"""

import time
import json
import os
from datetime import datetime
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

class PoeConversationLister:
    def __init__(self, config_path=None, headless=True):
        self.config_path = config_path or "/home/kevin/Projects/poe-search/config/poe_tokens.json"
        self.headless = headless
        self.driver = None
        self.tokens = self.load_tokens()
        
    def load_tokens(self):
        """Load tokens from config file"""
        try:
            with open(self.config_path, 'r') as f:
                tokens = json.load(f)
            print(f"✅ Loaded tokens from: {self.config_path}")
            print(f"🔑 p-b token: {tokens.get('p-b', 'Not found')[:15]}...")
            if tokens.get('p-lat'):
                print(f"🔑 p-lat token: {tokens.get('p-lat', 'Not found')[:15]}...")
            return tokens
        except Exception as e:
            print(f"❌ Failed to load tokens from {self.config_path}: {e}")
            return {}
        
    def setup_browser(self):
        """Setup Chrome browser optimized for Poe.com"""
        options = ChromeOptions()
        if self.headless:
            options.add_argument("--headless")
        
        # Essential options for modern web apps
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        # Realistic user agent for Linux
        options.add_argument("--user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        
        # Disable unnecessary features to speed up loading
        prefs = {
            "profile.default_content_setting_values.notifications": 2,
            "profile.default_content_settings.popups": 0,
            "profile.managed_default_content_settings.images": 1
        }
        options.add_experimental_option("prefs", prefs)
        
        self.driver = webdriver.Chrome(options=options)
        
        # Remove automation indicators
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        # Longer timeout for slow loading
        self.driver.implicitly_wait(15)
        
    def set_auth_cookies(self):
        """Set authentication cookies for Poe.com"""
        if not self.tokens.get('p-b'):
            print("❌ No p-b token found in config!")
            return False
            
        print("🔑 Setting authentication cookies...")
        
        # Navigate to poe.com first to establish domain
        self.driver.get("https://poe.com")
        time.sleep(2)
        
        # Cookies to set
        cookies_to_set = [
            {
                'name': 'p-b',
                'value': self.tokens['p-b'],
                'domain': '.poe.com',
                'path': '/',
                'secure': True
            }
        ]
        
        # Add p-lat if available
        if self.tokens.get('p-lat'):
            cookies_to_set.append({
                'name': 'p-lat', 
                'value': self.tokens['p-lat'],
                'domain': '.poe.com',
                'path': '/',
                'secure': True
            })
        
        # Set each cookie with error handling
        for cookie in cookies_to_set:
            cookie_name = cookie['name']
            cookie_value = cookie['value']
            
            # Try multiple methods to set cookie
            success = False
            
            # Method 1: Standard selenium
            try:
                self.driver.add_cookie(cookie)
                print(f"   ✅ Set {cookie_name} via selenium")
                success = True
            except Exception as e:
                print(f"   ⚠️ Selenium failed for {cookie_name}: {e}")
                
                # Method 2: JavaScript
                try:
                    js_cookie = f"document.cookie = '{cookie_name}={cookie_value}; path=/; domain=.poe.com; secure';"
                    self.driver.execute_script(js_cookie)
                    print(f"   ✅ Set {cookie_name} via JavaScript")
                    success = True
                except Exception as e2:
                    print(f"   ❌ JavaScript failed for {cookie_name}: {e2}")
            
            if not success:
                print(f"   ❌ Failed to set {cookie_name} cookie!")
                return False
        
        return True
    
    def navigate_to_chats(self):
        """Navigate to the chats page and verify access"""
        print("🌐 Navigating to Poe.com chats page...")
        
        try:
            # Go directly to chats page
            self.driver.get("https://poe.com/chats")
            time.sleep(5)  # Give extra time for page load
            
            current_url = self.driver.current_url
            page_title = self.driver.title
            
            print(f"📍 Current URL: {current_url}")
            print(f"📄 Page title: {page_title}")
            
            # Check if we're redirected to login
            if 'login' in current_url.lower():
                print("❌ Redirected to login page - authentication failed")
                return False
            
            # Check if we're on the chats page
            if '/chats' in current_url or 'chats' in page_title.lower():
                print("✅ Successfully accessed chats page")
                return True
            
            # Check for any content that suggests we're logged in
            time.sleep(3)  # Wait for dynamic content to load
            
            # Look for page content indicators
            page_indicators = [
                "main",
                "[role='main']", 
                "nav",
                "[role='navigation']",
                "[data-testid]",
                ".chat",
                ".conversation",
                "a[href*='/chat/']"
            ]
            
            found_content = False
            for indicator in page_indicators:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, indicator)
                    if elements:
                        print(f"   ✅ Found content: {indicator} ({len(elements)} elements)")
                        found_content = True
                        break
                except:
                    continue
            
            if found_content:
                print("✅ Page loaded with content - likely authenticated")
                return True
            else:
                print("❌ No recognizable content found - may not be authenticated")
                return False
                
        except Exception as e:
            print(f"❌ Failed to navigate to chats: {e}")
            return False
    
    def find_conversations_on_chats_page(self):
        """Find conversations specifically on the /chats page"""
        print("\n🔍 Searching for conversations on chats page...")
        conversations = []
        
        # Wait for page to fully load
        time.sleep(5)
        
        # Method 1: Look for conversation links with various selectors
        print("📋 Method 1: Direct conversation link search...")
        
        link_selectors = [
            "a[href*='/chat/']",
            "a[href*='/conversation/']",
            "[data-testid*='chat'] a",
            "[data-testid*='conversation'] a",
            "[class*='chat'] a",
            "[class*='conversation'] a",
            "a[data-testid*='chat']",
            "a[data-testid*='conversation']"
        ]
        
        for selector in link_selectors:
            try:
                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                print(f"   Selector '{selector}': {len(elements)} elements")
                
                for elem in elements:
                    try:
                        href = elem.get_attribute('href')
                        if not href or not ('/chat/' in href or '/conversation/' in href):
                            continue
                            
                        # Get conversation title/text
                        title = (elem.text.strip() or 
                                elem.get_attribute('title') or 
                                elem.get_attribute('aria-label') or 
                                'Untitled Conversation')
                        
                        conversations.append({
                            'title': title[:100],
                            'url': href,
                            'method': f'link-{selector}',
                            'element_tag': elem.tag_name,
                            'found_at': datetime.now().isoformat()
                        })
                        
                    except Exception as e:
                        continue
                        
            except Exception as e:
                print(f"   Error with selector {selector}: {e}")
        
        # Method 2: Look for conversation containers/cards
        print("📋 Method 2: Conversation container search...")
        
        container_selectors = [
            "[data-testid*='chat']",
            "[data-testid*='conversation']",
            "[class*='chat']",
            "[class*='conversation']",
            "[class*='Chat']",
            "[class*='Conversation']",
            "div[role='button']",
            "article",
            ".card",
            "[class*='card']"
        ]
        
        for selector in container_selectors:
            try:
                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                print(f"   Container '{selector}': {len(elements)} elements")
                
                for elem in elements:
                    try:
                        # Look for links within the container
                        links = elem.find_elements(By.TAG_NAME, 'a')
                        for link in links:
                            href = link.get_attribute('href')
                            if href and '/chat/' in href:
                                # Use container text as title
                                title = elem.text.strip()[:100] or 'Container Conversation'
                                
                                conversations.append({
                                    'title': title,
                                    'url': href,
                                    'method': f'container-{selector}',
                                    'container_tag': elem.tag_name,
                                    'found_at': datetime.now().isoformat()
                                })
                                break  # One link per container
                    except:
                        continue
                        
            except Exception as e:
                print(f"   Error with container {selector}: {e}")
        
        # Method 3: Scroll and load more conversations
        print("📋 Method 3: Scrolling to load more conversations...")
        
        try:
            # Get initial count
            initial_count = len(conversations)
            
            # Scroll down a few times to trigger lazy loading
            for i in range(3):
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)
                
                # Look for new links after scroll
                new_links = self.driver.find_elements(By.CSS_SELECTOR, "a[href*='/chat/']")
                print(f"   After scroll {i+1}: found {len(new_links)} total chat links")
            
            # Collect any new conversations found after scrolling
            all_chat_links = self.driver.find_elements(By.CSS_SELECTOR, "a[href*='/chat/']")
            
            for link in all_chat_links:
                try:
                    href = link.get_attribute('href')
                    title = link.text.strip() or 'Scrolled Conversation'
                    
                    # Check if we already have this URL
                    if not any(conv['url'] == href for conv in conversations):
                        conversations.append({
                            'title': title[:100],
                            'url': href,
                            'method': 'scroll-discovery',
                            'found_at': datetime.now().isoformat()
                        })
                        
                except:
                    continue
            
            new_count = len(conversations)
            print(f"   Found {new_count - initial_count} additional conversations via scrolling")
            
        except Exception as e:
            print(f"   Scrolling method failed: {e}")
        
        # Method 4: Page source analysis for missed conversations
        print("📋 Method 4: Page source analysis...")
        
        try:
            page_source = self.driver.page_source
            
            import re
            
            # Look for chat URLs in page source
            patterns = [
                r'href="([^"]*\/chat\/[^"]*)"',
                r'"url":"([^"]*\/chat\/[^"]*)"',
                r'\/chat\/([a-zA-Z0-9_-]+)',
                r'"chatId":"([^"]+)"'
            ]
            
            for pattern in patterns:
                matches = re.findall(pattern, page_source)
                print(f"   Pattern '{pattern}': {len(matches)} matches")
                
                for match in matches[:10]:  # Limit to avoid spam
                    if pattern.startswith(r'\/chat\/') or pattern.endswith('"'):
                        # This is just an ID
                        url = f"https://poe.com/chat/{match}"
                        title = f"Source ID: {match}"
                    else:
                        # This is a full URL
                        url = match if match.startswith('http') else f"https://poe.com{match}"
                        title = f"Source URL: {match.split('/')[-1]}"
                    
                    # Check if we already have this URL
                    if not any(conv['url'] == url for conv in conversations):
                        conversations.append({
                            'title': title,
                            'url': url,
                            'method': f'source-{pattern[:20]}',
                            'found_at': datetime.now().isoformat()
                        })
            
        except Exception as e:
            print(f"   Page source analysis failed: {e}")
        
        # Remove duplicates and sort
        seen_urls = set()
        unique_conversations = []
        
        for conv in conversations:
            if conv['url'] not in seen_urls:
                seen_urls.add(conv['url'])
                unique_conversations.append(conv)
        
        # Sort by title for better organization
        unique_conversations.sort(key=lambda x: x['title'].lower())
        
        print(f"🎯 Found {len(unique_conversations)} unique conversations")
        return unique_conversations
    
    def list_conversations(self):
        """Main method to discover conversations"""
        try:
            print("🚀 Starting Poe.com conversation discovery...")
            print(f"📁 Config: {self.config_path}")
            
            if not self.tokens:
                print("❌ No tokens loaded")
                return []
            
            # Setup browser
            print("🌐 Setting up browser...")
            self.setup_browser()
            
            # Set authentication cookies
            if not self.set_auth_cookies():
                print("❌ Failed to set authentication cookies")
                return []
            
            # Navigate to chats page
            if not self.navigate_to_chats():
                print("❌ Failed to access chats page")
                # Save debug info
                try:
                    with open('debug_chats_access.html', 'w', encoding='utf-8') as f:
                        f.write(self.driver.page_source)
                    print("   📄 Page source saved to debug_chats_access.html")
                except:
                    pass
                return []
            
            # Find conversations on the chats page
            conversations = self.find_conversations_on_chats_page()
            
            return conversations
            
        except Exception as e:
            print(f"❌ Error during conversation discovery: {e}")
            import traceback
            traceback.print_exc()
            return []
        
        finally:
            if self.driver:
                print("🔄 Closing browser...")
                self.driver.quit()
    
    def print_conversations(self, conversations):
        """Print conversations in organized format"""
        if not conversations:
            print("\n❌ No conversations found!")
            print("\nTroubleshooting steps:")
            print("1. Verify your tokens are current and valid")
            print("2. Check if you can manually access https://poe.com/chats")
            print("3. Look at debug file: debug_chats_access.html")
            print("4. Try with headless=False to see the browser")
            print("5. Your tokens might have expired - get fresh ones")
            return
        
        print(f"\n✅ Discovered {len(conversations)} conversations:")
        print("=" * 120)
        
        # Group by discovery method for analysis
        methods = {}
        for conv in conversations:
            method = conv['method']
            if method not in methods:
                methods[method] = []
            methods[method].append(conv)
        
        print(f"📊 Discovery method breakdown:")
        for method, convs in methods.items():
            print(f"   {method}: {len(convs)} conversations")
        print()
        
        # Print all conversations
        for i, conv in enumerate(conversations, 1):
            print(f"{i:3d}. {conv['title'][:80]}")
            print(f"     URL: {conv['url']}")
            print(f"     Method: {conv['method']}")
            print(f"     Found: {conv.get('found_at', 'Unknown')[:19]}")
            print("-" * 120)
        
        # Save results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"poe_conversations_{timestamp}.json"
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(conversations, f, indent=2, ensure_ascii=False)
            print(f"\n💾 Results saved to: {filename}")
            
            # Also save as CSV for easy viewing
            csv_filename = f"poe_conversations_{timestamp}.csv"
            with open(csv_filename, 'w', encoding='utf-8') as f:
                f.write("Title,URL,Method,Found At\n")
                for conv in conversations:
                    title = conv['title'].replace('"', '""')  # Escape quotes
                    f.write(f'"{title}","{conv["url"]}","{conv["method"]}","{conv.get("found_at", "")}"\n')
            print(f"💾 CSV export saved to: {csv_filename}")
            
        except Exception as e:
            print(f"❌ Failed to save results: {e}")

def main():
    """Main function"""
    print("🔍 Poe.com Conversation Lister (Updated for /chats)")
    print("=" * 60)
    
    # Check config file
    default_config = "/home/kevin/Projects/poe-search/config/poe_tokens.json"
    
    if not os.path.exists(default_config):
        print(f"❌ Config file not found: {default_config}")
        config_path = input("Enter path to poe_tokens.json: ").strip()
        if not config_path or not os.path.exists(config_path):
            print("❌ Invalid config path")
            return
    else:
        config_path = default_config
    
    # Browser visibility option
    show_browser = input("Show browser window? (y/N): ").strip().lower()
    headless = show_browser != 'y'
    
    print(f"\n🔧 Configuration:")
    print(f"   Config: {config_path}")
    print(f"   Target: https://poe.com/chats")
    print(f"   Headless: {headless}")
    
    # Run the lister
    lister = PoeConversationLister(config_path, headless=headless)
    conversations = lister.list_conversations()
    lister.print_conversations(conversations)

if __name__ == "__main__":
    main()