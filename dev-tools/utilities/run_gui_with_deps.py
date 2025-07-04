#!/usr/bin/env python3
"""
Enhanced GUI main with automatic dependency installation.
"""

import logging
import os
import sys

# Add project paths
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
src_path = os.path.join(project_root, 'src')
utils_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'utilities')
sys.path.insert(0, src_path)
sys.path.insert(0, utils_path)

def ensure_gui_ready():
    """Ensure the GUI application has all required dependencies."""
    try:
        from auto_installer import ensure_all_dependencies
        print("Checking and installing all project dependencies...")
        
        if not ensure_all_dependencies():
            print("❌ Failed to install some dependencies. The application may not work correctly.")
            return False
        
        print("✅ All dependencies are ready")
        return True
        
    except ImportError:
        print("⚠️  Auto-installer not available, proceeding without dependency check...")
        return True

def main():
    """Enhanced main function with dependency checking."""
    # First ensure all dependencies are available
    if not ensure_gui_ready():
        print("Dependency installation failed. Please install missing packages manually:")
        print("pip install PyQt6 httpx requests pydantic fastapi-poe poe-api-wrapper SQLAlchemy")
        print("pip install 'numpy<2.0' 'pandas>=1.5.0,<2.0.0'")
        sys.exit(1)
    
    try:
        # Now import and run the GUI
        from poe_search.gui.__main__ import main as gui_main
        gui_main()
        
    except ImportError as e:
        print(f"❌ Failed to import GUI components: {e}")
        print("Make sure you're running from the project root directory")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Application error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
