#!/bin/bash

# ==============================================================================
# Project Modernization Verification Script
# ==============================================================================
# This script verifies that all modernization steps have been completed
# and the project is ready for production use.

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Logging function
log() {
    local level=$1
    shift
    local message="$*"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    
    case $level in
        "ERROR")
            echo -e "${RED}[ERROR]${NC} $message" >&2
            ;;
        "SUCCESS")
            echo -e "${GREEN}[SUCCESS]${NC} $message"
            ;;
        "WARNING")
            echo -e "${YELLOW}[WARNING]${NC} $message"
            ;;
        "INFO")
            echo -e "${BLUE}[INFO]${NC} $message"
            ;;
        *)
            echo "$message"
            ;;
    esac
}

# Check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check file exists
check_file() {
    local file=$1
    local description=$2
    
    if [[ -f "$PROJECT_ROOT/$file" ]]; then
        log "SUCCESS" "✅ $description: $file"
        return 0
    else
        log "ERROR" "❌ Missing $description: $file"
        return 1
    fi
}

# Check directory exists
check_directory() {
    local dir=$1
    local description=$2
    
    if [[ -d "$PROJECT_ROOT/$dir" ]]; then
        log "SUCCESS" "✅ $description: $dir/"
        return 0
    else
        log "ERROR" "❌ Missing $description: $dir/"
        return 1
    fi
}

