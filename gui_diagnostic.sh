#!/bin/bash
# Poe Search GUI Comprehensive Diagnostic Script
# Diagnoses GUI issues while CLI scripts work
# Author: Assistant
# Version: 1.0.0

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR" && pwd)"
LOG_FILE="gui_diagnostic_$(date +%Y%m%d_%H%M%S).log"
REPORT_FILE="gui_diagnostic_report_$(date +%Y%m%d_%H%M%S).json"

# Logging functions
log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" | tee -a "$LOG_FILE"
}

log_error() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - ERROR: $1" | tee -a "$LOG_FILE"
}

log_warning() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - WARNING: $1" | tee -a "$LOG_FILE"
}

# Output formatting functions
print_header() {
    echo -e "\n${BLUE}================================================================${NC}"
    echo -e "${WHITE} $1${NC}"
    echo -e "${BLUE}================================================================${NC}"
    log "SECTION: $1"
}

print_section() {
    echo -e "\n${CYAN}============================================${NC}"
    echo -e "${CYAN} $1${NC}"
    echo -e "${CYAN}============================================${NC}"
    log "SUBSECTION: $1"
}

print_step() {
    echo -e "\n${YELLOW}🔍 $1${NC}"
    echo "----------------------------------------"
    log "STEP: $1"
}

print_success() {
    echo -e "${GREEN}✅${NC} $1"
    log "SUCCESS: $1"
}

print_error() {
    echo -e "${RED}❌${NC} $1"
    log_error "$1"
}

print_warning() {
    echo -e "${YELLOW}⚠️${NC} $1"
    log_warning "$1"
}

print_info() {
    echo -e "${BLUE}ℹ️${NC} $1"
    log "INFO: $1"
}

# Global variables for tracking results
declare -A DIAGNOSTIC_RESULTS
declare -A ISSUES_FOUND
declare -A SOLUTIONS

# Initialize diagnostic tracking
init_diagnostics() {
    DIAGNOSTIC_RESULTS=()
    ISSUES_FOUND=()
    SOLUTIONS=()
}

# Add result to tracking
add_result() {
    local test_name="$1"
    local result="$2"
    local details="$3"

    DIAGNOSTIC_RESULTS["$test_name"]="$result"
    if [[ "$result" == "FAIL" ]]; then
        ISSUES_FOUND["$test_name"]="$details"
    fi
}

# Add solution
add_solution() {
    local issue="$1"
    local solution="$2"
    SOLUTIONS["$issue"]="$solution"
}

# System information check
check_system_info() {
    print_step "System Information Analysis"

    local os_name=$(uname -s)
    local kernel_version=$(uname -r)
    local architecture=$(uname -m)
    local hostname=$(hostname)

    echo "🖥️  System Details:"
    echo "   Operating System: $os_name"
    echo "   Kernel Version: $kernel_version"
    echo "   Architecture: $architecture"
    echo "   Hostname: $hostname"
    echo "   Working Directory: $PROJECT_ROOT"

    # Detect specific environments
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        if command -v lsb_release &> /dev/null; then
            local distro=$(lsb_release -d | cut -f2)
            echo "   Distribution: $distro"
        elif [ -f /etc/os-release ]; then
            local distro=$(grep PRETTY_NAME /etc/os-release | cut -d'"' -f2)
            echo "   Distribution: $distro"
        fi

        # Check for WSL
        if grep -qi microsoft /proc/version || grep -qi wsl /proc/version; then
            print_warning "WSL Environment Detected - GUI may require X server setup"
            add_result "WSL_DETECTED" "WARNING" "WSL environment detected"
            add_solution "WSL_GUI" "Install X server (VcXsrv/X410) and set DISPLAY variable"
        else
            print_success "Native Linux environment"
        fi

    elif [[ "$OSTYPE" == "darwin"* ]]; then
        local macos_version=$(sw_vers -productVersion)
        echo "   macOS Version: $macos_version"
        print_success "macOS environment (GUI should work by default)"

    elif [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "cygwin" ]]; then
        print_info "Windows environment detected"
        print_success "Windows GUI support available"
    fi

    add_result "SYSTEM_INFO" "PASS" "System information collected"
}

