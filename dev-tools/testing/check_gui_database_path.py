#!/usr/bin/env python3
"""Check which database path the GUI is actually using."""

import sys
from pathlib import Path

# Add the src directory to the Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / "src"))

def check_database_path():
    """Check the database path resolution from the GUI."""
    # Simulate the path resolution as done in main_window.py
    main_window_file = project_root / "src" / "poe_search" / "gui" / "main_window.py"
    
    # This is how the path is calculated in main_window.py:
    # Path(__file__).parent.parent.parent / "data" / "poe_search.db"
    # Where __file__ would be main_window.py
    
    db_path = main_window_file.parent.parent.parent.parent / "data" / "poe_search.db"
    
    print(f"Main window file: {main_window_file}")
    print(f"Database path calculation:")
    print(f"  main_window.py parent: {main_window_file.parent}")
    print(f"  parent.parent: {main_window_file.parent.parent}")
    print(f"  parent.parent.parent: {main_window_file.parent.parent.parent}")
    print(f"  Final db_path: {db_path}")
    print(f"  Resolved: {db_path.resolve()}")
    print(f"  Exists: {db_path.exists()}")
    
    # Check what it should be
    correct_path = project_root / "data" / "poe_search.db"
    print(f"\nCorrect path should be: {correct_path}")
    print(f"  Exists: {correct_path.exists()}")
    
    if db_path.resolve() != correct_path.resolve():
        print(f"\n*** PATH MISMATCH ***")
        print(f"GUI calculates: {db_path.resolve()}")
        print(f"Should be: {correct_path.resolve()}")
    else:
        print(f"\n*** PATH IS CORRECT ***")

if __name__ == "__main__":
    check_database_path()
