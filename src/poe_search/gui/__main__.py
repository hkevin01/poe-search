"""Main entry point for the Poe Search GUI application."""

import logging
import sys
from pathlib import Path

from PyQt6.QtWidgets import QApplication

from poe_search import PoeSearchClient
from poe_search.gui.main_window import MainWindow
from poe_search.utils.config import load_config

# Enable debug logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('poe_search.log')
    ]
)

def main():
    """Main entry point for the GUI application."""
    # Create Qt application
    app = QApplication(sys.argv)
    app.setApplicationName("Poe Search")
    app.setApplicationVersion("1.0.0")
    
    # Load configuration
    config = load_config()
    
    # Create and show main window
    window = MainWindow(config)
    window.show()
    
    # Run application
    sys.exit(app.exec())

if __name__ == "__main__":
    main() 