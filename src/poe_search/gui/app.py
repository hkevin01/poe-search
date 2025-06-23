"""Main application class for Poe Search GUI."""

import sys
import logging
from pathlib import Path
from typing import Optional

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt, QDir
from PyQt6.QtGui import QIcon, QFont

import qdarktheme

from poe_search.gui.main_window import MainWindow
from poe_search.utils.config import load_config, setup_logging

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
        
        # Setup logging
        setup_logging(self.config)
        
    def setup_application(self) -> QApplication:
        """Set up the QApplication with Windows 11 styling."""
        # Enable high DPI scaling
        QApplication.setHighDpiScaleFactorRoundingPolicy(
            Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
        )
        
        app = QApplication(sys.argv)
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
        else:
            # Use a default icon from system
            app.setWindowIcon(app.style().standardIcon(app.style().StandardPixmap.SP_ComputerIcon))
    
    def apply_windows11_theme(self, app: QApplication) -> None:
        """Apply Windows 11 dark theme styling."""
        # Use qdarktheme for modern dark theme
        qdarktheme.setup_theme("auto")  # Auto-detect system theme
        
        # Additional Windows 11 specific styling
        app.setStyleSheet(app.styleSheet() + """
            /* Windows 11 specific styling */
            QMainWindow {
                background-color: #202020;
            }
            
            QMenuBar {
                background-color: #2b2b2b;
                color: #ffffff;
                border: none;
                padding: 4px;
            }
            
            QMenuBar::item {
                background-color: transparent;
                padding: 8px 12px;
                border-radius: 4px;
            }
            
            QMenuBar::item:selected {
                background-color: #3d3d3d;
            }
            
            QStatusBar {
                background-color: #2b2b2b;
                color: #ffffff;
                border-top: 1px solid #404040;
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
                color: #808080;
            }
            
            QLineEdit {
                background-color: #323232;
                border: 2px solid #404040;
                border-radius: 4px;
                padding: 8px;
                color: #ffffff;
                font-size: 14px;
            }
            
            QLineEdit:focus {
                border-color: #0078d4;
            }
            
            QTableWidget {
                background-color: #2b2b2b;
                alternate-background-color: #323232;
                gridline-color: #404040;
                selection-background-color: #0078d4;
                border: 1px solid #404040;
                border-radius: 4px;
            }
            
            QTableWidget::item {
                padding: 8px;
                border: none;
            }
            
            QHeaderView::section {
                background-color: #3d3d3d;
                color: #ffffff;
                padding: 8px;
                border: none;
                border-right: 1px solid #404040;
                font-weight: 600;
            }
            
            QScrollBar:vertical {
                background-color: #2b2b2b;
                width: 12px;
                border-radius: 6px;
            }
            
            QScrollBar::handle:vertical {
                background-color: #404040;
                border-radius: 6px;
                min-height: 20px;
            }
            
            QScrollBar::handle:vertical:hover {
                background-color: #505050;
            }
            
            QTabWidget::pane {
                border: 1px solid #404040;
                background-color: #2b2b2b;
                border-radius: 4px;
            }
            
            QTabBar::tab {
                background-color: #3d3d3d;
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
                background-color: #505050;
            }
            
            QProgressBar {
                border: 1px solid #404040;
                border-radius: 4px;
                text-align: center;
                background-color: #323232;
            }
            
            QProgressBar::chunk {
                background-color: #0078d4;
                border-radius: 3px;
            }
            
            QComboBox {
                background-color: #323232;
                border: 2px solid #404040;
                border-radius: 4px;
                padding: 8px;
                color: #ffffff;
                min-width: 100px;
            }
            
            QComboBox:focus {
                border-color: #0078d4;
            }
            
            QComboBox::drop-down {
                border: none;
                width: 30px;
            }
            
            QComboBox::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid #ffffff;
                margin-top: 2px;
            }
            
            /* Tooltip styling */
            QToolTip {
                background-color: #323232;
                color: #ffffff;
                border: 1px solid #404040;
                border-radius: 4px;
                padding: 8px;
                font-size: 12px;
            }
        """)
    
    def set_application_font(self, app: QApplication) -> None:
        """Set the application font to match Windows 11."""
        # Use Segoe UI Variable if available, fallback to Segoe UI
        font = QFont("Segoe UI Variable", 10)
        if not font.exactMatch():
            font = QFont("Segoe UI", 10)
        
        font.setWeight(QFont.Weight.Normal)
        app.setFont(font)
    
    def run(self) -> int:
        """Run the application.
        
        Returns:
            Exit code
        """
        try:
            self.app = self.setup_application()
            
            # Create and show main window
            self.main_window = MainWindow(config=self.config)
            self.main_window.show()
            
            logger.info("Poe Search GUI started successfully")
            
            # Run the event loop
            return self.app.exec()
            
        except Exception as e:
            logger.error(f"Failed to start GUI application: {e}")
            if self.app:
                self.app.quit()
            return 1
    
    def quit(self) -> None:
        """Quit the application."""
        if self.app:
            self.app.quit()
