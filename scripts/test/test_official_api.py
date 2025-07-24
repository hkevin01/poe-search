#!/usr/bin/env python3
"""Test script for the official Poe API."""

import argparse
import json
import logging
import sys
from pathlib import Path
from typing import Any, Dict, Optional

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from poe_search.api.official_client import OfficialPoeAPIClient
from poe_search.utils.config import get_poe_api_key, load_config

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class OfficialAPITester:
    """Test class for the official Poe API."""
    
    def __init__(self):
        """Initialize the tester."""
        self.config = None
        self.client = None
    
    def setup(self, api_key: Optional[str] = None):
        """Set up the test environment."""
        print("🔧 Setting up official API tester...")
        
        try:
            # Load configuration
            self.config = load_config()
            print("✅ Configuration loaded")
            
            # Use provided API key or get from secure loader
            if api_key:
                api_key_to_use = api_key
            else:
                api_key_to_use = get_poe_api_key()
            
            if not api_key_to_use:
                print("❌ No API key available")
                print("💡 To test the official API:")
                print("   1. Get your API key from https://poe.com/api_key")
                print("   2. Run: python scripts/test_official_api.py YOUR_API_KEY")
                return False
            
            # Initialize official client
            self.client = OfficialPoeAPIClient(api_key=api_key_to_use, config=self.config)
            print("✅ Official API client initialized")
            return True
            
        except Exception as e:
            print(f"❌ Setup failed: {e}")
            return False
    
    def test_connection(self):
        """Test the API connection."""
        print(f"\n🔗 Testing API connection...")
        
        if not self.client:
            print("❌ Client not available")
            return False
        
        try:
            result = self.client.test_connection()
            
            if result.get('success'):
                print("✅ Connection test passed!")
                print(f"   📊 API Key valid: {result.get('api_key_valid', False)}")
                print(f"   📝 Response length: {result.get('response_length', 0)} chars")
                print(f"   📄 Response preview: {result.get('response_preview', 'N/A')}")
                return True
            else:
                print("❌ Connection test failed!")
                print(f"   Error: {result.get('error', 'Unknown error')}")
                return False
                
        except Exception as e:
            print(f"❌ Connection test failed: {e}")
            return False
    
    def test_available_bots(self):
        """Test getting available bots."""
        print(f"\n🤖 Testing available bots...")
        
        if not self.client:
            print("❌ Client not available")
            return
        
        try:
            bots = self.client.get_available_bots()
            print(f"✅ Found {len(bots)} available bots")
            
            # Display bots
            for i, bot in enumerate(bots[:10]):  # Show first 10
                bot_id = bot.get('id', 'Unknown')
                display_name = bot.get('displayName', 'Unknown')
                print(f"   {i+1}. {display_name} ({bot_id})")
            
            if len(bots) > 10:
                print(f"   ... and {len(bots) - 10} more bots")
                
        except Exception as e:
            print(f"❌ Failed to get bots: {e}")
    
    def test_bot_response(self, message: str = "Hello! This is a test message from Poe Search.", bot_name: str = "GPT-3.5-Turbo"):
        """Test sending a message to a bot."""
        print(f"\n💬 Testing bot response...")
        print(f"   🤖 Bot: {bot_name}")
        print(f"   📝 Message: {message}")
        
        if not self.client:
            print("❌ Client not available")
            return
        
        try:
            response = self.client.get_bot_response(message, bot_name)
            
            print(f"✅ Response received!")
            print(f"   📊 Length: {len(response)} characters")
            print(f"   📄 Response:")
            print(f"   {'='*50}")
            print(response)
            print(f"   {'='*50}")
            
            return response
            
        except Exception as e:
            print(f"❌ Failed to get response: {e}")
            return None
    
    def test_file_upload(self, file_path: str = None):
        """Test file upload functionality."""
        print(f"\n📎 Testing file upload...")
        
        if not self.client:
            print("❌ Client not available")
            return
        
        if not file_path:
            print("⚠️  No file path provided, skipping file upload test")
            return
        
        try:
            # Test file upload
            attachment = self.client.upload_file(file_path)
            
            if attachment:
                print(f"✅ File uploaded successfully!")
                print(f"   📁 File: {file_path}")
                print(f"   📎 Attachment: {type(attachment)}")
                
                # Test sending message with file
                message = "Please analyze this file."
                response = self.client.get_bot_response_with_file(message, file_path, "GPT-3.5-Turbo")
                
                if response:
                    print(f"✅ Response with file received!")
                    print(f"   📊 Length: {len(response)} characters")
                    print(f"   📄 Preview: {response[:200]}...")
                else:
                    print(f"❌ Failed to get response with file")
            else:
                print(f"❌ File upload failed")
                
        except Exception as e:
            print(f"❌ File upload test failed: {e}")
    
    def test_user_info(self):
        """Test getting user information."""
        print(f"\n👤 Testing user info...")
        
        if not self.client:
            print("❌ Client not available")
            return
        
        try:
            user_info = self.client.get_user_info()
            
            print(f"✅ User info retrieved!")
            print(f"   📊 API Type: {user_info.get('api_type', 'Unknown')}")
            print(f"   📊 Rate Limit: {user_info.get('rate_limit', 'Unknown')}")
            print(f"   📊 Point System: {user_info.get('point_system', 'Unknown')}")
            print(f"   📊 Available Features: {user_info.get('available_features', [])}")
            print(f"   📊 Limitations: {user_info.get('limitations', [])}")
            
        except Exception as e:
            print(f"❌ Failed to get user info: {e}")
    
    def run_comprehensive_test(self, api_key: Optional[str] = None):
        """Run comprehensive official API test."""
        print("🚀 Starting comprehensive official API test")
        
        if not self.setup(api_key):
            print("❌ Setup failed, aborting test")
            return
        
        # Run all tests
        connection_ok = self.test_connection()
        
        if connection_ok:
            self.test_available_bots()
            self.test_bot_response()
            self.test_user_info()
            # self.test_file_upload()  # Uncomment if you have a test file
        
        print(f"\n{'='*80}")
        print("📊 OFFICIAL API TEST SUMMARY")
        print(f"{'='*80}")
        
        if connection_ok:
            print("✅ Official API is working!")
            print("💡 You can now:")
            print("   1. Send new messages to Poe bots")
            print("   2. Upload files for analysis")
            print("   3. Use the GUI to switch between wrapper and official APIs")
        else:
            print("❌ Official API test failed")
            print("💡 Make sure you have a valid API key from https://poe.com/api_key")


