"""
Automated token management for Poe.com API access.

This module handles automatic token checking, validation, and refresh
on application startup.
"""

import json
import logging
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Optional, Tuple

logger = logging.getLogger(__name__)


class TokenManager:
    """Manages Poe.com authentication tokens with automatic refresh."""
    
    def __init__(self, config_dir: Optional[Path] = None):
        """Initialize the token manager.
        
        Args:
            config_dir: Directory containing token files. If None, auto-detect.
        """
        self.config_dir = config_dir or self._find_config_dir()
        self.token_file = self.config_dir / "poe_tokens.json"
        self.token_backup_dir = self.config_dir / "token_backups"
        
        # Ensure directories exist
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.token_backup_dir.mkdir(parents=True, exist_ok=True)
    
    def _find_config_dir(self) -> Path:
        """Find the configuration directory."""
        # Check for existing token files
        possible_paths = [
            Path.cwd() / "config",
            Path.cwd() / "src" / "config",
            Path(__file__).parent.parent.parent.parent / "config",
            Path.home() / ".poe-search"
        ]
        
        for path in possible_paths:
            if (path / "poe_tokens.json").exists():
                return path
                
        # Default to project config directory
        return Path.cwd() / "config"
    
    def load_tokens(self) -> Optional[Dict[str, str]]:
        """Load tokens from file.
        
        Returns:
            Dictionary of tokens or None if file doesn't exist.
        """
        if not self.token_file.exists():
            logger.warning(f"Token file not found: {self.token_file}")
            return None
            
        try:
            with open(self.token_file, 'r') as f:
                tokens = json.load(f)
            
            # Validate token structure
            required_keys = ['p-b', 'p-lat', 'formkey']
            if all(key in tokens and tokens[key] for key in required_keys):
                return tokens
            else:
                logger.warning("Token file has incomplete tokens")
                return None
                
        except Exception as e:
            logger.error(f"Error loading tokens: {e}")
            return None
    
    def save_tokens(self, tokens: Dict[str, str]) -> bool:
        """Save tokens to file with backup.
        
        Args:
            tokens: Dictionary of tokens to save.
            
        Returns:
            True if successful, False otherwise.
        """
        try:
            # Create backup if file exists
            if self.token_file.exists():
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_name = f"poe_tokens_{timestamp}.json"
                backup_file = self.token_backup_dir / backup_name
                self.token_file.rename(backup_file)
                logger.info(f"Backed up existing tokens to {backup_file}")
            
            # Save new tokens
            with open(self.token_file, 'w') as f:
                json.dump(tokens, f, indent=2)
            
            logger.info(f"Tokens saved to {self.token_file}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving tokens: {e}")
            return False
    
    def get_token_age(self) -> Optional[timedelta]:
        """Get the age of the current token file.
        
        Returns:
            Age of token file or None if file doesn't exist.
        """
        if not self.token_file.exists():
            return None
            
        try:
            mtime = datetime.fromtimestamp(self.token_file.stat().st_mtime)
            return datetime.now() - mtime
        except Exception as e:
            logger.error(f"Error getting token age: {e}")
            return None
    
    def are_tokens_fresh(self, max_age_hours: int = 36) -> bool:
        """Check if tokens are fresh enough to use.
        
        Args:
            max_age_hours: Maximum age in hours before tokens are stale.
            
        Returns:
            True if tokens are fresh, False otherwise.
        """
        age = self.get_token_age()
        if age is None:
            return False
            
        return age.total_seconds() < (max_age_hours * 3600)
    
    def test_tokens(self, tokens: Dict[str, str]) -> bool:
        """Test if tokens work with the API.
        
        Args:
            tokens: Dictionary of tokens to test.
            
        Returns:
            True if tokens work, False otherwise.
        """
        try:
            from poe_search.api.client import PoeAPIClient
            
            client = PoeAPIClient(token=tokens)
            if client.client is None:
                return False
            
            # Try to get bots
            bots = client.get_bots()
            if isinstance(bots, dict) and len(bots) > 0:
                # Check if we got real bots (not mock data)
                real_bot_indicators = ['claude', 'gpt', 'gemini', 'sage']
                has_real_bots = any(
                    any(indicator in bot_id.lower()
                        for indicator in real_bot_indicators)
                    for bot_id in bots.keys()
                )
                return has_real_bots
            
            return False
            
        except Exception as e:
            logger.error(f"Error testing tokens: {e}")
            return False
    
    def try_browser_cookies(self) -> Optional[Dict[str, str]]:
        """Try to extract tokens from browser cookies automatically.
        
        Returns:
            Dictionary with p-b and p-lat tokens, or None if failed.
        """
        try:
            import browser_cookie3
            
            browsers = [
                ('chrome', browser_cookie3.chrome),
                ('firefox', browser_cookie3.firefox),
                ('edge', browser_cookie3.edge),
            ]
            
            for browser_name, browser_func in browsers:
                try:
                    cookies = browser_func(domain_name='poe.com')
                    cookie_dict = {
                        cookie.name: cookie.value for cookie in cookies
                    }
                    
                    if 'p-b' in cookie_dict and 'p-lat' in cookie_dict:
                        logger.info(f"Found tokens in {browser_name}")
                        return {
                            'p-b': cookie_dict['p-b'],
                            'p-lat': cookie_dict['p-lat'],
                            'formkey': ''  # Still needs manual input
                        }
                        
                except Exception as e:
                    logger.debug(f"Could not extract from {browser_name}: {e}")
                    continue
                    
        except ImportError:
            msg = "browser_cookie3 not installed - cannot auto-extract cookies"
            logger.warning(msg)
            return None
        
        return None
    
    def prompt_for_formkey(self) -> str:
        """Prompt user for formkey input.
        
        Returns:
            Formkey string entered by user.
        """
        print("\n" + "="*60)
        print("FORMKEY REQUIRED")
        print("="*60)
        print("The formkey could not be extracted automatically.")
        print("Please follow these steps to get it:")
        print()
        print("1. Open https://poe.com in your browser")
        print("2. Open Developer Tools (F12)")
        print("3. Go to 'Network' tab")
        print("4. Refresh the page or send a message")
        print("5. Look for GraphQL requests")
        print("6. In request headers, find 'Poe-Formkey'")
        print()
        return input("Enter the 'Poe-Formkey' value: ").strip()
    
    def interactive_refresh(self) -> bool:
        """Perform interactive token refresh with user prompts.
        
        Returns:
            True if tokens were successfully refreshed, False otherwise.
        """
        print("\n" + "="*60)
        print("POE.COM TOKEN REFRESH")
        print("="*60)
        
        # Try browser cookies first
        tokens = self.try_browser_cookies()
        
        if tokens and tokens.get('p-b') and tokens.get('p-lat'):
            print("✅ Found p-b and p-lat tokens automatically!")
            
            # Still need formkey
            formkey = self.prompt_for_formkey()
            tokens['formkey'] = formkey
            
        else:
            print("Could not extract tokens automatically.")
            print("Please get tokens manually:")
            print()
            print("1. Open https://poe.com in your browser")
            print("2. Log in to your account")
            print("3. Open Developer Tools (F12)")
            print("4. Go to 'Application' > 'Storage' > 'Cookies'")
            print("5. Select 'https://poe.com'")
            print()
            
            tokens = {}
            tokens['p-b'] = input("Enter 'p-b' cookie value: ").strip()
            tokens['p-lat'] = input("Enter 'p-lat' cookie value: ").strip()
            tokens['formkey'] = self.prompt_for_formkey()
        
        # Validate tokens
        required_keys = ['p-b', 'p-lat', 'formkey']
        for key in required_keys:
            if not tokens.get(key) or len(tokens[key]) < 10:
                print(f"❌ Invalid {key} token (too short or empty)")
                return False
        
        # Test tokens
        print("\nTesting tokens...")
        if self.test_tokens(tokens):
            print("✅ Tokens are working!")
            
            # Save tokens
            if self.save_tokens(tokens):
                print("✅ Tokens saved successfully!")
                return True
            else:
                print("❌ Failed to save tokens")
                return False
        else:
            print("❌ Tokens are not working")
            return False
    
    def ensure_fresh_tokens(
        self, max_age_hours: int = 36, interactive: bool = True
    ) -> Tuple[bool, Optional[Dict[str, str]]]:
        """Ensure tokens are fresh and working.
        
        Args:
            max_age_hours: Maximum age in hours before tokens are stale.
            interactive: Whether to prompt user for refresh if needed.
            
        Returns:
            Tuple of (success, tokens). Success is True if fresh tokens
            are available.
        """
        # Load existing tokens
        tokens = self.load_tokens()
        
        # Check if tokens exist and are fresh
        if tokens and self.are_tokens_fresh(max_age_hours):
            # Test if they work
            if self.test_tokens(tokens):
                logger.info("Existing tokens are fresh and working")
                return True, tokens
            else:
                logger.warning("Existing tokens are fresh but not working")
        
        # Tokens are missing, stale, or not working
        if tokens:
            age = self.get_token_age()
            if age:
                hours = age.total_seconds() / 3600
                msg = f"Tokens are {hours:.1f}h old (max: {max_age_hours}h)"
                logger.warning(msg)
            else:
                logger.warning("Cannot determine token age")
        else:
            logger.warning("No tokens found")
        
        if not interactive:
            msg = "Token refresh required but running in non-interactive mode"
            logger.error(msg)
            return False, None
        
        # Try to refresh tokens interactively
        print("\n🔄 Token refresh required...")
        if self.interactive_refresh():
            tokens = self.load_tokens()
            return True, tokens
        else:
            return False, None


def ensure_tokens_on_startup(
    interactive: bool = True, max_age_hours: int = 36
) -> Tuple[bool, Optional[Dict[str, str]]]:
    """Convenience function to ensure tokens are fresh on application startup.
    
    Args:
        interactive: Whether to prompt user for refresh if needed.
        max_age_hours: Maximum age in hours before tokens are stale.
        
    Returns:
        Tuple of (success, tokens). Success is True if fresh tokens
        are available.
    """
    manager = TokenManager()
    return manager.ensure_fresh_tokens(max_age_hours, interactive)


if __name__ == "__main__":
    # CLI mode for manual token refresh
    logging.basicConfig(level=logging.INFO)
    manager = TokenManager()
    success, tokens = manager.ensure_fresh_tokens(interactive=True)
    sys.exit(0 if success else 1)
