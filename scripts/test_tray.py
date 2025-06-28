#!/usr/bin/env python3
"""Test script for system tray functionality."""

import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from PyQt6.QtGui import QAction, QIcon
from PyQt6.QtWidgets import QApplication, QMainWindow, QMenu, QMessageBox, QSystemTrayIcon


class TrayTestWindow(QMainWindow):
    """Simple test window for system tray functionality."""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Poe Search - Tray Test")
        self.setGeometry(100, 100, 400, 300)
        
        # Setup system tray
        self.setup_system_tray()
    
    def setup_system_tray(self):
        """Set up the system tray."""
        # Check if system tray is available
        if not QSystemTrayIcon.isSystemTrayAvailable():
            print("System tray is not available on this system")
            return
        
        # Create system tray icon
        self.tray_icon = QSystemTrayIcon(self)
        
        # Try to load tray icon from file
        icon_paths = [
            Path(__file__).parent.parent / "src" / "poe_search" / "gui" / 
            "resources" / "icons" / "tray_icon.png",
            Path(__file__).parent.parent / "src" / "poe_search" / "gui" / 
            "resources" / "icons" / "tray_icon_32x32.png",
        ]
        
        icon_loaded = False
        for icon_path in icon_paths:
            if icon_path.exists():
                self.tray_icon.setIcon(QIcon(str(icon_path)))
                icon_loaded = True
                print(f"Loaded tray icon from: {icon_path}")
                break
        
        if not icon_loaded:
            print("No tray icon files found")
            return
        
        self.tray_icon.setToolTip("Poe Search - Test")
        
        # Create tray menu
        tray_menu = QMenu()
        
        # Show/Hide action
        show_action = QAction("Show/Hide", self)
        show_action.triggered.connect(self.toggle_window_visibility)
        tray_menu.addAction(show_action)
        
        tray_menu.addSeparator()
        
        # Test action
        test_action = QAction("Test Message", self)
        test_action.triggered.connect(self.show_test_message)
        tray_menu.addAction(test_action)
        
        tray_menu.addSeparator()
        
        # Exit action
        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.quit_application)
        tray_menu.addAction(exit_action)
        
        # Set the menu
        self.tray_icon.setContextMenu(tray_menu)
        
        # Connect double-click to show window
        self.tray_icon.activated.connect(self.on_tray_activated)
        
        # Show the tray icon
        if self.tray_icon.show():
            print("System tray icon created successfully")
        else:
            print("Failed to show system tray icon")
    
    def toggle_window_visibility(self):
        """Toggle window visibility."""
        if self.isVisible():
            self.hide()
            self.tray_icon.showMessage(
                "Poe Search",
                "Application minimized to system tray",
                QSystemTrayIcon.MessageIcon.Information,
                2000
            )
        else:
            self.show()
            self.raise_()
            self.activateWindow()
    
    def on_tray_activated(self, reason):
        """Handle tray icon activation."""
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            self.toggle_window_visibility()
    
    def show_test_message(self):
        """Show a test message."""
        QMessageBox.information(self, "Test", "Tray menu is working!")
    
    def quit_application(self):
        """Quit the application."""
        if hasattr(self, 'tray_icon') and self.tray_icon:
            self.tray_icon.hide()
        QApplication.quit()
    
    def closeEvent(self, event):
        """Handle close event."""
        if (hasattr(self, 'tray_icon') and 
            self.tray_icon and 
            self.tray_icon.isVisible()):
            
            reply = QMessageBox.question(
                self,
                "Poe Search",
                "The application will be minimized to the system tray.\n"
                "To quit the application, right-click the tray icon and "
                "select 'Exit'.\n\n"
                "Do you want to minimize to tray?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.Yes
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                self.hide()
                self.tray_icon.showMessage(
                    "Poe Search",
                    "Application minimized to system tray",
                    QSystemTrayIcon.MessageIcon.Information,
                    2000
                )
                event.ignore()
            else:
                self.quit_application()
                event.accept()
        else:
            event.accept()


def main():
    """Main function."""
    app = QApplication(sys.argv)
    app.setApplicationName("Poe Search Tray Test")
    
    # Set application icon
    icon_paths = [
        Path(__file__).parent.parent / "src" / "poe_search" / "gui" / 
        "resources" / "icons" / "app_icon.png",
        Path(__file__).parent.parent / "src" / "poe_search" / "gui" / 
        "resources" / "icons" / "app_icon_128x128.png",
    ]
    
    for icon_path in icon_paths:
        if icon_path.exists():
            app.setWindowIcon(QIcon(str(icon_path)))
            break
    
    window = TrayTestWindow()
    window.show()
    
    print("Poe Search Tray Test started")
    print("Right-click the tray icon to see the menu")
    print("Double-click the tray icon to show/hide the window")
    
    return app.exec()


if __name__ == "__main__":
    sys.exit(main()) 