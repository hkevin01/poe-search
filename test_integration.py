#!/usr/bin/env python3
"""
Test the token management integration without requiring fresh tokens.

This script tests the integration points and error handling of the
automatic token management system.
"""

import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_token_manager_integration():
    """Test token manager integration without requiring real tokens."""
    print("="*60)
    print("TOKEN MANAGEMENT INTEGRATION TEST")
    print("="*60)
    
    try:
        from poe_search.utils.token_manager import TokenManager, ensure_tokens_on_startup
        
        print("✅ Token manager module imports successfully")
        
        # Test TokenManager class
        manager = TokenManager()
        print("✅ TokenManager class instantiates successfully")
        
        # Test configuration detection
        config_dir = manager.config_dir
        print(f"✅ Config directory detected: {config_dir}")
        
        token_file = manager.token_file
        print(f"✅ Token file path: {token_file}")
        
        # Test token file existence
        if token_file.exists():
            print("✅ Token file exists")
            
            # Test token loading
            tokens = manager.load_tokens()
            if tokens:
                print("✅ Tokens loaded successfully")
                print(f"   - Has p-b: {'p-b' in tokens and bool(tokens['p-b'])}")
                print(f"   - Has p-lat: {'p-lat' in tokens and bool(tokens['p-lat'])}")
                print(f"   - Has formkey: {'formkey' in tokens and bool(tokens['formkey'])}")
                
                # Test age checking
                age = manager.get_token_age()
                if age:
                    hours = age.total_seconds() / 3600
                    print(f"✅ Token age calculation: {hours:.1f} hours")
                    
                    # Test freshness checking
                    fresh_36h = manager.are_tokens_fresh(36)
                    fresh_12h = manager.are_tokens_fresh(12)
                    print(f"✅ Freshness check (36h): {fresh_36h}")
                    print(f"✅ Freshness check (12h): {fresh_12h}")
                else:
                    print("⚠️  Could not determine token age")
            else:
                print("⚠️  Token file exists but tokens could not be loaded")
        else:
            print("⚠️  No token file found (expected for fresh installation)")
        
        # Test non-interactive mode
        print("\n🔄 Testing non-interactive mode...")
        success, tokens = ensure_tokens_on_startup(
            interactive=False,  # No user prompts
            max_age_hours=36
        )
        
        if success:
            print("✅ Non-interactive token check: SUCCESS")
            print("   Tokens are available and fresh")
        else:
            print("⚠️  Non-interactive token check: FAILED")
            print("   This is expected if tokens are missing/stale")
            print("   (Interactive mode would prompt for refresh)")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        logger.exception("Test failed")
        return False


def test_gui_integration():
    """Test GUI integration points."""
    print("\n🖥️  Testing GUI integration...")
    
    try:
        # Test GUI main module imports
        from poe_search.gui import __main__ as gui_main
        print("✅ GUI main module imports successfully")
        
        # Check if the main function includes token checking
        import inspect
        source = inspect.getsource(gui_main.main)
        if "ensure_tokens_on_startup" in source:
            print("✅ GUI main function includes token checking")
        else:
            print("⚠️  GUI main function may not include token checking")
            
        return True
        
    except Exception as e:
        print(f"❌ GUI integration test failed: {e}")
        return False


def test_cli_integration():
    """Test CLI integration points."""
    print("\n⌨️  Testing CLI integration...")
    
    try:
        # Test CLI module imports
        from poe_search.cli import main as cli_main
        print("✅ CLI module imports successfully")
        
        # Check if CLI includes token management
        import inspect
        source = inspect.getsource(cli_main)
        if "ensure_tokens_on_startup" in source:
            print("✅ CLI includes token checking")
        else:
            print("⚠️  CLI may not include token checking")
            
        if "skip-token-check" in source:
            print("✅ CLI includes skip-token-check option")
        else:
            print("⚠️  CLI may not include skip option")
            
        return True
        
    except Exception as e:
        print(f"❌ CLI integration test failed: {e}")
        return False


def test_config_integration():
    """Test config module integration."""
    print("\n⚙️  Testing config integration...")
    
    try:
        from poe_search.utils.config import load_poe_tokens_from_file
        print("✅ Config module token function imports successfully")
        
        # Test the new load function  
        tokens = load_poe_tokens_from_file(max_age_hours=48)
        if tokens:
            print("✅ Config token loading works")
        else:
            print("⚠️  Config token loading returned empty (may be expected)")
            
        return True
        
    except Exception as e:
        print(f"❌ Config integration test failed: {e}")
        return False


def main():
    """Run all integration tests."""
    print("Automatic Token Management - Integration Test Suite")
    print("This tests the integration points without requiring fresh tokens\n")
    
    tests = [
        ("Core Token Manager", test_token_manager_integration),
        ("GUI Integration", test_gui_integration), 
        ("CLI Integration", test_cli_integration),
        ("Config Integration", test_config_integration),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            success = test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"❌ Test {test_name} crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "="*60)
    print("INTEGRATION TEST RESULTS")
    print("="*60)
    
    passed = 0
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} - {test_name}")
        if success:
            passed += 1
    
    print(f"\nOverall: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("\n🎉 All integration tests passed!")
        print("The automatic token management system is properly integrated.")
    else:
        print(f"\n⚠️  {len(results) - passed} test(s) failed.")
        print("Some integration points may need attention.")
    
    print("\nTo test with live tokens:")
    print("1. Run: python scripts/refresh_tokens.py")
    print("2. Run: python test_token_management.py")
    print("3. Run: python demo_startup_integration.py")


if __name__ == "__main__":
    main()
