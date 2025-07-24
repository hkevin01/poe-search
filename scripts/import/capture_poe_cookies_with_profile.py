#!/usr/bin/env python3
"""Script to capture Poe.com session cookies using your real Chrome/Chromium profile with Playwright."""

import json
import time
from pathlib import Path
from playwright.sync_api import sync_playwright

SECRETS_PATH = Path(__file__).parent.parent / 'secrets.json'
POE_CHATS_URL = "https://poe.com/chats"

# Update this path to your real Chrome/Chromium profile directory
# For Google Chrome: ~/.config/google-chrome/Default
# For Chromium: ~/.config/chromium/Default
USER_DATA_DIR = str(Path.home() / ".config" / "chromium" / "Default")


def save_cookies_to_secrets(cookies):
    secrets = {}
    if SECRETS_PATH.exists():
        with open(SECRETS_PATH, 'r') as f:
            try:
                secrets = json.load(f)
            except Exception:
                pass
    for c in cookies:
        secrets[c['name']] = c['value']
    with open(SECRETS_PATH, 'w') as f:
        json.dump(secrets, f, indent=2)
    print(f"[+] Saved cookies to {SECRETS_PATH}")


def main():
    print("=== Poe.com Cookie Capture (with real browser profile) ===\n")
    print(f"Launching Chromium with your real profile: {USER_DATA_DIR}")
    print("A browser window will open. Log in to Poe.com using 'Continue with Google' or any method.")
    print("Once you see your chats, return here and press Enter to save your session cookies.")
    with sync_playwright() as p:
        browser = p.chromium.launch_persistent_context(
            user_data_dir=USER_DATA_DIR,
            headless=False
        )
        page = browser.new_page()
        page.goto(POE_CHATS_URL)
        input("\n[!] Press Enter here after you have logged in and see your chats...")
        cookies = browser.cookies()
        save_cookies_to_secrets(cookies)
        browser.close()
    print("\n[+] Done! Your session cookies are now saved for API use.")

if __name__ == "__main__":
    main() 