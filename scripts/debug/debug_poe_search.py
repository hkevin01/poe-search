#!/usr/bin/env python3
"""Debug script for Poe Search GUI issues."""

import json
import logging
import os
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

# Setup logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def debug_poe_search():
    """Complete debugging for Poe Search issues."""
    
    print("=== Poe Search Debug Report ===\n")
    
    # 1. Check configuration
    print("1. Configuration Check:")
    try:
        from poe_search.utils.config import load_config
        
        config = load_config()
        api_key = config.poe_token
        
        if api_key:
            print(f"   ✓ API key loaded: {api_key[:10]}...")
        else:
            print("   ✗ API key is empty or missing")
            return
    except Exception as e:
        print(f"   ✗ Config error: {e}")
        return
    
    # 2. Check icon files
    print("\n2. Icon Files Check:")
    icon_dir = Path(__file__).parent.parent / "src" / "poe_search" / "gui" / "resources" / "icons"
    icon_files = ["app_icon.png", "app_icon_128x128.png", "tray_icon.png", "tray_icon_32x32.png"]
    
    for icon_file in icon_files:
        icon_path = icon_dir / icon_file
        if icon_path.exists():
            size = icon_path.stat().st_size
            print(f"   ✓ {icon_file} exists ({size} bytes)")
        else:
            print(f"   ✗ {icon_file} missing")
    
    # 3. Test API client
    print("\n3. API Client Test:")
    try:
        from poe_search.client import PoeSearchClient
        
        client = PoeSearchClient(token=api_key)
        print("   ✓ API client created successfully")
        
        # Test getting conversations
        conversations = client.get_conversations()
        print(f"   ✓ API client works: {len(conversations)} conversations")
        
        if conversations:
            print(f"   ✓ Sample conversation: {conversations[0].get('title', 'No title')}")
            print(f"   ✓ Conversation ID: {conversations[0].get('id', 'No ID')}")
        else:
            print("   ⚠ No conversations returned (may be normal for new accounts)")
            
    except Exception as e:
        print(f"   ✗ API client failed: {e}")
        import traceback
        traceback.print_exc()
    
    # 4. Test database
    print("\n4. Database Test:")
    try:
        from poe_search.storage.database import Database
        
        db = Database()
        print("   ✓ Database connection successful")
        
        # Try to get conversation count
        try:
            count = db.get_conversation_count()
            print(f"   ✓ Database accessible: {count} conversations stored")
        except AttributeError:
            print("   ⚠ Database has no get_conversation_count method")
        except Exception as e:
            print(f"   ⚠ Database count error: {e}")
            
    except Exception as e:
        print(f"   ✗ Database error: {e}")
    
    # 5. Test configuration loading
    print("\n5. Configuration Loading Test:")
    try:
        from poe_search.utils.config import load_config
        
        config = load_config()
        print("   ✓ Configuration loaded successfully")
        print(f"   ✓ Poe token: {config.poe_token[:10] if config.poe_token else 'None'}...")
        
        if config.poe_token:
            print("   ✓ Poe token found in config")
        else:
            print("   ✗ Poe token not found in config")
            
    except Exception as e:
        print(f"   ✗ Configuration loading error: {e}")
        import traceback
        traceback.print_exc()
    
    # 6. Test GUI imports
    print("\n6. GUI Import Test:")
    try:
        from poe_search.gui.app import PoeSearchApp
        from poe_search.gui.main_window import MainWindow
        print("   ✓ GUI modules import successfully")
    except Exception as e:
        print(f"   ✗ GUI import error: {e}")
        import traceback
        traceback.print_exc()
    
    # 7. Check PyQt6 availability
    print("\n7. PyQt6 Test:")
    try:
        from PyQt6.QtGui import QIcon
        from PyQt6.QtWidgets import QApplication
        print("   ✓ PyQt6 available")
    except ImportError as e:
        print(f"   ✗ PyQt6 not available: {e}")
    except Exception as e:
        print(f"   ⚠ PyQt6 error: {e}")
    
    print("\n=== Debug Complete ===")
    print("\nNext steps:")
    print("1. If API client test failed, check your API key and internet connection")
    print("2. If database test failed, check database configuration")
    print("3. If GUI import failed, check PyQt6 installation")
    print("4. Run the GUI with: python -m poe_search.gui.app")


if __name__ == "__main__":
    debug_poe_search() 