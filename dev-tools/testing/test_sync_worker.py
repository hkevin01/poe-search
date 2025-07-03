import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

try:
    from poe_search.gui.workers.sync_worker import SyncWorker
    print("SUCCESS: SyncWorker import works")
    
    if hasattr(SyncWorker, 'sync_finished'):
        print("SUCCESS: sync_finished signal exists")
    else:
        print("ERROR: sync_finished signal missing")
        
except Exception as e:
    print(f"ERROR: {e}")
