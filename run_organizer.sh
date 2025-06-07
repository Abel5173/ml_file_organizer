#!/bin/bash

# Script to run ml_file_organizer main.py for batch processing

# Define project directory (adjust if different)
PROJECT_DIR="$HOME/abel/Projects/ml_file_organizer"
VENV_DIR="$PROJECT_DIR/.venv"
LOG_FILE="$PROJECT_DIR/organizer.log"

# Check if project directory exists
if [ ! -d "$PROJECT_DIR" ]; then
    echo "$(date): ERROR: Project directory $PROJECT_DIR not found" >> "$LOG_FILE"
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "$VENV_DIR" ]; then
    echo "$(date): ERROR: Virtual environment $VENV_DIR not found" >> "$LOG_FILE"
    exit 1
fi

# Check if .env file exists
if [ ! -f "$PROJECT_DIR/.env" ]; then
    echo "$(date): ERROR: .env file not found in $PROJECT_DIR" >> "$LOG_FILE"
    exit 1
fi

# Activate virtual environment
source "$VENV_DIR/bin/activate" || {
    echo "$(date): ERROR: Failed to activate virtual environment" >> "$LOG_FILE"
    exit 1
}

# Change to project directory
cd "$PROJECT_DIR" || {
    echo "$(date): ERROR: Failed to change to $PROJECT_DIR" >> "$LOG_FILE"
    exit 1
}

# Run main.py with logging
echo "$(date): Starting ml_file_organizer (main.py)" >> "$LOG_FILE"
python3 main.py >> "$LOG_FILE" 2>&1
EXIT_CODE=$?

# Log completion or error
if [ $EXIT_CODE -eq 0 ]; then
    echo "$(date): ml_file_organizer completed successfully" >> "$LOG_FILE"
else
    echo "$(date): ERROR: ml_file_organizer failed with exit code $EXIT_CODE" >> "$LOG_FILE"
fi

# Deactivate virtual environment
deactivate

exit $EXIT_CODE
