import json
import logging
import os
import sqlite3
import subprocess
import time
from datetime import datetime, timedelta
from pathlib import Path

from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
from playwright.sync_api import sync_playwright

try:
    import browser_cookie3
except ImportError:
    import sys
    print("\nERROR: The 'browser-cookie3' module is required for automatic Poe.com login.")
    print("Install it with: pip install browser-cookie3\n")
    sys.exit(1)

logger = logging.getLogger(__name__)

SECRETS_PATH = Path(__file__).parent.parent.parent / 'secrets.json'
SESSION_PATH = Path(__file__).parent.parent.parent / 'session.json'

REQUIRED_COOKIES = ["p-b", "p-lat", "formkey", "cf_clearance"]
REQUIRED_HEADERS = ["poe-formkey", "poe-tchannel", "poe-tag-id"]

POE_LOGIN_URL = "https://poe.com/login"
POE_CHATS_URL = "https://poe.com/chats"


def load_secrets():
    """Load secrets from file."""
    if SECRETS_PATH.exists():
        try:
            with open(SECRETS_PATH, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.warning(f"Failed to load secrets: {e}")
    return {}


def save_secrets(data):
    """Save secrets to file."""
    try:
        SECRETS_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(SECRETS_PATH, 'w') as f:
            json.dump(data, f, indent=2)
        logger.info("Secrets saved successfully")
    except Exception as e:
        logger.error(f"Failed to save secrets: {e}")


def load_session():
    """Load session data from file."""
    if SESSION_PATH.exists():
        try:
            with open(SESSION_PATH, 'r') as f:
                session_data = json.load(f)
                
            # Check if session is still valid (not expired)
            if is_session_valid(session_data):
                logger.info("Valid session found")
                return session_data
            else:
                logger.info("Session expired, will re-login")
                return None
        except Exception as e:
            logger.warning(f"Failed to load session: {e}")
    return None


def save_session(session_data):
    """Save session data to file."""
    try:
        SESSION_PATH.parent.mkdir(parents=True, exist_ok=True)
        
        # Add expiration time (7 days from now)
        session_data['expires_at'] = (datetime.now() + timedelta(days=7)).isoformat()
        
        with open(SESSION_PATH, 'w') as f:
            json.dump(session_data, f, indent=2)
        logger.info("Session saved successfully")
    except Exception as e:
        logger.error(f"Failed to save session: {e}")


def is_session_valid(session_data):
    """Check if session data is still valid."""
    try:
        expires_at = session_data.get('expires_at')
        if not expires_at:
            return False
            
        expiration_time = datetime.fromisoformat(expires_at)
        return datetime.now() < expiration_time
    except Exception:
        return False


def get_credentials():
    """Get user credentials for Poe.com login."""
    secrets = load_secrets()
    if 'username' in secrets and 'password' in secrets:
        return secrets['username'], secrets['password']
    
    # Prompt user for credentials
    print("\n=== Poe.com Login ===")
    print("Please enter your Poe.com credentials.")
    print("Note: For Google login, use your Google email and password.")
    print("These will be saved securely for future use.")
    print()
    
    username = input('Poe.com Email/Username: ').strip()
    password = input('Poe.com Password: ').strip()
    
    if username and password:
        secrets['username'] = username
        secrets['password'] = password
        save_secrets(secrets)
        return username, password
    else:
        raise ValueError("Username and password are required")


def get_browser_tokens(headless=True, use_google_auth=True):
    """
    Use Playwright to automate login and extract Poe.com cookies.
    - First, check if already logged in (look for a user element)
    - If not, try Google auth or standard login
    - If login form is not found, log error and abort
    """
    import asyncio
    import base64
    
    logger.info("Starting browser-based authentication...")
    
    def run_playwright():
        with sync_playwright() as p:
            # Launch browser with security and extension best practices
            browser = p.chromium.launch(
                headless=headless,
                args=[
                    '--no-sandbox',
                    '--disable-dev-shm-usage',
                    '--disable-extensions-except',
                    '--disable-extensions',
                    '--disable-plugins',
                    '--disable-background-timer-throttling',
                    '--disable-backgrounding-occluded-windows',
                    '--disable-component-extensions-with-background-pages',
                    '--disable-default-apps',
                    '--disable-features=TranslateUI',
                    '--disable-ipc-flooding-protection',
                    '--disable-renderer-backgrounding',
                    '--disable-sync',
                    '--metrics-recording-only',
                    '--no-first-run',
                    '--safebrowsing-disable-auto-update',
                    '--disable-component-update'
                ]
            )
            context = browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            )
            page = context.new_page()
            try:
                logger.info("Navigating to Poe.com login page...")
                page.goto(POE_LOGIN_URL, timeout=30000)
                page.wait_for_load_state('networkidle', timeout=15000)
                
                # Check if already logged in (look for chat list or user avatar)
                try:
                    # Example: look for chat list or user menu
                    if page.query_selector('a[href^="/chat/"]') or page.query_selector('img[alt*="avatar"]'):
                        logger.info("Already logged in to Poe.com, extracting cookies...")
                        cookies = context.cookies()
                        return {cookie['name']: cookie['value'] for cookie in cookies if cookie['domain'].endswith('poe.com')}
                except Exception as e:
                    logger.info(f"Not already logged in: {e}")
                
                # Try Google authentication if enabled
                if use_google_auth:
                    try:
                        logger.info("Attempting Google authentication...")
                        google_btn = page.wait_for_selector('button:has-text("Continue with Google")', timeout=7000)
                        google_btn.click()
                        page.wait_for_load_state('networkidle', timeout=10000)
                        logger.info("Found Google login button, clicking...")
                        # Wait for Google login page
                        page.wait_for_selector('input[type="email"]', timeout=10000)
                        logger.info("Redirected to Google login page")
                        # (You can add autofill here if desired)
                        # If you want to automate, fill email and password here
                        # Otherwise, let user complete login manually
                        # Wait for login to complete or timeout
                        page.wait_for_selector('a[href^="/chat/"]', timeout=20000)
                        logger.info("Google login successful, extracting cookies...")
                        cookies = context.cookies()
                        return {cookie['name']: cookie['value'] for cookie in cookies if cookie['domain'].endswith('poe.com')}
                    except PlaywrightTimeoutError as e:
                        logger.error(f"Google login failed: {e}")
                        # Fall back to standard login
                        logger.info("Falling back to standard login...")
                # Try standard login
                try:
                    # Check for login form
                    email_input = page.query_selector('input[name="email"]')
                    if not email_input:
                        logger.error("Login form not found. Cannot proceed with login automation.")
                        return None
                    logger.info("Standard login form found. Please complete login manually if needed.")
                    # Wait for user to complete login (or autofill if desired)
                    page.wait_for_selector('a[href^="/chat/"]', timeout=20000)
                    logger.info("Standard login successful, extracting cookies...")
                    cookies = context.cookies()
                    return {cookie['name']: cookie['value'] for cookie in cookies if cookie['domain'].endswith('poe.com')}
                except PlaywrightTimeoutError as e:
                    logger.error(f"Standard login failed: {e}")
                    return None
            except Exception as e:
                logger.error(f"Authentication failed: {e}")
                # Save a screenshot for debugging
                try:
                    page.screenshot(path="playwright_login_debug.png")
                    logger.info("Debug screenshot saved as playwright_login_debug.png")
                except Exception:
                    pass
                return None
            finally:
                context.close()
                browser.close()
    
    return run_playwright()


