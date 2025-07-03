#!/usr/bin/env python3
"""
Advanced formkey extraction utility using Playwright.

This script attempts to extract the Poe.com formkey using various methods,
with Playwright browser automation as the primary approach.
"""

import logging
from typing import Optional

logger = logging.getLogger(__name__)


def try_playwright_formkey_extraction() -> Optional[str]:
    """Try to extract formkey using Playwright browser automation.
    
    This is more reliable than cookie extraction but requires playwright.
    
    Returns:
        Formkey string if successful, None otherwise.
    """
    try:
        from playwright.sync_api import sync_playwright
        
        print("🤖 Attempting automated formkey extraction with Playwright...")
        
        with sync_playwright() as p:
            # Launch browser in headless mode
            browser = p.chromium.launch(
                headless=True,
                args=[
                    "--no-sandbox",
                    "--disable-dev-shm-usage",
                    "--disable-web-security"
                ]
            )
            
            try:
                # Create new page
                page = browser.new_page(
                    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                               "AppleWebKit/537.36 (KHTML, like Gecko) "
                               "Chrome/120.0.0.0 Safari/537.36"
                )
                
                # Navigate to Poe.com
                print("   • Loading poe.com...")
                page.goto("https://poe.com", wait_until="domcontentloaded")
                
                # Wait for page to load completely
                page.wait_for_timeout(3000)
                
                # Method 1: Look for formkey in meta tags
                print("   • Searching meta tags...")
                meta_elements = page.query_selector_all("meta")
                for meta in meta_elements:
                    name = meta.get_attribute("name")
                    if name and "formkey" in name.lower():
                        content = meta.get_attribute("content")
                        if content and len(content) > 10:
                            print("   ✅ Found formkey in meta tag!")
                            return content
                
                # Method 2: Execute JavaScript to find formkey
                print("   • Searching with JavaScript...")
                js_methods = [
                    "document.querySelector('meta[name=\"formkey\"]')?.content",
                    "document.querySelector('meta[name=\"poe-formkey\"]')"
                    "?.content",
                    "window.formkey",
                    "window.poeFormkey",
                    """
                    (() => {
                        // Look for formkey in window variables
                        for (let prop in window) {
                            if (prop.toLowerCase().includes('formkey')) {
                                return window[prop];
                            }
                        }
                        return null;
                    })()
                    """,
                    """
                    (() => {
                        // Look in localStorage
                        for (let i = 0; i < localStorage.length; i++) {
                            let key = localStorage.key(i);
                            if (key && key.toLowerCase().includes('formkey')) {
                                return localStorage.getItem(key);
                            }
                        }
                        return null;
                    })()
                    """,
                    """
                    (() => {
                        // Look in sessionStorage
                        for (let i = 0; i < sessionStorage.length; i++) {
                            let key = sessionStorage.key(i);
                            if (key && key.toLowerCase().includes('formkey')) {
                                return sessionStorage.getItem(key);
                            }
                        }
                        return null;
                    })()
                    """
                ]
                
                for i, js_code in enumerate(js_methods, 1):
                    try:
                        result = page.evaluate(js_code)
                        if result and len(str(result)) > 10:
                            print(f"   ✅ Found formkey via JS method {i}!")
                            return str(result)
                    except Exception as e:
                        logger.debug(f"JS method {i} failed: {e}")
                        continue
                
                # Method 3: Try to intercept network requests
                print("   • Setting up network interception...")
                
                captured_formkey = None
                
                def handle_request(request):
                    nonlocal captured_formkey
                    headers = request.headers
                    for header_name, header_value in headers.items():
                        if "formkey" in header_name.lower():
                            if len(header_value) > 10:
                                captured_formkey = header_value
                
                page.on("request", handle_request)
                
                # Look for input field to trigger a request
                print("   • Looking for chat input...")
                input_selectors = [
                    "textarea[placeholder*='message' i]",
                    "textarea[placeholder*='Message' i]",
                    "input[type='text']",
                    "textarea",
                    "[contenteditable='true']",
                    "[data-testid*='chat']",
                    "[data-testid*='input']"
                ]
                
                message_input = None
                for selector in input_selectors:
                    try:
                        message_input = page.query_selector(selector)
                        if message_input and message_input.is_visible():
                            print(f"   • Found input: {selector}")
                            break
                    except Exception:
                        continue
                
                if message_input:
                    try:
                        # Try to interact with the input to trigger requests
                        print("   • Interacting with input...")
                        message_input.click()
                        page.wait_for_timeout(500)
                        message_input.fill("test")
                        page.wait_for_timeout(1000)
                        
                        # Check if we captured formkey in requests
                        if captured_formkey:
                            print("   ✅ Found formkey in network requests!")
                            return captured_formkey
                            
                    except Exception as e:
                        logger.debug(f"Input interaction failed: {e}")
                
                # Method 4: Look for formkey in page source
                print("   • Searching page source...")
                try:
                    page_content = page.content()
                    import re
                    
                    formkey_patterns = [
                        r'formkey["\']?\s*[:=]\s*["\']([a-zA-Z0-9_\-+=/.]{20,})'
                        r'["\']',
                        r'poe-formkey["\']?\s*[:=]\s*["\']([a-zA-Z0-9_\-+=/.]{20,})'
                        r'["\']',
                        r'["\']formkey["\']\s*:\s*["\']([a-zA-Z0-9_\-+=/.]{20,})'
                        r'["\']',
                        r'name=["\']formkey["\'][^>]*content=["\']'
                        r'([a-zA-Z0-9_\-+=/.]{20,})["\']',
                    ]
                    
                    for pattern in formkey_patterns:
                        matches = re.findall(pattern, page_content,
                                           re.IGNORECASE)
                        for match in matches:
                            if len(match) > 10:
                                print("   ✅ Found formkey in page source!")
                                return match
                                
                except Exception as e:
                    logger.debug(f"Page source search failed: {e}")
                
                print("   ❌ No formkey found with Playwright")
                return None
                
            finally:
                browser.close()
                
    except ImportError:
        print("❌ Playwright not installed. Install with:")
        print("   pip install playwright")
        print("   playwright install chromium")
        return None
    except Exception as e:
        print(f"❌ Playwright extraction failed: {e}")
        logger.debug(f"Playwright error details: {e}")
        return None


