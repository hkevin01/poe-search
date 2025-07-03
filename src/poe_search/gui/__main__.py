"""Main entry point for the Poe Search GUI application."""

import logging
import sys

from PyQt6.QtWidgets import QApplication, QMessageBox

from poe_search.gui.main_window import MainWindow
from poe_search.utils.config import load_config
from poe_search.utils.token_manager import ensure_tokens_on_startup

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
    
    # Check and refresh tokens on startup
    success, _ = ensure_tokens_on_startup(
        interactive=True, max_age_hours=36
    )
    
    if not success:
        # Show error dialog and exit
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Icon.Critical)
        msg.setWindowTitle("Token Error")
        msg.setText("Failed to obtain valid Poe.com tokens")
        msg.setInformativeText(
            "Please run the token refresh script manually:\n"
            "python scripts/refresh_tokens.py"
        )
        msg.exec()
        sys.exit(1)
    
    # Load configuration
    _ = load_config()
    
    # Create and show main window
    window = MainWindow()
    window.show()
    
    # Run application
    sys.exit(app.exec())


if __name__ == "__main__":
    main()