"""Main entry point for the GUI application."""

import sys

from poe_search.gui.app import PoeSearchApp


def main():
    """Entry point for the GUI application."""
    app = PoeSearchApp()
    return app.run()


if __name__ == "__main__":
    sys.exit(main()) 