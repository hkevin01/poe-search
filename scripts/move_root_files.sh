#!/usr/bin/env bash
# Move all root-level scripts, db, logs, and desktop entry to their proper folders
# Run this from the project root: bash scripts/move_root_files.sh

set -e

# Test scripts
mkdir -p scripts/test
mv -v test_auth.py test_conversation_sync.py test_graphql_debug.py test_gui_approach.py test_simple_graphql.py test_sync_status.py test_wrapper_sync.py scripts/test/ 2>/dev/null || true

# Dev/debug scripts
mkdir -p dev-tools/graphql dev-tools/token dev-tools/api
mv -v debug_graphql.py dev-tools/graphql/ 2>/dev/null || true
mv -v debug_graphql_focused.py dev-tools/graphql/ 2>/dev/null || true
mv -v force_token_extraction.py dev-tools/token/ 2>/dev/null || true
mv -v query_poe_api.py dev-tools/api/ 2>/dev/null || true

# Database and logs
mkdir -p data logs
mv -v poe_search.db data/ 2>/dev/null || true
mv -v poe_search.log logs/ 2>/dev/null || true

# Desktop entry
mkdir -p scripts/desktop
mv -v poe-search.desktop scripts/desktop/ 2>/dev/null || true

echo "All root-level files have been moved to their proper folders."
