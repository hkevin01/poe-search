#!/usr/bin/env python3
"""
Debug script to test browser client conversation extraction
"""

import sys
import os
import logging
from pathlib import Path

# Add src to path
project_root = Path(__file__).parent  # This file is in the project root
sys.path.insert(0, str(project_root / "src"))

def test_browser_client():
    """Test the browser client to see why no conversations are found."""
    try:
        from poe_search.api.browser_client import PoeApiClient

        # Load token
        config_file = project_root / "config" / "poe_tokens.json"
        print(f"🔍 Looking for config file at: {config_file}")
        print(f"📁 Config file exists: {config_file.exists()}")

        if not config_file.exists():
            print(f"❌ No token config file found at: {config_file}")
            print("Please create config/poe_tokens.json")
            return

        import json
        try:
            with open(config_file) as f:
                content = f.read()
                print(f"📄 Config file content: {content[:100]}...")

                # Parse JSON
                tokens = json.loads(content)
                token = tokens.get('p-b')
                lat_token = tokens.get('p-lat')

        except json.JSONDecodeError as e:
            print(f"❌ JSON parsing error: {e}")
            print("Make sure config/poe_tokens.json is valid JSON (no comments)")
            return
        except Exception as e:
            print(f"❌ Error reading config: {e}")
            return

        if not token:
            print("❌ No p-b token found in config")
            return

        print(f"✅ Using token: {token[:8]}...{token[-8:]}")

        # Create client (non-headless for debugging)
        with PoeApiClient(token=token, lat_token=lat_token, headless=False) as client:
            print("🔗 Authenticating...")
            if not client.authenticate():
                print("❌ Authentication failed")
                return

            print("✅ Authentication successful")

            # Run debug extraction
            print("\n🧪 Running debug extraction...")
            meaningful_elements = client.debug_conversation_extraction()

            # Try getting conversations
            print("\n📋 Attempting to get conversations...")
            def progress_callback(msg, pct):
                print(f"  Progress: {pct}% - {msg}")

            conversations = client.get_conversations(limit=10, progress_callback=progress_callback)

            print(f"\n✅ Found {len(conversations)} conversations:")
            for i, conv in enumerate(conversations):
                print(f"  {i+1}. {conv['title'][:50]} | {conv['bot']} | {conv['method']}")

            if not conversations:
                print("\n❌ No conversations found. This might indicate:")
                print("  1. Authentication issues")
                print("  2. Poe.com UI changes")
                print("  3. Rate limiting")
                print("  4. Different page structure")

                print(f"\n📊 Debug info:")
                print(f"  - Meaningful elements found: {len(meaningful_elements)}")
                print(f"  - Page title: {client.driver.title}")
                print(f"  - Current URL: {client.driver.current_url}")

                # Save screenshot for debugging
                screenshot_path = project_root / "debug_screenshot.png"
                client.driver.save_screenshot(str(screenshot_path))
                print(f"  - Screenshot saved to: {screenshot_path}")

                # Wait for manual inspection
                input("\nPress Enter to continue (you can inspect the browser window)...")

    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure you're in the project root and have installed dependencies")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    test_browser_client()
