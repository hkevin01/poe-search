#!/usr/bin/env python3
"""Standalone test script for browser cookie extraction."""

import json
import os
import sqlite3
import tempfile
import shutil
import glob
from pathlib import Path
from datetime import datetime, timedelta

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


def extract_firefox_cookies():
    """Extract cookies from Firefox browser."""
    try:
        # Find Firefox profile directory
        firefox_profile = None
        
        # Common Firefox profile locations
        possible_paths = [
            Path.home() / ".mozilla" / "firefox" / "*.default",
            Path.home() / ".mozilla" / "firefox" / "*.default-release",
            Path.home() / "AppData" / "Roaming" / "Mozilla" / "Firefox" / "Profiles" / "*.default",
            Path.home() / "Library" / "Application Support" / "Firefox" / "Profiles" / "*.default",
        ]
        
        for pattern in possible_paths:
            if '*' in str(pattern):
                # Handle glob patterns
                matches = glob.glob(str(pattern))
                if matches:
                    firefox_profile = Path(matches[0])
                    break
            elif pattern.exists():
                firefox_profile = pattern
                break
        
        if not firefox_profile:
            print("   ❌ Firefox profile not found")
            return None
        
        cookies_db = firefox_profile / "cookies.sqlite"
        if not cookies_db.exists():
            print(f"   ❌ Firefox cookies database not found at {cookies_db}")
            return None
        
        print(f"   📁 Found Firefox profile: {firefox_profile}")
        
        # Create a temporary copy of the cookies database
        temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        temp_db.close()
        
        try:
            shutil.copy2(cookies_db, temp_db.name)
            
            # Extract cookies from the database
            conn = sqlite3.connect(temp_db.name)
            cursor = conn.cursor()
            
            # Query for Poe.com cookies
            cursor.execute("""
                SELECT name, value, host, path, expiry, isSecure, isHttpOnly
                FROM moz_cookies 
                WHERE host LIKE '%poe.com%'
                ORDER BY name
            """)
            
            cookies = {}
            for row in cursor.fetchall():
                name, value, host, path, expiry, is_secure, is_httponly = row
                cookies[name] = {
                    'value': value,
                    'host': host,
                    'path': path,
                    'expiry': expiry,
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
        print(f"   ❌ Failed to extract Firefox cookies: {e}")
        return None


def test_browser_extraction():
    """Test browser cookie extraction."""
    
    print("=== Browser Cookie Extraction Test ===\n")
    
    print("1. Testing Chrome cookie extraction...")
    chrome_cookies = extract_chrome_cookies()
    if chrome_cookies and chrome_cookies.get('p-b'):
        print(f"   ✅ Chrome extraction successful!")
        print(f"   ✅ p-b token: {chrome_cookies['p-b'][:10]}...")
    else:
        print("   ❌ Chrome extraction failed")
    
    print("\n2. Testing Firefox cookie extraction...")
    firefox_cookies = extract_firefox_cookies()
    if firefox_cookies and firefox_cookies.get('p-b'):
        print(f"   ✅ Firefox extraction successful!")
        print(f"   ✅ p-b token: {firefox_cookies['p-b'][:10]}...")
    else:
        print("   ❌ Firefox extraction failed")
    
    print("\n3. Summary:")
    if chrome_cookies and chrome_cookies.get('p-b'):
        print("   ✅ Chrome has valid Poe.com cookies")
    if firefox_cookies and firefox_cookies.get('p-b'):
        print("   ✅ Firefox has valid Poe.com cookies")
    
    if not (chrome_cookies or firefox_cookies):
        print("   ❌ No valid Poe.com cookies found in any browser")
        print("\n   💡 Make sure you are logged in to Poe.com in Chrome or Firefox")
    
    print("\n=== Test Complete ===")
    print("\nNext steps:")
    print("1. If cookies were found, you can use 'Tools → Extract from Browser' in the main app")
    print("2. If no cookies were found, make sure you're logged in to Poe.com in your browser")


if __name__ == "__main__":
    test_browser_extraction() 