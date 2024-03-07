#!/bin/bash

# Optional: Activate virtual environment if needed and if Poetry has been used to create it
# source $HOME/.poetry/env

# Note: Assumes the Python project is configured to use Poetry

# Optional: Set any environment variables your Python application requires
# export VARIABLE_NAME=value

# Ensure the specified Python version is used for the project
# Adjust 'python3.11' to the path of the desired Python executable if necessary
poetry env use python3.11

# Check if the correct Python version is now set
if [ $? -ne 0 ]; then
    echo "Failed to set Python version to 3.11. Please ensure Python 3.11 is installed."
    exit 1
fi

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

# Attempt to start the application regardless of the previous steps' success
echo "Starting outfit-square application..."

# Start your Python application in the background, redirect output to a log file,
# and store its PID in a separate file. Attempt to start even if there were issues.
poetry run python main.py > outfit-square.log 2>&1 & echo $! > outfit-square.pid

if [ -f outfit-square.pid ]; then
    if [ -s outfit-square.pid ]; then
        echo "outfit-square application has been started."
    else
        echo "Failed to start the outfit-square application. PID file is empty."
    fi
else
    echo "Failed to start the outfit-square application. No PID file was created."
fi
