#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Clean previous output
echo "Cleaning previous output..."
rm -rf "artifacts/output_example"
rm -rf "tests/example/artifacts/output_example"

# Run the full workflow using the new CLI interface
echo "Running example workflow with config.json..."
export PATH="/home/ubuntu/.local/bin:$PATH"
export PYTHONPATH=src
python3 -m c2puml.main --config tests/example/config.json --verbose

echo "PlantUML diagrams generated in: ./artifacts/output_example (see config.json)"

# Run assertions to validate the generated PUML files
echo "Running assertions to validate generated PUML files..."
cd tests/example
python3 test-example.py