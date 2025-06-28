"""Main application class for Poe Search GUI."""

import sys
import logging
from pathlib import Path
from typing import Optional, Dict, Any

from PyQt6.QtWidgets import QApplication, QMessageBox
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon, QFont

from poe_search.gui.main_window import MainWindow
from poe_search.utils.config import load_config

logger = logging.getLogger(__name__)


class PoeSearchApp:
    """Main application class for Poe Search GUI."""
    
    def __init__(self, config_path: Optional[Path] = None):
        """Initialize the application.
        
        Args:
            config_path: Optional path to configuration file
        """
        self.config_path = config_path
        self.config = load_config(config_path)
        self.app = None
        self.main_window = None
    
    def create_app(self) -> QApplication:
        """Create and configure the QApplication instance.
        
        Returns:
            Configured QApplication instance
        """
        app = QApplication(sys.argv)
        
        # Set application properties
        app.setApplicationName("Poe Search")
        app.setApplicationDisplayName("Poe Search")
        app.setApplicationVersion("0.1.0")
        app.setOrganizationName("Poe Search")
        app.setOrganizationDomain("github.com/kevin/poe-search")
        
        # Set application icon
        self.set_application_icon(app)
        
        # Apply Windows 11 theme
        self.apply_windows11_theme(app)
        
        # Set application font
        self.set_application_font(app)
        
        return app
    
    def set_application_icon(self, app: QApplication) -> None:
        """Set the application icon."""
        icon_path = Path(__file__).parent / "resources" / "icons" / "app_icon.png"
        if icon_path.exists():
            app.setWindowIcon(QIcon(str(icon_path)))
    
    def apply_windows11_theme(self, app: QApplication) -> None:
        """Apply Windows 11-style dark theme."""
        try:
            # Try to use pyqtdarktheme if available
            import pyqtdarktheme
            pyqtdarktheme.setup_theme()
        except ImportError:
            # Apply custom dark theme
            self.apply_custom_dark_theme(app)
    
    def apply_custom_dark_theme(self, app: QApplication) -> None:
        """Apply a custom dark theme if other options fail."""
        style = """
        QMainWindow {
            background-color: #1e1e1e;
            color: #ffffff;
        }
        
        QWidget {
            background-color: #1e1e1e;
            color: #ffffff;
            selection-background-color: #0078d4;
        }
        
        QTabWidget::pane {
            border: 1px solid #444444;
            background-color: #2b2b2b;
        }
        
        QTabBar::tab {
            background-color: #2b2b2b;
            color: #ffffff;
            padding: 8px 16px;
            margin-right: 2px;
            border-top-left-radius: 4px;
            border-top-right-radius: 4px;
        }
        
        QTabBar::tab:selected {
            background-color: #0078d4;
        }
        
        QTabBar::tab:hover {
            background-color: #404040;
        }
        
        QLineEdit {
            background-color: #3b3b3b;
            border: 1px solid #555555;
            padding: 8px;
            border-radius: 4px;
            color: #ffffff;
        }
        
        QLineEdit:focus {
            border-color: #0078d4;
        }
        
        QTableWidget {
            background-color: #2b2b2b;
            alternate-background-color: #353535;
            gridline-color: #555555;
            color: #ffffff;
        }
        
        QTableWidget::item {
            padding: 8px;
        }
        
        QTableWidget::item:selected {
            background-color: #0078d4;
        }
        
        QHeaderView::section {
            background-color: #404040;
            color: #ffffff;
            padding: 8px;
            border: none;
        }
        
        QScrollBar:vertical {
            background-color: #2b2b2b;
            width: 12px;
        }
        
        QScrollBar::handle:vertical {
            background-color: #555555;
            border-radius: 6px;
            min-height: 20px;
        }
        
        QScrollBar::handle:vertical:hover {
            background-color: #666666;
        }
        
        QMenuBar {
            background-color: #2b2b2b;
            color: #ffffff;
        }
        
        QMenuBar::item {
            background-color: transparent;
            padding: 4px 8px;
        }
        
        QMenuBar::item:selected {
            background-color: #404040;
        }
        
        QMenu {
            background-color: #2b2b2b;
            color: #ffffff;
            border: 1px solid #555555;
        }
        
        QMenu::item {
            padding: 6px 16px;
        }
        
        QMenu::item:selected {
            background-color: #0078d4;
        }
        
        QStatusBar {
            background-color: #2b2b2b;
            color: #ffffff;
            border-top: 1px solid #555555;
        }
        
        QToolBar {
            background-color: #2b2b2b;
            border: none;
            spacing: 4px;
            padding: 4px;
        }
        
        QPushButton {
            background-color: #0078d4;
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 4px;
            font-weight: 500;
        }
        
        QPushButton:hover {
            background-color: #106ebe;
        }
        
        QPushButton:pressed {
            background-color: #005a9e;
        }
        
        QPushButton:disabled {
            background-color: #404040;
            color: #888888;
        }
        
        QComboBox {
            background-color: #3b3b3b;
            border: 1px solid #555555;
            padding: 6px;
            border-radius: 4px;
            color: #ffffff;
        }
        
        QComboBox::drop-down {
            border: none;
            width: 20px;
        }
        
        QComboBox::down-arrow {
            image: none;
            border-left: 5px solid transparent;
            border-right: 5px solid transparent;
            border-top: 5px solid #ffffff;
        }
        
        QComboBox QAbstractItemView {
            background-color: #2b2b2b;
            border: 1px solid #555555;
            selection-background-color: #0078d4;
            color: #ffffff;
        }
        
        QCheckBox {
            color: #ffffff;
        }
        
        QCheckBox::indicator {
            width: 16px;
            height: 16px;
            border: 1px solid #555555;
            border-radius: 3px;
            background-color: #3b3b3b;
        }
        
        QCheckBox::indicator:checked {
            background-color: #0078d4;
            border-color: #0078d4;
        }
        
        QProgressBar {
            background-color: #3b3b3b;
            border: 1px solid #555555;
            border-radius: 4px;
            text-align: center;
            color: #ffffff;
        }
        
        QProgressBar::chunk {
            background-color: #0078d4;
            border-radius: 3px;
        }
        
        QGroupBox {
            color: #ffffff;
            border: 1px solid #555555;
            border-radius: 4px;
            margin: 8px 0px;
            padding-top: 8px;
        }
        
        QGroupBox::title {
            subcontrol-origin: margin;
            left: 8px;
            padding: 0 4px 0 4px;
        }
        
        QTextEdit {
            background-color: #2b2b2b;
            color: #ffffff;
            border: 1px solid #555555;
            border-radius: 4px;
        }
        
        QListWidget {
            background-color: #2b2b2b;
            color: #ffffff;
            border: 1px solid #555555;
            border-radius: 4px;
        }
        
        QListWidget::item {
            padding: 4px;
            border-bottom: 1px solid #444444;
        }
        
        QListWidget::item:selected {
            background-color: #0078d4;
        }
        
        QSpinBox, QDateEdit {
            background-color: #3b3b3b;
            border: 1px solid #555555;
            padding: 6px;
            border-radius: 4px;
            color: #ffffff;
        }
        """
        
        app.setStyleSheet(style)
    
    def set_application_font(self, app: QApplication) -> None:
        """Set the application font to match Windows 11."""
        font = QFont("Segoe UI", 9)
        app.setFont(font)
    
    def run(self) -> int:
        """Run the application.
        
        Returns:
            Application exit code
        """
        try:
            # Create QApplication
            self.app = self.create_app()
            
            # Create main window
            self.main_window = MainWindow(self.config)
            
            # Show main window
            self.main_window.show()
            
            # Run event loop
            return self.app.exec()
            
        except Exception as e:
            logger.error(f"Application error: {e}")
            if self.app:
                QMessageBox.critical(
                    None,
                    "Application Error",
                    f"An error occurred: {e}\n\nThe application will now exit."
                )
            return 1


def main():
    """Main entry point for the GUI application."""
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Create and run application
    app = PoeSearchApp()
    return app.run()


if __name__ == "__main__":
    sys.exit(main())
