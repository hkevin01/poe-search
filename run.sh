#!/bin/bash

# Poe Search - Enhanced Launcher Script
# Enhanced version with better error handling and GUI management

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$SCRIPT_DIR"

# Configuration
VENV_DIR="$PROJECT_ROOT/.venv"
PYTHON_MIN_VERSION="3.8"
GUI_MODULE="src.poe_search.gui"
REQUIREMENTS_FILE="$PROJECT_ROOT/requirements.txt"
LOCKFILE="$PROJECT_ROOT/.poe_search_gui.lock"

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

# Function to check Python version
check_python_version() {
    print_status "Checking Python version..."
    
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 is not installed or not in PATH"
        exit 1
    fi
    
    PYTHON_VERSION=$(python3 -c "import sys; print('.'.join(map(str, sys.version_info[:2])))")
    REQUIRED_VERSION="$PYTHON_MIN_VERSION"
    
    if ! python3 -c "import sys; exit(0 if sys.version_info >= tuple(map(int, '$REQUIRED_VERSION'.split('.'))) else 1)"; then
        print_error "Python $REQUIRED_VERSION or higher is required. Found: $PYTHON_VERSION"
        exit 1
    fi
    
    print_success "Python $PYTHON_VERSION detected"
}

# Function to setup virtual environment
setup_venv() {
    print_status "Setting up virtual environment..."
    
    if [[ ! -d "$VENV_DIR" ]]; then
        print_status "Creating new virtual environment..."
        python3 -m venv "$VENV_DIR"
    fi
    
    # Activate virtual environment
    source "$VENV_DIR/bin/activate"
    print_success "Virtual environment activated"
    
    # Upgrade pip
    print_status "Upgrading pip..."
    pip install --upgrade pip > /dev/null 2>&1
}

# Function to install dependencies
install_dependencies() {
    print_status "Installing/updating dependencies..."
    
    # Install the package in development mode
    if [[ -f "$PROJECT_ROOT/pyproject.toml" ]]; then
        print_status "Installing package with pyproject.toml..."
        pip install -e ".[gui,dev]" > /dev/null 2>&1
    elif [[ -f "$REQUIREMENTS_FILE" ]]; then
        print_status "Installing from requirements.txt..."
        pip install -r "$REQUIREMENTS_FILE" > /dev/null 2>&1
    else
        print_warning "No requirements file found, installing basic dependencies..."
        pip install PyQt6 selenium webdriver-manager > /dev/null 2>&1
    fi
    
    print_success "Dependencies installed successfully"
}

# Function to check for existing GUI processes
check_existing_processes() {
    print_status "Checking for existing Poe Search GUI processes..."
    
    # Check for lockfile
    if [[ -f "$LOCKFILE" ]]; then
        PID=$(cat "$LOCKFILE" 2>/dev/null || echo "")
        if [[ -n "$PID" ]] && kill -0 "$PID" 2>/dev/null; then
            print_warning "Poe Search GUI is already running (PID: $PID)"
            read -p "Do you want to kill the existing process and start a new one? (y/N): " -n 1 -r
            echo
            if [[ $REPLY =~ ^[Yy]$ ]]; then
                kill "$PID" 2>/dev/null || true
                rm -f "$LOCKFILE"
                print_success "Existing process terminated"
            else
                print_status "Bringing existing window to front..."
                # Try to bring window to front (Linux specific)
                if command -v wmctrl &> /dev/null; then
                    wmctrl -a "Poe Search" 2>/dev/null || true
                fi
                exit 0
            fi
        else
            # Stale lockfile
            rm -f "$LOCKFILE"
        fi
    fi
    
    # Check for any Python processes running poe-search
    EXISTING_PIDS=$(pgrep -f "poe.*search.*gui" 2>/dev/null || true)
    if [[ -n "$EXISTING_PIDS" ]]; then
        print_warning "Found existing poe-search processes: $EXISTING_PIDS"
        read -p "Kill existing processes? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            echo "$EXISTING_PIDS" | xargs kill 2>/dev/null || true
            print_success "Existing processes terminated"
        fi
    fi
}

# Function to check system requirements
check_system_requirements() {
    print_status "Checking system requirements..."
    
    # Check for display
    if [[ -z "$DISPLAY" ]] && [[ -z "$WAYLAND_DISPLAY" ]]; then
        print_error "No display detected. GUI applications require a display server."
        exit 1
    fi
    
    # Check for Chrome/Chromium (for Selenium)
    if ! command -v google-chrome &> /dev/null && ! command -v chromium-browser &> /dev/null && ! command -v chromium &> /dev/null; then
        print_warning "Chrome/Chromium not found. Selenium may not work properly."
        print_status "Install Chrome with: sudo apt install google-chrome-stable"
    fi
    
    # Check for required system libraries
    if ! python3 -c "import PyQt6" 2>/dev/null; then
        print_warning "PyQt6 not available. Installing..."
    fi
}

