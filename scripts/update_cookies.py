#!/usr/bin/env python3
"""Script to update Poe Search configuration with real cookies."""

import json
import sys
from pathlib import Path


def update_cookies():
    """Update configuration with real Poe cookies."""
    
    print("🔧 Updating Poe Search Configuration with Real Cookies")
    print("=" * 55)
    print()
    
    # Your real Poe cookies (updated with latest from Poe.com response)
    p_b = "DfQXTxycsUmw8n54WtgAMA%3D%3D"  # Updated from Poe.com response
    p_lat = "XlUmYDlcuOk51uFjIRYRSeoJhdWSfwHp3XR2kgZFlw%3D%3D"
    
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
            print(f"  p-lat: {tokens.get('p-lat', 'Not set')[:10] if tokens.get('p-lat') else 'Not set'}...")
        
        print()
        print("🔄 Updating with real Poe cookies...")
        
        # Create new config with real cookies
        new_config = {
            "poe_tokens": {
                "p-b": p_b,
                "p-lat": p_lat,
                "formkey": ""
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
        print(f"  p-lat: {p_lat[:10]}...")
        print(f"  formkey: Not set (optional)")
        
        print()
        print("🧪 Testing configuration...")
        
        # Test the configuration
        try:
            sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
            from poe_search.utils.config import load_config
            
            config = load_config()
            print("✅ Configuration loaded successfully")
            
            # Test API connection
            if hasattr(config, 'get_poe_tokens'):
                tokens = config.get_poe_tokens()
                print(f"✅ Found tokens: p-b={bool(tokens.get('p-b'))}, p-lat={bool(tokens.get('p-lat'))}")
            else:
                print("⚠️  No tokens found in configuration")
            
        except Exception as e:
            print(f"❌ Configuration test failed: {e}")
            return False
        
        print()
        print("🎉 Cookie update completed!")
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
    success = update_cookies()
    sys.exit(0 if success else 1) 