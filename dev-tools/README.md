# Development Tools

This directory contains development utilities, test files, and debugging tools for the Poe Search project.

## Directory Structure

### `/testing/`
Test scripts and validation utilities:
- `test_*.py` - Various unit and integration tests
- `quick_test.py` - Quick validation script
- `standalone_api_test.py` - Standalone API testing
- `conversation_test_results_*.json` - Test result data

### `/debug/`
Debugging and analysis tools:
- `demo_startup_integration.py` - Startup integration demo
- `enhanced_summary.py` - Project summary generator
- `implementation_summary.py` - Implementation analysis
- `playwright_login_debug.png` - Browser automation screenshots

### `/utilities/`
Development utilities and helper scripts:
- `formkey_extraction_guide.py` - Guide for manual formkey extraction
- `save_formkey.py` - Utility to save formkey to config

## Usage

These tools are for development and debugging purposes only. They are not part of the main application and should not be distributed with production builds.

### Running Tests
```bash
cd dev-tools/testing
python test_api_simple.py
python test_token_management.py
```

### Using Utilities
```bash
cd dev-tools/utilities
python formkey_extraction_guide.py
python save_formkey.py
```

## Notes

- All test files are isolated and safe to run
- Debug tools may require additional dependencies
- Utilities are provided for convenience during development
