#!/usr/bin/env python3
"""
Quick GUI Fix - Get Poe Search GUI working immediately

This script fixes the immediate import issues and gets the GUI functional
without full reorganization.
"""

import sys
import shutil
from pathlib import Path


def fix_immediate_issues():
    """Fix immediate issues to get GUI working."""
    print("🔧 Quick GUI Fix - Making GUI work now...")

    project_root = Path(__file__).parent

    # 1. Create missing directories
    required_dirs = [
        "src/poe_search/gui",
        "src/poe_search/api",
        "src/poe_search/core",
        "src/poe_search/services",
    ]

    for dir_path in required_dirs:
        full_path = project_root / dir_path
        full_path.mkdir(parents=True, exist_ok=True)
        print(f"✅ Created directory: {dir_path}")

        # Create __init__.py files
        init_file = full_path / "__init__.py"
        if not init_file.exists():
            init_file.write_text('"""Package module."""\n')
            print(f"✅ Created {dir_path}/__init__.py")

    # 2. Create basic main_window.py if it doesn't exist
    main_window_path = project_root / "src/poe_search/gui/main_window.py"
    if not main_window_path.exists():
        main_window_content = '''"""
Main GUI window for Poe Search.
"""

def run_gui():
    """Run the GUI application."""
    print("🚀 Starting Poe Search GUI...")

    try:
        from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel, QWidget, QVBoxLayout
        from PyQt6.QtCore import Qt
        import sys

        class MainWindow:
            def __init__(self):
                self.app = QApplication(sys.argv)
                self.window = QMainWindow()
                self.window.setWindowTitle("🔍 Poe Search - GUI Working!")
                self.window.setGeometry(200, 200, 600, 400)

                # Create central widget
                central_widget = QWidget()
                self.window.setCentralWidget(central_widget)
                layout = QVBoxLayout(central_widget)

                # Add content
                title = QLabel("🎉 Poe Search GUI is Working!")
                title.setStyleSheet("font-size: 24px; font-weight: bold; padding: 30px;")
                title.setAlignment(Qt.AlignmentFlag.AlignCenter)
                layout.addWidget(title)

                message = QLabel("""
The GUI is now functional!

To get the full application with all features:
1. Run: python run_comprehensive_organization.py
2. This will create the complete professional structure
3. Restart the GUI for full functionality

Current status: Basic GUI working ✅
                """)
                message.setStyleSheet("padding: 20px; font-size: 14px; line-height: 1.6;")
                message.setAlignment(Qt.AlignmentFlag.AlignCenter)
                layout.addWidget(message)

            def run(self):
                self.window.show()
                return self.app.exec()

        gui = MainWindow()
        return gui.run()

    except ImportError as e:
        print(f"❌ Missing PyQt6: {e}")
        print("Install with: pip install PyQt6")
        return 1
    except Exception as e:
        print(f"❌ GUI Error: {e}")
        return 1
'''
        main_window_path.write_text(main_window_content)
        print(f"✅ Created basic GUI: {main_window_path}")

    # 3. Create basic browser_client.py if needed
    browser_client_path = project_root / "src/poe_search/api/browser_client.py"
    if not browser_client_path.exists():
        browser_client_content = '''"""
Browser client placeholder.
"""

class PoeApiClient:
    """Placeholder API client."""

    def __init__(self, token=None, **kwargs):
        self.token = token

    def __enter__(self):
        return self

    def __exit__(self, *args):
        pass

    def get_conversations(self, limit=50, **kwargs):
        """Placeholder method."""
        return []
'''
        browser_client_path.write_text(browser_client_content)
        print(f"✅ Created placeholder browser client: {browser_client_path}")

    # 4. Fix pyproject.toml TOML syntax error
    pyproject_path = project_root / "pyproject.toml"
    if pyproject_path.exists():
        try:
            content = pyproject_path.read_text()
            # Fix Windows path separators in TOML
            fixed_content = content.replace('scripts\\\\', 'scripts/')
            fixed_content = fixed_content.replace('scripts\\', 'scripts/')
            pyproject_path.write_text(fixed_content)
            print("✅ Fixed pyproject.toml syntax")
        except Exception as e:
            print(f"⚠️  Could not fix pyproject.toml: {e}")

    # 5. Create simplified pyproject.toml if broken
    if not pyproject_path.exists() or "TOMLDecodeError" in str(e):
        simple_pyproject = '''[build-system]
requires = ["setuptools>=61.0", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "poe-search"
version = "1.3.0"
description = "Enhanced AI Conversation Manager for Poe.com"
authors = [{name = "Kevin", email = "kevin@example.com"}]
license = {text = "MIT"}
requires-python = ">=3.9"
dependencies = [
    "PyQt6>=6.5.0",
    "selenium>=4.15.0",
    "requests>=2.31.0",
    "beautifulsoup4>=4.12.0",
    "webdriver-manager>=4.0.0",
]

[project.optional-dependencies]
gui = ["PyQt6>=6.5.0"]
dev = [
    "pytest>=7.0.0",
    "black>=22.0.0",
    "flake8>=5.0.0",
]

[tool.setuptools.packages.find]
where = ["src"]

[tool.setuptools.package-dir]
"" = "src"
'''
        pyproject_path.write_text(simple_pyproject)
        print("✅ Created clean pyproject.toml")

    print("\n🎯 Quick fix complete!")
    return True


def install_package():
    """Install the package in development mode."""
    import subprocess

    print("📦 Installing package in development mode...")

    try:
        # Install in development mode
        result = subprocess.run([
            sys.executable, "-m", "pip", "install", "-e", "."
        ], capture_output=True, text=True, cwd=Path(__file__).parent)

        if result.returncode == 0:
            print("✅ Package installed successfully")
            return True
        else:
            print(f"❌ Installation failed: {result.stderr}")
            return False

    except Exception as e:
        print(f"❌ Installation error: {e}")
        return False


def test_imports():
    """Test that imports work."""
    print("🧪 Testing imports...")

    try:
        # Test poe_search import
        import poe_search
        print("✅ poe_search import: OK")

        # Test GUI import
        from poe_search.gui import main_window
        print("✅ poe_search.gui import: OK")

        # Test PyQt6
        from PyQt6.QtWidgets import QApplication
        print("✅ PyQt6 import: OK")

        return True

    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False


def main():
    """Main fix function."""
    print("🚀 Poe Search Quick GUI Fix")
    print("=" * 50)

    # 1. Fix immediate structure issues
    if not fix_immediate_issues():
        print("❌ Could not fix immediate issues")
        return 1

    # 2. Install package
    if not install_package():
        print("❌ Could not install package")
        return 1

    # 3. Test imports
    if not test_imports():
        print("❌ Imports still failing")
        return 1

    print("\n🎉 SUCCESS! GUI should now work!")
    print("\n🚀 Try running:")
    print("   python gui_launcher.py")
    print("\n📋 For full features, run:")
    print("   python run_comprehensive_organization.py")

    return 0


if __name__ == "__main__":
    sys.exit(main())
