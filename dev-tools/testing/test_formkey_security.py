#!/usr/bin/env python3
"""Direct test of formkey validation without token loading."""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Import just what we need for validation
from poe_search.utils.token_manager import TokenManager


def test_validation_only():
    """Test only the validate_formkey method."""
    # Create manager but don't load tokens
    manager = TokenManager()
    
    print('🔒 FORMKEY VALIDATION SECURITY TEST')
    print('='*60)
    
    # Test dangerous values
    dangerous_tests = [
        ('pkill -f python', 'Shell command'),
        ('rm -rf /', 'Destructive command'),
        ('eval("code");', 'JavaScript eval'),
        ('http://evil.com', 'URL'),
        ('<script>alert()</script>', 'HTML script'),
        ('window.location', 'DOM manipulation'),
        ('document.cookie', 'Cookie access'),
        ('import os', 'Python import'),
        ('subprocess.call', 'Subprocess'),
        ('javascript:alert()', 'JavaScript URL'),
        ('data:text/html,<script>', 'Data URL'),
        ('vbscript:msgbox', 'VBScript'),
        ('onload=evil()', 'Event handler'),
        ('www.evil.com', 'Domain'),
        ('ftp://server', 'FTP URL'),
        ('&&', 'Command chaining'),
        ('||', 'Command chaining'),
        (';', 'Command separator'),
        ('|', 'Pipe'),
        ('>', 'Redirect'),
        ('<', 'Redirect'),
        ('$var', 'Variable expansion'),
        ('`command`', 'Command substitution'),
        ('', 'Empty string'),
        ('short', 'Too short'),
    ]
    
    blocked_count = 0
    for value, description in dangerous_tests:
        is_valid = manager.validate_formkey(value)
        status = "❌ ALLOWED" if is_valid else "✅ BLOCKED"
        print(f'  {description:<20} "{value[:15]:<15}" -> {status}')
        if not is_valid:
            blocked_count += 1
    
    print(f'\n📊 Dangerous values blocked: {blocked_count}/{len(dangerous_tests)}')
    
    # Test valid values
    print('\n✅ TESTING VALID FORMKEY VALUES')
    print('='*60)
    
    valid_tests = [
        ('abc123def456ghi789jkl012mno345pqr678stu901', 'Alphanumeric long'),
        ('1a2b3c4d5e6f7g8h9i0j1k2l3m4n5o6p7q8r9s0t', 'Mixed alphanumeric'),
        ('AbCdEf123456789012345678901234567890AbCdEf', 'Mixed case'),
        ('valid_formkey_with_underscores_1234567890', 'With underscores'),
        ('FormKey-With-Dashes-1234567890123456789', 'With dashes'),
        ('key+value=data/encoding.test123456789', 'With allowed special chars'),
    ]
    
    allowed_count = 0
    for value, description in valid_tests:
        is_valid = manager.validate_formkey(value)
        status = "✅ ALLOWED" if is_valid else "❌ BLOCKED"
        print(f'  {description:<25} -> {status}')
        if is_valid:
            allowed_count += 1
    
    print(f'\n📊 Valid values allowed: {allowed_count}/{len(valid_tests)}')
    
    # Summary
    all_dangerous_blocked = blocked_count == len(dangerous_tests)
    all_valid_allowed = allowed_count == len(valid_tests)
    
    print('\n🎯 SECURITY VALIDATION SUMMARY')
    print('='*60)
    if all_dangerous_blocked:
        print('✅ All dangerous patterns correctly blocked')
    else:
        print(f'❌ {len(dangerous_tests) - blocked_count} dangerous patterns not blocked!')
        
    if all_valid_allowed:
        print('✅ All valid formkeys correctly allowed')
    else:
        print(f'❌ {len(valid_tests) - allowed_count} valid formkeys incorrectly blocked!')
        
    if all_dangerous_blocked and all_valid_allowed:
        print('\n🎉 FORMKEY VALIDATION IS SECURE AND WORKING!')
        return True
    else:
        print('\n⚠️  FORMKEY VALIDATION NEEDS IMPROVEMENT!')
        return False

if __name__ == "__main__":
    try:
        success = test_validation_only()
        print(f'\n🔐 Security test {"PASSED" if success else "FAILED"}')
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f'❌ Test failed with error: {e}')
        sys.exit(1)
