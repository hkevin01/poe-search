#!/usr/bin/env python3
"""
Auto-installer utility for handling missing Python dependencies.
This module provides functions to automatically install missing packages before running scripts.
"""

import importlib
import logging
import subprocess
import sys
from typing import Dict, List, Optional

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def install_package(package_name: str, pip_name: Optional[str] = None) -> bool:
    """Install a package using pip.
    
    Args:
        package_name: Name of the package to install
        pip_name: Alternative pip package name if different from import name
        
    Returns:
        True if installation successful, False otherwise
    """
    install_name = pip_name or package_name
    try:
        logger.info(f"Installing {install_name}...")
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", install_name
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        logger.info(f"Successfully installed {install_name}")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to install {install_name}: {e}")
        return False

def check_and_install_packages(required_packages: List[Dict[str, str]]) -> bool:
    """Check for required packages and install missing ones.
    
    Args:
        required_packages: List of dicts with 'import' and optional 'pip' keys
        
    Returns:
        True if all packages are available after installation attempts
    """
    all_available = True
    
    for pkg_info in required_packages:
        import_name = pkg_info['import']
        pip_name = pkg_info.get('pip', import_name)
        
        try:
            importlib.import_module(import_name)
            logger.debug(f"✓ {import_name} is available")
        except ImportError:
            logger.warning(f"✗ {import_name} not found, attempting to install...")
            if install_package(import_name, pip_name):
                try:
                    # Clear import cache and try again
                    if import_name in sys.modules:
                        del sys.modules[import_name]
                    importlib.import_module(import_name)
                    logger.info(f"✓ {import_name} now available after installation")
                except ImportError:
                    logger.error(f"✗ {import_name} still not available after installation")
                    all_available = False
            else:
                all_available = False
    
    return all_available

def ensure_gui_dependencies() -> bool:
    """Ensure GUI-specific dependencies are available."""
    gui_packages = [
        {'import': 'PyQt6', 'pip': 'PyQt6'},
        {'import': 'PyQt6.QtCore'},
        {'import': 'PyQt6.QtWidgets'},
        {'import': 'PyQt6.QtGui'},
    ]
    return check_and_install_packages(gui_packages)

def ensure_api_dependencies() -> bool:
    """Ensure API-specific dependencies are available."""
    api_packages = [
        {'import': 'httpx'},
        {'import': 'requests'},
        {'import': 'pydantic'},
        {'import': 'fastapi_poe', 'pip': 'fastapi-poe'},
        {'import': 'poe_api_wrapper', 'pip': 'poe-api-wrapper'},
    ]
    return check_and_install_packages(api_packages)

def ensure_database_dependencies() -> bool:
    """Ensure database-specific dependencies are available."""
    db_packages = [
        {'import': 'sqlalchemy', 'pip': 'SQLAlchemy'},
    ]
    return check_and_install_packages(db_packages)

def ensure_compatibility_dependencies() -> bool:
    """Ensure compatibility dependencies (pandas/numpy) are correctly installed."""
    compat_packages = [
        {'import': 'numpy', 'pip': 'numpy<2.0'},  # Use compatible numpy version
        {'import': 'pandas', 'pip': 'pandas>=1.5.0,<2.0.0'},  # Use compatible pandas version
    ]
    return check_and_install_packages(compat_packages)

def ensure_testing_dependencies() -> bool:
    """Ensure testing dependencies are available."""
    test_packages = [
        {'import': 'pytest'},
        {'import': 'pytest_qt', 'pip': 'pytest-qt'},
    ]
    return check_and_install_packages(test_packages)

def ensure_browser_dependencies() -> bool:
    """Ensure browser automation dependencies are available."""
    browser_packages = [
        {'import': 'browser_cookie3', 'pip': 'browser-cookie3'},
        {'import': 'playwright'},
        {'import': 'keyring'},
    ]
    return check_and_install_packages(browser_packages)

def ensure_all_dependencies() -> bool:
    """Ensure all project dependencies are available."""
    logger.info("Checking and installing all project dependencies...")
    
    success = True
    success &= ensure_compatibility_dependencies()  # Do this first to avoid conflicts
    success &= ensure_gui_dependencies()
    success &= ensure_api_dependencies()
    success &= ensure_database_dependencies()
    success &= ensure_testing_dependencies()
    success &= ensure_browser_dependencies()
    
    if success:
        logger.info("✅ All dependencies are available")
    else:
        logger.error("❌ Some dependencies could not be installed")
    
    return success

if __name__ == "__main__":
    ensure_all_dependencies()
