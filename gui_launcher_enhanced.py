#!/usr/bin/env python3
"""
GUI Launcher for Poe Search - Enhanced AI Conversation Manager

Smart launcher that works with current project structure and guides
through organization process.
"""

import sys
import os
from pathlib import Path

def check_dependencies():
    """Check if required dependencies are available."""
    print("🚀 Starting Poe Search GUI v1.3 (Enhanced)...")

    missing_deps = []

    # Check PyQt6
    try:
        import PyQt6
        print("✅ PyQt6 found")
    except ImportError:
        print("❌ PyQt6 not found")
        missing_deps.append('PyQt6')

    # Check Selenium
    try:
        import selenium
        print("✅ Selenium found")
    except ImportError:
        print("❌ Selenium not found")
        missing_deps.append('selenium')

    return missing_deps

def setup_import_paths():
    """Setup import paths for current project structure."""
    project_root = Path(__file__).parent

    # Add both possible source locations to path
    possible_paths = [
        project_root / "src",  # New structure
        project_root,          # Current structure
    ]

    for path in possible_paths:
        if path.exists():
            sys.path.insert(0, str(path))

def check_project_organization():
    """Check if project has been organized."""
    project_root = Path(__file__).parent

    # Check for new structure indicators
    new_structure_paths = [
        project_root / "src" / "poe_search" / "api" / "browser_client.py",
        project_root / "src" / "poe_search" / "gui" / "main_window.py",
        project_root / "tests" / "unit",
        project_root / "docs" / "api",
    ]

    organized = all(path.exists() for path in new_structure_paths)

    if organized:
        print("✅ Project is organized with new structure")
        return True
    else:
        print("⚠️  Project needs organization")
        return False

def launch_organized_gui():
    """Launch GUI from organized structure."""
    try:
        from poe_search.gui.main_window import run_gui
        print("✅ Using organized GUI structure")
        return run_gui()
    except ImportError as e:
        print(f"❌ Failed to import from organized structure: {e}")
        return launch_setup_gui()

