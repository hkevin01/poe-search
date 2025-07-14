#!/usr/bin/env bash

# Run Poe Search GUI from project root
set -e

# Create logs directory if it doesn't exist
mkdir -p logs

# Set up log file (overwrite on each startup)
LOG_FILE="logs/gui_startup_and_runtime.log"
echo "=== Poe Search GUI Startup - $(date) ===" > "$LOG_FILE"

# Function to log and echo messages
log_and_echo() {
    echo "$1" | tee -a "$LOG_FILE"
}

# Activate virtual environment if it exists
if [ -d ".venv" ]; then
    source .venv/bin/activate
    log_and_echo "Activated virtual environment."
elif [ -d "venv" ]; then
    source venv/bin/activate
    log_and_echo "Activated virtual environment (legacy)."
else
    log_and_echo "ERROR: No virtual environment found. Please create one with 'python -m venv .venv' and install dependencies."
    exit 1
fi

# Log startup information
log_and_echo "Python path: $PWD/src:$PYTHONPATH"
log_and_echo "Starting Poe Search GUI..."
log_and_echo "All output will be logged to: $LOG_FILE"
echo "" >> "$LOG_FILE"

# Run the GUI with all output redirected to both terminal and log file
PYTHONPATH="$PWD/src:$PYTHONPATH" python -m poe_search.gui "$@" 2>&1 | tee -a "$LOG_FILE"

# Log shutdown
echo "" >> "$LOG_FILE"
echo "=== GUI Session Ended - $(date) ===" >> "$LOG_FILE" 