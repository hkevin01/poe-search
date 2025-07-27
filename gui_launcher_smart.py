#!/usr/bin/env python3
"""
GUI Launcher for Poe Search - Smart Launcher with Organization Support

This launcher detects the current project structure and either runs the GUI
or guides you through the organization process.
"""

import sys
from pathlib import Path


def check_dependencies():
    """Check for required dependencies."""
    print("🚀 Starting Poe Search GUI v1.3 (Smart Launcher)...")

    missing_deps = []

    try:
        import PyQt6  # noqa: F401
        print("✅ PyQt6 found")
    except ImportError:
        print("❌ PyQt6 not found")
        missing_deps.append('PyQt6')

    try:
        import selenium  # noqa: F401
        print("✅ Selenium found")
    except ImportError:
        print("❌ Selenium not found")
        missing_deps.append('selenium')

    return missing_deps


def setup_import_paths():
    """Setup import paths."""
    project_root = Path(__file__).parent
    sys.path.insert(0, str(project_root / "src"))
    sys.path.insert(0, str(project_root))


def check_project_organization():
    """Check if project has been organized."""
    project_root = Path(__file__).parent

    # Check for organized structure
    organized_indicators = [
        project_root / "src" / "poe_search" / "gui" / "main_window.py",
        project_root / "src" / "poe_search" / "api" / "browser_client.py",
        project_root / "tests" / "unit",
    ]

    return all(path.exists() for path in organized_indicators)


def try_run_organized_gui():
    """Try to run GUI from organized structure."""
    try:
        from poe_search.gui.main_window import run_gui
        print("✅ Using organized GUI structure")
        return run_gui()
    except ImportError as e:
        print(f"❌ Cannot import from organized structure: {e}")
        return None


