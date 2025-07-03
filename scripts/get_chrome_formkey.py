#!/usr/bin/env python3
"""
Extract formkey from Chrome's current Poe.com session.

This script extracts the formkey from Chrome's live session data,
including cookies, local storage, and session storage.
"""

import logging
import os
import sqlite3
from pathlib import Path
from typing import Dict, Optional

logger = logging.getLogger(__name__)


def find_chrome_profile_paths() -> list:
    """Find Chrome profile directories on the system."""
    chrome_paths = []
    
    # Common Chrome profile locations
    possible_paths = [
        # Linux
        Path.home() / ".config" / "google-chrome" / "Default",
        Path.home() / ".config" / "google-chrome" / "Profile 1",
        Path.home() / ".config" / "chromium" / "Default",
        # Windows
        (Path.home() / "AppData" / "Local" / "Google" / "Chrome" /
         "User Data" / "Default"),
        (Path.home() / "AppData" / "Local" / "Google" / "Chrome" /
         "User Data" / "Profile 1"),
        # macOS
        (Path.home() / "Library" / "Application Support" / "Google" /
         "Chrome" / "Default"),
        (Path.home() / "Library" / "Application Support" / "Google" /
         "Chrome" / "Profile 1"),
    ]
    
    for path in possible_paths:
        if path.exists():
            chrome_paths.append(path)
    
    return chrome_paths


def extract_cookies_from_chrome(profile_path: Path) -> Dict[str, str]:
    """Extract Poe.com cookies from Chrome profile."""
    cookies_db = profile_path / "Cookies"
    
    if not cookies_db.exists():
        return {}
    
    # Make a copy to avoid locking issues
    import shutil
    import tempfile
    
    with tempfile.NamedTemporaryFile(delete=False) as temp_db:
        try:
            shutil.copy2(cookies_db, temp_db.name)
            
            conn = sqlite3.connect(temp_db.name)
            cursor = conn.cursor()
            
            # Query for poe.com cookies
            cursor.execute(
                "SELECT name, value, encrypted_value "
                "FROM cookies "
                "WHERE host_key LIKE '%poe.com%'"
            )
            
            cookies = {}
            for name, value, encrypted_value in cursor.fetchall():
                if value:
                    cookies[name] = value
                elif encrypted_value:
                    # On some systems, cookies are encrypted
                    # For now, skip encrypted cookies
                    logger.debug(f"Skipping encrypted cookie: {name}")
            
            conn.close()
            return cookies
            
        except Exception as e:
            logger.error(f"Error reading cookies: {e}")
            return {}
        finally:
            # Clean up temp file
            try:
                os.unlink(temp_db.name)
            except Exception:
                pass


def extract_local_storage_from_chrome(profile_path: Path) -> Dict[str, str]:
    """Extract local storage data for poe.com from Chrome."""
    local_storage_dir = profile_path / "Local Storage" / "leveldb"
    
    if not local_storage_dir.exists():
        return {}
    
    try:
        # Look for poe.com related storage files
        storage_data = {}
        
        for file_path in local_storage_dir.glob("*.ldb"):
            try:
                with open(file_path, 'rb') as f:
                    content = f.read()
                    
                # Look for formkey in the binary data
                content_str = content.decode('utf-8', errors='ignore')
                if ('poe.com' in content_str and
                        'formkey' in content_str.lower()):
                    # Try to extract formkey
                    import re
                    patterns = [
                        (r'formkey["\']?\s*[:=]\s*["\']'
                         r'([a-zA-Z0-9_\-+=/.]{20,})["\']'),
                        r'["\']([a-zA-Z0-9_\-+=/.]{30,})["\']'
                    ]
                    
                    for pattern in patterns:
                        matches = re.findall(pattern, content_str)
                        for match in matches:
                            if len(match) > 20:
                                storage_data['formkey'] = match
                                break
                        
                        if 'formkey' in storage_data:
                            break
                            
            except Exception as e:
                logger.debug(f"Error reading {file_path}: {e}")
                continue
        
        return storage_data
        
    except Exception as e:
        logger.error(f"Error reading local storage: {e}")
        return {}


def get_formkey_from_network_logs(profile_path: Path) -> Optional[str]:
    """Try to extract formkey from Chrome's network logs."""
    # Chrome doesn't store network logs persistently by default
    # This would require DevTools to be open with network logging enabled
    return None


