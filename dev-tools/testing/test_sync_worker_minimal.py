#!/usr/bin/env python3
"""Test SyncWorker signals without importing complex dependencies."""

import os
import sys

# Add the src directory to the Python path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
src_path = os.path.join(project_root, 'src')
sys.path.insert(0, src_path)

def test_minimal_sync_worker():
    """Test SyncWorker imports and basic signal setup."""
    try:
        from PyQt6.QtCore import QThread, pyqtSignal
        print("✓ PyQt6 imports successful")
        
        # Try to import just the SyncWorker class
        from poe_search.gui.workers.sync_worker import SyncWorker
        print("✓ SyncWorker import successful")
        
        # Check the class definition for signals
        print("\nChecking SyncWorker signals:")
        
        expected_signals = [
            'progress_updated',
            'conversation_synced',
            'error_occurred', 
            'sync_error',
            'sync_complete',
            'sync_finished'
        ]
        
        for signal_name in expected_signals:
            if hasattr(SyncWorker, signal_name):
                signal_attr = getattr(SyncWorker, signal_name)
                print(f"✓ {signal_name}: {type(signal_attr)}")
            else:
                print(f"✗ {signal_name}: MISSING")
                
        # Try to check the signal types without instantiating
        for name, obj in SyncWorker.__dict__.items():
            if isinstance(obj, pyqtSignal):
                print(f"Found signal in class: {name}")
                
        return True
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_minimal_sync_worker()
    print(f"\nTest {'PASSED' if success else 'FAILED'}")
    sys.exit(0 if success else 1)
