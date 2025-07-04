#!/usr/bin/env bash

# Run Poe Search GUI from project root
set -e

# Activate virtual environment if it exists
if [ -d ".venv" ]; then
    source .venv/bin/activate
    echo "Activated virtual environment."
elif [ -d "venv" ]; then
    source venv/bin/activate
    echo "Activated virtual environment (legacy)."
else
    echo "No virtual environment found. Please create one with 'python -m venv .venv' and install dependencies."
    exit 1
fi

# Run the GUI
PYTHONPATH="$PWD/src:$PYTHONPATH" python -m poe_search.gui "$@" 