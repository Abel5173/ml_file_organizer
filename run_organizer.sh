#!/bin/bash

# Script to run ml_file_organizer main.py for batch processing

# Define project directory
PROJECT_DIR="/mnt/ssd-extra/Projects/ml_file_organizer"
VENV_DIR="$PROJECT_DIR/.venv"
LOG_FILE="$PROJECT_DIR/organizer.log"

# Ensure log file exists
touch "$LOG_FILE" 2>/dev/null || {
    echo "$(date): ERROR: Cannot create log file $LOG_FILE" >&2
    exit 1
}

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

# Check if main.py exists
if [ ! -f "$PROJECT_DIR/main.py" ]; then
    echo "$(date): ERROR: main.py not found in $PROJECT_DIR" >> "$LOG_FILE"
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