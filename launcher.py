#!/usr/bin/env python3
# launcher.py - Simple Python launcher for debugging

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
        
        # Try to import our API client with correct name
        try:
            from poe_search.api.client import PoeAPIClient  # Correct name!
            print("✅ API client found")
        except ImportError as e:
            print(f"❌ API client not found: {e}")
            return 1
        
        # Try to import and create a simple GUI
        try:
            from PyQt6.QtWidgets import (
                QApplication, QMainWindow, QWidget, QVBoxLayout, 
                QLabel, QPushButton, QTextEdit, QHBoxLayout, QMessageBox
            )
            from PyQt6.QtCore import Qt
            
            print("✅ Creating simple GUI...")
            
            app = QApplication(sys.argv)
            app.setApplicationName("Poe Search")
            
            # Create simple main window
            window = QMainWindow()
            window.setWindowTitle("Poe Search - AI Conversation Manager")
            window.setGeometry(100, 100, 1200, 800)
            
            # Central widget
            central_widget = QWidget()
            window.setCentralWidget(central_widget)
            layout = QVBoxLayout(central_widget)
            
            # Header
            header = QLabel("🔍 Poe Search - AI Conversation Manager")
            header.setStyleSheet("""
                QLabel {
                    font-size: 24px;
                    font-weight: bold;
                    color: #0078d4;
                    padding: 20px;
                    text-align: center;
                }
            """)
            header.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(header)
            
            # Status area
            status_text = QTextEdit()
            status_text.setPlainText("""
✅ Poe Search GUI is running!

This is a simple test interface to verify the application works.

Features available:
• ✅ PyQt6 GUI framework loaded
• ✅ API client (PoeAPIClient) imported successfully
• ✅ Project structure recognized
• 🔧 Ready for full GUI implementation

Next steps:
1. Add your Poe token to connect to your account
2. Implement the full conversation browser
3. Add search and filtering capabilities

Status: Ready for development!
            """)
            status_text.setStyleSheet("""
                QTextEdit {
                    background-color: #1e1e1e;
                    color: #ffffff;
                    border: 1px solid #404040;
                    border-radius: 8px;
                    padding: 15px;
                    font-family: 'Consolas', 'Monaco', monospace;
                    font-size: 12px;
                }
            """)
            layout.addWidget(status_text)
            
            # Button area
            button_layout = QHBoxLayout()
            
            test_button = QPushButton("🧪 Test API Client")
            test_button.setStyleSheet("""
                QPushButton {
                    background-color: #0078d4;
                    color: white;
                    border: none;
                    border-radius: 6px;
                    padding: 10px 20px;
                    font-size: 14px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #106ebe;
                }
            """)
            
            def test_api():
                try:
                    # Test creating API client
                    client = PoeAPIClient(token="test_token", headless=True)
                    QMessageBox.information(window, "Test Result", 
                        "✅ API Client created successfully!\n\n"
                        "The PoeAPIClient class is working correctly.")
                except Exception as e:
                    QMessageBox.warning(window, "Test Error", 
                        f"❌ API Client test failed:\n\n{str(e)}")
            
            test_button.clicked.connect(test_api)
            button_layout.addWidget(test_button)
            
            close_button = QPushButton("❌ Close")
            close_button.setStyleSheet("""
                QPushButton {
                    background-color: #d13438;
                    color: white;
                    border: none;
                    border-radius: 6px;
                    padding: 10px 20px;
                    font-size: 14px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #b52d31;
                }
            """)
            close_button.clicked.connect(window.close)
            button_layout.addWidget(close_button)
            
            layout.addLayout(button_layout)
            
            # Apply dark theme
            app.setStyleSheet("""
                QMainWindow {
                    background-color: #1e1e1e;
                    color: #ffffff;
                }
                QWidget {
                    background-color: #1e1e1e;
                    color: #ffffff;
                }
            """)
            
            window.show()
            print("✅ GUI launched successfully!")
            
            return app.exec()
            
        except Exception as e:
            print(f"❌ Failed to create GUI: {e}")
            import traceback
            traceback.print_exc()
            return 1
        
    except Exception as e:
        print(f"❌ Failed to launch GUI: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())