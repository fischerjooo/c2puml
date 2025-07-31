#!/usr/bin/env bash

# Clean previous output
echo "Cleaning previous output..."
rm -rf output tests/example/output

# Run the full workflow using the new CLI interface
echo "Running example workflow with config.json..."
PYTHONPATH=src python3 -m c2puml.main --config tests/example/config.json

echo "PlantUML diagrams generated in: ./output (see config.json)"

# Run assertions to validate the generated PUML files
echo "Running assertions to validate generated PUML files..."
cd tests/example && python3 test-example.py