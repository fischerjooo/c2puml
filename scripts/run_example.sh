#!/usr/bin/env bash

# Get script directory and change to project root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR/.."

# Clean previous output
echo "Cleaning previous output..."
rm -rf artifacts/output_example tests/example/artifacts/output_example

# Run the full workflow using the standalone c2puml.py
echo "Running example workflow with config.json..."
python3 c2puml.py --config tests/example/config.json

echo "PlantUML diagrams generated in: ./artifacts/output_example (see config.json)"

# Run assertions to validate the generated PUML files
echo "Running assertions to validate generated PUML files..."
cd tests/example && python3 test-example.py