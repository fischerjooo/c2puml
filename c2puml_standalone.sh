#!/bin/bash
# Standalone C to PlantUML converter for Unix-like systems
# This script allows running c2puml without installation

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed or not in PATH"
    echo "Please install Python 3.7 or later and try again"
    exit 1
fi

# Run the standalone script with all arguments passed through
python3 c2puml_standalone.py "$@"