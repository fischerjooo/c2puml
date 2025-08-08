#!/usr/bin/env bash

# Get script directory and change to project root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR/.."

# Clean previous output
echo "Cleaning previous output..."
rm -rf artifacts/output_example tests/example/artifacts/output_example

# Run the full workflow using the standalone main.py
echo "Running example workflow with config.json..."
python3 main.py --config tests/example/config.json

echo "PlantUML diagrams generated in: ./artifacts/output_example (see config.json)"

# Run example tests via pytest
echo "Running example tests with pytest..."
python3 -m pytest tests/example -q | cat