#!/bin/bash

# Optional: Activate virtual environment if needed and if Poetry has been used to create it
# source $HOME/.poetry/env

# Note: Assumes the Python project is configured to use Poetry

# Optional: Set any environment variables your Python application requires
# export VARIABLE_NAME=value

# Install dependencies to ensure they are up to date
poetry install

# Check if the application is already running
if [ -f outfit-square.pid ]; then
    OLD_PID=$(cat outfit-square.pid)
    if kill -0 $OLD_PID > /dev/null 2>&1; then
        echo "Stopping running application..."
        kill $OLD_PID
        # wait for the old process to stop
        while kill -0 $OLD_PID > /dev/null 2>&1; do
            sleep 1
        done
    fi
fi

# Remove old log and pid files
rm -f outfit-square.log outfit-square.pid

# Print out a message indicating the application is starting
echo "Starting outfit-square application..."

# Start your Python application in the background, redirect output to a log file,
# and store its PID in a separate file
# Using 'main.py' as the entry point for the application
poetry run python main.py > outfit-square.log 2>&1 & echo $! > outfit-square.pid

# Print out a message indicating the application has been started
echo "outfit-square application has been started."