# Main verification function
main() {
    log "INFO" "🔍 Starting Poe Search modernization verification..."
    log "INFO" "📁 Project root: $PROJECT_ROOT"
    echo
    
    local errors=0
    
    # ========================================================================
    # 1. Project Structure Verification
    # ========================================================================
    log "INFO" "📋 1. Verifying project structure..."
    
    # Core directories
    check_directory "src/poe_search" "Core source code" || ((errors++))
    check_directory "tests" "Test suite" || ((errors++))
    check_directory "docs" "Documentation" || ((errors++))
    check_directory "scripts" "Automation scripts" || ((errors++))
    check_directory "config" "Configuration files" || ((errors++))
    check_directory "dev-tools" "Development tools" || ((errors++))
    
    # Key files
    check_file "pyproject.toml" "Project configuration" || ((errors++))
    check_file "README.md" "Project documentation" || ((errors++))
    check_file "run.sh" "GUI launcher script" || ((errors++))
    check_file ".gitignore" "Git ignore rules" || ((errors++))
    check_file ".pre-commit-config.yaml" "Pre-commit hooks" || ((errors++))
    
    echo
    
    # ========================================================================
    # 2. Configuration Files Verification
    # ========================================================================
    log "INFO" "⚙️ 2. Verifying configuration files..."
    
    check_file ".tool-config.toml" "Tool configuration" || ((errors++))
    check_file ".prettierrc" "Code formatting config" || ((errors++))
    check_file "scripts/run_tests.sh" "Test runner script" || ((errors++))
    
    # GitHub workflows
    check_file ".github/workflows/ci.yml" "CI workflow" || ((errors++))
    check_file ".github/workflows/release.yml" "Release workflow" || ((errors++))
    check_file ".github/workflows/dependency-update.yml" "Dependency updates" || ((errors++))
    
    echo
    
    # ========================================================================
    # 3. Python Environment Verification
    # ========================================================================
    log "INFO" "🐍 3. Verifying Python environment..."
    
    if command_exists python; then
        local python_version=$(python --version 2>&1 | cut -d' ' -f2)
        log "SUCCESS" "✅ Python version: $python_version"
        
        # Check if virtual environment is active
        if [[ -n "${VIRTUAL_ENV:-}" ]]; then
            log "SUCCESS" "✅ Virtual environment active: $VIRTUAL_ENV"
        else
            log "WARNING" "⚠️ No virtual environment detected"
        fi
    else
        log "ERROR" "❌ Python not found"
        ((errors++))
    fi
    
    echo
    
    # ========================================================================
    # 4. Dependencies Verification
    # ========================================================================
    log "INFO" "📦 4. Verifying dependencies..."
    
    cd "$PROJECT_ROOT"
    
    if pip show poe-search >/dev/null 2>&1; then
        log "SUCCESS" "✅ poe-search package installed"
        
        # Test CLI
        if poe-search --version >/dev/null 2>&1; then
            log "SUCCESS" "✅ CLI command functional"
        else
            log "ERROR" "❌ CLI command not working"
            ((errors++))
        fi
        
        # Test GUI imports
        if python -c "from poe_search.gui import main" 2>/dev/null; then
            log "SUCCESS" "✅ GUI components importable"
        else
            log "ERROR" "❌ GUI import failed"
            ((errors++))
        fi
    else
        log "WARNING" "⚠️ poe-search not installed in development mode"
        log "INFO" "   Run: pip install -e .[dev,gui]"
    fi
    
    echo
    
    # ========================================================================
    # 5. Database Verification
    # ========================================================================
    log "INFO" "🗄️ 5. Verifying database..."
    
    if [[ -f "$PROJECT_ROOT/data/poe_search.db" ]]; then
        log "SUCCESS" "✅ Database file exists"
        
        # Check if database has conversations
        local conv_count=$(sqlite3 "$PROJECT_ROOT/data/poe_search.db" \
            "SELECT COUNT(*) FROM conversations;" 2>/dev/null || echo "0")
        
        if [[ $conv_count -gt 0 ]]; then
            log "SUCCESS" "✅ Database contains $conv_count conversations"
        else
            log "WARNING" "⚠️ Database is empty (no conversations imported)"
        fi
    else
        log "WARNING" "⚠️ Database file not found"
        log "INFO" "   This is normal for a fresh installation"
    fi
    
    echo
    
    # ========================================================================
    # 6. Testing Infrastructure Verification
    # ========================================================================
    log "INFO" "🧪 6. Verifying testing infrastructure..."
    
    if command_exists pytest; then
        log "SUCCESS" "✅ pytest available"
        
        # Run a quick test to verify setup
        if pytest --version >/dev/null 2>&1; then
            log "SUCCESS" "✅ pytest functional"
        else
            log "ERROR" "❌ pytest not working properly"
            ((errors++))
        fi
    else
        log "ERROR" "❌ pytest not installed"
        ((errors++))
    fi
    
    # Check if test script is executable
    if [[ -x "$PROJECT_ROOT/scripts/run_tests.sh" ]]; then
        log "SUCCESS" "✅ Test runner script is executable"
    else
        log "WARNING" "⚠️ Test runner script not executable"
        log "INFO" "   Run: chmod +x scripts/run_tests.sh"
    fi
    
    echo
    
    # ========================================================================
    # 7. Code Quality Tools Verification
    # ========================================================================
    log "INFO" "🔍 7. Verifying code quality tools..."
    
    local quality_tools=("black" "isort" "ruff" "mypy" "bandit")
    for tool in "${quality_tools[@]}"; do
        if command_exists "$tool"; then
            log "SUCCESS" "✅ $tool available"
        else
            log "WARNING" "⚠️ $tool not installed"
        fi
    done
    
    echo
    
    # ========================================================================
    # 8. Documentation Verification
    # ========================================================================
    log "INFO" "📚 8. Verifying documentation..."
    
    local doc_files=(
        "docs/user-guide/installation.md"
        "docs/user-guide/configuration.md"
        "docs/user-guide/gui-tutorial.md"
        "docs/api/reference.md"
        "docs/development/setup.md"
    )
    
    for doc_file in "${doc_files[@]}"; do
        if check_file "$doc_file" "Documentation" >/dev/null 2>&1; then
            log "SUCCESS" "✅ $doc_file"
        else
            log "WARNING" "⚠️ Missing: $doc_file"
        fi
    done
    
    echo
    
    # ========================================================================
    # 9. Git Repository Verification
    # ========================================================================
    log "INFO" "📝 9. Verifying git repository..."
    
    if [[ -d "$PROJECT_ROOT/.git" ]]; then
        log "SUCCESS" "✅ Git repository initialized"
        
        # Check for uncommitted changes
        cd "$PROJECT_ROOT"
        if git diff --quiet && git diff --staged --quiet; then
            log "SUCCESS" "✅ Working directory clean"
        else
            log "WARNING" "⚠️ Uncommitted changes detected"
            log "INFO" "   Consider committing your changes"
        fi
        
        # Check branch
        local current_branch=$(git branch --show-current 2>/dev/null || echo "unknown")
        log "INFO" "📍 Current branch: $current_branch"
    else
        log "ERROR" "❌ Not a git repository"
        ((errors++))
    fi
    
    echo
    
    # ========================================================================
    # Summary
    # ========================================================================
    log "INFO" "📊 Verification Summary"
    echo "=================================="
    
    if [[ $errors -eq 0 ]]; then
        log "SUCCESS" "🎉 All checks passed! Project is ready for production."
        echo
        log "INFO" "Next steps:"
        log "INFO" "  1. Commit any remaining changes: git add . && git commit -m 'Complete project modernization'"
        log "INFO" "  2. Push to repository: git push origin main"
        log "INFO" "  3. Create a release: git tag v1.0.0 && git push origin v1.0.0"
        log "INFO" "  4. Run the application: ./run.sh"
        echo
        return 0
    else
        log "ERROR" "❌ Found $errors error(s). Please address them before proceeding."
        echo
        log "INFO" "Common fixes:"
        log "INFO" "  • Install dependencies: pip install -e .[dev,gui]"
        log "INFO" "  • Make scripts executable: chmod +x scripts/*.sh"
        log "INFO" "  • Initialize git: git init && git add . && git commit -m 'Initial commit'"
        echo
        return 1
    fi
}

# Run main function
main "$@"
