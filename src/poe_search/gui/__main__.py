"""Main entry point for the Poe Search GUI application."""

import logging
import sys
from poe_search.gui.app import PoeSearchApp

# Enable debug logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('poe_search.log')
    ]
)


def main():
    """Main entry point for the GUI application."""
    app = PoeSearchApp()
    sys.exit(app.run())


if __name__ == "__main__":
    main()