# Python environment comprehensive check
check_python_environment() {
    print_step "Python Environment Comprehensive Analysis"

    local python_found=false
    local python_cmd=""

    # Check multiple Python versions
    echo "🐍 Python Installation Check:"
    for py_cmd in python3 python python3.12 python3.11 python3.10 python3.9 python3.8; do
        if command -v "$py_cmd" &> /dev/null; then
            local version=$($py_cmd --version 2>&1)
            local location=$(which $py_cmd)
            print_success "$py_cmd: $version (Location: $location)"

            if [[ -z "$python_cmd" ]]; then
                python_cmd="$py_cmd"
                python_found=true
            fi
        fi
    done

    if [[ "$python_found" == false ]]; then
        print_error "No Python installation found"
        add_result "PYTHON_INSTALL" "FAIL" "No Python installation found"
        add_solution "PYTHON_MISSING" "Install Python 3.8+ from python.org or package manager"
        return 1
    fi

    # Check Python version compatibility
    local python_version=$($python_cmd -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
    if [[ $(echo "$python_version >= 3.8" | bc -l 2>/dev/null || echo "0") == "1" ]] ||
       [[ "$python_version" == "3.8" ]] || [[ "$python_version" == "3.9" ]] ||
       [[ "$python_version" == "3.10" ]] || [[ "$python_version" == "3.11" ]] ||
       [[ "$python_version" == "3.12" ]]; then
        print_success "Python version $python_version is compatible"
    else
        print_warning "Python version $python_version may not be fully compatible (recommended: 3.8+)"
        add_result "PYTHON_VERSION" "WARNING" "Python version may not be compatible"
    fi

    # Check pip
    echo -e "\n📦 Package Manager Check:"
    for pip_cmd in pip3 pip; do
        if command -v "$pip_cmd" &> /dev/null; then
            local pip_version=$($pip_cmd --version 2>&1)
            print_success "$pip_cmd: $pip_version"
        fi
    done

    if ! command -v pip &> /dev/null && ! command -v pip3 &> /dev/null; then
        print_error "No pip installation found"
        add_result "PIP_INSTALL" "FAIL" "No pip installation found"
        add_solution "PIP_MISSING" "Install pip: python -m ensurepip --upgrade"
    fi

    add_result "PYTHON_ENV" "PASS" "Python environment validated"
    return 0
}

# Virtual environment detailed check
check_virtual_environment() {
    print_step "Virtual Environment Analysis"

    echo "🔧 Virtual Environment Status:"

    # Check if currently in virtual environment
    if [[ -n "$VIRTUAL_ENV" ]]; then
        print_success "Virtual environment active: $VIRTUAL_ENV"
        echo "   Python executable: $(which python)"
        echo "   Pip location: $(which pip 2>/dev/null || echo 'Not found')"
        add_result "VIRTUAL_ENV_ACTIVE" "PASS" "Virtual environment is active"
    else
        print_warning "No virtual environment detected"
        add_result "VIRTUAL_ENV_ACTIVE" "WARNING" "No virtual environment active"
        add_solution "VIRTUAL_ENV_SETUP" "Create virtual environment: python -m venv poe-search-env && source poe-search-env/bin/activate"
    fi

    # Look for virtual environment directories
    echo -e "\n🔍 Searching for virtual environment directories:"
    local venv_dirs=("venv" ".venv" "env" ".env" "poe-search-env" "virtualenv")
    local found_venv=false

    for venv_dir in "${venv_dirs[@]}"; do
        if [ -d "$PROJECT_ROOT/$venv_dir" ]; then
            print_info "Found virtual environment directory: $venv_dir"

            # Check if it's a valid venv
            if [ -f "$PROJECT_ROOT/$venv_dir/bin/activate" ] || [ -f "$PROJECT_ROOT/$venv_dir/Scripts/activate" ]; then
                print_success "Valid virtual environment found: $venv_dir"
                found_venv=true

                if [[ -z "$VIRTUAL_ENV" ]]; then
                    add_solution "ACTIVATE_VENV" "Activate virtual environment: source $venv_dir/bin/activate"
                fi
            fi
        fi
    done

    if [[ "$found_venv" == false ]] && [[ -z "$VIRTUAL_ENV" ]]; then
        print_warning "No virtual environment found in project directory"
        add_solution "CREATE_VENV" "Create virtual environment: python -m venv poe-search-env"
    fi
}

# Display system comprehensive check
check_display_system() {
    print_step "Display System Analysis"

    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        echo "🖥️ Linux Display System Check:"

        # Check DISPLAY variable
        if [[ -n "$DISPLAY" ]]; then
            print_success "DISPLAY variable set: $DISPLAY"
            add_result "DISPLAY_VAR" "PASS" "DISPLAY variable is set"
        else
            print_error "DISPLAY variable not set"
            add_result "DISPLAY_VAR" "FAIL" "DISPLAY variable not set"
            add_solution "DISPLAY_SETUP" "Set DISPLAY variable: export DISPLAY=:0.0"
        fi

        # Check X11 accessibility
        if command -v xset &> /dev/null; then
            if timeout 5s xset q &> /dev/null; then
                print_success "X11 server accessible"
                add_result "X11_ACCESS" "PASS" "X11 server accessible"
            else
                print_error "X11 server not accessible"
                add_result "X11_ACCESS" "FAIL" "X11 server not accessible"
                add_solution "X11_SETUP" "Start X server or install X11 forwarding"
            fi
        else
            print_warning "xset command not found (X11 utilities not installed)"
            add_result "X11_UTILS" "WARNING" "X11 utilities not installed"
            add_solution "X11_UTILS_INSTALL" "Install X11 utilities: sudo apt-get install x11-utils"
        fi

        # Check Wayland
        if [[ -n "$WAYLAND_DISPLAY" ]]; then
            print_info "Wayland display detected: $WAYLAND_DISPLAY"
            print_info "Note: PyQt6 should work with Wayland"
        fi

        # Check for GUI-related libraries
        echo -e "\n📚 System GUI Libraries Check:"
        local gui_libs=("libqt6-core6" "libqt6-gui6" "libqt6-widgets6" "qt6-base-dev")

        for lib in "${gui_libs[@]}"; do
            if dpkg -l 2>/dev/null | grep -q "^ii.*$lib " || rpm -qa 2>/dev/null | grep -q "$lib"; then
                print_success "System library found: $lib"
            else
                print_warning "System library not found: $lib"
                add_solution "QT6_SYSTEM_LIBS" "Install Qt6 system libraries: sudo apt-get install qt6-base-dev"
            fi
        done

    elif [[ "$OSTYPE" == "darwin"* ]]; then
        print_success "macOS display system (should work by default)"
        add_result "DISPLAY_SYSTEM" "PASS" "macOS display system"

    elif [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "cygwin" ]]; then
        print_success "Windows display system"
        add_result "DISPLAY_SYSTEM" "PASS" "Windows display system"
    fi
}

