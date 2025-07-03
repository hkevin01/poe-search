#!/usr/bin/env python3
"""
Save formkey to token configuration.
"""

import json
import sys
from pathlib import Path


def save_formkey_directly(formkey: str):
    """Save formkey directly to token file."""
    
    # Validate formkey format
    if not formkey or len(formkey) < 10:
        print("❌ Invalid formkey: too short")
        return False
    
    # Basic validation - should be alphanumeric/hex
    if not all(c.isalnum() for c in formkey):
        print("❌ Invalid formkey: should be alphanumeric")
        return False
    
    # Load existing tokens
    config_dir = Path("config")
    token_file = config_dir / "poe_tokens.json"
    
    try:
        if token_file.exists():
            with open(token_file, 'r') as f:
                tokens = json.load(f)
        else:
            tokens = {}
        
        # Update formkey
        tokens['formkey'] = formkey
        
        # Save tokens
        config_dir.mkdir(exist_ok=True)
        with open(token_file, 'w') as f:
            json.dump(tokens, f, indent=2)
        
        print(f"✅ Formkey saved to {token_file}")
        print(f"   Formkey: {formkey}")
        print(f"   Length: {len(formkey)} characters")
        
        return True
        
    except Exception as e:
        print(f"❌ Error saving formkey: {e}")
        return False

if __name__ == "__main__":
    formkey = "c25281d6b4dfb3f76fb03c597e3e61aa"
    print("🔑 Saving Poe.com Formkey")
    print("=" * 30)
    
    if save_formkey_directly(formkey):
        print("\n✅ Success! Your formkey has been saved.")
        print("You can now use the Poe Search application.")
    else:
        print("\n❌ Failed to save formkey.")
        sys.exit(1)
