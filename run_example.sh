#!/usr/bin/env bash

# Clean previous output
echo "Cleaning previous output..."
rm -rf plantuml_output example/output

# Run the full workflow using the new CLI interface
echo "Running example workflow with config.json..."
python3 main.py --config example/config.json

echo "PlantUML diagrams generated in: ./plantuml_output or ./output (see config.json)"