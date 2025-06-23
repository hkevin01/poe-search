"""GUI module for Poe Search application."""

from poe_search.gui.main_window import MainWindow
from poe_search.gui.app import PoeSearchApp

__all__ = ["MainWindow", "PoeSearchApp"]


def main():
    """Entry point for the GUI application."""
    app = PoeSearchApp()
    app.run()


if __name__ == "__main__":
    main()
