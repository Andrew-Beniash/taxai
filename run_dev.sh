#!/bin/bash

# TaxAI Development Server Script

# Exit on error
set -e

# Function to display status messages
print_status() {
    echo -e "\n\033[1;34m$1\033[0m"
}

# Check if virtual environment is activated
if [[ "$VIRTUAL_ENV" == "" ]]; then
    print_status "Activating virtual environment..."
    source venv/bin/activate
    if [[ "$VIRTUAL_ENV" == "" ]]; then
        echo -e "\033[1;31mFailed to activate virtual environment. Run 'source venv/bin/activate' first.\033[0m"
        exit 1
    fi
fi

# Change to src directory and run the application
print_status "Starting development server..."
cd src
python main.py
