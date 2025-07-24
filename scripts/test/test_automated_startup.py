#!/usr/bin/env python3
"""Test script for automated startup with browser extraction."""

import sys
import os
import json
import sqlite3
import tempfile
import shutil
import glob
from pathlib import Path

REQUIRED_COOKIES = ["p-b", "p-lat", "formkey", "cf_clearance"]


def extract_chrome_cookies():
    """Extract cookies from Chrome browser."""
    try:
        # Find Chrome profile directory
        chrome_profile = None
        
        # Common Chrome profile locations
        possible_paths = [
            Path.home() / ".config" / "google-chrome" / "Default",
            Path.home() / ".config" / "google-chrome" / "Profile 1",
            Path.home() / ".config" / "chromium" / "Default",
            Path.home() / "AppData" / "Local" / "Google" / "Chrome" / "User Data" / "Default",
            Path.home() / "Library" / "Application Support" / "Google" / "Chrome" / "Default",
        ]
        
        for path in possible_paths:
            if path.exists():
                chrome_profile = path
                break
        
        if not chrome_profile:
            print("   ❌ Chrome profile not found")
            return None
        
        cookies_db = chrome_profile / "Cookies"
        if not cookies_db.exists():
            print(f"   ❌ Chrome cookies database not found at {cookies_db}")
            return None
        
        print(f"   📁 Found Chrome profile: {chrome_profile}")
        
        # Create a temporary copy of the cookies database (Chrome locks the original)
        temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        temp_db.close()
        
        try:
            shutil.copy2(cookies_db, temp_db.name)
            
            # Extract cookies from the database
            conn = sqlite3.connect(temp_db.name)
            cursor = conn.cursor()
            
            # Query for Poe.com cookies
            cursor.execute("""
                SELECT name, value, host_key, path, expires_utc, is_secure, is_httponly
                FROM cookies 
                WHERE host_key LIKE '%poe.com%'
                ORDER BY name
            """)
            
            cookies = {}
            for row in cursor.fetchall():
                name, value, host_key, path, expires_utc, is_secure, is_httponly = row
                cookies[name] = {
                    'value': value,
                    'host_key': host_key,
                    'path': path,
                    'expires_utc': expires_utc,
                    'is_secure': bool(is_secure),
                    'is_httponly': bool(is_httponly)
                }
            
            conn.close()
            
            # Extract just the values for the required cookies
            extracted_cookies = {}
            for cookie_name in REQUIRED_COOKIES:
                if cookie_name in cookies:
                    extracted_cookies[cookie_name] = cookies[cookie_name]['value']
                    print(f"   ✅ Found cookie: {cookie_name}")
                else:
                    print(f"   ❌ Missing cookie: {cookie_name}")
                    # Set empty string for missing cookies
                    extracted_cookies[cookie_name] = ""
            
            return extracted_cookies
            
        finally:
            # Clean up temporary file
            try:
                os.unlink(temp_db.name)
            except:
                pass
                
    except Exception as e:
        print(f"   ❌ Failed to extract Chrome cookies: {e}")
        return None


def get_tokens_from_browser():
    """Try to extract tokens from existing browser sessions."""
    print("   🔍 Attempting to extract tokens from existing browser sessions...")
    
    # Try Chrome first
    cookies = extract_chrome_cookies()
    if cookies and cookies.get('p-b'):
        print("   ✅ Successfully extracted tokens from Chrome")
        return cookies
    
    print("   ❌ No valid tokens found in browser sessions")
    return None


def test_automated_startup():
    """Test the automated startup workflow."""
    
    print("=== Automated Startup Test ===\n")
    
    print("1. Testing browser token extraction...")
    browser_tokens = get_tokens_from_browser()
    if browser_tokens and browser_tokens.get('p-b'):
        print(f"   ✅ Browser extraction successful!")
        print(f"   ✅ Found cookies: {list(browser_tokens.keys())}")
        print(f"   ✅ p-b token: {browser_tokens['p-b'][:10]}...")
        
        # Simulate what the app would do
        print("\n2. Simulating app startup workflow...")
        print("   📝 App would save these tokens to session.json")
        print("   📝 App would initialize API client with these tokens")
        print("   📝 App would test connection to Poe.com")
        print("   📝 App would start syncing conversations")
        
        return True
    else:
        print("   ❌ Browser extraction failed")
        print("   💡 Make sure you are logged in to Poe.com in Chrome or Firefox")
        return False


def main():
    """Main test function."""
    success = test_automated_startup()
    
    print("\n=== Test Results ===")
    if success:
        print("✅ Automated startup should work correctly!")
        print("\nNext steps:")
        print("1. Run the main app: python -m poe_search.gui")
        print("2. The app should automatically extract tokens from your browser")
        print("3. No manual login should be required")
        print("4. If needed, use: Tools → Extract from Browser")
    else:
        print("❌ Automated startup needs manual intervention")
        print("\nTroubleshooting:")
        print("1. Make sure you are logged in to Poe.com in Chrome or Firefox")
        print("2. Try the manual extraction: Tools → Extract from Browser")
        print("3. Or use the manual login: Tools → Re-login to Poe")


if __name__ == "__main__":
    main() 