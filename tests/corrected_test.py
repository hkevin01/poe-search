#!/usr/bin/env python3
"""
Final test with correct token format - using hyphens instead of underscores
"""

import sys
import os
import urllib.parse

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

try:
    from poe_api_wrapper import PoeApi
    print("✓ PoeApi imported successfully")
except ImportError as e:
    print(f"❌ Failed to import PoeApi: {e}")
    sys.exit(1)

def main():
    print("🔧 Testing PoeApi with CORRECTED token format (hyphens instead of underscores)")
    
    # Read the tokens from the extracted file
    token_file = "/home/kevin/Projects/poe-search/tests/extracted_tokens.txt"
    
    try:
        with open(token_file, 'r') as f:
            content = f.read().strip()
            print(f"Raw token content: {content[:100]}...")
            
            # URL decode the content
            decoded_content = urllib.parse.unquote(content)
            print(f"Decoded content: {decoded_content[:100]}...")
            
            # Parse tokens manually
            tokens = {}
            for part in decoded_content.split(';'):
                part = part.strip()
                if '=' in part:
                    key, value = part.split('=', 1)
                    key = key.strip()
                    value = value.strip()
                    if key in ['p-b', 'p-lat', 'formkey']:
                        tokens[key] = value
            
            # Add missing formkey if not present
            if 'formkey' not in tokens:
                tokens['formkey'] = 'c25281d6b4dfb3f76fb03c597e3e61aa'
            
            print(f"✓ Parsed tokens: {list(tokens.keys())}")
            print(f"Token values:")
            for key, value in tokens.items():
                if value:
                    print(f"  {key}: {value[:10]}...{value[-10:] if len(value) > 20 else value}")
                else:
                    print(f"  {key}: (empty)")
            
    except FileNotFoundError:
        print("❌ Token file not found, using manual tokens with correct format")
        # Use the corrected format with hyphens
        tokens = {
            "p-b": "AG58MLIXFnbOh98QAv4YHA==",
            "p-lat": "87OepyV2QcF9TkiuqhaFyWZgROH+Vp00g0QZLwZEMg==",
            "formkey": "c25281d6b4dfb3f76fb03c597e3e61aa"
        }
        print(f"Manual tokens: {list(tokens.keys())}")
    
    # Test 1: Create client with corrected token format
    print("\n🧪 Test 1: Creating PoeApi client with corrected token format")
    try:
        client = PoeApi(tokens)
        print("✓ PoeApi client created successfully!")
        
        # Test 2: Get user info
        print("\n🧪 Test 2: Getting user info")
        try:
            settings = client.get_settings()
            print(f"✓ Settings retrieved: {type(settings)}")
            if hasattr(settings, '__dict__'):
                print(f"  Settings keys: {list(settings.__dict__.keys())}")
            
        except Exception as e:
            print(f"❌ Failed to get settings: {e}")
        
        # Test 3: Get conversation history
        print("\n🧪 Test 3: Getting conversation history")
        try:
            conversations = client.get_conversation_history(limit=5)
            print(f"✓ Retrieved {len(conversations)} conversations!")
            
            for i, conv in enumerate(conversations[:3]):  # Show first 3
                if hasattr(conv, 'title'):
                    title = conv.title[:50] + "..." if len(conv.title) > 50 else conv.title
                    print(f"  {i+1}. {title}")
                elif isinstance(conv, dict) and 'title' in conv:
                    title = conv['title'][:50] + "..." if len(conv['title']) > 50 else conv['title']
                    print(f"  {i+1}. {title}")
                else:
                    print(f"  {i+1}. {type(conv)} - {str(conv)[:50]}...")
            
            if len(conversations) > 0:
                print("✅ SUCCESS: We can retrieve conversations!")
                return True
            else:
                print("⚠️  Retrieved 0 conversations - need to investigate further")
                return False
                
        except Exception as e:
            print(f"❌ Failed to get conversation history: {e}")
            return False
            
    except Exception as e:
        print(f"❌ Failed to create client: {e}")
        return False

if __name__ == "__main__":
    success = main()
    if success:
        print("\n✅ CONCLUSION: Authentication successful and can retrieve conversations!")
    else:
        print("\n❌ CONCLUSION: Still unable to fetch conversations")
