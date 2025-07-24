#!/usr/bin/env bash
# Script: kill_frozen_vscode.sh
# Purpose: Kill all frozen or zombie VS Code and Python GUI processes for this project

set -e

# Kill all python processes running poe_search.gui
PIDS=$(pgrep -f "python -m poe_search.gui")
if [ -n "$PIDS" ]; then
  echo "Killing Poe Search GUI processes: $PIDS"
  kill $PIDS || true
fi

# Kill all VS Code processes (if any are frozen)
VSCODE_PIDS=$(pgrep -f "[c]ode")
if [ -n "$VSCODE_PIDS" ]; then
  echo "Killing VS Code processes: $VSCODE_PIDS"
  kill $VSCODE_PIDS || true
fi

# Optionally, kill any zombie python processes (uncomment if needed)
# ZOMBIE_PIDS=$(ps aux | awk '/python/ && /Z/ {print $2}')
# if [ -n "$ZOMBIE_PIDS" ]; then
#   echo "Killing zombie python processes: $ZOMBIE_PIDS"
#   kill -9 $ZOMBIE_PIDS || true
# fi

echo "Cleanup complete."
