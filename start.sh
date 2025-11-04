#!/bin/bash
# Startup script for Local LLM Desktop Chat Application
# This script activates the virtual environment and runs the application

# Navigate to the script directory
cd "$(dirname "$0")"

# Activate virtual environment
source venv/bin/activate

# Run the application
python run.py