# Project structure validation
check_project_structure() {
    print_step "Project Structure Validation"

    echo "📁 Project Structure Check:"

    # Critical files and directories
    local critical_paths=(
        "src/poe_search"
        "gui_launcher.py"
        "pyproject.toml"
        "requirements.txt"
    )

    # Important files and directories
    local important_paths=(
        "config"
        "scripts"
        "tests"
        "docs"
        "src/poe_search/__init__.py"
        "src/poe_search/gui"
        "src/poe_search/api"
        "src/poe_search/database"
    )

    local critical_missing=0
    local important_missing=0

    echo "   Critical components:"
    for path in "${critical_paths[@]}"; do
        if [ -e "$PROJECT_ROOT/$path" ]; then
            print_success "Found: $path"
        else
            print_error "Missing: $path"
            ((critical_missing++))
        fi
    done

    echo -e "\n   Important components:"
    for path in "${important_paths[@]}"; do
        if [ -e "$PROJECT_ROOT/$path" ]; then
            print_success "Found: $path"
        else
            print_warning "Missing: $path"
            ((important_missing++))
        fi
    done

    # Validate Python package structure
    echo -e "\n🐍 Python Package Structure:"
    if [ -f "$PROJECT_ROOT/src/poe_search/__init__.py" ]; then
        print_success "Valid Python package structure"

        # Check for GUI module
        if [ -d "$PROJECT_ROOT/src/poe_search/gui" ]; then
            print_success "GUI module directory found"

            if [ -f "$PROJECT_ROOT/src/poe_search/gui/__init__.py" ]; then
                print_success "GUI module is properly initialized"
            else
                print_warning "GUI module missing __init__.py"
                add_solution "GUI_INIT" "Create __init__.py in gui directory"
            fi
        else
            print_error "GUI module directory not found"
            add_result "GUI_MODULE" "FAIL" "GUI module directory missing"
        fi
    else
        print_error "Invalid Python package structure"
        add_result "PACKAGE_STRUCTURE" "FAIL" "Invalid Python package structure"
    fi

    if [[ $critical_missing -eq 0 ]]; then
        add_result "PROJECT_STRUCTURE" "PASS" "All critical components found"
    else
        add_result "PROJECT_STRUCTURE" "FAIL" "$critical_missing critical components missing"
        add_solution "PROJECT_SETUP" "Ensure you're in the correct project directory and all files are present"
    fi
}