def try_requests_formkey_extraction() -> Optional[str]:
    """Try to extract formkey using direct HTTP requests.
    
    Returns:
        Formkey string if successful, None otherwise.
    """
    try:
        import requests
        from bs4 import BeautifulSoup
        
        print("🌐 Attempting HTTP-based formkey extraction...")
        
        # Set up session with realistic headers
        session = requests.Session()
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                         'AppleWebKit/537.36 (KHTML, like Gecko) '
                         'Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        })
        
        # Get the main page
        response = session.get("https://poe.com", timeout=10)
        response.raise_for_status()
        
        # Parse HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Look for formkey in meta tags
        meta_tags = soup.find_all('meta')
        for meta in meta_tags:
            name = meta.get('name', '').lower()
            if 'formkey' in name:
                content = meta.get('content')
                if content and len(content) > 10:
                    print("   ✅ Found formkey in meta tag!")
                    return content
        
        # Look for formkey in script tags
        script_tags = soup.find_all('script')
        for script in script_tags:
            if script.string:
                script_content = script.string
                if 'formkey' in script_content.lower():
                    # Try to extract formkey from JavaScript
                    import re
                    patterns = [
                        r'formkey["\']?\s*[:=]\s*["\']([a-zA-Z0-9_\-+=/.]{20,})["\']',
                        r'poe-formkey["\']?\s*[:=]\s*["\']([a-zA-Z0-9_\-+=/.]{20,})["\']',
                        r'["\']formkey["\']\s*:\s*["\']([a-zA-Z0-9_\-+=/.]{20,})["\']',
                    ]
                    
                    for pattern in patterns:
                        match = re.search(pattern, script_content, re.IGNORECASE)
                        if match:
                            formkey = match.group(1)
                            if len(formkey) > 10:
                                print("   ✅ Found formkey in script tag!")
                                return formkey
        
        print("   ❌ Could not find formkey in HTML")
        return None
        
    except ImportError:
        print("❌ Required libraries not installed:")
        print("   pip install requests beautifulsoup4")
        return None
    except Exception as e:
        print(f"❌ HTTP extraction failed: {e}")
        return None


def extract_formkey_advanced() -> Optional[str]:
    """Try multiple advanced methods to extract formkey.
    
    Returns:
        Formkey string if successful, None otherwise.
    """
    print("🔍 Advanced Formkey Extraction")
    print("="*50)
    
    # Method 1: Playwright browser automation (most likely to work)
    formkey = try_playwright_formkey_extraction()
    if formkey:
        # Validate the formkey before returning
        from poe_search.utils.token_manager import TokenManager
        manager = TokenManager()
        if manager.validate_formkey(formkey):
            return formkey
        else:
            print("❌ Found formkey but it failed validation")
    
    # Method 2: HTTP requests with parsing
    formkey = try_requests_formkey_extraction()
    if formkey:
        # Validate the formkey before returning
        from poe_search.utils.token_manager import TokenManager
        manager = TokenManager()
        if manager.validate_formkey(formkey):
            return formkey
        else:
            print("❌ Found formkey but it failed validation")
    
    # Method 3: Browser cookies (from existing implementation)
    try:
        from poe_search.utils.token_manager import TokenManager
        manager = TokenManager()
        formkey = manager.try_extract_formkey_from_browser()
        if formkey and manager.validate_formkey(formkey):
            print("✅ Found formkey in browser cookies!")
            return formkey
    except Exception as e:
        print(f"❌ Cookie extraction failed: {e}")
    
    print("❌ All automatic extraction methods failed")
    return None


def main():
    """Main function to test formkey extraction."""
    print("Advanced Poe.com Formkey Extraction Tool (Playwright-based)")
    print("="*60)
    
    formkey = extract_formkey_advanced()
    
    if formkey:
        print(f"\n✅ SUCCESS! Found formkey:")
        print(f"   Preview: {formkey[:20]}...")
        print(f"   Length: {len(formkey)} characters")
        
        # Ask if user wants to save it
        try:
            save = input("\nSave this formkey to token file? (y/n): ").strip().lower()
            if save in ['y', 'yes']:
                from poe_search.utils.token_manager import TokenManager
                manager = TokenManager()
                
                # Load existing tokens
                tokens = manager.load_tokens() or {}
                tokens['formkey'] = formkey
                
                if manager.save_tokens(tokens):
                    print("✅ Formkey saved successfully!")
                else:
                    print("❌ Failed to save formkey")
        except Exception as e:
            print(f"Error saving formkey: {e}")
    else:
        print("\n❌ Could not extract formkey automatically")
        print("\nThis is normal - Poe.com's security makes automatic")
        print("formkey extraction difficult. You'll need to get it manually:")
        print("\nMANUAL EXTRACTION GUIDE:")
        print("1. Open https://poe.com in your browser")
        print("2. Press F12 → Network tab") 
        print("3. Clear network log (trash icon)")
        print("4. Send a message to any bot")
        print("5. Look for '/api/gql_POST' request")
        print("6. Click it → Headers → Request Headers")
        print("7. Find 'Poe-Formkey' and copy its value")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
