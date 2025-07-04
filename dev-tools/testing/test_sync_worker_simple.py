#!/usr/bin/env python3
"""Simple test to verify SyncWorker signals are properly defined."""

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
    """Ensure required dependencies are available."""
    try:
        from auto_installer import ensure_gui_dependencies
        print("Checking GUI dependencies...")
        return ensure_gui_dependencies()
    except ImportError:
        print("Auto-installer not available, proceeding...")
        return True

def test_sync_worker_signals():
    """Test that SyncWorker has all required signals."""
    try:
        from PyQt6.QtWidgets import QApplication

        from poe_search.gui.workers.sync_worker import SyncWorker

        # Create QApplication if none exists
        app = QApplication.instance()
        if app is None:
            app = QApplication([])
        
        # Create a minimal client mock
        class MockClient:
            def __init__(self):
                self.database = None
                self.api_client = None
        
        # Create SyncWorker instance
        client = MockClient()
        worker = SyncWorker(client)
        
        # Check that all required signals exist
        required_signals = [
            'progress_updated',
            'conversation_synced', 
            'error_occurred',
            'sync_error',
            'sync_complete',
            'sync_finished'
        ]
        
        print("Testing SyncWorker signals...")
        
        for signal_name in required_signals:
            if hasattr(worker, signal_name):
                signal = getattr(worker, signal_name)
                print(f"✓ {signal_name}: {type(signal)}")
            else:
                print(f"✗ {signal_name}: MISSING")
                return False
        
        print("\nAll signals are properly defined!")
        
        # Test signal emission (without running the worker)
        print("\nTesting signal emission...")
        
        def test_handler(message="test"):
            print(f"Signal received: {message}")
        
        # Connect test handlers
        worker.sync_error.connect(test_handler)
        worker.sync_finished.connect(lambda: test_handler("sync_finished"))
        
        # Test emitting signals
        worker.sync_error.emit("Test error message")
        worker.sync_finished.emit()
        
        print("✓ Signal emission test passed!")
        
        return True
        
    except ImportError as e:
        print(f"Import error: {e}")
        return False
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    # Ensure dependencies first
    if not ensure_dependencies():
        print("Failed to install required dependencies")
        sys.exit(1)
    
    success = test_sync_worker_signals()
    sys.exit(0 if success else 1)
