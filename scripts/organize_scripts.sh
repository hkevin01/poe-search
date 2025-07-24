#!/usr/bin/env bash
# Organize scripts/ folder into subfolders and move files
# Run this from the project root: bash scripts/organize_scripts.sh

set -e

# Create subfolders
mkdir -p scripts/test
mkdir -p scripts/desktop
mkdir -p scripts/db
mkdir -p scripts/export
mkdir -p scripts/import
mkdir -p scripts/util

# Move test scripts
mv -v scripts/test_auth.py scripts/test/ 2>/dev/null || true
mv -v scripts/test_conversation_sync.py scripts/test/ 2>/dev/null || true
mv -v scripts/test_graphql_debug.py scripts/test/ 2>/dev/null || true
mv -v scripts/test_gui_approach.py scripts/test/ 2>/dev/null || true
mv -v scripts/test_simple_graphql.py scripts/test/ 2>/dev/null || true
mv -v scripts/test_sync_status.py scripts/test/ 2>/dev/null || true
mv -v scripts/test_wrapper_sync.py scripts/test/ 2>/dev/null || true
# Move provided test scripts
mv -v scripts/check_poe_config.py scripts/test/ 2>/dev/null || true
mv -v scripts/comprehensive_poe_tests.py scripts/test/ 2>/dev/null || true
mv -v scripts/direct_poe_token_test.py scripts/test/ 2>/dev/null || true
mv -v scripts/get_my_conversations.py scripts/test/ 2>/dev/null || true
mv -v scripts/poe_retry.py scripts/test/ 2>/dev/null || true
mv -v scripts/quick_test.py scripts/test/ 2>/dev/null || true

# Move desktop scripts
mv -v scripts/poe-search.desktop scripts/desktop/ 2>/dev/null || true
mv -v scripts/browser_poe.py scripts/desktop/ 2>/dev/null || true
mv -v scripts/browser_poe_fixed.py scripts/desktop/ 2>/dev/null || true
mv -v scripts/poe_gui_automated.py scripts/desktop/ 2>/dev/null || true

# Move db scripts
mv -v scripts/db_*.py scripts/db/ 2>/dev/null || true

# Move export/import scripts
mv -v scripts/export_*.py scripts/export/ 2>/dev/null || true
mv -v scripts/import_*.py scripts/import/ 2>/dev/null || true
# Move provided import scripts
mv -v scripts/capture_poe_cookies.py scripts/import/ 2>/dev/null || true
mv -v scripts/capture_poe_cookies_with_profile.py scripts/import/ 2>/dev/null || true
mv -v scripts/extract_formkey.py scripts/import/ 2>/dev/null || true
mv -v scripts/get_chrome_formkey.py scripts/import/ 2>/dev/null || true
mv -v scripts/get_cookies.py scripts/import/ 2>/dev/null || true
mv -v scripts/refresh_tokens.py scripts/import/ 2>/dev/null || true
mv -v scripts/update_cookies.py scripts/import/ 2>/dev/null || true
mv -v scripts/update_config.py scripts/import/ 2>/dev/null || true
mv -v scripts/manage_credentials.py scripts/import/ 2>/dev/null || true

# Move utility scripts
mv -v scripts/util_*.py scripts/util/ 2>/dev/null || true
# Move provided util scripts
mv -v scripts/generate_icons.py scripts/util/ 2>/dev/null || true
mv -v scripts/poe_bot.py scripts/util/ 2>/dev/null || true

# Move any remaining .py files in scripts/ root to util (except __init__.py)
for f in scripts/*.py; do
  case "$f" in
    scripts/__init__.py) :;;
    scripts/test_*.py|scripts/db_*.py|scripts/export_*.py|scripts/import_*.py|scripts/util_*.py) :;;
    *) mv -v "$f" scripts/util/;;
  esac
done

# Clean up empty files
find scripts/ -type f -empty -delete

echo "Scripts folder organized into subfolders."
