#!/usr/bin/env bash
# Advanced organization of scripts/ folder into relevant subfolders
# Run this from the project root: bash scripts/organize_scripts_advanced.sh

set -e

# Create subfolders
mkdir -p scripts/test
mkdir -p scripts/desktop
mkdir -p scripts/db
mkdir -p scripts/export
mkdir -p scripts/import
mkdir -p scripts/util
mkdir -p scripts/debug
mkdir -p scripts/automation

# Move test scripts (unit/integration)
find scripts -maxdepth 1 -type f -name 'test_*.py' -exec mv -v {} scripts/test/ \;

# Move desktop entry and related scripts
find scripts -maxdepth 1 -type f -name '*desktop*' -exec mv -v {} scripts/desktop/ \;

# Move db scripts
find scripts -maxdepth 1 -type f -name 'db_*.py' -exec mv -v {} scripts/db/ \;

# Move export scripts
find scripts -maxdepth 1 -type f -name 'export_*.py' -exec mv -v {} scripts/export/ \;

# Move import scripts
find scripts -maxdepth 1 -type f -name 'import_*.py' -exec mv -v {} scripts/import/ \;

# Move utility scripts
find scripts -maxdepth 1 -type f -name 'util_*.py' -exec mv -v {} scripts/util/ \;

# Move debug scripts
find scripts -maxdepth 1 -type f -name 'debug_*.py' -exec mv -v {} scripts/debug/ \;
find scripts -maxdepth 1 -type f -name 'debug_*.sh' -exec mv -v {} scripts/debug/ \;

# Move automation scripts
find scripts -maxdepth 1 -type f -name '*automation*' -exec mv -v {} scripts/automation/ \;

# Move other .sh scripts (except organizing scripts)
for f in scripts/*.sh; do
  case "$f" in
    scripts/organize_scripts.sh|scripts/organize_scripts_advanced.sh|scripts/move_root_files.sh) :;;
    *) mv -v "$f" scripts/util/;;
  esac
done

# Clean up empty files
find scripts/ -type f -empty -delete

echo "Scripts folder organized into relevant subfolders."
