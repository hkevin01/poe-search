#!/usr/bin/env python3
"""Quick test of token manager integration."""

try:
    from poe_search.utils.token_manager import TokenManager
    print('✅ Token manager imports successfully')
    
    manager = TokenManager()
    print('✅ Token manager instantiates successfully')
    print(f'Config dir: {manager.config_dir}')
    print(f'Token file: {manager.token_file}')
    
    from poe_search.utils.token_manager import ensure_tokens_on_startup
    print('✅ ensure_tokens_on_startup imports successfully')
    
    print('✅ All integration tests passed!')
    
except Exception as e:
    print(f'❌ Integration test failed: {e}')
