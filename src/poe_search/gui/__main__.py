# src/poe_search/gui/__main__.py
"""
Poe Search GUI - Main Entry Point
This module provides the primary entry point for the PyQt6 GUI application.
"""

import sys
import os
import logging
from pathlib import Path
from typing import Optional

# Ensure the project root is in the Python path
project_root = Path(__file__).parent.parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

try:
    from PyQt6.QtWidgets import QApplication, QMessageBox
    from PyQt6.QtCore import Qt, QTimer
    from PyQt6.QtGui import QIcon
except ImportError as e:
    print(f"❌ PyQt6 not found: {e}")
    print("📦 Install with: pip install PyQt6")
    sys.exit(1)

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def setup_application() -> QApplication:
    """Set up the QApplication with proper configuration"""
    # Enable high DPI scaling
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )
    
    app = QApplication(sys.argv)
    app.setApplicationName("Poe Search")
    app.setApplicationDisplayName("Poe Search - AI Conversation Manager")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("PoeSearch")
    app.setOrganizationDomain("poe-search.dev")
    
    # Set application icon if available
    icon_paths = [
        project_root / "assets" / "icon.png",
        project_root / "assets" / "logo.png", 
        project_root / "src" / "poe_search" / "gui" / "assets" / "icon.png"
    ]
    
    for icon_path in icon_paths:
        if icon_path.exists():
            app.setWindowIcon(QIcon(str(icon_path)))
            break
    
    # Apply dark theme
    app.setStyleSheet("""
        QApplication {
            background-color: #1e1e1e;
            color: #ffffff;
            font-family: 'Segoe UI', Arial, sans-serif;
        }
        QMainWindow {
            background-color: #1e1e1e;
            color: #ffffff;
        }
        QWidget {
            background-color: #1e1e1e;
            color: #ffffff;
        }
    """)
    
    return app

def import_main_window():
    """Import the main window with proper error handling"""
    try:
        # Try relative import first
        from .main_window import PoeSearchMainWindow
        return PoeSearchMainWindow
    except ImportError:
        try:
            # Try absolute import
            from poe_search.gui.main_window import PoeSearchMainWindow
            return PoeSearchMainWindow
        except ImportError:
            try:
                # Try direct import from src
                from src.poe_search.gui.main_window import PoeSearchMainWindow
                return PoeSearchMainWindow
            except ImportError as e:
                logger.error(f"Failed to import main window: {e}")
                return None

def check_dependencies() -> list:
    """Check for required dependencies and return missing ones"""
    missing = []
    
    required_packages = [
        ('PyQt6', 'PyQt6'),
        ('selenium', 'selenium'),
        ('webdriver_manager', 'webdriver-manager')
    ]
    
    for package_name, install_name in required_packages:
        try:
            __import__(package_name)
        except ImportError:
            missing.append(install_name)
    
    return missing

def show_dependency_error(missing_packages: list):
    """Show error dialog for missing dependencies"""
    app = QApplication([])  # Minimal app for error dialog
    
    message = (
        "Missing Required Dependencies\n\n"
        f"The following packages are required but not installed:\n"
        f"• {chr(10).join(missing_packages)}\n\n"
        f"Install them with:\n"
        f"pip install {' '.join(missing_packages)}\n\n"
        f"Or install the full GUI package:\n"
        f"pip install -e '.[gui]'"
    )
    
    QMessageBox.critical(None, "Poe Search - Dependency Error", message)
    return 1

def show_import_error():
    """Show error dialog for import failures"""
    app = QApplication([])  # Minimal app for error dialog
    
    message = (
        "GUI Import Error\n\n"
        "Failed to import the main window module.\n\n"
        "This usually means:\n"
        "• The project structure is incorrect\n"
        "• You're not running from the project root\n"
        "• The package isn't properly installed\n\n"
        "Try:\n"
        "1. cd to the project root directory\n"
        "2. pip install -e '.[gui]'\n"
        "3. python -m poe_search.gui"
    )
    
    QMessageBox.critical(None, "Poe Search - Import Error", message)
    return 1

def handle_exception(exc_type, exc_value, exc_traceback):
    """Global exception handler for better error reporting"""
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    
    logger.critical("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))
    
    # Try to show error dialog if QApplication exists
    if QApplication.instance():
        error_msg = f"An unexpected error occurred:\n\n{exc_type.__name__}: {exc_value}"
        QMessageBox.critical(None, "Poe Search - Unexpected Error", error_msg)

def main() -> int:
    """Main entry point for the Poe Search GUI application"""
    try:
        # Set up global exception handling
        sys.excepthook = handle_exception
        
        logger.info("🚀 Starting Poe Search GUI...")
        logger.info(f"📁 Project root: {project_root}")
        logger.info(f"🐍 Python: {sys.version}")
        logger.info(f"📂 Working directory: {os.getcwd()}")
        
        # Check dependencies
        missing_deps = check_dependencies()
        if missing_deps:
            logger.error(f"❌ Missing dependencies: {missing_deps}")
            return show_dependency_error(missing_deps)
        
        logger.info("✅ All dependencies found")
        
        # Import main window
        MainWindow = import_main_window()
        if MainWindow is None:
            logger.error("❌ Failed to import main window")
            return show_import_error()
        
        logger.info("✅ Main window imported successfully")
        
        # Set up application
        app = setup_application()
        logger.info("✅ QApplication created")
        
        # Create and show main window
        try:
            window = MainWindow()
            logger.info("✅ Main window created")
            
            window.show()
            logger.info("✅ Main window displayed")
            
            # Center window on screen
            QTimer.singleShot(100, lambda: center_window(window))
            
        except Exception as e:
            logger.error(f"❌ Failed to create/show main window: {e}")
            QMessageBox.critical(
                None, 
                "Poe Search - Startup Error",
                f"Failed to create main window:\n\n{str(e)}\n\n"
                f"Please check the logs for more details."
            )
            return 1
        
        logger.info("🎉 GUI launched successfully! Starting event loop...")
        
        # Start the application event loop
        return app.exec()
        
    except KeyboardInterrupt:
        logger.info("👋 Application interrupted by user")
        return 0
    except Exception as e:
        logger.error(f"❌ Fatal error during startup: {e}")
        import traceback
        traceback.print_exc()
        
        # Try to show error dialog
        try:
            app = QApplication([])
            QMessageBox.critical(
                None,
                "Poe Search - Fatal Error", 
                f"A fatal error occurred during startup:\n\n{str(e)}\n\n"
                f"Please check the console output for details."
            )
        except:
            pass  # If we can't even show an error dialog, just exit
        
        return 1

def center_window(window):
    """Center the window on the screen"""
    try:
        screen = QApplication.primaryScreen()
        if screen:
            screen_geometry = screen.availableGeometry()
            window_geometry = window.frameGeometry()
            center_point = screen_geometry.center()
            window_geometry.moveCenter(center_point)
            window.move(window_geometry.topLeft())
    except Exception as e:
        logger.warning(f"Failed to center window: {e}")

def gui_main():
    """Alternative entry point function"""
    return main()

# Support for different calling patterns
if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)