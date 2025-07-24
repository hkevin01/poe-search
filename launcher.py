# launcher.py - Simple Python launcher for debugging
#!/usr/bin/env python3

import sys
import os
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "src"))

def main():
    """Simple launcher for Poe Search GUI"""
    try:
        print("🚀 Starting Poe Search GUI...")
        
        # Check PyQt6
        try:
            from PyQt6.QtWidgets import QApplication
            print("✅ PyQt6 found")
        except ImportError as e:
            print(f"❌ PyQt6 not found: {e}")
            print("Install with: pip install PyQt6")
            return 1
        
        # Try to import our GUI
        try:
            from poe_search.gui.main_window import MainWindow
            print("✅ GUI module found")
        except ImportError as e:
            print(f"❌ GUI module not found: {e}")
            print("Make sure you're in the project root directory")
            return 1
        
        # Launch GUI
        app = QApplication(sys.argv)
        app.setApplicationName("Poe Search")
        
        window = MainWindow()
        window.show()
        
        print("✅ GUI launched successfully!")
        return app.exec()
        
    except Exception as e:
        print(f"❌ Failed to launch GUI: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())