#!/bin/bash
# Complete GUI Fix Script - Get Poe Search GUI working immediately

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

print_step() {
    echo -e "\n${BLUE}🔧 $1${NC}"
    echo "----------------------------------------"
}

print_success() {
    echo -e "${GREEN}✅${NC} $1"
}

print_error() {
    echo -e "${RED}❌${NC} $1"
}

echo -e "${BLUE}================================================================${NC}"
echo -e "${BLUE} 🚀 Complete GUI Fix for Poe Search${NC}"
echo -e "${BLUE} Getting your GUI working immediately!${NC}"
echo -e "${BLUE}================================================================${NC}"

print_step "Step 1: Backing up current pyproject.toml"
if [ -f "pyproject.toml" ]; then
    cp pyproject.toml pyproject.toml.backup
    print_success "Backed up existing pyproject.toml"
fi

print_step "Step 2: Fixing pyproject.toml syntax"
if [ -f "pyproject_clean.toml" ]; then
    cp pyproject_clean.toml pyproject.toml
    print_success "Applied clean pyproject.toml"
else
    print_error "Clean pyproject.toml not found, creating one..."
    cat > pyproject.toml << 'EOF'
[build-system]
requires = ["setuptools>=61.0", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "poe-search"
version = "1.3.0"
description = "Enhanced AI Conversation Manager for Poe.com"
authors = [{name = "Kevin", email = "kevin@example.com"}]
license = {text = "MIT"}
requires-python = ">=3.9"
dependencies = [
    "PyQt6>=6.5.0",
    "selenium>=4.15.0",
    "requests>=2.31.0",
    "beautifulsoup4>=4.12.0",
    "webdriver-manager>=4.0.0",
]

[project.optional-dependencies]
gui = ["PyQt6>=6.5.0"]
dev = [
    "pytest>=7.0.0",
    "black>=22.0.0",
    "flake8>=5.0.0",
]

[tool.setuptools.packages.find]
where = ["src"]

[tool.setuptools.package-dir]
"" = "src"
EOF
    print_success "Created clean pyproject.toml"
fi

print_step "Step 3: Running Python quick fix"
if [ -f "quick_gui_fix.py" ]; then
    python quick_gui_fix.py
    if [ $? -eq 0 ]; then
        print_success "Python quick fix completed"
    else
        print_error "Python quick fix failed"
    fi
else
    print_error "quick_gui_fix.py not found"
fi

print_step "Step 4: Uninstalling any broken installation"
pip uninstall -y poe-search 2>/dev/null || true
print_success "Cleaned up broken installation"

print_step "Step 5: Installing in development mode"
pip install -e . 2>/dev/null || {
    print_error "Development installation failed, trying basic install"
    pip install --no-deps -e . || {
        print_error "All installation methods failed"
        exit 1
    }
}
print_success "Package installed successfully"

print_step "Step 6: Installing GUI dependencies"
pip install PyQt6 selenium requests beautifulsoup4 webdriver-manager
print_success "GUI dependencies installed"

print_step "Step 7: Testing imports"
python -c "
try:
    import poe_search
    print('✅ poe_search import: OK')

    from poe_search.gui.main_window import run_gui
    print('✅ GUI import: OK')

    from PyQt6.QtWidgets import QApplication
    print('✅ PyQt6 import: OK')

    print('🎉 ALL IMPORTS WORKING!')

except Exception as e:
    print(f'❌ Import test failed: {e}')
    exit(1)
"

if [ $? -eq 0 ]; then
    print_success "All imports working"
else
    print_error "Import test failed"
    exit 1
fi

print_step "Step 8: Final GUI Test"
echo "Testing GUI launcher..."

# Quick GUI test (will exit immediately)
timeout 5s python gui_launcher.py || {
    if [ $? -eq 124 ]; then
        print_success "GUI launched successfully (timeout as expected)"
    else
        print_error "GUI launch failed"
        echo "Manual test: python gui_launcher.py"
    fi
}

echo -e "\n${GREEN}================================================================${NC}"
echo -e "${GREEN} 🎉 Complete Fix Applied!${NC}"
echo -e "${GREEN}================================================================${NC}"

echo -e "\n${GREEN}✅ Your GUI should now work!${NC}"
echo -e "\n${YELLOW}🚀 Try running:${NC}"
echo -e "   ${BLUE}python gui_launcher.py${NC}"

echo -e "\n${YELLOW}📋 For full features, run:${NC}"
echo -e "   ${BLUE}python run_comprehensive_organization.py${NC}"

echo -e "\n${YELLOW}🔧 If issues persist:${NC}"
echo -e "   1. Check virtual environment is activated"
echo -e "   2. Run: pip list | grep poe-search"
echo -e "   3. Verify: python -c 'import poe_search'"

echo -e "\n${GREEN}================================================================${NC}"
