"""Basic test to verify GUI components can be imported and initialized."""

import pytest
import sys
from unittest.mock import patch


def test_gui_imports():
    """Test that GUI modules can be imported without PyQt6 being installed."""
    try:
        # Try importing GUI modules
        from poe_search.gui import main
        from poe_search.gui.app import PoeSearchApp
        from poe_search.gui.main_window import MainWindow
        
        # If PyQt6 is available, test basic initialization
        import PyQt6
        assert True  # Imports successful
        
    except ImportError as e:
        if "PyQt6" in str(e):
            pytest.skip("PyQt6 not installed - GUI tests skipped")
        else:
            raise


def test_gui_optional_dependency():
    """Test that the main package works without GUI dependencies."""
    # Test that core functionality works without PyQt6
    from poe_search import __version__
    from poe_search.storage.database import Database
    from poe_search.search.engine import SearchEngine
    
    # These should work regardless of GUI dependencies
    assert __version__ is not None


@pytest.mark.skipif(
    "PyQt6" not in sys.modules and not pytest.importorskip("PyQt6", reason="PyQt6 not available"),
    reason="PyQt6 not installed"
)
def test_gui_main_function():
    """Test GUI main function (only if PyQt6 is available)."""
    from poe_search.gui import main
    
    # Test that main function exists and is callable
    assert callable(main)


if __name__ == "__main__":
    test_gui_imports()
    test_gui_optional_dependency()
    print("✅ All GUI import tests passed!")
