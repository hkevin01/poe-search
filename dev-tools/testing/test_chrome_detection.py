#!/usr/bin/env python3
"""
Test script for Chrome formkey extraction functionality.
"""

from scripts.get_chrome_formkey import find_chrome_profile_paths


def test_chrome_detection():
    """Test if we can find Chrome profiles."""
    print("Testing Chrome profile detection...")
    
    profiles = find_chrome_profile_paths()
    
    if profiles:
        print(f"✅ Found {len(profiles)} Chrome profile(s):")
        for i, profile in enumerate(profiles, 1):
            print(f"   {i}. {profile}")
            print(f"      Exists: {profile.exists()}")
            if profile.exists():
                cookies_db = profile / "Cookies"
                print(f"      Cookies DB: {cookies_db.exists()}")
    else:
        print("❌ No Chrome profiles found")
        print("   This is normal if Chrome isn't installed or")
        print("   is installed in a non-standard location")


if __name__ == "__main__":
    test_chrome_detection()
