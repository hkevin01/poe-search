#!/usr/bin/env python3
"""
Poe Credential Helper
====================

This script helps you safely manage your Poe.com credentials for the Poe Search application.

Usage:
    python scripts/manage_credentials.py --extract    # Guide for manual extraction
    python scripts/manage_credentials.py --validate   # Test current credentials
    python scripts/manage_credentials.py --update     # Update credentials interactively
"""

import json
import os
import sys
from pathlib import Path
from typing import Dict, Optional
import asyncio

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

try:
    from poe_search.api.client import PoeAPIClient
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Make sure you've installed the package: pip install -e .")
    sys.exit(1)


class CredentialManager:
    """Manages Poe.com credentials safely and securely."""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.config_dir = self.project_root / "config"
        self.credentials_file = self.config_dir / "poe_tokens.json"
        
        # Ensure config directory exists
        self.config_dir.mkdir(exist_ok=True)
    
    def load_credentials(self) -> Optional[Dict[str, str]]:
        """Load existing credentials from file."""
        if not self.credentials_file.exists():
            return None
        
        try:
            with open(self.credentials_file, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            print(f"❌ Error loading credentials: {e}")
            return None
    
    def save_credentials(self, credentials: Dict[str, str]) -> bool:
        """Save credentials to file securely."""
        try:
            # Set restrictive permissions before writing
            with open(self.credentials_file, 'w') as f:
                json.dump(credentials, f, indent=2)
            
            # Set file permissions to be readable only by owner
            os.chmod(self.credentials_file, 0o600)
            return True
        except IOError as e:
            print(f"❌ Error saving credentials: {e}")
            return False
    
    def show_extraction_guide(self):
        """Show step-by-step guide for extracting credentials."""
        print("🔍 How to Extract Your Poe.com Credentials")
        print("=" * 50)
        print()
        print("1️⃣ **Open Poe.com in your browser**")
        print("   • Go to https://poe.com")
        print("   • Make sure you're logged in")
        print()
        print("2️⃣ **Open Developer Tools**")
        print("   • Press F12 (or Ctrl+Shift+I on Linux/Windows)")
        print("   • Or right-click → Inspect Element")
        print()
        print("3️⃣ **Navigate to Cookies**")
        print("   • Go to 'Application' tab (Chrome/Edge)")
        print("   • Or 'Storage' tab (Firefox)")
        print("   • Expand 'Cookies' → Click 'https://poe.com'")
        print()
        print("4️⃣ **Copy Required Values**")
        print("   • Find 'p-b' cookie → Copy its Value")
        print("   • Find 'p-lat' cookie → Copy its Value (if present)")
        print()
        print("5️⃣ **Get Form Key**")
        print("   • Go to 'Network' tab in DevTools")
        print("   • Refresh the page or interact with Poe")
        print("   • Look for requests to 'gql_POST'")
        print("   • In request headers, find 'poe-formkey'")
        print()
        print("📝 **Example Values:**")
        print("   p-b: AG58MLIXFnbOh98QAv4YHA%3D%3D")
        print("   formkey: 1a2b3c4d5e6f7g8h9i0j...")
        print()
        print("⚠️  **Security Note:**")
        print("   • Keep these values private")
        print("   • Don't share them or commit to version control")
        print("   • They expire periodically and need updating")
    
    async def validate_credentials(self, credentials: Dict[str, str]) -> bool:
        """Test if credentials work with Poe.com."""
        print("🔄 Testing credentials...")
        
        try:
            # Create a temporary client to test
            client = PoeAPIClient()
            
            # Try to fetch user info
            user_info = await client.get_user_info()
            if user_info:
                print("✅ Credentials are valid!")
                print(f"   User: {user_info.get('displayName', 'Unknown')}")
                return True
            else:
                print("❌ Credentials are invalid or expired")
                return False
                
        except Exception as e:
            print(f"❌ Error testing credentials: {e}")
            return False
    
    def interactive_update(self):
        """Interactive credential update process."""
        print("🔧 Interactive Credential Update")
        print("=" * 40)
        print()
        
        # Load existing credentials
        current_creds = self.load_credentials() or {}
        
        print("📋 Current credentials:")
        for key, value in current_creds.items():
            masked_value = value[:8] + "..." if len(value) > 8 else value
            print(f"   {key}: {masked_value}")
        print()
        
        # Get new credentials
        new_creds = {}
        
        print("Enter new credentials (press Enter to keep existing):")
        
        # p-b cookie
        current_pb = current_creds.get('p-b', '')
        pb_prompt = f"p-b cookie [{current_pb[:8]}...]: " if current_pb else "p-b cookie: "
        new_pb = input(pb_prompt).strip()
        new_creds['p-b'] = new_pb if new_pb else current_pb
        
        # p-lat cookie (optional)
        current_plat = current_creds.get('p-lat', '')
        plat_prompt = f"p-lat cookie [{current_plat[:8]}...]: " if current_plat else "p-lat cookie (optional): "
        new_plat = input(plat_prompt).strip()
        if new_plat or current_plat:
            new_creds['p-lat'] = new_plat if new_plat else current_plat
        
        # formkey
        current_formkey = current_creds.get('formkey', '')
        formkey_prompt = f"formkey [{current_formkey[:8]}...]: " if current_formkey else "formkey: "
        new_formkey = input(formkey_prompt).strip()
        new_creds['formkey'] = new_formkey if new_formkey else current_formkey
        
        # Validate required fields
        if not new_creds.get('p-b') or not new_creds.get('formkey'):
            print("❌ p-b cookie and formkey are required!")
            return False
        
        # Save credentials
        if self.save_credentials(new_creds):
            print("✅ Credentials saved successfully!")
            return True
        else:
            print("❌ Failed to save credentials!")
            return False


async def main():
    """Main function to handle command line arguments."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Manage Poe.com credentials")
    parser.add_argument('--extract', action='store_true', 
                       help='Show guide for extracting credentials')
    parser.add_argument('--validate', action='store_true',
                       help='Validate current credentials')
    parser.add_argument('--update', action='store_true',
                       help='Update credentials interactively')
    
    args = parser.parse_args()
    
    manager = CredentialManager()
    
    if args.extract:
        manager.show_extraction_guide()
    
    elif args.validate:
        credentials = manager.load_credentials()
        if not credentials:
            print("❌ No credentials found. Run with --update to add them.")
            return
        
        is_valid = await manager.validate_credentials(credentials)
        if not is_valid:
            print("\n💡 Tip: Run with --extract to see how to get new credentials")
            print("      Or run with --update to update them")
    
    elif args.update:
        success = manager.interactive_update()
        if success:
            # Validate the new credentials
            credentials = manager.load_credentials()
            if credentials:
                await manager.validate_credentials(credentials)
    
    else:
        # Show current status
        credentials = manager.load_credentials()
        if credentials:
            print("📊 Current Credential Status")
            print("=" * 30)
            print(f"✅ p-b cookie: {'Present' if credentials.get('p-b') else 'Missing'}")
            print(f"✅ p-lat cookie: {'Present' if credentials.get('p-lat') else 'Missing'}")
            print(f"✅ formkey: {'Present' if credentials.get('formkey') else 'Missing'}")
            print()
            print("🔧 Available commands:")
            print("   --extract   Show extraction guide")
            print("   --validate  Test current credentials")
            print("   --update    Update credentials")
        else:
            print("❌ No credentials found!")
            print("Run: python scripts/manage_credentials.py --update")


if __name__ == "__main__":
    asyncio.run(main())
