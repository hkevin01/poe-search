#!/usr/bin/env python3
"""
Quick Poe.com Conversation Lister - Simplified (no formkey required)
"""

import time
import json
import os
import argparse
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options as ChromeOptions

def setup_browser(headless=True):
    opts = ChromeOptions()
    if headless:
        opts.add_argument("--headless")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--disable-gpu")
    opts.add_argument("--window-size=1920,1080")
    driver = webdriver.Chrome(options=opts)
    driver.implicitly_wait(10)
    return driver

def load_tokens(config_path):
    """Load p-b (required) and p-lat/formkey (optional) from JSON."""
    if not os.path.isfile(config_path):
        raise FileNotFoundError(f"Config not found: {config_path}")
    with open(config_path, 'r', encoding='utf-8') as f:
        tokens = json.load(f)
    if "p-b" not in tokens or not tokens["p-b"]:
        raise KeyError(f"Missing required token 'p-b' in {config_path}")
    # p-lat and formkey are optional
    return tokens

def set_cookies(driver, tokens):
    """Navigate to base, set cookies, then go to /chats."""
    driver.get("https://poe.com")
    time.sleep(1)

    # always set p-b
    driver.add_cookie({
        "name":   "p-b",
        "value":  tokens["p-b"],
        "domain": "poe.com",
        "path":   "/",
        "secure": True
    })
    # optional p-lat
    if tokens.get("p-lat"):
        driver.add_cookie({
            "name":   "p-lat",
            "value":  tokens["p-lat"],
            "domain": "poe.com",
            "path":   "/",
            "secure": True
        })
    # optional formkey
    if tokens.get("formkey"):
        driver.add_cookie({
            "name":   "formkey",
            "value":  tokens["formkey"],
            "domain": "poe.com",
            "path":   "/",
            "secure": True
        })

    # now load the chats page
    driver.get("https://poe.com/chats")
    time.sleep(2)

def scroll_to_bottom(driver, pause=1.0):
    """Ensure lazy-loaded chats are all loaded."""
    last_h = driver.execute_script("return document.body.scrollHeight")
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(pause)
        new_h = driver.execute_script("return document.body.scrollHeight")
        if new_h == last_h:
            break
        last_h = new_h

def extract_conversations(driver):
    """Extract chat links and titles."""
    scroll_to_bottom(driver)

    convs = []
    # Method 1: direct /chat/ links
    links = driver.find_elements(By.CSS_SELECTOR, "a[href*='/chat/']")
    for idx, a in enumerate(links, start=1):
        href = a.get_attribute("href")
        title = a.text.strip() or "(no title)"
        convs.append({
            "id":     idx,
            "title":  title[:100],
            "url":    href,
            "method": "link"
        })

    # Method 2: any chat tiles without link
    tiles = driver.find_elements(By.CSS_SELECTOR, "[data-testid^='chat']")
    for tile in tiles:
        text = tile.text.strip()
        if len(text) < 5:
            continue
        try:
            href = tile.find_element(By.TAG_NAME, "a").get_attribute("href")
        except:
            href = None
        convs.append({
            "id":     len(convs) + 1,
            "title":  text[:100],
            "url":    href or "(no-url)",
            "method": "tile"
        })

    # dedupe by URL
    seen = set()
    unique = []
    for c in convs:
        if c["url"] in seen:
            continue
        seen.add(c["url"])
        unique.append(c)
    return unique

def print_and_save(convs):
    if not convs:
        print("❌ No conversations found.")
        return
    print(f"\n✅ Found {len(convs)} conversations:\n" + "="*60)
    for c in convs:
        print(f"{c['id']:3d}. {c['title']}")
        print(f"     URL: {c['url']}   (via {c['method']})")
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    fname = f"conversations_{stamp}.json"
    with open(fname, 'w', encoding='utf-8') as f:
        json.dump(convs, f, indent=2, ensure_ascii=False)
    print(f"\n💾 Saved to {fname}")

def main():
    p = argparse.ArgumentParser(description="Quick Poe Conversation Lister")
    p.add_argument(
        "--config", "-c",
        default=os.path.expanduser("~/Projects/poe-search/config/poe_tokens.json"),
        help="Path to your poe_tokens.json"
    )
    p.add_argument(
        "--no-headless", action="store_true",
        help="Show browser window for debugging"
    )
    args = p.parse_args()

    print("🚀 Poe Conversation Lister")
    tokens = load_tokens(args.config)
    print(f"🔑 p-b token: {tokens['p-b'][:16]}…")
    driver = setup_browser(headless=not args.no_headless)

    try:
        set_cookies(driver, tokens)
        convs = extract_conversations(driver)
        print_and_save(convs)
    except Exception as e:
        print("❌ Error:", e)
        raise
    finally:
        driver.quit()

if __name__ == "__main__":
    main()