#!/usr/bin/env python3
"""Simple test to verify SyncWorker signals without PyQt app."""

import os
import sys

# Add project root to path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

def test_sync_worker_signals():
    """Test that SyncWorker has all required signals."""
    print("Testing SyncWorker signals (static check)...")
    
    try:
        # Import and inspect the class
        from src.poe_search.gui.workers.sync_worker import SyncWorker

        # Check that all required signals exist as class attributes
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
            if hasattr(SyncWorker, signal_name):
                print(f"  ✓ {signal_name}: Found in class")
            else:
                print(f"  ✗ {signal_name}: MISSING")
                all_signals_present = False
        
        if all_signals_present:
            print("\n✓ All required signals are present in SyncWorker class!")
            
            # Check the signal definitions by reading the source
            import inspect
            source = inspect.getsource(SyncWorker)
            
            print("\nSignal definitions found in source:")
            for signal_name in required_signals:
                if f"{signal_name} = pyqtSignal" in source:
                    print(f"  ✓ {signal_name}: Properly defined as pyqtSignal")
                else:
                    print(f"  ? {signal_name}: May be inherited or defined differently")
            
            return True
        else:
            print("\n✗ Some signals are missing!")
            return False
            
    except ImportError as e:
        print(f"✗ Failed to import SyncWorker: {e}")
        return False
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        return False

def main():
    """Main test function."""
    print("=" * 60)
    print("SyncWorker Signal Static Check")
    print("=" * 60)
    
    success = test_sync_worker_signals()
    
    print("\n" + "=" * 60)
    if success:
        print("✓ STATIC CHECK PASSED - All required signals found!")
    else:
        print("✗ STATIC CHECK FAILED - Some signals missing!")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
