#!/bin/bash
# Simple test runner script

echo "🧪 Running C to PlantUML Converter Tests"
echo "========================================"

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

# Run the test suite
$PYTHON_CMD run_all_tests.py

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