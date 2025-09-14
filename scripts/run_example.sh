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

# Run example tests via pytest if available, otherwise unittest
echo "Running example tests..."
python3 - <<'PY'
import importlib.util, os, sys, subprocess

root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
has_pytest = importlib.util.find_spec('pytest') is not None
cmd = [sys.executable, '-m', 'pytest', 'tests/example', '-q'] if has_pytest else [sys.executable, '-m', 'unittest', 'tests/example/test_901_basic_example.py', '-q']
print(f"Using {'pytest' if has_pytest else 'unittest'} to run example tests...")
subprocess.run(cmd, check=False)
PY