def show_organization_gui():
    """Show GUI for project organization."""
    try:
        from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget,
                                     QVBoxLayout, QHBoxLayout, QLabel,
                                     QPushButton, QMessageBox, QProgressBar)
        from PyQt6.QtCore import Qt, QThread, pyqtSignal
        import subprocess

        class OrganizationWorker(QThread):
            finished = pyqtSignal(bool, str)
            progress = pyqtSignal(str)

            def run(self):
                try:
                    self.progress.emit("Starting comprehensive organization...")

                    # Run the organization script
                    result = subprocess.run([
                        sys.executable, 'run_comprehensive_organization.py'
                    ], capture_output=True, text=True, cwd=Path(__file__).parent)

                    success = result.returncode == 0
                    output = result.stdout if success else (result.stderr or "Organization failed")
                    self.finished.emit(success, output)

                except Exception as e:
                    self.finished.emit(False, f"Error running organization: {str(e)}")

        class OrganizationGUI:
            def __init__(self):
                self.app = QApplication(sys.argv)
                self.window = QMainWindow()
                self.window.setWindowTitle("🔍 Poe Search - Organization Required")
                self.window.setGeometry(250, 250, 650, 450)

                # Apply theme
                self.app.setStyleSheet("""
                    QMainWindow, QWidget {
                        background-color: #2b2b2b;
                        color: #ffffff;
                    }
                """)

                self.setup_ui()

            def setup_ui(self):
                central = QWidget()
                self.window.setCentralWidget(central)
                layout = QVBoxLayout(central)

                # Title
                title = QLabel("🔍 Poe Search - Project Organization")
                title.setStyleSheet("font-size: 18px; font-weight: bold; padding: 15px;")
                title.setAlignment(Qt.AlignmentFlag.AlignCenter)
                layout.addWidget(title)

                # Description
                desc = QLabel("""
📋 Your project needs to be organized for full functionality.

The organization process will:
• Create professional directory structure
• Move source code to logical modules
• Set up comprehensive test structure
• Generate complete documentation
• Configure development tools

This is a one-time setup that makes your project production-ready!
                """.strip())
                desc.setStyleSheet("""
                    padding: 15px; background: #3a3a3a; border-radius: 6px;
                    border: 1px solid #555; line-height: 1.5;
                """)
                desc.setWordWrap(True)
                layout.addWidget(desc)

                # Progress section
                self.progress_bar = QProgressBar()
                self.progress_bar.setVisible(False)
                self.progress_bar.setStyleSheet("""
                    QProgressBar {
                        border: 1px solid #555; border-radius: 3px;
                        text-align: center; background: #3a3a3a;
                    }
                    QProgressBar::chunk {
                        background: #0078d4; border-radius: 2px;
                    }
                """)
                layout.addWidget(self.progress_bar)

                self.progress_label = QLabel("")
                self.progress_label.setVisible(False)
                self.progress_label.setStyleSheet("color: #0078d4; padding: 8px;")
                layout.addWidget(self.progress_label)

                # Buttons
                button_layout = QHBoxLayout()

                self.organize_btn = QPushButton("🚀 Start Organization")
                self.organize_btn.setStyleSheet("""
                    QPushButton {
                        background: #0078d4; color: white; border: none;
                        padding: 12px 24px; font-size: 14px; font-weight: bold;
                        border-radius: 6px;
                    }
                    QPushButton:hover { background: #106ebe; }
                    QPushButton:disabled { background: #555; color: #888; }
                """)
                self.organize_btn.clicked.connect(self.start_organization)
                button_layout.addWidget(self.organize_btn)

                manual_btn = QPushButton("📖 Manual Instructions")
                manual_btn.setStyleSheet("""
                    QPushButton {
                        background: #555; color: white; border: none;
                        padding: 12px 24px; font-size: 14px; border-radius: 6px;
                    }
                    QPushButton:hover { background: #666; }
                """)
                manual_btn.clicked.connect(self.show_manual_instructions)
                button_layout.addWidget(manual_btn)

                close_btn = QPushButton("Close")
                close_btn.setStyleSheet("""
                    QPushButton {
                        background: #666; color: white; border: none;
                        padding: 12px 24px; font-size: 14px; border-radius: 6px;
                    }
                    QPushButton:hover { background: #777; }
                """)
                close_btn.clicked.connect(self.window.close)
                button_layout.addWidget(close_btn)

                layout.addLayout(button_layout)

            def start_organization(self):
                """Start the organization process."""
                self.organize_btn.setEnabled(False)
                self.progress_bar.setVisible(True)
                self.progress_bar.setRange(0, 0)  # Indeterminate
                self.progress_label.setVisible(True)

                # Start worker thread
                self.worker = OrganizationWorker()
                self.worker.progress.connect(self.update_progress)
                self.worker.finished.connect(self.organization_complete)
                self.worker.start()

            def update_progress(self, message):
                """Update progress display."""
                self.progress_label.setText(f"🔄 {message}")

            def organization_complete(self, success, output):
                """Handle organization completion."""
                self.progress_bar.setVisible(False)
                self.progress_label.setVisible(False)
                self.organize_btn.setEnabled(True)

                if success:
                    QMessageBox.information(
                        self.window, "🎉 Organization Complete!",
                        "✅ Your project has been successfully organized!\n\n"
                        "New features:\n"
                        "• Professional directory structure\n"
                        "• Comprehensive test suite\n"
                        "• Complete documentation\n"
                        "• Modern development workflow\n\n"
                        "Please restart the GUI to access all features.\n\n"
                        "📄 Check ORGANIZATION_REPORT.md for details!"
                    )
                    self.window.close()
                else:
                    QMessageBox.warning(
                        self.window, "❌ Organization Failed",
                        f"The organization process encountered an error:\n\n{output}\n\n"
                        "You can try the manual instructions or check the error above."
                    )

            def show_manual_instructions(self):
                """Show manual organization instructions."""
                instructions = """
Manual Organization Steps:

1️⃣ Run Organization Script:
   python run_comprehensive_organization.py

2️⃣ Install Dependencies:
   pip install -r requirements/base.txt

3️⃣ Configure Authentication:
   Edit config/environments/tokens.json

4️⃣ Test Installation:
   python -m pytest tests/
   python gui_launcher.py

5️⃣ Explore Documentation:
   Open docs/ directory for guides

The organization creates a professional project structure
following modern Python development best practices.
                """

                QMessageBox.information(
                    self.window, "📖 Manual Instructions",
                    instructions.strip()
                )

            def run(self):
                self.window.show()
                return self.app.exec()

        gui = OrganizationGUI()
        return gui.run()

    except ImportError as e:
        print(f"❌ Cannot create organization GUI: {e}")
        print("\n📋 Manual Organization Steps:")
        print("1. Install PyQt6: pip install PyQt6")
        print("2. Run: python run_comprehensive_organization.py")
        print("3. Restart: python gui_launcher.py")
        return 1


def main():
    """Main launcher logic."""
    # Check dependencies
    missing_deps = check_dependencies()
    if missing_deps:
        print(f"❌ Missing dependencies: {missing_deps}")
        print("Install with: pip install " + " ".join(missing_deps))
        return 1

    # Setup paths
    setup_import_paths()

    # Check if organized
    if check_project_organization():
        print("✅ Project is organized - launching full GUI")
        result = try_run_organized_gui()
        if result is not None:
            return result

    # Show organization GUI
    print("⚠️ Project needs organization - showing setup")
    return show_organization_gui()


if __name__ == "__main__":
    sys.exit(main())
