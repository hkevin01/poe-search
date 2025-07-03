#!/usr/bin/env python3
"""
Token refresh utility for Poe.com API access.

This script helps you obtain and refresh Poe.com authentication tokens.
"""

import json
import os
import sys
from pathlib import Path
from typing import Dict, Optional


def get_manual_tokens() -> Dict[str, str]:
    """Get tokens manually from user input."""
    print("="*60)
    print("POE.COM TOKEN REFRESH")
    print("="*60)
    print()
    print("To get fresh tokens, follow these steps:")
    print()
    print("1. Open https://poe.com in your browser")
    print("2. Log in to your account")
    print("3. Open Developer Tools (F12)")
    print("4. Go to 'Application' > 'Storage' > 'Cookies' > 'https://poe.com'")
    print("5. Find and copy the following cookie values:")
    print()
    
    tokens = {}
    
    # Get p-b token
    print("Enter the 'p-b' cookie value:")
    tokens['p-b'] = input("p-b: ").strip()
    
    # Get p-lat token
    print("\nEnter the 'p-lat' cookie value:")
    tokens['p-lat'] = input("p-lat: ").strip()
    
    # Get formkey
    print("\nTo get the formkey:")
    print("6. Go to 'Network' tab in Developer Tools")
    print("7. Refresh the page or interact with Poe")
    print("8. Look for GraphQL requests")
    print("9. In request headers, find 'Poe-Formkey'")
    print("\nEnter the 'Poe-Formkey' value:")
    tokens['formkey'] = input("formkey: ").strip()
    
    return tokens


def try_browser_cookies() -> Optional[Dict[str, str]]:
    """Try to extract tokens from browser cookies automatically."""
    try:
        import browser_cookie3
        print("Attempting to extract cookies from browsers...")
        
        browsers = [
            ('chrome', browser_cookie3.chrome),
            ('firefox', browser_cookie3.firefox),
            ('edge', browser_cookie3.edge),
        ]
        
        for browser_name, browser_func in browsers:
            try:
                print(f"Checking {browser_name}...")
                cookies = browser_func(domain_name='poe.com')
                cookie_dict = {cookie.name: cookie.value for cookie in cookies}
                
                if 'p-b' in cookie_dict and 'p-lat' in cookie_dict:
                    print(f"Found tokens in {browser_name}!")
                    
                    # We still need formkey, which requires network inspection
                    print("Found p-b and p-lat tokens automatically.")
                    print("Still need formkey - checking network requests...")
                    
                    return {
                        'p-b': cookie_dict['p-b'],
                        'p-lat': cookie_dict['p-lat'],
                        'formkey': ''  # Will need manual input
                    }
                    
            except Exception as e:
                print(f"Could not extract from {browser_name}: {e}")
                continue
                
    except ImportError:
        print("browser_cookie3 not installed.")
        print("Install with: pip install browser-cookie3")
        return None
    
    return None


def validate_tokens(tokens: Dict[str, str]) -> bool:
    """Validate token format and completeness."""
    required_keys = ['p-b', 'p-lat', 'formkey']
    
    for key in required_keys:
        if key not in tokens or not tokens[key]:
            print(f"Missing or empty token: {key}")
            return False
        
        if len(tokens[key]) < 10:
            print(f"Token {key} seems too short (less than 10 characters)")
            return False
    
    return True


def save_tokens(tokens: Dict[str, str], config_path: Path) -> bool:
    """Save tokens to configuration file."""
    try:
        # Ensure config directory exists
        config_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Backup existing file
        if config_path.exists():
            backup_path = config_path.with_suffix('.json.backup')
            config_path.rename(backup_path)
            print(f"Backed up existing tokens to {backup_path}")
        
        # Save new tokens
        with open(config_path, 'w') as f:
            json.dump(tokens, f, indent=2)
        
        print(f"Tokens saved to {config_path}")
        return True
        
    except Exception as e:
        print(f"Failed to save tokens: {e}")
        return False


def test_tokens(tokens: Dict[str, str]) -> bool:
    """Test if tokens work with the API."""
    try:
        # Add current directory to path to import our modules
        current_dir = Path(__file__).parent
        src_dir = current_dir / "src"
        if src_dir.exists():
            sys.path.insert(0, str(src_dir))
        
        from poe_search.api.client import PoeAPIClient
        
        print("Testing tokens with API...")
        client = PoeAPIClient(token=tokens)
        
        if client.client is None:
            print("Failed to initialize API client with new tokens")
            return False
        
        # Try to get bots
        bots = client.get_bots()
        if isinstance(bots, dict) and len(bots) > 0:
            # Check if we got real bots (not just mock)
            real_bot_indicators = ['claude', 'gpt', 'gemini']
            has_real_bots = any(
                any(indicator in bot_id.lower() for indicator in real_bot_indicators)
                for bot_id in bots.keys()
            )
            
            if has_real_bots:
                print("✅ Tokens are working! Got real bot data.")
                print(f"Available bots: {list(bots.keys())[:5]}")
                return True
            else:
                print("⚠️  API client initialized but may be using mock data")
                print("This could indicate token issues or API rate limiting")
                return False
        else:
            print("❌ Could not retrieve bots with new tokens")
            return False
            
    except Exception as e:
        print(f"Error testing tokens: {e}")
        return False


def main():
    """Main token refresh workflow."""
    print("Poe.com Token Refresh Utility")
    print("="*40)
    
    # Determine config file path
    config_paths = [
        Path("config/poe_tokens.json"),
        Path("src/config/poe_tokens.json"),
        Path.home() / ".poe-search" / "poe_tokens.json"
    ]
    
    config_path = None
    for path in config_paths:
        if path.exists() or path.parent.exists():
            config_path = path
            break
    
    if config_path is None:
        config_path = config_paths[0]  # Default to first option
    
    print(f"Token file location: {config_path}")
    print()
    
    # Try automatic extraction first
    tokens = try_browser_cookies()
    
    if tokens and tokens.get('p-b') and tokens.get('p-lat'):
        print("Found some tokens automatically!")
        
        # Still need formkey manually
        if not tokens.get('formkey'):
            print("\nStill need formkey manually:")
            formkey = input("Enter formkey from network requests: ").strip()
            tokens['formkey'] = formkey
    else:
        # Get tokens manually
        tokens = get_manual_tokens()
    
    print("\n" + "="*40)
    print("VALIDATING TOKENS")
    print("="*40)
    
    if not validate_tokens(tokens):
        print("❌ Token validation failed!")
        return 1
    
    print("✅ Token format validation passed")
    
    # Save tokens
    if save_tokens(tokens, config_path):
        print("✅ Tokens saved successfully")
    else:
        print("❌ Failed to save tokens")
        return 1
    
    # Test tokens
    print("\n" + "="*40)
    print("TESTING TOKENS")
    print("="*40)
    
    if test_tokens(tokens):
        print("✅ Token test passed! Your tokens are working.")
    else:
        print("⚠️  Token test failed or returned mock data.")
        print("This might be due to:")
        print("- Invalid or expired tokens")
        print("- Rate limiting")
        print("- Network issues")
        print("- API changes")
    
    print("\n" + "="*60)
    print("TOKEN REFRESH COMPLETE")
    print("="*60)
    print("Your tokens have been updated. You can now:")
    print("1. Run the test suite: pytest tests/api/")
    print("2. Use the GUI: python -m poe_search.gui")
    print("3. Use the CLI: python -m poe_search.cli")
    print("="*60)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
