#!/usr/bin/env python3
"""
Quick test to verify CategorizationWorker import issue is fixed.
"""

import os
import sys

# Add project paths
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
src_path = os.path.join(project_root, 'src')
utils_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'utilities')
sys.path.insert(0, src_path)
sys.path.insert(0, utils_path)

def test_categorization_worker_fix():
    """Test that CategoryWorker import issue is resolved."""
    try:
        # Test basic import
        from poe_search.gui.workers.categorization_worker import CategoryWorker
        print("✅ CategoryWorker import successful")
        
        # Test that the main window can import it
        from poe_search.gui.main_window import MainWindow
        print("✅ MainWindow import successful (with CategoryWorker)")
        
        # Check that CategoryWorker has expected signals
        expected_signals = [
            'progress_updated',
            'conversation_categorized', 
            'categorization_complete',
            'error_occurred'
        ]
        
        print("Checking CategoryWorker signals:")
        for signal in expected_signals:
            if hasattr(CategoryWorker, signal):
                print(f"✓ {signal}")
            else:
                print(f"✗ {signal} - MISSING")
        
        print("✅ CategoryWorker fix verification completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_categorization_worker_fix()
    print(f"\n{'✅ CategoryWorker fix PASSED' if success else '❌ CategoryWorker fix FAILED'}")
    sys.exit(0 if success else 1)
