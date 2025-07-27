#!/bin/bash
# Poe Search GUI Import Fix Script
# Fixes the specific import issue identified

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

print_warning() {
    echo -e "${YELLOW}⚠️${NC} $1"
}

echo -e "${BLUE}================================================================${NC}"
echo -e "${BLUE} 🔧 Poe Search GUI Import Fix${NC}"
echo -e "${BLUE} Fixing the identified import issue${NC}"
echo -e "${BLUE}================================================================${NC}"

print_step "Step 1: Diagnosing Import Issue"

# Check current Python path
echo "Current Python path:"
python -c "import sys; print('\n'.join(sys.path))"

# Check if package is properly installed
echo -e "\nChecking package installation:"
pip show poe-search

print_step "Step 2: Checking Installation Mode"

# Check if installed in development mode
if pip list | grep -E "poe-search.*-e"; then
    print_success "Package is installed in development mode"
else
    print_warning "Package may not be in development mode"
fi

print_step "Step 3: Testing Import Paths"

# Test different import methods
echo "Testing import methods:"

echo "1. Direct import test:"
if python -c "import poe_search" 2>/dev/null; then
    print_success "Direct import works"
else
    print_error "Direct import fails"
fi

echo "2. Import with src path:"
if python -c "import sys; sys.path.insert(0, 'src'); import poe_search" 2>/dev/null; then
    print_success "Import with src path works"
else
    print_error "Import with src path fails"
fi

echo "3. Import from site-packages:"
SITE_PACKAGES=$(python -c "import site; print(site.getsitepackages()[0])")
echo "Site packages location: $SITE_PACKAGES"

if [ -d "$SITE_PACKAGES/poe_search" ]; then
    print_success "poe_search found in site-packages"
else
    print_warning "poe_search not found in site-packages"
fi

print_step "Step 4: Applying Fixes"

echo "Fix 1: Reinstalling in development mode"
pip uninstall -y poe-search 2>/dev/null || true

echo "Fix 2: Installing with proper development mode"
pip install -e .

echo "Fix 3: Installing GUI dependencies explicitly"
pip install -e ".[gui]"

print_step "Step 5: Verification"

echo "Testing imports after fix:"

if python -c "import poe_search; print('✅ poe_search import: OK')" 2>/dev/null; then
    print_success "poe_search import fixed"
else
    print_error "poe_search import still failing"

    # Additional debugging
    echo "Debugging information:"
    echo "Python sys.path:"
    python -c "import sys; [print(f'  {p}') for p in sys.path]"

    echo "Site-packages contents:"
    ls -la $(python -c "import site; print(site.getsitepackages()[0])") | grep poe || echo "No poe-related packages found"
fi

if python -c "from poe_search import gui; print('✅ poe_search.gui import: OK')" 2>/dev/null; then
    print_success "poe_search.gui import fixed"
else
    print_error "poe_search.gui import still failing"
fi

print_step "Step 6: Testing GUI Launcher"

echo "Testing GUI launcher:"
if python gui_launcher.py --help >/dev/null 2>&1; then
    print_success "GUI launcher working"
else
    print_error "GUI launcher still has issues"

    # Show actual error
    echo "GUI launcher error output:"
    python gui_launcher.py --help || true
fi

print_step "Step 7: Final Test"

echo "Running complete GUI test:"
python -c "
try:
    import sys
    print('Python executable:', sys.executable)

    import poe_search
    print('✅ poe_search imported successfully')

    from poe_search import gui
    print('✅ poe_search.gui imported successfully')

    from PyQt6.QtWidgets import QApplication
    app = QApplication.instance() or QApplication(sys.argv)
    print('✅ QApplication created successfully')

    print('🎉 ALL TESTS PASSED - GUI should now work!')
    app.quit()

except Exception as e:
    print(f'❌ Error: {e}')
    import traceback
    traceback.print_exc()
"

echo -e "\n${GREEN}================================================================${NC}"
echo -e "${GREEN} 🎉 Fix Complete!${NC}"
echo -e "${GREEN} Try running: python gui_launcher.py${NC}"
echo -e "${GREEN}================================================================${NC}"
