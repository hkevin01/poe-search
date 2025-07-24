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
    # Ensure required packages are installed
    pip install --quiet fastapi-poe browser-cookie3 poe-api-wrapper selenium webdriver-manager PyQt6
    log_and_echo "Ensured required Python packages are installed."
elif [ -d "venv" ]; then
    source venv/bin/activate
    log_and_echo "Activated virtual environment (legacy)."
    pip install --quiet fastapi-poe browser-cookie3 poe-api-wrapper selenium webdriver-manager PyQt6
    log_and_echo "Ensured required Python packages are installed."
else
    log_and_echo "ERROR: No virtual environment found. Please create one with 'python -m venv .venv' and install dependencies."
    exit 1
fi

# Terminate any prior running instances of Poe Search GUI
log_and_echo "Checking for existing Poe Search GUI processes..."
RUNNING_PIDS=$(pgrep -f "python -m poe_search.gui")
if [ -n "$RUNNING_PIDS" ]; then
    log_and_echo "Terminating existing Poe Search GUI processes: $RUNNING_PIDS"
    kill $RUNNING_PIDS || true
    sleep 1
fi

# Log startup information
log_and_echo "Python path: $PWD/src:$PYTHONPATH"
log_and_echo "Starting Poe Search GUI..."
log_and_echo "All output will be logged to: $LOG_FILE"
echo "" >> "$LOG_FILE"

# Run the GUI in the background, redirecting output to both terminal and log file
PYTHONPATH="$PWD/src:$PYTHONPATH" python -m poe_search.gui "$@" 2>&1 | tee -a "$LOG_FILE" &
GUI_PID=$!

# Trap exit and interrupt signals to ensure cleanup
cleanup() {
    log_and_echo "Cleaning up any remaining Poe Search GUI processes..."
    RUNNING_PIDS=$(pgrep -f "python -m poe_search.gui")
    if [ -n "$RUNNING_PIDS" ]; then
        log_and_echo "Killing remaining Poe Search GUI processes: $RUNNING_PIDS"
        kill $RUNNING_PIDS || true
        sleep 1
    fi
    echo "" >> "$LOG_FILE"
    echo "=== GUI Session Ended - $(date) ===" >> "$LOG_FILE"
}
trap cleanup EXIT INT TERM

# Wait for the GUI process to finish
wait $GUI_PID