#!/usr/bin/env bash
# Clean all 'chinchilla', 'beaver', 'capybara', 'a2', and 'a2_2' data from poe_search.db

DB_PATH="$(dirname "$0")/../poe_search.db"

if [ ! -f "$DB_PATH" ]; then
  echo "Database file not found at $DB_PATH"
  exit 1
fi

sqlite3 "$DB_PATH" <<SQL
-- Delete messages for conversations with these bots
DELETE FROM messages WHERE conversation_id IN (SELECT id FROM conversations WHERE bot IN ('chinchilla', 'beaver', 'capybara', 'a2', 'a2_2'));
-- Delete conversations
DELETE FROM conversations WHERE bot IN ('chinchilla', 'beaver', 'capybara', 'a2', 'a2_2');
-- Delete from bots table
DELETE FROM bots WHERE id IN ('chinchilla', 'beaver', 'capybara', 'a2', 'a2_2');
-- Delete from FTS index
DELETE FROM messages_fts WHERE conversation_id IN (SELECT id FROM conversations WHERE bot IN ('chinchilla', 'beaver', 'capybara', 'a2', 'a2_2'));
SQL

if [ $? -eq 0 ]; then
  echo "✅ Successfully removed all 'chinchilla', 'beaver', 'capybara', 'a2', and 'a2_2' data from the database."
else
  echo "❌ Failed to clean the database."
fi 