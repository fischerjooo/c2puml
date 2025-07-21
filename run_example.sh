#!/bin/bash

# Run the example workflow using the provided config.json and source files

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Clean previous output
echo "Cleaning previous output..."
rm -rf plantuml_output
mkdir -p plantuml_output

# Run the workflow

echo "Running example workflow with config.json..."
python3 main.py workflow example/source example/config.json

# Output location
echo "PlantUML diagrams generated in: $SCRIPT_DIR/plantuml_output"