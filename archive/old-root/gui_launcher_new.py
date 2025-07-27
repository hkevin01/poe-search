#!/usr/bin/env python3
"""
Compatibility wrapper for gui_launcher.py

This file maintains backward compatibility while the actual GUI
implementation has been moved to src/poe_search/gui/main_window.py
"""

import sys
from pathlib import Path

# Add src to path for imports
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "src"))


def main():
    """Launch the GUI application."""
    print("🚀 Launching Poe Search GUI...")

    try:
        # Import and run the actual GUI
        from poe_search.gui.main_window import run_gui
        return run_gui()
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure you've installed the required dependencies:")
        print("pip install -r requirements/base.txt")
        return 1
    except Exception as e:
        print(f"❌ Error launching GUI: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
