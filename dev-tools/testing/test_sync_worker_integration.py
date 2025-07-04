#!/usr/bin/env python3
"""Test the fixed SyncWorker with PoeSearchClient integration."""

import os
import sys

# Add the src directory to the Python path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
src_path = os.path.join(project_root, 'src')
sys.path.insert(0, src_path)

# Add utilities path for auto-installer
utils_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'utilities')
sys.path.insert(0, utils_path)

def ensure_dependencies():
    """Ensure all required dependencies are available."""
    try:
        from auto_installer import ensure_api_dependencies, ensure_database_dependencies, ensure_gui_dependencies
        print("Checking and installing dependencies...")
        
        success = True
        success &= ensure_gui_dependencies()
        success &= ensure_api_dependencies() 
        success &= ensure_database_dependencies()
        
        return success
    except ImportError:
        print("Auto-installer not available, proceeding without dependency check...")
        return True

def test_sync_worker_with_client():
    """Test SyncWorker with PoeSearchClient."""
    try:
        print("Testing SyncWorker with PoeSearchClient...")
        
        # Import required classes
        from poe_search.client import PoeSearchClient
        from poe_search.gui.workers.sync_worker import SyncWorker
        from poe_search.utils.config import PoeSearchConfig
        print("✓ All imports successful")
        
        # Create a config with empty tokens (for testing)
        config = PoeSearchConfig()
        config.poe_tokens = {"p-b": "", "p-lat": "", "formkey": ""}
        print("✓ Config created")
        
        # Create PoeSearchClient
        client = PoeSearchClient(config=config)
        print("✓ PoeSearchClient created")
        
        # Try to create SyncWorker with the client
        sync_worker = SyncWorker(client)
        print("✓ SyncWorker created successfully")
        
        # Check that signals exist
        expected_signals = [
            'progress_updated',
            'conversation_synced',
            'error_occurred',
            'sync_error',
            'sync_complete', 
            'sync_finished'
        ]
        
        print("\nVerifying signals:")
        for signal_name in expected_signals:
            if hasattr(sync_worker, signal_name):
                print(f"✓ {signal_name}")
            else:
                print(f"✗ {signal_name} - MISSING")
                return False
                
        print("\n✅ All tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    # Ensure dependencies first
    if not ensure_dependencies():
        print("Failed to install required dependencies")
        sys.exit(1)
    
    success = test_sync_worker_with_client()
    sys.exit(0 if success else 1)
