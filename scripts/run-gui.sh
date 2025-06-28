#!/bin/bash

# Poe Search GUI Launcher Script
# This script sets up the environment and launches the GUI application

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

print_status "Poe Search GUI Launcher"
print_status "Project root: $PROJECT_ROOT"

# Change to project directory
cd "$PROJECT_ROOT"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    print_warning "Virtual environment not found. Creating one..."
    python3 -m venv venv
    print_success "Virtual environment created"
fi

# Activate virtual environment
print_status "Activating virtual environment..."
source venv/bin/activate

# Check if GUI dependencies are installed
if ! python -c "import PyQt6" 2>/dev/null; then
    print_warning "GUI dependencies not found. Installing..."
    pip install -e ".[gui]"
    print_success "GUI dependencies installed"
fi

# Check if the application is properly installed
if ! python -c "import poe_search.gui" 2>/dev/null; then
    print_warning "Application not found. Installing..."
    pip install -e "."
    print_success "Application installed"
fi

# Set environment variables
export PYTHONPATH="$PROJECT_ROOT/src:$PYTHONPATH"
export POE_SEARCH_CONFIG_DIR="$PROJECT_ROOT/config"

# Create config directory if it doesn't exist
mkdir -p "$PROJECT_ROOT/config"

print_status "Launching Poe Search GUI..."
print_status "Press Ctrl+C to exit"

# Launch the GUI
python -m poe_search.gui

print_success "GUI application closed"
