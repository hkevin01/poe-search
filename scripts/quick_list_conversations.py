#!/usr/bin/env python3
"""
Quick Poe.com Conversation Lister - Simplified for immediate results
"""

import time
import json
import os
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options as ChromeOptions

def setup_browser(headless=True):
    """Quick browser setup"""
    options = ChromeOptions()
    if headless:
        options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    
    driver = webdriver.Chrome(options=options)
    driver.implicitly_wait(10)
    return driver

def load_tokens():
    """Load tokens from config"""
    config_path = "/home/kevin/Projects/poe-search/config/poe_tokens.json"
    with open(config_path, 'r') as f:
        return json.load(f)

def set_cookies_and_go_to_chats(driver, tokens):
    """Set cookies and navigate to chats"""
    print("🌐 Going to poe.com and setting cookies...")
    
    # Go to poe.com
    driver.get("https://poe.com")
    time.sleep(2)
    
    # Set cookies
    driver.add_cookie({
        'name': 'p-b',
        'value': tokens['p-b'],
        'domain': '.poe.com',
        'path': '/',
        'secure': True
    })
    
    if tokens.get('p-lat'):
        driver.add_cookie({
            'name': 'p-lat', 
            'value': tokens['p-lat'],
            'domain': '.poe.com',
            'path': '/',
            'secure': True
        })
    
    # Go to chats page
    print("🔗 Navigating to /chats...")
    driver.get("https://poe.com/chats")
    time.sleep(5)
    
    return driver.current_url

def extract_conversations(driver):
    """Extract conversation data quickly"""
    print("📋 Extracting conversations...")
    
    conversations = []
    
    # Method 1: Get all chat links
    chat_links = driver.find_elements(By.CSS_SELECTOR, "a[href*='/chat/']")
    print(f"   Found {len(chat_links)} chat links")
    
    for i, link in enumerate(chat_links):
        try:
            href = link.get_attribute('href')
            text = link.text.strip()
            
            if href and text:
                conversations.append({
                    'id': i + 1,
                    'title': text[:100],
                    'url': href,
                    'method': 'direct_link'
                })
                
        except Exception as e:
            continue
    
    # Method 2: Look for text in chat containers that don't have direct links
    chat_containers = driver.find_elements(By.CSS_SELECTOR, "[data-testid*='chat']")
    print(f"   Found {len(chat_containers)} chat containers")
    
    for i, container in enumerate(chat_containers):
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
            
            if text and len(text) > 5 and len(text) < 200:
                # Check if we already have this conversation
                exists = any(conv['url'] == href for conv in conversations if href)
                
                if not exists:
                    conversations.append({
                        'id': len(conversations) + 1,
                        'title': text[:100],
                        'url': href or 'No direct URL',
                        'method': 'container_text'
                    })
                    
        except Exception as e:
            continue
    
    # Remove duplicates by URL
    seen_urls = set()
    unique_conversations = []
    
    for conv in conversations:
        if conv['url'] not in seen_urls:
            seen_urls.add(conv['url'])
            unique_conversations.append(conv)
    
    return unique_conversations

def print_results(conversations):
    """Print results clearly"""
    if not conversations:
        print("❌ No conversations extracted!")
        return
    
    print(f"\n✅ Found {len(conversations)} conversations:")
    print("=" * 80)
    
    for conv in conversations:
        print(f"{conv['id']:3d}. {conv['title']}")
        print(f"     URL: {conv['url']}")
        print(f"     Method: {conv['method']}")
        print("-" * 80)
    
    # Save to file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"conversations_{timestamp}.json"
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(conversations, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Saved to: {filename}")

def main():
    """Main execution"""
    print("🚀 Quick Poe Conversation Extractor")
    print("=" * 40)
    
    # Load tokens
    tokens = load_tokens()
    print(f"🔑 Loaded p-b token: {tokens['p-b'][:15]}...")
    
    # Setup browser
    driver = setup_browser(headless=True)
    
    try:
        # Authenticate and navigate
        current_url = set_cookies_and_go_to_chats(driver, tokens)
        print(f"📍 Current URL: {current_url}")
        
        # Extract conversations
        conversations = extract_conversations(driver)
        
        # Print results
        print_results(conversations)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        driver.quit()

if __name__ == "__main__":
    main()