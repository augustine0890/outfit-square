#!/bin/bash

# Attempt to set the Python version to 3.11 for the project
# Ensure the specified Python version is used for the project
PYTHON_PATH="/usr/bin/python3.11"

# Remove the existing virtual environment to reset any issues
poetry env remove python3.11

# Re-use the Python version for the project
poetry env use $PYTHON_PATH || poetry env use python3.11

# Verify Python version is set correctly
poetry run python --version 2>&1 | grep -q "Python 3.11"
if [ $? -ne 0 ]; then
    echo "Failed to use Python 3.11. Please ensure Python 3.11 is installed and accessible to Poetry."
    exit 1
fi

# Install dependencies to ensure they are up to date
poetry install --no-dev
# poetry install

# Check if the application is already running
if [ -f outfit-square.pid ]; then
    OLD_PID=$(cat outfit-square.pid)
    if kill -0 $OLD_PID > /dev/null 2>&1; then
        echo "Stopping running application..."
        kill $OLD_PID
        while kill -0 $OLD_PID > /dev/null 2>&1; do sleep 1; done
    fi
fi

# Remove old log and pid files
rm -f outfit-square.log outfit-square.pid

# Start the application
echo "Starting outfit-square application..."
# Use 'exec -a' to name the process. Note: This might not be effective in all systems.
exec -a outfit-square poetry run python main.py > outfit-square.log 2>&1 & echo $! > outfit-square.pid

sleep 5 # Give some time for the application to start or fail

# Check if the application started successfully
if [ -s outfit-square.pid ]; then
    PID=$(cat outfit-square.pid)
    if ps -p $PID > /dev/null; then
        echo "outfit-square application has been started, PID $PID."
    else
        echo "Application PID exists but process is not running."
        rm -f outfit-square.pid # Clean up PID file as process did not start
    fi
else
    echo "Failed to start the outfit-square application. No PID file was created."
fi