# Dependency comprehensive check
check_dependencies() {
    print_step "Dependencies Analysis"

    local python_cmd="python3"
    if command -v python &> /dev/null; then
        python_cmd="python"
    fi

    echo "📦 Python Package Dependencies:"

    # Core dependencies for GUI
    local core_deps=("PyQt6" "sys" "os" "json" "pathlib")
    local optional_deps=("selenium" "requests" "sqlite3")
    local poe_deps=("poe_search")

    # Check core dependencies
    echo "   Core dependencies:"
    local core_failures=0
    for dep in "${core_deps[@]}"; do
        if timeout 10s $python_cmd -c "import $dep" 2>/dev/null; then
            local version=$($python_cmd -c "import $dep; print(getattr($dep, '__version__', 'built-in'))" 2>/dev/null)
            print_success "$dep: $version"
        else
            print_error "$dep: Not available"
            ((core_failures++))

            if [[ "$dep" == "PyQt6" ]]; then
                add_solution "PYQT6_INSTALL" "Install PyQt6: pip install PyQt6"
            fi
        fi
    done

    # Check optional dependencies
    echo -e "\n   Optional dependencies:"
    for dep in "${optional_deps[@]}"; do
        if timeout 10s $python_cmd -c "import $dep" 2>/dev/null; then
            local version=$($python_cmd -c "import $dep; print(getattr($dep, '__version__', 'unknown'))" 2>/dev/null)
            print_success "$dep: $version"
        else
            print_warning "$dep: Not available (optional)"
        fi
    done

    # Check project-specific imports
    echo -e "\n   Project-specific modules:"

    # Add src to Python path for testing
    export PYTHONPATH="$PROJECT_ROOT/src:$PYTHONPATH"

    for dep in "${poe_deps[@]}"; do
        if timeout 10s $python_cmd -c "import $dep" 2>/dev/null; then
            print_success "$dep: Available"

            # Test GUI module specifically
            if timeout 10s $python_cmd -c "from $dep import gui" 2>/dev/null; then
                print_success "$dep.gui: Available"
            else
                print_error "$dep.gui: Import failed"
                add_result "POE_GUI_IMPORT" "FAIL" "poe_search.gui import failed"
                add_solution "POE_INSTALL" "Install in development mode: pip install -e .[gui]"
            fi
        else
            print_error "$dep: Not available"
            add_result "POE_IMPORT" "FAIL" "poe_search import failed"
            add_solution "POE_INSTALL" "Install in development mode: pip install -e .[gui]"
        fi
    done

    # Check if package is installed
    echo -e "\n📋 Package Installation Status:"
    if command -v pip &> /dev/null; then
        if pip list 2>/dev/null | grep -q "poe-search"; then
            local installed_version=$(pip list 2>/dev/null | grep "poe-search" | awk '{print $2}')
            print_success "poe-search package installed: $installed_version"
        else
            print_warning "poe-search package not installed via pip"
            add_solution "PACKAGE_INSTALL" "Install package: pip install -e .[gui]"
        fi
    fi

    if [[ $core_failures -eq 0 ]]; then
        add_result "DEPENDENCIES" "PASS" "All core dependencies available"
    else
        add_result "DEPENDENCIES" "FAIL" "$core_failures core dependencies missing"
    fi
}

