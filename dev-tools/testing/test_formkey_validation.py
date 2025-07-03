#!/usr/bin/env python3
"""Test script to validate formkey security."""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from poe_search.utils.token_manager import TokenManager


def test_formkey_validation():
    """Test formkey validation against dangerous values."""
    manager = TokenManager()
    
    # Test dangerous formkey values that should be blocked
    dangerous_values = [
        'pkill -f python',
        'rm -rf /',
        'eval("alert()");',
        'http://evil.com',
        '<script>alert()</script>',
        'window.location.href',
        'document.cookie',
        'import os',
        'subprocess.call',
        'onload=evil()',
        'javascript:alert()',
        'www.evil.com'
    ]
    
    print('🔒 Testing formkey validation security:')
    print('='*50)
    
    all_blocked = True
    for value in dangerous_values:
        result = manager.validate_formkey(value)
        status = "✅ BLOCKED" if not result else "❌ ALLOWED"
        print(f'  "{value[:25]:<25}" -> {status}')
        if result:
            all_blocked = False
    
    # Test valid formkey values that should be allowed
    valid_values = [
        'abc123def456ghi789jkl012mno345pqr678stu901',
        '1a2b3c4d5e6f7g8h9i0j1k2l3m4n5o6p7q8r9s0t',
        'AbCdEf123456789012345678901234567890AbCdEf',
        'valid_formkey_with_underscores_123456789',
        'FormKey-With-Dashes-1234567890123456789'
    ]
    
    print('\n✅ Testing valid formkey values:')
    print('='*50)
    
    all_allowed = True
    for value in valid_values:
        result = manager.validate_formkey(value)
        status = "✅ ALLOWED" if result else "❌ BLOCKED"
        print(f'  "{value[:25]:<25}" -> {status}')
        if not result:
            all_allowed = False
    
    # Summary
    print('\n📊 VALIDATION SUMMARY:')
    print('='*50)
    if all_blocked:
        print('✅ All dangerous values were correctly BLOCKED')
    else:
        print('❌ Some dangerous values were incorrectly ALLOWED')
        
    if all_allowed:
        print('✅ All valid values were correctly ALLOWED')
    else:
        print('❌ Some valid values were incorrectly BLOCKED')
        
    if all_blocked and all_allowed:
        print('\n🎉 FORMKEY VALIDATION IS WORKING CORRECTLY!')
        return True
    else:
        print('\n⚠️  FORMKEY VALIDATION NEEDS IMPROVEMENT!')
        return False

if __name__ == "__main__":
    success = test_formkey_validation()
    sys.exit(0 if success else 1)