def handle_google_login(page, username, password):
    """Handle Google authentication flow."""
    try:
        # Look for "Continue with Google" button
        google_button = page.locator('button:has-text("Continue with Google"), button:has-text("Google")')
        if google_button.is_visible():
            logger.info("Found Google login button, clicking...")
            google_button.click()
            time.sleep(3)
            
            # Wait for Google login page
            page.wait_for_url("**/accounts.google.com/**", timeout=30000)
            logger.info("Redirected to Google login page")
            
            # Fill Google credentials
            page.fill('input[type="email"]', username)
            page.click('button:has-text("Next")')
            time.sleep(2)
            
            # Handle password page
            page.wait_for_selector('input[type="password"]', timeout=10000)
            page.fill('input[type="password"]', password)
            page.click('button:has-text("Next")')
            
            # Handle 2FA if present
            time.sleep(3)
            if page.is_visible('input[type="tel"], input[name="totp"]'):
                logger.info("2FA detected, please enter your code...")
                totp_code = input("Enter your Google Authenticator code: ").strip()
                if totp_code:
                    page.fill('input[type="tel"], input[name="totp"]', totp_code)
                    page.click('button:has-text("Next")')
            
            # Wait for redirect back to Poe
            page.wait_for_url("**/poe.com/**", timeout=30000)
            logger.info("Successfully authenticated with Google")
            
        else:
            logger.warning("Google login button not found, falling back to standard login")
            handle_standard_login(page, username, password)
            
    except Exception as e:
        logger.error(f"Google login failed: {e}")
        logger.info("Falling back to standard login...")
        handle_standard_login(page, username, password)


def handle_standard_login(page, username, password):
    """Handle standard email/password login flow."""
    try:
        # Wait for login form
        page.wait_for_selector('input[name="email"]', timeout=20000)
        logger.info("Found email input field")
        
        # Fill email
        page.fill('input[name="email"]', username)
        page.click('button:has-text("Go")')
        time.sleep(2)
        
        # Wait for password input
        page.wait_for_selector('input[name="password"]', timeout=20000)
        logger.info("Found password input field")
        
        # Fill password
        page.fill('input[name="password"]', password)
        page.keyboard.press('Enter')
        
        # Wait for redirect
        page.wait_for_url("**/chats", timeout=30000)
        logger.info("Successfully authenticated with email/password")
        
    except Exception as e:
        logger.error(f"Standard login failed: {e}")
        raise


