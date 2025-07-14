#!/usr/bin/env python3
"""Debug script to test database access with the exact same setup as the GUI."""

import sys
from pathlib import Path

# Add the src directory to the Python path (same as GUI)
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / "src"))

def debug_database_access():
    """Test database access using the same path calculation as the GUI."""
    
    print("=== Database Access Debug Script ===")
    print(f"Project root: {project_root}")
    
    # Import the same modules as the GUI
    from poe_search.config import load_config
    from poe_search.storage.database import Database

    # Test 1: Direct database access with known path
    print("\n1. Testing direct database access:")
    data_db_path = project_root / "data" / "poe_search.db"
    print(f"   Path: {data_db_path}")
    print(f"   Exists: {data_db_path.exists()}")
    
    if data_db_path.exists():
        database = Database(str(data_db_path))
        conversations = database.get_conversations()
        print(f"   Conversations found: {len(conversations)}")
        if conversations:
            for i, conv in enumerate(conversations[:2]):
                title = conv.get('title', 'No title')
                created = conv.get('created_at', 'No date')
                print(f"   Sample {i+1}: {title} ({created})")
    
    # Test 2: Simulate the exact path calculation from MainWindow
    print("\n2. Testing GUI path calculation:")
    # This mimics: Path(__file__).parent.parent.parent / "data" / "poe_search.db"
    # Where __file__ would be main_window.py
    main_window_path = project_root / "src" / "poe_search" / "gui" / "main_window.py"
    gui_calculated_path = main_window_path.parent.parent.parent.parent / "data" / "poe_search.db"
    print(f"   GUI calculated path: {gui_calculated_path}")
    print(f"   Resolved: {gui_calculated_path.resolve()}")
    print(f"   Exists: {gui_calculated_path.exists()}")
    
    if gui_calculated_path.exists():
        database2 = Database(str(gui_calculated_path))
        conversations2 = database2.get_conversations()
        print(f"   Conversations found: {len(conversations2)}")
    
    # Test 3: Check if there are other database files
    print("\n3. Checking for other database files:")
    for db_file in project_root.rglob("*.db"):
        print(f"   Found: {db_file}")
        if db_file.name == "poe_search.db":
            db = Database(str(db_file))
            convs = db.get_conversations()
            print(f"     -> {len(convs)} conversations")
    
    # Test 4: Test with config
    print("\n4. Testing with config (like GUI does):")
    try:
        config = load_config()
        print(f"   Config loaded successfully")
        # Check if config has any database settings
        if hasattr(config, 'database_url'):
            print(f"   Config database_url: {config.database_url}")
    except Exception as e:
        print(f"   Config load error: {e}")
    
    # Test 5: Check current working directory context
    print("\n5. Current working directory context:")
    import os
    print(f"   CWD: {os.getcwd()}")
    
    # Check relative path from CWD
    cwd_db_path = Path("data/poe_search.db")
    print(f"   Relative path from CWD: {cwd_db_path}")
    print(f"   Exists: {cwd_db_path.exists()}")
    
    if cwd_db_path.exists():
        database3 = Database(str(cwd_db_path))
        conversations3 = database3.get_conversations()
        print(f"   Conversations found: {len(conversations3)}")

if __name__ == "__main__":
    debug_database_access()
