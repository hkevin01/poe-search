# Data Directory

This directory contains runtime data files for the Poe Search application.

## File Types

### Database Files (*.db)
- `poe_search.db` - Main application database
- `my_conversations.db` - Conversation storage
- `test_conversations.db` - Test database

### Backup Files (*.json)
- `my_conversations_*.json` - Conversation backups
- Timestamped backup files from sync operations

## Important Notes

- **Do not delete** database files while the application is running
- Backup files are created automatically during sync operations
- Database files may be locked during application use
- Regular backups are recommended for important conversation data

## Cleanup

Old backup files can be safely deleted, but keep recent ones for recovery purposes.
Database files should only be deleted if you want to start fresh (this will lose all synced conversations).

# This folder contains exported conversation snapshots and large data files.
# These files are git-ignored by default. Move any large exports here.
# Note: This directory is intended for user exports and large files that are not
# part of the regular application data. Keeping exports here helps in managing
# storage and prevents accidental deletion of important data.