def launch_setup_gui():
    """Launch setup GUI for organization."""
    try:
        from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget,
                                     QVBoxLayout, QHBoxLayout, QLabel,
                                     QPushButton, QMessageBox, QTextEdit,
                                     QProgressBar)
        from PyQt6.QtCore import Qt, QThread, pyqtSignal
        from PyQt6.QtGui import QFont
        import subprocess

        class OrganizationThread(QThread):
            """Thread for running organization in background."""
            finished = pyqtSignal(bool, str)
            progress = pyqtSignal(str)

            def run(self):
                try:
                    self.progress.emit("Starting organization...")

                    result = subprocess.run([
                        sys.executable, 'run_comprehensive_organization.py'
                    ], capture_output=True, text=True,
                       cwd=Path(__file__).parent)

                    if result.returncode == 0:
                        self.finished.emit(True, result.stdout)
                    else:
                        self.finished.emit(False, result.stderr or "Unknown error")

                except Exception as e:
                    self.finished.emit(False, str(e))

        class SetupGUI:
            def __init__(self):
                self.app = QApplication(sys.argv)
                self.window = QMainWindow()
                self.window.setWindowTitle("🔍 Poe Search - Setup Required")
                self.window.setGeometry(200, 200, 700, 500)

                # Apply dark theme
                self.apply_theme()

                # Create central widget
                central_widget = QWidget()
                self.window.setCentralWidget(central_widget)
                layout = QVBoxLayout(central_widget)

                # Title
                title = QLabel("🔍 Poe Search - Enhanced AI Conversation Manager")
                title.setStyleSheet("font-size: 20px; font-weight: bold; padding: 20px; color: #ffffff;")
                title.setAlignment(Qt.AlignmentFlag.AlignCenter)
                layout.addWidget(title)

                # Status message
                status_text = """
📋 Project Organization Required

Your Poe Search project needs to be organized with the new professional structure.

🎯 What will be organized:
• Source code into logical modules (api/, gui/, services/, models/)
• Tests into comprehensive structure (unit/, integration/, e2e/)
• Documentation with guides and references
• Configuration files and assets
• Development tools and scripts

✨ Benefits after organization:
• Professional project structure following industry standards
• Comprehensive test suite with proper organization
• Complete documentation system
• Clean import patterns and better maintainability
• Ready for production deployment

Click "🚀 Organize Project" to transform your project!
                """

                status = QLabel(status_text.strip())
                status.setStyleSheet("""
                    padding: 20px;
                    background: #3c3c3c;
                    border-radius: 8px;
                    line-height: 1.6;
                    color: #ffffff;
                    border: 1px solid #555555;
                """)
                status.setWordWrap(True)
                layout.addWidget(status)

                # Progress bar (initially hidden)
                self.progress_bar = QProgressBar()
                self.progress_bar.setVisible(False)
                self.progress_bar.setStyleSheet("""
                    QProgressBar {
                        border: 2px solid #555555;
                        border-radius: 5px;
                        text-align: center;
                        color: white;
                        background: #2b2b2b;
                    }
                    QProgressBar::chunk {
                        background-color: #0078d4;
                        border-radius: 3px;
                    }
                """)
                layout.addWidget(self.progress_bar)

                # Progress text
                self.progress_text = QLabel("")
                self.progress_text.setVisible(False)
                self.progress_text.setStyleSheet("color: #0078d4; padding: 10px;")
                layout.addWidget(self.progress_text)

                # Buttons
                button_layout = QHBoxLayout()

                # Organize button
                self.organize_btn = QPushButton("🚀 Organize Project")
                self.organize_btn.setStyleSheet("""
                    QPushButton {
                        background-color: #0078d4;
                        color: white;
                        border: none;
                        padding: 15px 30px;
                        font-size: 16px;
                        font-weight: bold;
                        border-radius: 8px;
                    }
                    QPushButton:hover {
                        background-color: #106ebe;
                    }
                    QPushButton:disabled {
                        background-color: #555555;
                        color: #888888;
                    }
                """)
                self.organize_btn.clicked.connect(self.run_organization)
                button_layout.addWidget(self.organize_btn)

                # Manual organization button
                manual_btn = QPushButton("📚 View Manual Setup")
                manual_btn.setStyleSheet("""
                    QPushButton {
                        background-color: #555555;
                        color: white;
                        border: none;
                        padding: 15px 30px;
                        font-size: 16px;
                        border-radius: 8px;
                    }
                    QPushButton:hover {
                        background-color: #666666;
                    }
                """)
                manual_btn.clicked.connect(self.show_manual_setup)
                button_layout.addWidget(manual_btn)

                # Close button
                close_btn = QPushButton("Close")
                close_btn.setStyleSheet("""
                    QPushButton {
                        background-color: #666666;
                        color: white;
                        border: none;
                        padding: 15px 30px;
                        font-size: 16px;
                        border-radius: 8px;
                    }
                    QPushButton:hover {
                        background-color: #777777;
                    }
                """)
                close_btn.clicked.connect(self.window.close)
                button_layout.addWidget(close_btn)

                layout.addLayout(button_layout)

            def apply_theme(self):
                """Apply dark theme."""
                dark_style = """
                    QMainWindow {
                        background-color: #2b2b2b;
                        color: #ffffff;
                    }
                    QWidget {
                        background-color: #2b2b2b;
                        color: #ffffff;
                    }
                """
                self.app.setStyleSheet(dark_style)

            def run_organization(self):
                """Run the organization script."""
                # Show progress
                self.organize_btn.setEnabled(False)
                self.progress_bar.setVisible(True)
                self.progress_bar.setRange(0, 0)  # Indeterminate
                self.progress_text.setVisible(True)
                self.progress_text.setText("🚀 Starting project organization...")

                # Start organization thread
                self.org_thread = OrganizationThread()
                self.org_thread.progress.connect(self.update_progress)
                self.org_thread.finished.connect(self.organization_finished)
                self.org_thread.start()

            def update_progress(self, message):
                """Update progress display."""
                self.progress_text.setText(f"⚙️ {message}")

            def organization_finished(self, success, output):
                """Handle organization completion."""
                # Hide progress
                self.progress_bar.setVisible(False)
                self.progress_text.setVisible(False)
                self.organize_btn.setEnabled(True)

                if success:
                    QMessageBox.information(
                        self.window,
                        "Organization Complete! 🎉",
                        "✅ Project organization completed successfully!\n\n"
                        "Your project now has:\n"
                        "• Professional directory structure\n"
                        "• Organized source code and tests\n"
                        "• Complete documentation system\n"
                        "• Clean configuration management\n\n"
                        "Please restart the GUI to use the new structure.\n\n"
                        "Check ORGANIZATION_REPORT.md for details!"
                    )
                    self.window.close()
                else:
                    QMessageBox.warning(
                        self.window,
                        "Organization Failed",
                        f"❌ Organization failed:\n\n{output}\n\n"
                        "You can try manual organization or check the error above."
                    )

            def show_manual_setup(self):
                """Show manual setup instructions."""
                manual_text = """
Manual Setup Instructions:

1. Run Organization Script:
   python run_comprehensive_organization.py

2. Install Dependencies:
   pip install -r requirements/base.txt

3. Configure Tokens:
   Edit config/environments/tokens.json with your Poe.com tokens

4. Test Installation:
   python -m pytest tests/
   python gui_launcher.py

5. View Documentation:
   Check docs/ directory for complete guides

The organization script will create a professional project structure
with proper separation of source code, tests, documentation, and
configuration files.
                """

                QMessageBox.information(
                    self.window,
                    "Manual Setup Instructions",
                    manual_text.strip()
                )

            def run(self):
                """Run the application."""
                self.window.show()
                return self.app.exec()

        gui = SetupGUI()
        return gui.run()

    except ImportError as e:
        print(f"❌ Cannot create GUI: {e}")
        print("Please install PyQt6: pip install PyQt6")
        return 1

def main():
    """Main entry point."""
    # Check dependencies
    missing_deps = check_dependencies()

    if missing_deps:
        print(f"❌ Missing dependencies: {missing_deps}")
        print("Please install missing dependencies:")
        for dep in missing_deps:
            print(f"  pip install {dep}")
        return 1

    # Setup import paths
    setup_import_paths()

    # Check if project is organized
    if check_project_organization():
        return launch_organized_gui()
    else:
        return launch_setup_gui()

if __name__ == "__main__":
    sys.exit(main())
