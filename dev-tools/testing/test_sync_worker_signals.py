#!/usr/bin/env python3
"""Test script to verify all SyncWorker signals are present and working correctly."""

import logging
import os
import sys
from unittest.mock import MagicMock, Mock

# Add project root to path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from PyQt6.QtCore import QCoreApplication

from src.poe_search.gui.workers.sync_worker import SyncWorker

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_sync_worker_signals():
    """Test that SyncWorker has all required signals."""
    print("Testing SyncWorker signals...")
    
    # Create a mock client
    mock_client = Mock()
    mock_client.database = Mock()
    mock_client.api_client = Mock()
    
    # Create SyncWorker instance
    worker = SyncWorker(mock_client, days=1)
    
    # Check that all required signals exist
    required_signals = [
        'progress_updated',
        'conversation_synced', 
        'error_occurred',
        'sync_error',
        'sync_complete',
        'sync_finished'
    ]
    
    print("Checking for required signals:")
    all_signals_present = True
    
    for signal_name in required_signals:
        if hasattr(worker, signal_name):
            signal = getattr(worker, signal_name)
            print(f"  ✓ {signal_name}: {signal}")
        else:
            print(f"  ✗ {signal_name}: MISSING")
            all_signals_present = False
    
    if all_signals_present:
        print("\n✓ All required signals are present!")
    else:
        print("\n✗ Some signals are missing!")
        return False
    
    # Test signal connections (basic smoke test)
    print("\nTesting signal connections:")
    try:
        # Create mock slot functions
        def mock_progress_slot(progress, message):
            print(f"  Progress: {progress}% - {message}")
        
        def mock_error_slot(error):
            print(f"  Error: {error}")
        
        def mock_sync_error_slot(error):
            print(f"  Sync Error: {error}")
        
        def mock_finished_slot():
            print("  Sync finished")
        
        def mock_complete_slot(stats):
            print(f"  Sync complete: {stats}")
        
        def mock_conversation_slot(data):
            print(f"  Conversation synced: {data.get('id', 'unknown')}")
        
        # Connect signals
        worker.progress_updated.connect(mock_progress_slot)
        worker.error_occurred.connect(mock_error_slot)
        worker.sync_error.connect(mock_sync_error_slot)
        worker.sync_finished.connect(mock_finished_slot)
        worker.sync_complete.connect(mock_complete_slot)
        worker.conversation_synced.connect(mock_conversation_slot)
        
        print("  ✓ All signals connected successfully!")
        
        # Test signal emissions
        print("\nTesting signal emissions:")
        worker.progress_updated.emit(50, "Test progress")
        worker.error_occurred.emit("Test error")
        worker.sync_error.emit("Test sync error")
        worker.sync_finished.emit()
        worker.sync_complete.emit({'test': 'stats'})
        worker.conversation_synced.emit({'id': 'test_conversation'})
        
        print("  ✓ All signals emit correctly!")
        
    except Exception as e:
        print(f"  ✗ Signal connection/emission failed: {e}")
        return False
    
    return True

def test_gui_compatibility():
    """Test GUI compatibility by checking signal signatures."""
    print("\nTesting GUI compatibility:")
    
    # Create a mock client
    mock_client = Mock()
    worker = SyncWorker(mock_client)
    
    # Check signal signatures match what GUI expects
    try:
        # These should work without errors if signatures match
        worker.progress_updated.connect(lambda p, m: None)  # int, str
        worker.conversation_synced.connect(lambda d: None)  # dict
        worker.error_occurred.connect(lambda e: None)       # str
        worker.sync_error.connect(lambda e: None)           # str
        worker.sync_complete.connect(lambda s: None)        # dict
        worker.sync_finished.connect(lambda: None)          # no args
        
        print("  ✓ All signal signatures are compatible with GUI!")
        return True
        
    except Exception as e:
        print(f"  ✗ Signal signature mismatch: {e}")
        return False

def main():
    """Main test function."""
    print("=" * 60)
    print("SyncWorker Signal Compatibility Test")
    print("=" * 60)
    
    # Create QCoreApplication for signal testing
    app = QCoreApplication([])
    
    try:
        # Run tests
        signals_test = test_sync_worker_signals()
        compatibility_test = test_gui_compatibility()
        
        print("\n" + "=" * 60)
        if signals_test and compatibility_test:
            print("✓ ALL TESTS PASSED - SyncWorker is fully compatible!")
            return True
        else:
            print("✗ SOME TESTS FAILED - SyncWorker needs fixes!")
            return False
            
    except Exception as e:
        print(f"Test execution failed: {e}")
        return False
    finally:
        app.quit()

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
