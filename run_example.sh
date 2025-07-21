#!/usr/bin/env bash

# Clean previous output
echo "Cleaning previous output..."
rm -rf output example/output

# Run the full workflow using the new CLI interface
echo "Running example workflow with config.json..."
python3 main.py --config example/config.json --verbose

echo "PlantUML diagrams generated in: ./output (see config.json)"