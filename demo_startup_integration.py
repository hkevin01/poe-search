#!/usr/bin/env python3
"""
Startup token refresh integration demo.

This script demonstrates how the automatic token refresh works
when integrated into the main application startup sequence.
"""

import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def simulate_app_startup(app_name: str = "Poe Search Demo"):
    """Simulate application startup with token refresh."""
    print("="*60)
    print(f"{app_name.upper()} - STARTUP SEQUENCE")
    print("="*60)
    
    try:
        from poe_search.utils.token_manager import ensure_tokens_on_startup
        
        # Step 1: Application initialization
        print("🚀 Step 1: Application initialization...")
        print(f"   - Starting {app_name}")
        print("   - Loading configuration...")
        print("   - Setting up logging...")
        
        # Step 2: Token management
        print("\n🔐 Step 2: Poe.com authentication...")
        print("   - Checking token freshness...")
        
        success, tokens = ensure_tokens_on_startup(
            interactive=True,
            max_age_hours=36
        )
        
        if success:
            print("   ✅ Tokens are fresh and ready")
            logger.info("Token validation successful")
            
            # Show token status without revealing sensitive data
            if tokens:
                age_info = ""
                try:
                    from poe_search.utils.token_manager import TokenManager
                    manager = TokenManager()
                    age = manager.get_token_age()
                    if age:
                        hours = age.total_seconds() / 3600
                        age_info = f" (age: {hours:.1f}h)"
                except Exception:
                    pass
                
                print(f"   - p-b token: Present{age_info}")
                print(f"   - p-lat token: Present{age_info}")
                print(f"   - formkey: Present{age_info}")
        else:
            print("   ❌ Token validation failed")
            logger.error("Could not obtain valid tokens")
            return False
        
        # Step 3: API client initialization
        print("\n🌐 Step 3: API client initialization...")
        try:
            from poe_search.api.client import PoeAPIClient
            client = PoeAPIClient(token=tokens)
            
            if client.client:
                print("   ✅ API client initialized successfully")
                
                # Test API connectivity
                print("   - Testing API connectivity...")
                bots = client.get_bots()
                if isinstance(bots, dict) and len(bots) > 0:
                    print(f"   ✅ Connected - {len(bots)} bots available")
                    
                    # Show a few bot names
                    bot_names = list(bots.keys())[:3]
                    print(f"   - Sample bots: {', '.join(bot_names)}")
                else:
                    msg = "API connected but limited data (may be mock)"
                    print(f"   ⚠️  {msg}")
            else:
                print("   ❌ API client initialization failed")
                return False
                
        except Exception as e:
            print(f"   ❌ API initialization error: {e}")
            return False
        
        # Step 4: Application ready
        print("\n🎉 Step 4: Application ready!")
        print("   ✅ All systems operational")
        print("   ✅ Ready to sync conversations")
        print("   ✅ Ready to search and export")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure you're running from the project root directory")
        return False
    except Exception as e:
        print(f"💥 Unexpected error: {e}")
        logger.exception("Startup failed")
        return False


def main():
    """Main demo function."""
    print("Token Refresh Integration Demo")
    print("This demonstrates automatic token refresh on app startup\n")
    
    # Demo different scenarios
    scenarios = [
        "GUI Application",
        "CLI Application",
        "Background Sync Service"
    ]
    
    for i, scenario in enumerate(scenarios, 1):
        print(f"\n🔄 Demo {i}/{len(scenarios)}: {scenario}")
        success = simulate_app_startup(scenario)
        
        if success:
            print(f"✅ {scenario} startup: SUCCESS")
        else:
            print(f"❌ {scenario} startup: FAILED")
            
        # Only run first demo unless tokens are working
        if not success:
            print("\nℹ️  Skipping remaining demos due to token issues")
            break
        
        if i < len(scenarios):
            print("\n" + "-"*40)
    
    print("\n" + "="*60)
    print("INTEGRATION DEMO COMPLETE")
    print("="*60)
    
    print("\nKey Benefits:")
    print("✅ Automatic token freshness checking")
    print("✅ Interactive refresh when needed")
    print("✅ Graceful error handling")
    print("✅ No manual token management required")
    print("✅ Works with GUI, CLI, and background services")
    
    print("\nUsage in your applications:")
    print("from poe_search.utils.token_manager import \\")
    print("    ensure_tokens_on_startup")
    print("success, tokens = ensure_tokens_on_startup()")
    print("if success:")
    print("    # Your app logic here")
    print("    pass")


if __name__ == "__main__":
    main()
