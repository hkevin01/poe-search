#!/bin/bash
# Setup Playwright in venv and run the Poe.com cookie capture script

set -e

# Activate venv
source venv/bin/activate

# Install Playwright and browsers
pip install --upgrade pip
pip install playwright
python -m playwright install

# Run the cookie capture script
python scripts/capture_poe_cookies.py 