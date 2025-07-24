#!/usr/bin/env python3
"""Test script for browser cookie extraction functionality."""

import sys
import os
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

# Import the browser_tokens module directly
sys.path.insert(0, str(Path(__file__).parent.parent / "src" / "poe_search" / "utils"))
from browser_tokens import (
    extract_cookies_from_browser, get_tokens_from_browser
)


def test_browser_extraction():
    """Test browser cookie extraction."""
    
    print("=== Browser Cookie Extraction Test ===\n")
    
    print("1. Testing Chrome cookie extraction...")
    try:
        chrome_cookies = extract_cookies_from_browser("chrome")
        if chrome_cookies:
            print(f"   ✅ Chrome cookies found: {list(chrome_cookies.keys())}")
            if chrome_cookies.get('p-b'):
                print(f"   ✅ p-b token: {chrome_cookies['p-b'][:10]}...")
            else:
                print("   ❌ p-b token not found")
        else:
            print("   ❌ No Chrome cookies found")
    except Exception as e:
        print(f"   ❌ Chrome extraction failed: {e}")
    
    print("\n2. Testing Firefox cookie extraction...")
    try:
        firefox_cookies = extract_cookies_from_browser("firefox")
        if firefox_cookies:
            print(f"   ✅ Firefox cookies found: {list(firefox_cookies.keys())}")
            if firefox_cookies.get('p-b'):
                print(f"   ✅ p-b token: {firefox_cookies['p-b'][:10]}...")
            else:
                print("   ❌ p-b token not found")
        else:
            print("   ❌ No Firefox cookies found")
    except Exception as e:
        print(f"   ❌ Firefox extraction failed: {e}")
    
    print("\n3. Testing automatic browser detection...")
    try:
        tokens = get_tokens_from_browser()
        if tokens and tokens.get('p-b'):
            print(f"   ✅ Automatic extraction successful!")
            print(f"   ✅ Found cookies: {list(tokens.keys())}")
            print(f"   ✅ p-b token: {tokens['p-b'][:10]}...")
        else:
            print("   ❌ Automatic extraction failed - no valid tokens found")
    except Exception as e:
        print(f"   ❌ Automatic extraction failed: {e}")
    
    print("\n=== Test Complete ===")
    print("\nInstructions:")
    print("1. Make sure you are logged in to Poe.com in Chrome or Firefox")
    print("2. Run this test to verify cookie extraction works")
    print("3. Use 'Tools → Extract from Browser' in the main app")


if __name__ == "__main__":
    test_browser_extraction() 