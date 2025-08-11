#!/bin/bash
# Simple test runner script

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "🧪 Running C to PlantUML Converter Tests"
echo "========================================"
echo "Script directory: $SCRIPT_DIR"

# Change to the project root directory (parent of scripts)
cd "$SCRIPT_DIR/.."

# Run mapping validation first
echo "🔎 Pre-check: Validating tests mapping rules..."
python3 scripts/check_tests_mapping.py || { echo "❌ Test mapping validation failed."; exit 1; }
echo "✅ Test mapping validation passed!"

# Detect Python version
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
elif command -v python &> /dev/null; then
    PYTHON_CMD="python"
else
    echo "❌ Error: Python not found. Please install Python 3.8+"
    exit 1
fi

echo "🐍 Using Python: $($PYTHON_CMD --version)"
echo "📁 Working directory: $(pwd)"

# Run all tests
echo "🎯 Running all tests..."
$PYTHON_CMD scripts/run_all_tests.py

# Check exit code and provide feedback
if [ $? -eq 0 ]; then
    echo ""
    echo "✅ All tests passed successfully!"
    exit 0
else
    echo ""
    echo "❌ Some tests failed. Please check the output above."
    exit 1
fi