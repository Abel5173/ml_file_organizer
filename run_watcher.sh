#!/bin/bash

# Script to run ml_file_organizer watcher.py for real-time monitoring

# Define project directory (adjust if different)
PROJECT_DIR="$HOME/abel/Projects/ml_file_organizer"
VENV_DIR="$PROJECT_DIR/.venv"
LOG_FILE="$PROJECT_DIR/watcher.log"
PID_FILE="$PROJECT_DIR/watcher.pid"

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

# Check if watcher is already running
if [ -f "$PID_FILE" ]; then
    PID=$(cat "$PID_FILE")
    if ps -p "$PID" > /dev/null; then
        echo "$(date): Watcher is already running with PID $PID" >> "$LOG_FILE"
        exit 0
    else
        echo "$(date): Stale PID file found, removing" >> "$LOG_FILE"
        rm "$PID_FILE"
    fi
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

# Run watcher.py in background with logging
echo "$(date): Starting ml_file_organizer (watcher.py)" >> "$LOG_FILE"
nohup python3 watcher.py >> "$LOG_FILE" 2>&1 &
PID=$!
echo $PID > "$PID_FILE"

# Check if process started
sleep 2
if ps -p "$PID" > /dev/null; then
    echo "$(date): Watcher started successfully with PID $PID" >> "$LOG_FILE"
else
    echo "$(date): ERROR: Watcher failed to start" >> "$LOG_FILE"
    rm "$PID_FILE"
    exit 1
fi

# Deactivate virtual environment
deactivate

exit 0