# Function to launch GUI
launch_gui() {
    print_status "Launching Poe Search GUI..."
    
    # Create lockfile with PID
    echo $$ > "$LOCKFILE"
    
    # Set up cleanup trap
    trap 'rm -f "$LOCKFILE"; exit' INT TERM EXIT
    
    # Change to project root
    cd "$PROJECT_ROOT"
    
    # Try different launch methods
    launch_methods=(
        "python -m $GUI_MODULE"
        "python src/poe_search/gui/__main__.py"
        "python -c 'from src.poe_search.gui.main_window import MainWindow; import sys; from PyQt6.QtWidgets import QApplication; app = QApplication(sys.argv); window = MainWindow(); window.show(); sys.exit(app.exec())'"
    )
    
    for method in "${launch_methods[@]}"; do
        print_status "Trying: $method"
        if eval "$method" 2>/dev/null; then
            break
        else
            print_warning "Launch method failed: $method"
        fi
    done
}

# Function to show usage
show_usage() {
    echo "Poe Search - Enhanced Launcher Script"
    echo ""
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  -h, --help        Show this help message"
    echo "  -c, --check       Check system requirements only"
    echo "  -i, --install     Install/update dependencies only"
    echo "  -k, --kill        Kill existing GUI processes"
    echo "  -v, --verbose     Verbose output"
    echo "  --dev             Launch in development mode"
    echo "  --headless        Launch in headless mode (for testing)"
    echo ""
    echo "Environment Variables:"
    echo "  POE_TOKEN         Your Poe authentication token"
    echo "  POE_HEADLESS      Set to '1' for headless mode"
    echo ""
}

# Function to kill existing processes
kill_existing() {
    print_status "Killing existing Poe Search processes..."
    
    # Kill by lockfile
    if [[ -f "$LOCKFILE" ]]; then
        PID=$(cat "$LOCKFILE" 2>/dev/null || echo "")
        if [[ -n "$PID" ]] && kill -0 "$PID" 2>/dev/null; then
            kill "$PID" 2>/dev/null || true
            print_success "Killed process from lockfile (PID: $PID)"
        fi
        rm -f "$LOCKFILE"
    fi
    
    # Kill by process name
    EXISTING_PIDS=$(pgrep -f "poe.*search" 2>/dev/null || true)
    if [[ -n "$EXISTING_PIDS" ]]; then
        echo "$EXISTING_PIDS" | xargs kill 2>/dev/null || true
        print_success "Killed existing processes: $EXISTING_PIDS"
    else
        print_status "No existing processes found"
    fi
}

# Parse command line arguments
VERBOSE=false
DEV_MODE=false
HEADLESS_MODE=false

while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            show_usage
            exit 0
            ;;
        -c|--check)
            check_python_version
            check_system_requirements
            print_success "System requirements check completed"
            exit 0
            ;;
        -i|--install)
            check_python_version
            setup_venv
            install_dependencies
            print_success "Installation completed"
            exit 0
            ;;
        -k|--kill)
            kill_existing
            exit 0
            ;;
        -v|--verbose)
            VERBOSE=true
            set -x  # Enable verbose bash output
            shift
            ;;
        --dev)
            DEV_MODE=true
            shift
            ;;
        --headless)
            HEADLESS_MODE=true
            export POE_HEADLESS=1
            shift
            ;;
        *)
            print_error "Unknown option: $1"
            show_usage
            exit 1
            ;;
    esac
done

# Main execution
main() {
    print_status "Starting Poe Search GUI..."
    print_status "Project root: $PROJECT_ROOT"
    
    # Environment info
    if [[ "$VERBOSE" == true ]]; then
        print_status "Environment:"
        echo "  - Python: $(python3 --version)"
        echo "  - PWD: $(pwd)"
        echo "  - DISPLAY: ${DISPLAY:-not set}"
        echo "  - POE_TOKEN: ${POE_TOKEN:+set (hidden)}"
    fi
    
    # Run setup steps
    check_python_version
    check_system_requirements
    setup_venv
    install_dependencies
    check_existing_processes
    
    # Launch GUI
    print_success "Setup completed! Launching GUI..."
    launch_gui
}

# Run main function
main "$@"