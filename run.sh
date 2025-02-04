#!/bin/bash

# Function to deactivate virtualenv and exit
cleanup() {
    if [ -n "$VIRTUAL_ENV" ]; then
        echo "Deactivating virtual environment"
        deactivate
    fi
    exit 0
}

# Search for .env file and then export the variables
if [ -f .env ]; then
    export $(grep -v '^#' .env | xargs)
fi

# Check for DOPPLER_TOKEN environment variable
if [ -z "$DOPPLER_TOKEN" ]; then
    echo "DOPPLER_TOKEN is missing"
    exit 1
fi

# Trap SIGINT (Ctrl + C) and call cleanup
trap cleanup SIGINT

# Start the contacts app
 
# Check if running inside Docker
if [ -f /.dockerenv ]; then
    echo "[+] Running inside Docker"
    doppler run --command='gunicorn --log-level info --access-logfile - -w 4 -b 0.0.0.0:$PORT server:app'
else
    echo "[+] Running on local machine"
    source .venv/bin/activate

    # Run Gunicorn server
    doppler run --command='gunicorn --log-level info --access-logfile - -w 4 -b 0.0.0.0:$PORT server:app'
    deactivate
fi