def main():
    """Main function."""
    print("🎯 Poe Search - Official API Tester")
    print("=" * 50)
    
    parser = argparse.ArgumentParser(description="Test the official Poe API.")
    parser.add_argument("api_key", nargs="?", default=None, help="Poe API key (optional, will use secure loader if not provided)")
    parser.add_argument("--bot", default="GPT-3.5-Turbo", help="Bot name (default: GPT-3.5-Turbo)")
    parser.add_argument("--message", default=None, help="Message to send to the bot")
    parser.add_argument("--file", default=None, help="File path to upload (optional)")
    args = parser.parse_args()

    # Prompt for message if not provided
    message = args.message
    if message is None:
        message = input(f"Enter a message for the bot [{args.bot}]: ")
        if not message:
            message = "Hello! This is a test message from Poe Search."

    # Run the test
    tester = OfficialAPITester()
    tester.run_comprehensive_test(args.api_key)
    
    # Custom bot response
    print("\n--- Custom Bot Message Test ---")
    print(f"Bot: {args.bot}")
    print(f"Message: {message}")
    tester.setup(args.api_key)
    tester.test_bot_response(message=message, bot_name=args.bot)
    
    # File upload test if file provided
    if args.file:
        print(f"\n--- File Upload Test ---")
        print(f"File: {args.file}")
        tester.setup(args.api_key)
        tester.test_file_upload(file_path=args.file)


if __name__ == "__main__":
    main() 