# GUI-specific tests
test_gui_functionality() {
    print_step "GUI Functionality Testing"

    local python_cmd="python3"
    if command -v python &> /dev/null; then
        python_cmd="python"
    fi

    export PYTHONPATH="$PROJECT_ROOT/src:$PYTHONPATH"

    echo "🖥️ GUI Component Tests:"

    # Test 1: Basic PyQt6 import
    echo "   Test 1: PyQt6 Basic Import"
    if timeout 15s $python_cmd -c "
import sys
import PyQt6
from PyQt6.QtWidgets import QApplication
print('PyQt6 import successful')
" 2>/dev/null; then
        print_success "PyQt6 basic import: OK"
    else
        print_error "PyQt6 basic import: FAILED"
        add_result "PYQT6_IMPORT" "FAIL" "PyQt6 basic import failed"
        add_solution "PYQT6_FIX" "Reinstall PyQt6: pip uninstall PyQt6 && pip install PyQt6"
        return 1
    fi

    # Test 2: QApplication creation
    echo "   Test 2: QApplication Creation"
    if timeout 15s $python_cmd -c "
import sys
from PyQt6.QtWidgets import QApplication
app = QApplication.instance() or QApplication(sys.argv)
print('QApplication creation successful')
app.quit()
" 2>/dev/null; then
        print_success "QApplication creation: OK"
    else
        print_error "QApplication creation: FAILED"
        add_result "QAPPLICATION" "FAIL" "QApplication creation failed"
        add_solution "DISPLAY_FIX" "Check display system and GUI environment"
        return 1
    fi

    # Test 3: Basic widget creation
    echo "   Test 3: Basic Widget Creation"
    if timeout 15s $python_cmd -c "
import sys
from PyQt6.QtWidgets import QApplication, QWidget, QLabel
app = QApplication.instance() or QApplication(sys.argv)
widget = QWidget()
label = QLabel('Test')
widget.setWindowTitle('Test')
print('Widget creation successful')
app.quit()
" 2>/dev/null; then
        print_success "Basic widget creation: OK"
    else
        print_error "Basic widget creation: FAILED"
        add_result "WIDGET_CREATION" "FAIL" "Widget creation failed"
        return 1
    fi

    # Test 4: Poe Search GUI imports
    echo "   Test 4: Poe Search GUI Imports"
    if timeout 15s $python_cmd -c "
import sys
sys.path.insert(0, '$PROJECT_ROOT/src')
import poe_search
from poe_search import gui
print('Poe Search GUI import successful')
" 2>/dev/null; then
        print_success "Poe Search GUI imports: OK"
    else
        print_error "Poe Search GUI imports: FAILED"
        add_result "POE_GUI_IMPORTS" "FAIL" "Poe Search GUI imports failed"
        add_solution "POE_REINSTALL" "Reinstall in development mode: pip install -e .[gui]"
        return 1
    fi

    add_result "GUI_FUNCTIONALITY" "PASS" "All GUI functionality tests passed"
    return 0
}

# Command execution tests
test_gui_commands() {
    print_step "GUI Command Execution Testing"

    echo "⚙️ GUI Command Tests:"

    # List of commands to test
    local commands=(
        "python $PROJECT_ROOT/gui_launcher.py --help"
        "python -m poe_search.gui --help"
    )

    # Test each command
    local command_failures=0
    for cmd in "${commands[@]}"; do
        echo "   Testing: $cmd"

        if timeout 10s bash -c "cd '$PROJECT_ROOT' && PYTHONPATH='$PROJECT_ROOT/src:\$PYTHONPATH' $cmd" &>/dev/null; then
            print_success "Command works: $cmd"
        else
            print_error "Command failed: $cmd"
            ((command_failures++))
        fi
    done

    # Test GUI launcher specifically
    echo -e "\n   Testing GUI launcher direct execution:"
    if [ -f "$PROJECT_ROOT/gui_launcher.py" ]; then
        if timeout 10s bash -c "cd '$PROJECT_ROOT' && python gui_launcher.py --version" &>/dev/null; then
            print_success "GUI launcher executable"
        else
            print_warning "GUI launcher may have issues (test with --version failed)"
        fi

        # Check if launcher is executable
        if [ -x "$PROJECT_ROOT/gui_launcher.py" ]; then
            print_success "GUI launcher has execute permissions"
        else
            print_info "GUI launcher execute permissions: chmod +x gui_launcher.py"
        fi
    else
        print_error "GUI launcher not found: gui_launcher.py"
        add_result "GUI_LAUNCHER" "FAIL" "GUI launcher file missing"
    fi

    if [[ $command_failures -eq 0 ]]; then
        add_result "COMMAND_EXECUTION" "PASS" "GUI commands executable"
    else
        add_result "COMMAND_EXECUTION" "FAIL" "$command_failures commands failed"
    fi
}

# Performance and resource check
check_system_resources() {
    print_step "System Resources Analysis"

    echo "💻 System Resources:"

    # Memory check
    if command -v free &> /dev/null; then
        local mem_info=$(free -h)
        echo "   Memory Status:"
        echo "$mem_info" | head -2 | tail -1 | while read -r line; do
            echo "     $line"
        done

        local available_mem=$(free -m | awk 'NR==2{printf "%.0f", $7}')
        if [[ $available_mem -gt 1000 ]]; then
            print_success "Sufficient memory available: ${available_mem}MB"
        else
            print_warning "Limited memory available: ${available_mem}MB"
        fi
    fi

    # Disk space check
    local available_space=$(df -h "$PROJECT_ROOT" | awk 'NR==2 {print $4}')
    echo "   Available disk space: $available_space"

    # CPU load
    if command -v uptime &> /dev/null; then
        local load_avg=$(uptime | awk -F'load average:' '{print $2}')
        echo "   System load:$load_avg"
    fi

    add_result "SYSTEM_RESOURCES" "PASS" "System resources checked"
}

