#!/usr/bin/env python3
"""
Poe Search Diagnostic Script
Comprehensive testing of all components

Author: Kevin Hao
Version: 1.0.0
License: MIT
"""

import sys
import os
import json
import logging
import traceback
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "src"))

def setup_logging():
    """Setup logging for diagnostics."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('diagnostic.log', mode='w')
        ]
    )

def print_section(title: str):
    """Print a formatted section header."""
    print("\n" + "="*60)
    print(f" {title}")
    print("="*60)

def print_step(step: str):
    """Print a formatted step."""
    print(f"\n🔍 {step}")
    print("-" * 40)

def check_dependencies() -> Dict[str, bool]:
    """Check all required dependencies."""
    print_step("Checking Dependencies")
    
    results = {}
    
    # Check PyQt6
    try:
        from PyQt6.QtWidgets import QApplication
        print("✅ PyQt6: Available")
        results['pyqt6'] = True
    except ImportError as e:
        print(f"❌ PyQt6: Missing ({e})")
        results['pyqt6'] = False
    
    # Check Selenium
    try:
        import selenium
        from selenium import webdriver
        print(f"✅ Selenium: Available (v{selenium.__version__})")
        results['selenium'] = True
    except ImportError as e:
        print(f"❌ Selenium: Missing ({e})")
        results['selenium'] = False
    
    # Check webdriver-manager
    try:
        from webdriver_manager.chrome import ChromeDriverManager
        print("✅ WebDriver Manager: Available")
        results['webdriver_manager'] = True
    except ImportError as e:
        print(f"⚠️ WebDriver Manager: Missing ({e}) - Will try system chromedriver")
        results['webdriver_manager'] = False
    
    # Check browser client
    try:
        from poe_search.api.browser_client import PoeApiClient
        print("✅ Browser Client: Available")
        results['browser_client'] = True
    except ImportError as e:
        print(f"❌ Browser Client: Missing ({e})")
        results['browser_client'] = False
    
    return results

def check_tokens() -> Dict[str, Any]:
    """Check token configuration."""
    print_step("Checking Token Configuration")
    
    config_file = project_root / "config" / "poe_tokens.json"
    results = {'file_exists': False, 'tokens': {}}
    
    if config_file.exists():
        print(f"✅ Config file found: {config_file}")
        results['file_exists'] = True
        
        try:
            with open(config_file, 'r') as f:
                tokens = json.load(f)
                results['tokens'] = tokens
                
            if tokens.get('p-b'):
                masked_token = tokens['p-b'][:8] + "..." + tokens['p-b'][-8:]
                print(f"✅ Primary token (p-b): {masked_token}")
                results['has_primary'] = True
            else:
                print("❌ Primary token (p-b): Missing")
                results['has_primary'] = False
                
            if tokens.get('p-lat'):
                masked_lat = tokens['p-lat'][:8] + "..." + tokens['p-lat'][-8:]
                print(f"✅ Secondary token (p-lat): {masked_lat}")
                results['has_secondary'] = True
            else:
                print("⚠️ Secondary token (p-lat): Missing (optional)")
                results['has_secondary'] = False
                
        except Exception as e:
            print(f"❌ Error reading tokens: {e}")
            results['error'] = str(e)
    else:
        print(f"❌ Config file not found: {config_file}")
        print("💡 Create config file with your Poe tokens")
    
    return results

def test_browser_setup() -> bool:
    """Test browser setup without authentication."""
    print_step("Testing Browser Setup")
    
    try:
        from poe_search.api.browser_client import PoeApiClient
        
        print("🔄 Initializing browser client...")
        client = PoeApiClient(headless=True)
        
        if client.driver:
            print("✅ Browser initialized successfully")
            
            # Test basic navigation
            print("🔄 Testing basic navigation...")
            client.driver.get("https://www.google.com")
            title = client.driver.title
            print(f"✅ Navigation test passed (title: {title[:50]}...)")
            
            client.close()
            return True
        else:
            print("❌ Browser failed to initialize")
            return False
            
    except Exception as e:
        print(f"❌ Browser setup error: {e}")
        traceback.print_exc()
        return False

def test_poe_authentication(tokens: Dict[str, str]) -> bool:
    """Test Poe.com authentication."""
    print_step("Testing Poe.com Authentication")
    
    if not tokens.get('p-b'):
        print("❌ Cannot test authentication: No primary token")
        return False
    
    try:
        from poe_search.api.browser_client import PoeApiClient
        
        print("🔄 Creating authenticated client...")
        client = PoeApiClient(
            token=tokens['p-b'],
            lat_token=tokens.get('p-lat'),
            headless=True
        )
        
        print("🔄 Testing authentication...")
        auth_result = client.authenticate()
        
        if auth_result:
            print("✅ Authentication successful!")
            client.close()
            return True
        else:
            print("❌ Authentication failed")
            client.close()
            return False
            
    except Exception as e:
        print(f"❌ Authentication test error: {e}")
        traceback.print_exc()
        return False

def test_conversation_extraction(tokens: Dict[str, str]) -> List[Dict[str, Any]]:
    """Test conversation extraction."""
    print_step("Testing Conversation Extraction")
    
    if not tokens.get('p-b'):
        print("❌ Cannot test extraction: No primary token")
        return []
    
    try:
        from poe_search.api.browser_client import PoeApiClient
        
        print("🔄 Creating client for conversation extraction...")
        client = PoeApiClient(
            token=tokens['p-b'],
            lat_token=tokens.get('p-lat'),
            headless=True
        )
        
        def progress_callback(message, percentage):
            print(f"  📊 {percentage:3d}% - {message}")
        
        print("🔄 Authenticating...")
        if not client.authenticate(progress_callback):
            print("❌ Authentication failed during extraction test")
            client.close()
            return []
        
        print("🔄 Extracting conversations (limit: 5)...")
        conversations = client.get_conversations(limit=5, progress_callback=progress_callback)
        
        print(f"✅ Extracted {len(conversations)} conversations")
        
        # Analyze conversation structure
        if conversations:
            sample = conversations[0]
            print(f"\n📋 Sample conversation structure:")
            for key, value in sample.items():
                if key == 'messages':
                    print(f"  {key}: {len(value)} messages")
                elif isinstance(value, str) and len(value) > 50:
                    print(f"  {key}: {value[:50]}...")
                else:
                    print(f"  {key}: {value}")
        
        client.close()
        return conversations
        
    except Exception as e:
        print(f"❌ Conversation extraction error: {e}")
        traceback.print_exc()
        return []

def test_gui_components() -> bool:
    """Test GUI components without launching full app."""
    print_step("Testing GUI Components")
    
    try:
        from PyQt6.QtWidgets import QApplication
        from PyQt6.QtCore import QTimer
        import sys
        
        # Create minimal app for testing
        app = QApplication(sys.argv) if not QApplication.instance() else QApplication.instance()
        
        print("🔄 Testing GUI imports...")
        
        # Test main window creation
        sys.path.insert(0, str(project_root))
        
        # Import without creating full window
        print("✅ PyQt6 widgets import successful")
        
        # Test that we can create basic widgets
        from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel
        
        test_widget = QWidget()
        layout = QVBoxLayout(test_widget)
        label = QLabel("Test")
        layout.addWidget(label)
        
        print("✅ Basic widget creation successful")
        
        return True
        
    except Exception as e:
        print(f"❌ GUI component test error: {e}")
        traceback.print_exc()
        return False

def test_file_structure() -> Dict[str, bool]:
    """Test project file structure."""
    print_step("Testing File Structure")
    
    required_files = {
        'gui_launcher.py': project_root / 'gui_launcher.py',
        'browser_client.py': project_root / 'src' / 'poe_search' / 'api' / 'browser_client.py',
        'config_dir': project_root / 'config',
        'logs_dir': project_root / 'logs',
        'src_dir': project_root / 'src',
    }
    
    results = {}
    
    for name, path in required_files.items():
        if path.exists():
            print(f"✅ {name}: Found at {path}")
            results[name] = True
        else:
            print(f"❌ {name}: Missing at {path}")
            results[name] = False
    
    return results

def run_integration_test(tokens: Dict[str, str]) -> bool:
    """Run full integration test."""
    print_step("Running Integration Test")
    
    if not tokens.get('p-b'):
        print("❌ Cannot run integration test: No primary token")
        return False
    
    try:
        print("🔄 Starting integration test...")
        
        # Test 1: Browser client standalone
        print("\n1️⃣ Testing browser client...")
        from poe_search.api.browser_client import PoeApiClient
        
        client = PoeApiClient(token=tokens['p-b'], headless=True)
        
        if not client.authenticate():
            print("❌ Integration test failed: Authentication")
            return False
        
        conversations = client.get_conversations(limit=3)
        client.close()
        
        if not conversations:
            print("❌ Integration test failed: No conversations extracted")
            return False
        
        print(f"✅ Successfully extracted {len(conversations)} conversations")
        
        # Test 2: Data structure validation
        print("\n2️⃣ Validating data structure...")
        required_fields = ['id', 'title', 'bot', 'url', 'method']
        
        for i, conv in enumerate(conversations):
            missing_fields = []
            for field in required_fields:
                if field not in conv:
                    missing_fields.append(field)
            
            if missing_fields:
                print(f"⚠️ Conversation {i+1} missing fields: {missing_fields}")
            else:
                print(f"✅ Conversation {i+1} structure valid")
        
        print("✅ Integration test passed!")
        return True
        
    except Exception as e:
        print(f"❌ Integration test error: {e}")
        traceback.print_exc()
        return False

def generate_test_report(results: Dict[str, Any]):
    """Generate comprehensive test report."""
    print_section("🔍 DIAGNOSTIC REPORT")
    
    report_file = project_root / f"diagnostic_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    
    report_lines = [
        f"Poe Search Diagnostic Report",
        f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"Project Root: {project_root}",
        "",
        "=" * 50,
        ""
    ]
    
    # Dependency Status
    report_lines.extend([
        "DEPENDENCY STATUS:",
        f"  PyQt6: {'✅ Available' if results.get('dependencies', {}).get('pyqt6') else '❌ Missing'}",
        f"  Selenium: {'✅ Available' if results.get('dependencies', {}).get('selenium') else '❌ Missing'}",
        f"  Browser Client: {'✅ Available' if results.get('dependencies', {}).get('browser_client') else '❌ Missing'}",
        ""
    ])
    
    # Token Status
    token_info = results.get('tokens', {})
    report_lines.extend([
        "TOKEN STATUS:",
        f"  Config File: {'✅ Found' if token_info.get('file_exists') else '❌ Missing'}",
        f"  Primary Token: {'✅ Present' if token_info.get('has_primary') else '❌ Missing'}",
        f"  Secondary Token: {'✅ Present' if token_info.get('has_secondary') else '⚠️ Missing (optional)'}",
        ""
    ])
    
    # Test Results
    report_lines.extend([
        "TEST RESULTS:",
        f"  Browser Setup: {'✅ Passed' if results.get('browser_setup') else '❌ Failed'}",
        f"  Authentication: {'✅ Passed' if results.get('authentication') else '❌ Failed'}",
        f"  Conversation Extraction: {'✅ Passed' if results.get('extraction_count', 0) > 0 else '❌ Failed'}",
        f"  GUI Components: {'✅ Passed' if results.get('gui_test') else '❌ Failed'}",
        f"  Integration Test: {'✅ Passed' if results.get('integration') else '❌ Failed'}",
        ""
    ])
    
    # Recommendations
    report_lines.extend([
        "RECOMMENDATIONS:",
    ])
    
    if not results.get('dependencies', {}).get('pyqt6'):
        report_lines.append("  ❌ Install PyQt6: pip install PyQt6")
    
    if not results.get('dependencies', {}).get('selenium'):
        report_lines.append("  ❌ Install Selenium: pip install selenium")
    
    if not token_info.get('has_primary'):
        report_lines.append("  ❌ Configure Poe tokens in config/poe_tokens.json")
    
    if not results.get('browser_setup'):
        report_lines.append("  ❌ Check Chrome/Chromium installation")
    
    if not results.get('authentication'):
        report_lines.append("  ❌ Verify Poe tokens are valid and not expired")
    
    if results.get('extraction_count', 0) == 0:
        report_lines.append("  ❌ Check Poe.com access and token permissions")
    
    if not results.get('gui_test'):
        report_lines.append("  ❌ Check display settings and GUI dependencies")
    
    # Write report
    try:
        with open(report_file, 'w') as f:
            f.write('\n'.join(report_lines))
        
        print(f"📄 Full report saved to: {report_file}")
        
        # Print summary
        print("\n📊 SUMMARY:")
        total_tests = 5
        passed_tests = sum([
            results.get('browser_setup', False),
            results.get('authentication', False),
            results.get('extraction_count', 0) > 0,
            results.get('gui_test', False),
            results.get('integration', False)
        ])
        
        print(f"  Tests Passed: {passed_tests}/{total_tests}")
        
        if passed_tests == total_tests:
            print("  🎉 All tests passed! Your system should work correctly.")
        elif passed_tests >= 3:
            print("  ⚠️ Most tests passed. Check failed tests above.")
        else:
            print("  ❌ Multiple tests failed. Review recommendations above.")
            
    except Exception as e:
        print(f"❌ Could not save report: {e}")

def main():
    """Run comprehensive diagnostics."""
    print("🔍 Poe Search Comprehensive Diagnostics")
    print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    setup_logging()
    
    results = {}
    
    # Test 1: Dependencies
    print_section("1️⃣ DEPENDENCY CHECK")
    results['dependencies'] = check_dependencies()
    
    # Test 2: Tokens
    print_section("2️⃣ TOKEN CONFIGURATION")
    results['tokens'] = check_tokens()
    
    # Test 3: File structure
    print_section("3️⃣ FILE STRUCTURE")
    results['file_structure'] = test_file_structure()
    
    # Test 4: Browser setup
    print_section("4️⃣ BROWSER SETUP")
    results['browser_setup'] = test_browser_setup()
    
    # Test 5: GUI components
    print_section("5️⃣ GUI COMPONENTS")
    results['gui_test'] = test_gui_components()
    
    # Test 6: Authentication (only if tokens available)
    if results['tokens'].get('has_primary'):
        print_section("6️⃣ POE AUTHENTICATION")
        results['authentication'] = test_poe_authentication(results['tokens'].get('tokens', {}))
        
        # Test 7: Conversation extraction (only if auth works)
        if results.get('authentication'):
            print_section("7️⃣ CONVERSATION EXTRACTION")
            conversations = test_conversation_extraction(results['tokens'].get('tokens', {}))
            results['extraction_count'] = len(conversations)
            results['sample_conversations'] = conversations[:2] if conversations else []
            
            # Test 8: Integration test
            print_section("8️⃣ INTEGRATION TEST")
            results['integration'] = run_integration_test(results['tokens'].get('tokens', {}))
    else:
        print_section("6️⃣ SKIPPING AUTHENTICATION TESTS")
        print("❌ No primary token found - skipping authentication tests")
    
    # Generate report
    generate_test_report(results)
    
    return results

if __name__ == "__main__":
    try:
        results = main()
        
        # Exit with appropriate code
        if results.get('integration') or (results.get('extraction_count', 0) > 0):
            sys.exit(0)  # Success
        else:
            sys.exit(1)  # Failure
            
    except KeyboardInterrupt:
        print("\n🛑 Diagnostics interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"\n❌ Diagnostic script error: {e}")
        traceback.print_exc()
        sys.exit(1)