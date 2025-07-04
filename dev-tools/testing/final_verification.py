#!/usr/bin/env python3
"""
Final verification script to test all fixes are working correctly.
"""

import os
import sys

# Add project paths
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
src_path = os.path.join(project_root, 'src')
utils_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'utilities')
sys.path.insert(0, src_path)
sys.path.insert(0, utils_path)

def test_all_fixes():
    """Test all fixes are working correctly."""
    print("🔍 FINAL VERIFICATION - Testing All Fixes")
    print("=" * 50)
    
    all_passed = True
    
    try:
        print("\n1️⃣ Testing MainWindow Import...")
        from poe_search.gui.main_window import MainWindow
        print("✅ MainWindow imports successfully")
        
        print("\n2️⃣ Testing CategoryWorker Import...")
        from poe_search.gui.workers.categorization_worker import CategoryWorker
        print("✅ CategoryWorker imports successfully")
        
        print("\n3️⃣ Testing SyncWorker Import...")
        from poe_search.gui.workers.sync_worker import SyncWorker
        print("✅ SyncWorker imports successfully")
        
        print("\n4️⃣ Testing SearchWorker Import...")
        from poe_search.gui.workers.search_worker import SearchWorker
        print("✅ SearchWorker imports successfully")
        
        print("\n5️⃣ Testing PoeSearchClient Integration...")
        from poe_search.client import PoeSearchClient
        from poe_search.utils.config import PoeSearchConfig
        
        config = PoeSearchConfig()
        config.poe_tokens = {"p-b": "", "p-lat": "", "formkey": ""}
        client = PoeSearchClient(config=config)
        print("✅ PoeSearchClient creates successfully")
        
        print("\n6️⃣ Testing Worker Instantiation...")
        # Test SyncWorker with correct client
        sync_worker = SyncWorker(client)
        print("✅ SyncWorker instantiates with PoeSearchClient")
        
        # Test CategoryWorker with correct client  
        category_worker = CategoryWorker(client)
        print("✅ CategoryWorker instantiates with PoeSearchClient")
        
        print("\n7️⃣ Testing Signal Definitions...")
        # Check SyncWorker signals
        sync_signals = ['progress_updated', 'conversation_synced', 'error_occurred', 
                       'sync_error', 'sync_complete', 'sync_finished']
        for signal in sync_signals:
            if hasattr(sync_worker, signal):
                print(f"✓ SyncWorker.{signal}")
            else:
                print(f"✗ SyncWorker.{signal} - MISSING")
                all_passed = False
        
        # Check CategoryWorker signals
        cat_signals = ['progress_updated', 'conversation_categorized', 
                      'categorization_complete', 'error_occurred']
        for signal in cat_signals:
            if hasattr(category_worker, signal):
                print(f"✓ CategoryWorker.{signal}")
            else:
                print(f"✗ CategoryWorker.{signal} - MISSING")
                all_passed = False
        
        print("\n8️⃣ Testing MainWindow Methods...")
        # Check if MainWindow has the required methods
        required_methods = ['on_categorization_complete', 'load_conversations', 'start_sync']
        for method in required_methods:
            if hasattr(MainWindow, method):
                print(f"✓ MainWindow.{method}")
            else:
                print(f"✗ MainWindow.{method} - MISSING")
                all_passed = False
        
        if all_passed:
            print("\n🎉 ALL FIXES VERIFIED SUCCESSFULLY!")
            print("✅ The application is ready for full testing and deployment")
        else:
            print("\n❌ Some issues found - see details above")
            
        return all_passed
        
    except Exception as e:
        print(f"\n❌ Error during verification: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_all_fixes()
    print(f"\n{'🎯 VERIFICATION PASSED' if success else '❌ VERIFICATION FAILED'}")
    sys.exit(0 if success else 1)