# Configuration analysis
check_configuration() {
    print_step "Configuration Analysis"

    echo "⚙️ Configuration Check:"

    # Check for configuration files
    local config_files=("config/config.yaml" "config/poe_tokens.json" ".env")

    for config_file in "${config_files[@]}"; do
        if [ -f "$PROJECT_ROOT/$config_file" ]; then
            print_success "Configuration file found: $config_file"
        else
            print_info "Configuration file not found: $config_file (optional)"
        fi
    done

    # Check environment variables
    echo -e "\n   Environment Variables:"
    local env_vars=("POE_TOKEN" "DATABASE_URL" "LOG_LEVEL" "DISPLAY")

    for env_var in "${env_vars[@]}"; do
        if [[ -n "${!env_var}" ]]; then
            if [[ "$env_var" == "POE_TOKEN" ]]; then
                local masked_value="${!env_var:0:8}..."
                print_success "$env_var: $masked_value (masked)"
            else
                print_success "$env_var: ${!env_var}"
            fi
        else
            print_info "$env_var: Not set"
        fi
    done

    add_result "CONFIGURATION" "PASS" "Configuration analyzed"
}

# Generate comprehensive solutions
generate_solutions() {
    print_section "💡 Comprehensive Solutions & Recommendations"

    echo "Based on the diagnostic results, here are the solutions:"
    echo

    # Critical issues first
    local critical_issues=()
    local warnings=()
    local info_items=()

    # Categorize issues
    for test_name in "${!DIAGNOSTIC_RESULTS[@]}"; do
        case "${DIAGNOSTIC_RESULTS[$test_name]}" in
            "FAIL")
                critical_issues+=("$test_name")
                ;;
            "WARNING")
                warnings+=("$test_name")
                ;;
        esac
    done

    # Display critical issues
    if [[ ${#critical_issues[@]} -gt 0 ]]; then
        echo -e "${RED}🚨 Critical Issues (Must Fix):${NC}"
        for issue in "${critical_issues[@]}"; do
            echo -e "   ${RED}❌${NC} $issue: ${ISSUES_FOUND[$issue]}"

            # Show solutions
            for solution_key in "${!SOLUTIONS[@]}"; do
                if [[ "$issue" == *"$solution_key"* ]] || [[ "$solution_key" == *"$issue"* ]]; then
                    echo -e "      ${GREEN}💡${NC} ${SOLUTIONS[$solution_key]}"
                fi
            done
        done
        echo
    fi

    # Display warnings
    if [[ ${#warnings[@]} -gt 0 ]]; then
        echo -e "${YELLOW}⚠️ Warnings (Recommended to Fix):${NC}"
        for warning in "${warnings[@]}"; do
            echo -e "   ${YELLOW}⚠️${NC} $warning"

            # Show solutions
            for solution_key in "${!SOLUTIONS[@]}"; do
                if [[ "$warning" == *"$solution_key"* ]] || [[ "$solution_key" == *"$warning"* ]]; then
                    echo -e "      ${GREEN}💡${NC} ${SOLUTIONS[$solution_key]}"
                fi
            done
        done
        echo
    fi

    # General setup instructions
    echo -e "${BLUE}🔧 Step-by-Step Setup Guide:${NC}"
    echo

    echo "1. Virtual Environment Setup:"
    echo "   cd $PROJECT_ROOT"
    echo "   python3 -m venv poe-search-env"
    echo "   source poe-search-env/bin/activate  # Linux/Mac"
    echo "   # OR: poe-search-env\\Scripts\\activate  # Windows"
    echo

    echo "2. Install Dependencies:"
    echo "   pip install --upgrade pip"
    echo "   pip install -e .[gui]"
    echo

    echo "3. System-Specific Setup:"
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        echo "   # For Ubuntu/Debian:"
        echo "   sudo apt update"
        echo "   sudo apt install python3-pyqt6 python3-pyqt6.qtwidgets"
        echo "   sudo apt install qt6-base-dev  # Optional system libraries"
        echo
        echo "   # For display issues:"
        echo "   export DISPLAY=:0.0"
        echo "   # For WSL:"
        echo "   export DISPLAY=\$(cat /etc/resolv.conf | grep nameserver | awk '{print \$2; exit;}'):0.0"
        echo
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        echo "   # For macOS:"
        echo "   brew install python3"
        echo "   pip3 install PyQt6"
        echo
    fi

    echo "4. Test Installation:"
    echo "   python gui_launcher.py"
    echo "   # OR:"
    echo "   python -m poe_search.gui"
    echo

    echo "5. Troubleshooting:"
    echo "   # If still not working, try:"
    echo "   pip uninstall PyQt6"
    echo "   pip install --no-cache-dir PyQt6"
    echo "   # Check this diagnostic log: $LOG_FILE"
    echo
}

# Generate JSON report
generate_json_report() {
    print_step "Generating Diagnostic Report"

    local timestamp=$(date -Iseconds)

    cat > "$REPORT_FILE" << EOF
{
  "diagnostic_report": {
    "timestamp": "$timestamp",
    "system_info": {
      "os": "$(uname -s)",
      "kernel": "$(uname -r)",
      "architecture": "$(uname -m)",
      "hostname": "$(hostname)",
      "working_directory": "$PROJECT_ROOT"
    },
    "test_results": {
EOF

    # Add test results
    local first=true
    for test_name in "${!DIAGNOSTIC_RESULTS[@]}"; do
        if [[ "$first" == true ]]; then
            first=false
        else
            echo "," >> "$REPORT_FILE"
        fi

        echo -n "      \"$test_name\": \"${DIAGNOSTIC_RESULTS[$test_name]}\"" >> "$REPORT_FILE"
    done

    cat >> "$REPORT_FILE" << EOF

    },
    "issues_found": {
EOF

    # Add issues
    first=true
    for issue in "${!ISSUES_FOUND[@]}"; do
        if [[ "$first" == true ]]; then
            first=false
        else
            echo "," >> "$REPORT_FILE"
        fi

        echo -n "      \"$issue\": \"${ISSUES_FOUND[$issue]}\"" >> "$REPORT_FILE"
    done

    cat >> "$REPORT_FILE" << EOF

    },
    "solutions": {
EOF

    # Add solutions
    first=true
    for solution in "${!SOLUTIONS[@]}"; do
        if [[ "$first" == true ]]; then
            first=false
        else
            echo "," >> "$REPORT_FILE"
        fi

        echo -n "      \"$solution\": \"${SOLUTIONS[$solution]}\"" >> "$REPORT_FILE"
    done

    cat >> "$REPORT_FILE" << EOF

    },
    "log_file": "$LOG_FILE",
    "script_version": "1.0.0"
  }
}
EOF

    print_success "Diagnostic report saved: $REPORT_FILE"
}

# Summary report
generate_summary() {
    print_header "📋 DIAGNOSTIC SUMMARY"

    local total_tests=${#DIAGNOSTIC_RESULTS[@]}
    local passed_tests=0
    local failed_tests=0
    local warning_tests=0

    # Count results
    for result in "${DIAGNOSTIC_RESULTS[@]}"; do
        case "$result" in
            "PASS")
                ((passed_tests++))
                ;;
            "FAIL")
                ((failed_tests++))
                ;;
            "WARNING")
                ((warning_tests++))
                ;;
        esac
    done

    echo "📊 Test Results Summary:"
    echo "   Total Tests: $total_tests"
    echo -e "   ${GREEN}Passed: $passed_tests${NC}"
    echo -e "   ${RED}Failed: $failed_tests${NC}"
    echo -e "   ${YELLOW}Warnings: $warning_tests${NC}"
    echo

    # Overall status
    if [[ $failed_tests -eq 0 ]]; then
        if [[ $warning_tests -eq 0 ]]; then
            echo -e "${GREEN}🎉 Overall Status: EXCELLENT${NC}"
            echo "   All tests passed! GUI should work perfectly."
        else
            echo -e "${YELLOW}🔧 Overall Status: GOOD WITH WARNINGS${NC}"
            echo "   GUI should work, but consider addressing warnings."
        fi
    elif [[ $failed_tests -le 2 ]]; then
        echo -e "${YELLOW}⚠️ Overall Status: NEEDS ATTENTION${NC}"
        echo "   Some issues found. Follow the solutions above."
    else
        echo -e "${RED}❌ Overall Status: CRITICAL ISSUES${NC}"
        echo "   Multiple problems detected. Address critical issues first."
    fi

    echo
    echo "📄 Files Generated:"
    echo "   Detailed log: $LOG_FILE"
    echo "   JSON report: $REPORT_FILE"
    echo
    echo "🔗 Next Steps:"
    echo "   1. Review the solutions above"
    echo "   2. Follow the step-by-step setup guide"
    echo "   3. Re-run this diagnostic after making changes"
    echo "   4. If issues persist, check the project's GitHub issues"
    echo
}

# Quick fixes function
apply_quick_fixes() {
    print_section "🔧 Applying Quick Fixes"

    local fixes_applied=0

    # Fix 1: Create virtual environment if none exists
    if [[ -z "$VIRTUAL_ENV" ]] && [[ ! -d "poe-search-env" ]]; then
        echo "Creating virtual environment..."
        if python3 -m venv poe-search-env; then
            print_success "Virtual environment created: poe-search-env"
            echo "To activate: source poe-search-env/bin/activate"
            ((fixes_applied++))
        else
            print_error "Failed to create virtual environment"
        fi
    fi

    # Fix 2: Install basic requirements if pip is available
    if command -v pip &> /dev/null; then
        echo "Checking basic requirements..."
        if ! pip show PyQt6 &>/dev/null; then
            echo "Installing PyQt6..."
            if pip install PyQt6; then
                print_success "PyQt6 installed"
                ((fixes_applied++))
            else
                print_error "Failed to install PyQt6"
            fi
        fi
    fi

    # Fix 3: Set execute permissions
    if [ -f "gui_launcher.py" ] && [ ! -x "gui_launcher.py" ]; then
        chmod +x gui_launcher.py
        print_success "Added execute permissions to gui_launcher.py"
        ((fixes_applied++))
    fi

    if [[ $fixes_applied -gt 0 ]]; then
        print_success "Applied $fixes_applied quick fixes"
        echo "Re-run the diagnostic to see improvements"
    else
        print_info "No quick fixes needed or applicable"
    fi
}

# Main diagnostic function
main() {
    # Initialize
    init_diagnostics

    # Print header
    echo -e "${WHITE}================================================================${NC}"
    echo -e "${WHITE} 🔍 Poe Search GUI Comprehensive Diagnostic Tool${NC}"
    echo -e "${WHITE} 📅 $(date '+%Y-%m-%d %H:%M:%S')${NC}"
    echo -e "${WHITE} 📁 Project: $PROJECT_ROOT${NC}"
    echo -e "${WHITE} 📄 Log: $LOG_FILE${NC}"
    echo -e "${WHITE}================================================================${NC}"

    log "Starting Poe Search GUI diagnostic"
    log "Project root: $PROJECT_ROOT"

    # Run all diagnostic tests
    echo -e "\n${BLUE}🚀 Running comprehensive diagnostics...${NC}"

    # Core system checks
    print_header "1️⃣ SYSTEM ANALYSIS"
    check_system_info
    check_python_environment
    check_virtual_environment

    # Environment checks
    print_header "2️⃣ ENVIRONMENT ANALYSIS"
    check_display_system
    check_project_structure
    check_configuration

    # Technical checks
    print_header "3️⃣ TECHNICAL ANALYSIS"
    check_dependencies
    test_gui_functionality
    test_gui_commands

    # Resource checks
    print_header "4️⃣ SYSTEM RESOURCES"
    check_system_resources

    # Generate outputs
    print_header "5️⃣ SOLUTIONS & REPORTING"
    generate_solutions
    generate_json_report
    generate_summary

    # Offer quick fixes
    read -p "Apply quick fixes automatically? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        apply_quick_fixes
    fi

    log "Diagnostic completed"

    return 0
}

# Script execution
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    # Handle command line arguments
    case "${1:-}" in
        "--help"|"-h")
            echo "Poe Search GUI Diagnostic Script"
            echo "Usage: $0 [options]"
            echo ""
            echo "Options:"
            echo "  --help, -h     Show this help message"
            echo "  --quick, -q    Run quick diagnostic only"
            echo "  --fix, -f      Apply automatic fixes"
            echo ""
            echo "This script diagnoses GUI issues with Poe Search while CLI works."
            exit 0
            ;;
        "--quick"|"-q")
            echo "Running quick diagnostic..."
            init_diagnostics
            check_python_environment
            check_dependencies
            test_gui_functionality
            generate_summary
            ;;
        "--fix"|"-f")
            echo "Running diagnostic with automatic fixes..."
            main
            apply_quick_fixes
            ;;
        *)
            main
            ;;
    esac
else
    echo "Script loaded as library. Use main() to run diagnostics."
fi
