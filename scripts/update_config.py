#!/usr/bin/env python3
"""Script to help update Poe Search configuration with new cookie format."""

import json
import sys
from pathlib import Path


def update_config():
    """Update configuration to use new cookie format."""
    
    print("🔧 Poe Search Configuration Update")
    print("=" * 40)
    print()
    
    # Check current config
    config_path = Path("config/secrets.json")
    
    if not config_path.exists():
        print("❌ No existing configuration found")
        return False
    
    try:
        with open(config_path, 'r') as f:
            current_config = json.load(f)
        
        print("📋 Current configuration:")
        if 'poe_api_key' in current_config:
            print(f"  API Key: {current_config['poe_api_key'][:10]}...")
            print("  ⚠️  Using old API key format")
        elif 'poe_tokens' in current_config:
            print("  ✅ Using new cookie format")
            tokens = current_config['poe_tokens']
            print(f"  p-b: {tokens.get('p-b', 'Not set')[:10]}...")
            print(f"  p-lat: {tokens.get('p-lat', 'Not set')[:10] if tokens.get('p-lat') else 'Not set'}")
            print(f"  formkey: {tokens.get('formkey', 'Not set')[:10] if tokens.get('formkey') else 'Not set'}")
        
        print()
        
        # Check if we need to migrate
        if 'poe_api_key' in current_config:
            print("🔄 Migration needed: Converting from API key to cookie format")
            print()
            
            # Get user input for new cookies
            print("📝 Please provide your Poe.com cookies:")
            print("  1. Go to https://poe.com and sign in")
            print("  2. Press F12 → Application → Cookies → poe.com")
            print("  3. Copy the values below:")
            print()
            
            p_b = input("Enter p-b cookie value: ").strip()
            p_lat = input("Enter p-lat cookie value: ").strip()
            formkey = input("Enter formkey (optional, press Enter to skip): ").strip()
            
            if not p_b:
                print("❌ p-b cookie is required!")
                return False
            
            # Create new config
            new_config = {
                "poe_tokens": {
                    "p-b": p_b,
                    "p-lat": p_lat if p_lat else None,
                    "formkey": formkey if formkey else None
                },
                "sync_interval": 3600,
                "max_conversations": 10000,
                "theme": "default",
                "auto_sync": True,
                "debug_mode": False
            }
            
            # Backup old config
            backup_path = config_path.with_suffix('.json.backup')
            with open(backup_path, 'w') as f:
                json.dump(current_config, f, indent=2)
            print(f"💾 Backup saved to: {backup_path}")
            
            # Save new config
            with open(config_path, 'w') as f:
                json.dump(new_config, f, indent=2)
            
            print("✅ Configuration updated successfully!")
            print()
            print("🔍 New configuration:")
            print(f"  p-b: {p_b[:10]}...")
            print(f"  p-lat: {p_lat[:10] if p_lat else 'Not set'}...")
            print(f"  formkey: {formkey[:10] if formkey else 'Not set'}...")
            
        else:
            print("✅ Configuration is already in the correct format")
            
            # Check if cookies are complete
            tokens = current_config.get('poe_tokens', {})
            if not tokens.get('p-b'):
                print("❌ p-b cookie is missing!")
                return False
            
            if not tokens.get('p-lat'):
                print("⚠️  p-lat cookie is missing - this may cause issues")
                print("   Consider adding it for better compatibility")
            
            print("✅ Configuration looks good!")
        
        print()
        print("🧪 Testing configuration...")
        
        # Test the configuration
        try:
            sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
            from poe_search.utils.config import load_config
            
            config = load_config()
            print("✅ Configuration loaded successfully")
            
            # Test API connection
            if hasattr(config, 'poe_tokens'):
                tokens = config.poe_tokens
                print(f"✅ Found tokens: p-b={bool(tokens.get('p-b'))}, p-lat={bool(tokens.get('p-lat'))}")
            else:
                print("⚠️  No tokens found in configuration")
            
        except Exception as e:
            print(f"❌ Configuration test failed: {e}")
            return False
        
        print()
        print("🎉 Configuration update completed!")
        print()
        print("📋 Next steps:")
        print("  1. Run: python scripts/test_poe_api.py")
        print("  2. Run: ./run.sh")
        print("  3. Your real Poe conversations should now load!")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to update configuration: {e}")
        return False

if __name__ == "__main__":
    success = update_config()
    sys.exit(0 if success else 1) 