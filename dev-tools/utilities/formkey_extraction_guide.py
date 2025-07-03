#!/usr/bin/env python3
"""
Guide for finding formkey in Chrome Developer Tools.
This script provides step-by-step instructions and common locations.
"""

def print_formkey_guide():
    """Print comprehensive guide for finding formkey."""
    print("🔍 COMPREHENSIVE FORMKEY EXTRACTION GUIDE")
    print("=" * 60)
    
    print("\n📋 STEP-BY-STEP INSTRUCTIONS:")
    print("1. Open Chrome and go to https://poe.com")
    print("2. Make sure you're logged in")
    print("3. Press F12 to open Developer Tools")
    print("4. Click the 'Network' tab")
    print("5. Check 'Preserve log' (important!)")
    print("6. Clear the network log (🗑️ icon)")
    print("7. Type ANY message to ANY bot and send it")
    print("8. Look for these request patterns:")
    
    print("\n🎯 REQUEST PATTERNS TO LOOK FOR:")
    patterns = [
        "/api/gql_POST",
        "/api/send_message", 
        "/api/chat",
        "/graphql",
        "gql",
        "mutation"
    ]
    
    for pattern in patterns:
        print(f"   • {pattern}")
    
    print("\n🔍 FORMKEY LOCATIONS TO CHECK:")
    locations = [
        "Request Headers → 'Poe-Formkey'",
        "Request Headers → 'X-Formkey'", 
        "Request Headers → 'Formkey'",
        "Request Headers → 'X-Poe-Formkey'",
        "Request Headers → 'Authentication'",
        "Form Data → 'formkey'",
        "Request Payload → 'formkey'",
        "Query Parameters → 'formkey'"
    ]
    
    for location in locations:
        print(f"   • {location}")
    
    print("\n💡 ALTERNATIVE METHODS:")
    print("\nMETHOD 1 - Console Search:")
    print("1. Go to Console tab in DevTools")
    print("2. Try these commands one by one:")
    
    console_commands = [
        'document.querySelector(\'meta[name="formkey"]\')?.content',
        'document.querySelector(\'meta[name="poe-formkey"]\')?.content',
        'window.formkey',
        'window.poeFormkey', 
        'localStorage.getItem("formkey")',
        'sessionStorage.getItem("formkey")',
        'Object.keys(localStorage).filter(k => k.includes("formkey"))',
        'Object.keys(sessionStorage).filter(k => k.includes("formkey"))'
    ]
    
    for cmd in console_commands:
        print(f"   {cmd}")
    
    print("\nMETHOD 2 - Page Source Search:")
    print("1. Right-click on page → 'View Page Source'")
    print("2. Search (Ctrl+F) for:")
    print("   • 'formkey'")
    print("   • 'poe-formkey'") 
    print("   • 'Poe-Formkey'")
    print("   • 'X-Formkey'")
    
    print("\nMETHOD 3 - Application Storage:")
    print("1. Go to 'Application' tab in DevTools")
    print("2. Check 'Local Storage' → https://poe.com")
    print("3. Check 'Session Storage' → https://poe.com") 
    print("4. Check 'Cookies' → https://poe.com")
    print("5. Look for keys containing 'formkey'")
    
    print("\n⚠️ TROUBLESHOOTING:")
    print("If you still can't find it:")
    print("1. Make sure you're actually sending a message")
    print("2. Try different bots (Claude, GPT-4, etc.)")
    print("3. Check if requests are being filtered")
    print("4. Clear browser cache and try again")
    print("5. Try incognito mode")
    
    print(f"\n🤖 AUTOMATED EXTRACTION:")
    print("You can also try our automated extraction script:")
    print("   python scripts/get_chrome_formkey.py")

if __name__ == "__main__":
    print_formkey_guide()
