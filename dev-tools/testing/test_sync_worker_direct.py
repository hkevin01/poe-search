#!/usr/bin/env python3
"""Direct test of SyncWorker class definition without API dependencies."""

import os
import sys

# Add the src directory to the Python path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
src_path = os.path.join(project_root, 'src')
sys.path.insert(0, src_path)

def test_sync_worker_direct():
    """Test SyncWorker directly by reading the file content."""
    try:
        sync_worker_path = os.path.join(src_path, 'poe_search', 'gui', 'workers', 'sync_worker.py')
        
        if not os.path.exists(sync_worker_path):
            print(f"SyncWorker file not found at: {sync_worker_path}")
            return False
            
        with open(sync_worker_path, 'r') as f:
            content = f.read()
            
        # Check for signal definitions
        expected_signals = [
            'progress_updated = pyqtSignal',
            'conversation_synced = pyqtSignal',
            'error_occurred = pyqtSignal',
            'sync_error = pyqtSignal',
            'sync_complete = pyqtSignal',
            'sync_finished = pyqtSignal'
        ]
        
        print("Checking SyncWorker signals in source code:")
        
        all_found = True
        for signal in expected_signals:
            if signal in content:
                print(f"✓ Found: {signal}")
            else:
                print(f"✗ Missing: {signal}")
                all_found = False
                
        # Check for signal emissions
        emission_patterns = [
            'sync_error.emit(',
            'sync_finished.emit(',
            'error_occurred.emit(',
            'sync_complete.emit('
        ]
        
        print("\nChecking signal emissions:")
        for pattern in emission_patterns:
            count = content.count(pattern)
            if count > 0:
                print(f"✓ {pattern} - Found {count} emission(s)")
            else:
                print(f"? {pattern} - Not found")
                
        return all_found
        
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    success = test_sync_worker_direct()
    print(f"\nTest {'PASSED' if success else 'FAILED'}")
    sys.exit(0 if success else 1)