def verify_login_success(page):
    """Verify that login was successful."""
    try:
        # Navigate to chats page
        page.goto(POE_CHATS_URL, wait_until='networkidle')
        time.sleep(3)
        
        # Check if we're on the chats page and not redirected to login
        if "/chats" in page.url and not page.is_visible('input[name="email"]'):
            logger.info("Login verification successful")
            return True
        else:
            logger.warning("Login verification failed - still on login page")
            return False
            
    except Exception as e:
        logger.error(f"Login verification error: {e}")
        return False


def extract_tokens(context):
    """Extract all required tokens and cookies from browser context."""
    try:
        # Extract cookies
        cookies = {c['name']: c['value'] for c in context.cookies()}
        
        # Extract formkey from cookies or page
        formkey = cookies.get('formkey', '')
        
        tokens = {
            'p-b': cookies.get('p-b', ''),
            'p-lat': cookies.get('p-lat', ''),
            'formkey': formkey,
            'cf_clearance': cookies.get('cf_clearance', ''),
        }
        
        # Validate required tokens
        missing_tokens = [name for name, value in tokens.items() if not value]
        if missing_tokens:
            logger.warning(f"Missing tokens: {missing_tokens}")
        
        logger.info(f"Extracted tokens: {list(tokens.keys())}")
        return tokens
        
    except Exception as e:
        logger.error(f"Failed to extract tokens: {e}")
        raise


def extract_cookies_from_all_browsers():
    """
    Use browser_cookie3 to extract Poe.com cookies from all supported browsers.
    Returns a dict of cookies if found, else None.
    """
    import http.cookiejar
    import logging
    logger = logging.getLogger(__name__)
    
    browsers = [
        browser_cookie3.chrome,
        browser_cookie3.chromium,
        browser_cookie3.firefox,
        browser_cookie3.edge,
        browser_cookie3.opera,
        browser_cookie3.brave,
    ]
    
    for browser_func in browsers:
        try:
            cj = browser_func(domain_name="poe.com")
            cookies = {c.name: c.value for c in cj if c.domain.endswith("poe.com")}
            if cookies.get("p-b"):
                logger.info(f"Found p-b cookie in {browser_func.__name__}")
                return cookies
        except Exception as e:
            logger.warning(f"Failed to extract cookies from {browser_func.__name__}: {e}")
    logger.warning("No valid Poe.com cookies found in any browser.")
    return None


def extract_cookies_from_browser(_=None):
    """Extract Poe.com cookies from all browsers using browser_cookie3."""
    return extract_cookies_from_all_browsers()


def get_tokens_from_browser():
    """
    Try to extract tokens from all browser sessions using browser_cookie3.
    Returns tokens if found, None otherwise.
    """
    logger.info("Attempting to extract tokens from all browser sessions using browser_cookie3...")
    cookies = extract_cookies_from_all_browsers()
    if cookies and cookies.get('p-b'):
        logger.info("Successfully extracted tokens from browser using browser_cookie3")
        return cookies
    logger.warning("No valid tokens found in browser sessions")
    return None


def refresh_tokens_if_needed():
    """Check if tokens need refresh and refresh them if necessary. Fully automated: session -> browser -> Playwright (manual if needed)."""
    # First try to load existing session
    session_data = load_session()
    if session_data and session_data.get('tokens'):
        tokens = session_data['tokens']
        if tokens.get('p-b'):
            logger.info("Valid session found, no refresh needed")
            return tokens
    
    # Try to extract from existing browser session
    logger.info("No valid session found, trying to extract from browser...")
    browser_tokens = get_tokens_from_browser()
    if browser_tokens and browser_tokens.get('p-b'):
        logger.info("Using tokens from existing browser session")
        
        # Save the extracted tokens as a session
        session_data = {
            'tokens': browser_tokens,
            'cookies': browser_tokens,
            'login_time': datetime.now().isoformat(),
            'username': 'extracted_from_browser'
        }
        save_session(session_data)
        
        # Also save to secrets for backward compatibility
        secrets = load_secrets()
        secrets.update(browser_tokens)
        save_secrets(secrets)
        
        return browser_tokens
    
    logger.info("No valid tokens found in browser, launching Playwright for manual login...")
    # Run Playwright automation in non-headless mode for manual login
    return get_browser_tokens(headless=False, use_google_auth=True)


def clear_session():
    """Clear saved session data."""
    try:
        if SESSION_PATH.exists():
            SESSION_PATH.unlink()
            logger.info("Session data cleared")
    except Exception as e:
        logger.error(f"Failed to clear session: {e}")


def force_relogin():
    """Force a fresh login by clearing session and re-authenticating."""
    clear_session()
    return get_browser_tokens(headless=False, use_google_auth=True, force_login=True) 