#!/usr/bin/env python3
"""
Quick test to verify the SearchWorker parameter issue is resolved.
"""

import os
import sys

# Add project paths
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
src_path = os.path.join(project_root, 'src')
utils_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'utilities')
sys.path.insert(0, src_path)
sys.path.insert(0, utils_path)

def test_searchworker_fix():
    """Test that SearchWorker parameter issue is resolved."""
    try:
        from auto_installer import ensure_database_dependencies, ensure_gui_dependencies
        print("Installing required dependencies...")
        ensure_gui_dependencies()
        ensure_database_dependencies()
        
        print("Testing SearchWorker constructor...")
        
        # Import required classes
        from poe_search.gui.workers.search_worker import SearchWorker
        from poe_search.storage.database import Database

        # Create database instance
        database = Database("sqlite:///test.db")
        
        # Create search parameters
        search_params = {
            "query": "test",
            "bot": "All Bots",
            "category": "All Categories",
            "date_from": None,
            "date_to": None,
            "use_regex": False,
            "case_sensitive": False
        }
        
        # Try to create SearchWorker with correct parameters
        search_worker = SearchWorker(search_params, database)
        print("✅ SearchWorker created successfully with correct parameters!")
        
        # Check signals
        expected_signals = ['progress', 'results_ready', 'error', 'finished']
        print("Checking SearchWorker signals:")
        for signal in expected_signals:
            if hasattr(search_worker, signal):
                print(f"✓ {signal}")
            else:
                print(f"✗ {signal} - MISSING")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_searchworker_fix()
    print(f"\n{'✅ SearchWorker test PASSED' if success else '❌ SearchWorker test FAILED'}")
    sys.exit(0 if success else 1)