def extract_from_session_storage(profile_path: Path) -> Dict[str, str]:
    """Extract session storage data for poe.com."""
    session_storage_dir = profile_path / "Session Storage"
    
    if not session_storage_dir.exists():
        return {}
    
    try:
        storage_data = {}
        
        for file_path in session_storage_dir.glob("*"):
            try:
                with open(file_path, 'rb') as f:
                    content = f.read()
                    content_str = content.decode('utf-8', errors='ignore')
                    
                    if ('poe.com' in content_str and
                            'formkey' in content_str.lower()):
                        # Extract potential formkey
                        import re
                        pattern = (r'formkey["\']?\s*[:=]\s*["\']'
                                   r'([a-zA-Z0-9_\-+=/.]{20,})["\']')
                        match = re.search(pattern, content_str, re.IGNORECASE)
                        if match:
                            storage_data['formkey'] = match.group(1)
                            break
                            
            except Exception as e:
                logger.debug(f"Error reading session storage {file_path}: {e}")
                continue
        
        return storage_data
        
    except Exception as e:
        logger.error(f"Error reading session storage: {e}")
        return {}


def get_formkey_from_chrome() -> Optional[str]:
    """Extract formkey from Chrome's current session data."""
    print("🔍 Searching Chrome profiles for Poe.com formkey...")
    
    chrome_profiles = find_chrome_profile_paths()
    
    if not chrome_profiles:
        print("❌ No Chrome profiles found")
        return None
    
    print(f"Found {len(chrome_profiles)} Chrome profile(s)")
    
    for i, profile_path in enumerate(chrome_profiles, 1):
        print(f"\n📂 Checking profile {i}: {profile_path}")
        
        # Extract cookies
        print("   • Checking cookies...")
        cookies = extract_cookies_from_chrome(profile_path)
        
        # Look for p-b and p-lat in cookies
        if 'p-b' in cookies and 'p-lat' in cookies:
            print("   ✅ Found p-b and p-lat cookies!")
            
            # Now look for formkey in storage
            print("   • Checking local storage...")
            local_storage = extract_local_storage_from_chrome(profile_path)
            
            if 'formkey' in local_storage:
                formkey = local_storage['formkey']
                print("   ✅ Found formkey in local storage!")
                return formkey
            
            print("   • Checking session storage...")
            session_storage = extract_from_session_storage(profile_path)
            
            if 'formkey' in session_storage:
                formkey = session_storage['formkey']
                print("   ✅ Found formkey in session storage!")
                return formkey
            
            print("   ⚠️ Found auth cookies but no formkey in storage")
        else:
            print("   ⚠️ No Poe.com auth cookies found")
    
    return None


def save_formkey_to_tokens(formkey: str) -> bool:
    """Save the formkey to the token file."""
    try:
        from poe_search.utils.token_manager import TokenManager
        
        manager = TokenManager()
        
        # Validate formkey first
        if not manager.validate_formkey(formkey):
            print("❌ Formkey failed validation")
            return False
        
        # Load existing tokens
        tokens = manager.load_tokens() or {}
        
        # Update formkey
        tokens['formkey'] = formkey
        
        # Save tokens
        if manager.save_tokens(tokens):
            print("✅ Formkey saved to token file!")
            return True
        else:
            print("❌ Failed to save formkey")
            return False
            
    except Exception as e:
        print(f"❌ Error saving formkey: {e}")
        return False


def main():
    """Main function to extract and save formkey from Chrome."""
    print("Chrome Formkey Extractor")
    print("=" * 40)
    print("This script extracts the formkey from Chrome's current Poe.com session.")
    print("Make sure you're logged into poe.com in Chrome before running this.\n")
    
    # Check if Chrome is running
    try:
        import psutil
        chrome_running = any('chrome' in p.name().lower() for p in psutil.process_iter(['name']))
        if chrome_running:
            print("⚠️  Chrome is currently running. For best results:")
            print("   1. Go to poe.com in Chrome")
            print("   2. Make sure you're logged in")
            print("   3. Send a message to any bot")
            print("   4. Close Chrome")
            print("   5. Run this script again")
            
            choice = input("\nContinue anyway? (y/n): ").strip().lower()
            if choice not in ['y', 'yes']:
                return
    except ImportError:
        print("Note: Install psutil for Chrome process detection: pip install psutil")
    
    # Extract formkey
    formkey = get_formkey_from_chrome()
    
    if formkey:
        print(f"\n✅ SUCCESS! Found formkey:")
        print(f"   Preview: {formkey[:20]}...")
        print(f"   Length: {len(formkey)} characters")
        
        # Ask if user wants to save it
        save = input("\nSave this formkey to token file? (y/n): ").strip().lower()
        if save in ['y', 'yes']:
            save_formkey_to_tokens(formkey)
        else:
            print(f"\nFormkey: {formkey}")
            print("You can manually add this to your token file.")
    else:
        print("\n❌ Could not find formkey in Chrome data")
        print("\nTroubleshooting:")
        print("1. Make sure you're logged into poe.com in Chrome")
        print("2. Send at least one message to any bot")
        print("3. Close Chrome completely")
        print("4. Run this script again")
        print("\nAlternatively, use the manual extraction method:")
        print("1. Open poe.com in Chrome")
        print("2. Press F12 → Network tab")
        print("3. Send a message")
        print("4. Find '/api/gql_POST' request")
        print("5. Look for 'Poe-Formkey' in request headers")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
